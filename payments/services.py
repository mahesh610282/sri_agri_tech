from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import transaction
from billing.models import Bill
from customers.models import Customer
from .models import Payment

@transaction.atomic
def record_payment(*, bill_id, amount, method, user=None, reference_number="", notes=""):
    amount = Decimal(str(amount))
    if amount <= 0:
        raise ValidationError("Payment must be greater than zero.")

    bill = Bill.objects.select_for_update().select_related("customer").get(pk=bill_id)
    if amount > bill.remaining_amount:
        raise ValidationError("Payment cannot be greater than remaining amount.")

    payment = Payment.objects.create(
        customer=bill.customer,
        bill=bill,
        amount=amount,
        payment_method=method,
        reference_number=reference_number,
        notes=notes,
        created_by=user,
    )

    bill.paid_amount += amount
    bill.recalculate()
    bill.save(update_fields=["paid_amount", "remaining_amount", "payment_status"])

    customer = Customer.objects.select_for_update().get(pk=bill.customer_id)
    customer.outstanding_balance = max(customer.outstanding_balance - amount, Decimal("0.00"))
    customer.save(update_fields=["outstanding_balance"])

    return payment
