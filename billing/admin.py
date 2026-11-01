from django.contrib import admin

from .models import (
    Bill,
    BillItem,
    BillPayment,
)


class BillItemInline(admin.TabularInline):

    model = BillItem

    extra = 0

    readonly_fields = (
        "line_total",
    )


class BillPaymentInline(admin.TabularInline):

    model = BillPayment

    extra = 0

    readonly_fields = (
        "amount",
        "payment",
        "created_at",
    )


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):

    list_display = (
        "bill_number",
        "customer",
        "grand_total",
        "paid_amount",
        "remaining_amount",
        "payment_status",
        "created_at",
    )

    search_fields = (
        "bill_number",
        "customer__name",
        "customer__mobile",
    )

    list_filter = (
        "payment_status",
        "created_at",
    )

    readonly_fields = (
        "bill_number",
        "subtotal",
        "base_total",
        "grand_total",
        "paid_amount",
        "remaining_amount",
        "payment_status",
        "interest_amount",
        "interest_applied_until",
        "created_at",
        "updated_at",
    )

    inlines = [
        BillItemInline,
        BillPaymentInline,
    ]


@admin.register(BillPayment)
class BillPaymentAdmin(admin.ModelAdmin):

    list_display = (
        "bill",
        "payment",
        "amount",
        "created_at",
    )

    search_fields = (
        "bill__bill_number",
        "payment__customer__name",
        "payment__customer__mobile",
    )

    readonly_fields = (
        "bill",
        "payment",
        "amount",
        "created_at",
    )