from decimal import Decimal
from datetime import date

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from customers.models import Customer
from products.models import Product
from inventory.models import StockTransaction
from payments.models import Payment

from .models import Bill, BillItem, BillPayment


# ============================================================
# BILL NUMBER
# ============================================================

def generate_bill_number():
    """
    Generate bill numbers like:

    SMAC-2026-0001
    SMAC-2026-0002
    SMAC-2026-0003
    """

    year = date.today().year
    prefix = f"SMAC-{year}-"

    last_bill = (
        Bill.objects
        .filter(bill_number__startswith=prefix)
        .order_by("-id")
        .first()
    )

    if last_bill:
        try:
            last_number = int(
                last_bill.bill_number.split("-")[-1]
            )
        except (ValueError, IndexError):
            last_number = 0
    else:
        last_number = 0

    return f"{prefix}{last_number + 1:04d}"


# ============================================================
# CUSTOMER BALANCE
# ============================================================

def refresh_customer_balance(customer):
    """
    Recalculate customer outstanding balance
    from all bills.
    """

    total = sum(
        (
            bill.remaining_amount
            for bill in customer.bills.all()
        ),
        Decimal("0.00")
    )

    customer.outstanding_balance = total

    customer.save(
        update_fields=["outstanding_balance"]
    )

    return total


# ============================================================
# CREATE BILL
# ============================================================

@transaction.atomic
def create_bill(
    *,
    customer_id,
    items,
    discount=0,
    paid_amount=0,
    payment_method="CASH",
    reference_number="",
    notes="",
    user=None
):
    """
    Create a new bill.

    paid_amount is treated as a customer-level payment.

    Example:

    Old outstanding = ₹1500
    New bill        = ₹1500
    Payment         = ₹2700

    Allocation:

    Old bill = ₹1500
    New bill = ₹1200
    """

    # --------------------------------------------------------
    # Get customer and lock the row
    # --------------------------------------------------------

    customer = (
        Customer.objects
        .select_for_update()
        .get(pk=customer_id)
    )

    # --------------------------------------------------------
    # Convert values to Decimal
    # --------------------------------------------------------

    discount = Decimal(
        str(discount or "0")
    )

    paid_amount = Decimal(
        str(paid_amount or "0")
    )

    # --------------------------------------------------------
    # Validate discount
    # --------------------------------------------------------

    if discount < 0:
        raise ValidationError(
            "Discount cannot be negative."
        )

    # --------------------------------------------------------
    # Validate payment
    # --------------------------------------------------------

    if paid_amount < 0:
        raise ValidationError(
            "Payment cannot be negative."
        )

    # --------------------------------------------------------
    # Validate items
    # --------------------------------------------------------

    if not items:
        raise ValidationError(
            "At least one product is required."
        )

    # --------------------------------------------------------
    # Product locking
    # --------------------------------------------------------

    locked_products = {}

    subtotal = Decimal("0.00")

    # --------------------------------------------------------
    # Validate products and stock
    # --------------------------------------------------------

    for row in items:

        product_id = row.get("product_id")

        quantity = Decimal(
            str(row.get("quantity", "0"))
        )

        # Quantity validation
        if quantity <= 0:
            raise ValidationError(
                "Quantity must be greater than zero."
            )

        # Get product with row lock
        product = (
            Product.objects
            .select_for_update()
            .get(pk=product_id)
        )

        # Product active validation
        if not product.active:
            raise ValidationError(
                f"{product.name} is inactive."
            )

        # Stock validation
        if quantity > product.stock_quantity:
            raise ValidationError(
                f"Insufficient stock available "
                f"for {product.name}. "
                f"Available: {product.stock_quantity}"
            )

        # ----------------------------------------------------
        # Same product added multiple times
        # ----------------------------------------------------

        if product.pk in locked_products:

            old_product, old_quantity = (
                locked_products[product.pk]
            )

            total_quantity = (
                old_quantity + quantity
            )

            if total_quantity > product.stock_quantity:
                raise ValidationError(
                    f"Insufficient stock available "
                    f"for {product.name}."
                )

            locked_products[product.pk] = (
                product,
                total_quantity
            )

        else:

            locked_products[product.pk] = (
                product,
                quantity
            )

        # ----------------------------------------------------
        # Calculate subtotal
        # ----------------------------------------------------

        subtotal += (
            quantity *
            product.selling_price
        )

    # ========================================================
    # CALCULATE BILL TOTAL
    # ========================================================

    base_total = max(
        subtotal - discount,
        Decimal("0.00")
    )

    # ========================================================
    # GET CUSTOMER PREVIOUS OUTSTANDING
    # ========================================================

    customer_outstanding_before = sum(
        (
            bill.remaining_amount
            for bill in (
                customer.bills
                .select_for_update()
                .filter(
                    remaining_amount__gt=0
                )
            )
        ),
        Decimal("0.00")
    )

    # ========================================================
    # TOTAL PAYABLE
    # ========================================================

    total_payable = (
        customer_outstanding_before +
        base_total
    )

    # Payment cannot exceed total customer outstanding
    if paid_amount > total_payable:
        raise ValidationError(
            f"Payment ₹{paid_amount} is greater "
            f"than total customer outstanding "
            f"₹{total_payable}."
        )

    # ========================================================
    # CREATE BILL
    # ========================================================

    bill = Bill.objects.create(
        bill_number=generate_bill_number(),
        customer=customer,
        discount=discount,
        base_total=base_total,
        interest_amount=Decimal("0.00"),
        grand_total=base_total,
        paid_amount=Decimal("0.00"),
        remaining_amount=base_total,
        payment_status=Bill.PaymentStatus.UNPAID,
        created_by=user,
    )

    # ========================================================
    # CREATE BILL ITEMS + REDUCE STOCK
    # ========================================================

    for product, quantity in locked_products.values():

        line_total = (
            quantity *
            product.selling_price
        )

        BillItem.objects.create(
            bill=bill,
            product=product,
            quantity=quantity,
            unit_price=product.selling_price,
            line_total=line_total
        )

        # ----------------------------------------------------
        # Reduce stock
        # ----------------------------------------------------

        product.stock_quantity -= quantity

        product.save(
            update_fields=["stock_quantity"]
        )

        # ----------------------------------------------------
        # Stock transaction
        # ----------------------------------------------------

        StockTransaction.objects.create(
            product=product,
            transaction_type=(
                StockTransaction.Type.SALE
            ),
            quantity=quantity,
            balance_after=product.stock_quantity,
            reference=bill.bill_number,
            created_by=user,
        )

    # ========================================================
    # RECALCULATE BILL
    # ========================================================

    bill.recalculate()

    bill.save(
        update_fields=[
            "subtotal",
            "base_total",
            "grand_total",
            "remaining_amount",
            "payment_status",
            "updated_at",
        ]
    )

    # ========================================================
    # UPDATE CUSTOMER BALANCE
    # ========================================================

    refresh_customer_balance(customer)

    # ========================================================
    # ALLOCATE PAYMENT
    # ========================================================

    if paid_amount > 0:

        allocate_customer_payment(
            customer_id=customer.id,
            amount=paid_amount,
            payment_method=payment_method,
            reference_number=reference_number,
            notes=notes,
            user=user,
        )

    else:

        refresh_customer_balance(customer)

    return bill


