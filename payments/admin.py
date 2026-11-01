from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "customer",
        "amount",
        "payment_method",
        "reference_number",
        "payment_date",
        "created_by",
    )

    search_fields = (
        "customer__name",
        "customer__mobile",
        "reference_number",
    )

    list_filter = (
        "payment_method",
        "payment_date",
    )

    readonly_fields = (
        "payment_date",
        "created_at",
    )

    ordering = (
        "-payment_date",
    )