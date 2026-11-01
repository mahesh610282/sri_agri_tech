from django.contrib import messages
from django.shortcuts import redirect, render
from accounts.decorators import admin_required
from products.models import Product
from .models import StockTransaction
from .services import add_stock

@admin_required
def stock_list(request):
    products = Product.objects.select_related("category").order_by("name")
    transactions = StockTransaction.objects.select_related("product", "created_by")[:100]
    return render(request, "inventory/list.html", {"products": products, "transactions": transactions})

@admin_required
def stock_adjust(request):
    if request.method != "POST":
        return redirect("inventory:list")
    try:
        add_stock(
            product_id=request.POST["product_id"],
            quantity=request.POST["quantity"],
            transaction_type=request.POST["transaction_type"],
            user=request.user,
            reference=request.POST.get("reference", ""),
            notes=request.POST.get("notes", ""),
        )
        messages.success(request, "Stock updated.")
    except Exception as exc:
        messages.error(request, str(exc))
    return redirect("inventory:list")
