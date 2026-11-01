from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.shortcuts import render
from accounts.decorators import admin_required
from billing.models import Bill
from customers.models import Customer
from payments.models import Payment
from products.models import Product

@admin_required
def reports_home(request):
    sales_by_status = Bill.objects.values("payment_status").annotate(total=Sum("grand_total"), count=Count("id"))
    outstanding = Customer.objects.filter(outstanding_balance__gt=0).order_by("-outstanding_balance")
    low_stock = Product.objects.filter(stock_quantity__lte=__import__("django.db.models", fromlist=["F"]).F("low_stock_threshold"))
    payments = Payment.objects.values("payment_method").annotate(total=Sum("amount")).order_by("-total")
    return render(request, "reports/home.html", {
        "sales_by_status": sales_by_status,
        "outstanding": outstanding,
        "low_stock": low_stock,
        "payments": payments,
    })
