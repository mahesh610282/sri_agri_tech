from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from customers.models import Customer
from products.models import Product
from payments.models import Payment


class Bill(models.Model):

    class PaymentStatus(models.TextChoices):
        PAID = "PAID", "Paid"
        PARTIALLY_PAID = "PARTIALLY_PAID", "Partially Paid"
        UNPAID = "UNPAID", "Unpaid"

    bill_number = models.CharField(
        max_length=30,
        unique=True,
        editable=False
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name="bills"
    )

    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00")
    )

    discount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[
            MinValueValidator(Decimal("0.00"))
        ]
    )

    # Original bill amount after discount
    base_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00")
    )

    # Interest accumulated on this bill
    interest_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00")
    )

    # base_total + interest
    grand_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00")
    )

    paid_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00")
    )

    remaining_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00")
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.UNPAID
    )

    interest_applied_until = models.DateField(
        null=True,
        blank=True
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_bills"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.bill_number

    def recalculate(self):
        """
        Recalculate bill totals and payment status.
        """

        self.subtotal = sum(
            (
                item.line_total
                for item in self.items.all()
            ),
            Decimal("0.00")
        )

        self.base_total = max(
            self.subtotal - self.discount,
            Decimal("0.00")
        )

        self.grand_total = (
            self.base_total +
            self.interest_amount
        )

        self.remaining_amount = max(
            self.grand_total - self.paid_amount,
            Decimal("0.00")
        )

        if self.remaining_amount == Decimal("0.00"):
            self.payment_status = self.PaymentStatus.PAID

        elif self.paid_amount > Decimal("0.00"):
            self.payment_status = (
                self.PaymentStatus.PARTIALLY_PAID
            )

        else:
            self.payment_status = self.PaymentStatus.UNPAID


class BillItem(models.Model):

    bill = models.ForeignKey(
        Bill,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="bill_items"
    )

    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        validators=[
            MinValueValidator(Decimal("0.001"))
        ]
    )

    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0.00"))
        ]
    )

    line_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00")
    )

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"

    def save(self, *args, **kwargs):

        self.line_total = (
            self.quantity *
            self.unit_price
        )

        super().save(*args, **kwargs)


class BillPayment(models.Model):
    """
    Connects the existing Payment record
    with one or more bills.

    Example:

    Payment = ₹2700

    Old Bill = ₹1500
    New Bill = ₹1500

    Allocation:

    Old Bill  -> ₹1500
    New Bill  -> ₹1200
    """

    bill = models.ForeignKey(
        Bill,
        on_delete=models.CASCADE,
        related_name="payment_allocations"
    )

    payment = models.ForeignKey(
        Payment,
        on_delete=models.PROTECT,
        related_name="bill_allocations"
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0.01"))
        ]
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return (
            f"{self.bill.bill_number} - "
            f"₹{self.amount}"
        )