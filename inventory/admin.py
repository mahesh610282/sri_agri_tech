from django.contrib import admin
from .models import StockTransaction

@admin.register(StockTransaction)
class StockTransactionAdmin(admin.ModelAdmin):
    list_display = ("product", "transaction_type", "quantity", "balance_after", "created_by", "created_at")
    list_filter = ("transaction_type", "created_at")
    search_fields = ("product__name", "product__product_code", "reference")