# ============================================================
# CUSTOMER PAYMENT
# ============================================================

@transaction.atomic
def allocate_customer_payment(
    *,
    customer_id,
    amount,
    payment_method="CASH",
    reference_number="",
    notes="",
    user=None
):
    """
    Record customer payment.

    Payment is allocated to oldest unpaid bills first.

    Example:

    Bill 1 = ₹1500
    Bill 2 = ₹1500

    Payment = ₹2700

    Allocation:

    Bill 1 = ₹1500
    Bill 2 = ₹1200
    """

    # --------------------------------------------------------
    # Convert amount to Decimal
    # --------------------------------------------------------

    amount = Decimal(
        str(amount or "0")
    )

    if amount <= 0:
        raise ValidationError(
            "Payment amount must be greater than zero."
        )

    # --------------------------------------------------------
    # Lock customer
    # --------------------------------------------------------

    customer = (
        Customer.objects
        .select_for_update()
        .get(pk=customer_id)
    )

    # ========================================================
    # APPLY INTEREST BEFORE PAYMENT
    # ========================================================

    apply_customer_interest(
        customer=customer,
        user=user
    )

    # ========================================================
    # GET UNPAID BILLS
    # ========================================================

    bills = list(
        Bill.objects
        .select_for_update()
        .filter(
            customer=customer,
            remaining_amount__gt=0
        )
        .order_by("created_at", "id")
    )

    # ========================================================
    # TOTAL OUTSTANDING
    # ========================================================

    total_outstanding = sum(
        (
            bill.remaining_amount
            for bill in bills
        ),
        Decimal("0.00")
    )

    if amount > total_outstanding:
        raise ValidationError(
            f"Payment ₹{amount} cannot exceed "
            f"customer outstanding "
            f"₹{total_outstanding}."
        )

    # ========================================================
    # CREATE PAYMENT
    # ========================================================

    payment = Payment.objects.create(
        customer=customer,
        amount=amount,
        payment_method=payment_method,
        reference_number=reference_number or "",
        notes=notes or "",
        created_by=user,
    )

    remaining_payment = amount

    # ========================================================
    # FIFO PAYMENT ALLOCATION
    # ========================================================

    for bill in bills:

        if remaining_payment <= 0:
            break

        allocation = min(
            remaining_payment,
            bill.remaining_amount
        )

        if allocation <= 0:
            continue

        # ----------------------------------------------------
        # Create bill-payment allocation
        # ----------------------------------------------------

        BillPayment.objects.create(
            bill=bill,
            payment=payment,
            amount=allocation,
        )

        # ----------------------------------------------------
        # Update bill paid amount
        # ----------------------------------------------------

        bill.paid_amount += allocation

        bill.recalculate()

        bill.save(
            update_fields=[
                "paid_amount",
                "grand_total",
                "remaining_amount",
                "payment_status",
                "subtotal",
                "base_total",
                "interest_amount",
                "updated_at",
            ]
        )

        remaining_payment -= allocation

    # ========================================================
    # REFRESH CUSTOMER BALANCE
    # ========================================================

    refresh_customer_balance(customer)

    return payment


