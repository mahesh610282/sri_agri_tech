from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import transaction
from .models import StockTransaction
from products.models import Product

@transaction.atomic
def add_stock(*, product_id, quantity, transaction_type, user=None, reference="", notes=""):
    quantity = Decimal(str(quantity))
    if quantity <= 0:
        raise ValidationError("Quantity must be greater than zero.")

    product = Product.objects.select_for_update().get(pk=product_id)
    if transaction_type == StockTransaction.Type.SALE:
        if quantity > product.stock_quantity:
            raise ValidationError("Insufficient stock available.")
        product.stock_quantity -= quantity
    else:
        product.stock_quantity += quantity

    product.save(update_fields=["stock_quantity"])
    StockTransaction.objects.create(
        product=product,
        transaction_type=transaction_type,
        quantity=quantity,
        balance_after=product.stock_quantity,
        reference=reference,
        notes=notes,
        created_by=user,
    )
    return product