# ============================================================
# BILL PAYMENT
# ============================================================

@transaction.atomic
def pay_bill(
    *,
    bill_id,
    amount,
    payment_method="CASH",
    reference_number="",
    notes="",
    user=None
):
    """
    Pay a particular bill.

    Uses the same customer-level payment system.

    Note:
    The payment is allocated oldest-first, so if the
    customer has an older outstanding bill, that bill
    will be paid first.
    """

    # --------------------------------------------------------
    # Get bill
    # --------------------------------------------------------

    bill = (
        Bill.objects
        .select_for_update()
        .select_related("customer")
        .get(pk=bill_id)
    )

    # --------------------------------------------------------
    # Check bill status
    # --------------------------------------------------------

    if bill.remaining_amount <= 0:
        raise ValidationError(
            "This bill is already fully paid."
        )

    # --------------------------------------------------------
    # Convert amount
    # --------------------------------------------------------

    amount = Decimal(
        str(amount or "0")
    )

    if amount <= 0:
        raise ValidationError(
            "Payment amount must be greater than zero."
        )

    # ========================================================
    # CUSTOMER LEVEL PAYMENT
    # ========================================================

    return allocate_customer_payment(
        customer_id=bill.customer_id,
        amount=amount,
        payment_method=payment_method,
        reference_number=reference_number,
        notes=notes,
        user=user,
    )


# ============================================================
# INTEREST
# ============================================================

INTEREST_RATE = Decimal("0.015")


def completed_months(start_date, current_date):
    """
    Calculate completed months.

    Examples:

    1 Jan → 1 Feb = 1 month
    1 Jan → 1 Mar = 2 months
    1 Jan → 20 Jan = 0 months
    """

    months = (
        (current_date.year - start_date.year) * 12
        + current_date.month
        - start_date.month
    )

    if current_date.day < start_date.day:
        months -= 1

    return max(months, 0)


# ============================================================
# APPLY BILL INTEREST
# ============================================================

@transaction.atomic
def apply_bill_interest(
    *,
    bill,
    user=None
):
    """
    Apply 1.5% interest for every completed month.

    Example:

    Outstanding = ₹100

    Interest = ₹100 × 1.5%
             = ₹1.50

    Interest is applied only once per completed month.
    """

    # --------------------------------------------------------
    # Already paid
    # --------------------------------------------------------

    if bill.remaining_amount <= 0:
        return bill

    # --------------------------------------------------------
    # Current date
    # --------------------------------------------------------

    today = timezone.localdate()

    # --------------------------------------------------------
    # Bill date
    # --------------------------------------------------------

    bill_date = bill.created_at.date()

    # --------------------------------------------------------
    # Calculate completed months
    # --------------------------------------------------------

    months_completed = completed_months(
        bill_date,
        today
    )

    if months_completed <= 0:
        return bill

    # ========================================================
    # CHECK ALREADY APPLIED INTEREST
    # ========================================================

    if bill.interest_applied_until:

        already_applied_months = completed_months(
            bill_date,
            bill.interest_applied_until
        )

    else:

        already_applied_months = 0

    # --------------------------------------------------------
    # Months still requiring interest
    # --------------------------------------------------------

    months_to_apply = (
        months_completed -
        already_applied_months
    )

    if months_to_apply <= 0:
        return bill

    # ========================================================
    # CALCULATE INTEREST
    # ========================================================

    current_outstanding = bill.remaining_amount

    interest = (
        current_outstanding *
        INTEREST_RATE *
        months_to_apply
    ).quantize(
        Decimal("0.01")
    )

    # ========================================================
    # UPDATE INTEREST
    # ========================================================

    bill.interest_amount += interest

    bill.interest_applied_until = today

    # --------------------------------------------------------
    # Recalculate bill
    # --------------------------------------------------------

    bill.recalculate()

    bill.save(
        update_fields=[
            "interest_amount",
            "interest_applied_until",
            "grand_total",
            "remaining_amount",
            "payment_status",
            "updated_at",
        ]
    )

    return bill


# ============================================================
# CUSTOMER INTEREST
# ============================================================

def apply_customer_interest(
    *,
    customer,
    user=None
):
    """
    Apply interest to all unpaid bills
    belonging to the customer.
    """

    bills = (
        Bill.objects
        .select_for_update()
        .filter(
            customer=customer,
            remaining_amount__gt=0
        )
        .order_by("created_at", "id")
    )

    for bill in bills:

        apply_bill_interest(
            bill=bill,
            user=user
        )

    # --------------------------------------------------------
    # Refresh customer balance
    # --------------------------------------------------------

    refresh_customer_balance(customer)

    return customer