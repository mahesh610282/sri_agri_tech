from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render
from accounts.decorators import admin_required
from customers.models import Customer
from products.models import Product
from billing.models import Bill
from payments.models import Payment

@admin_required
def home(request):
    today = __import__("django.utils.timezone", fromlist=["localdate"]).localdate()
    context = {
        "total_customers": Customer.objects.filter(active=True).count(),
        "total_products": Product.objects.filter(active=True).count(),
        "total_stock": Product.objects.aggregate(total=Sum("stock_quantity"))["total"] or 0,
        "today_sales": Bill.objects.filter(created_at__date=today).aggregate(total=Sum("grand_total"))["total"] or 0,
        "total_sales": Bill.objects.aggregate(total=Sum("grand_total"))["total"] or 0,
        "paid_amount": Payment.objects.aggregate(total=Sum("amount"))["total"] or 0,
        "outstanding": Customer.objects.aggregate(total=Sum("outstanding_balance"))["total"] or 0,
        "paid_bills": Bill.objects.filter(payment_status=Bill.PaymentStatus.PAID).count(),
        "unpaid_bills": Bill.objects.exclude(payment_status=Bill.PaymentStatus.PAID).count(),
        "low_stock_products": Product.objects.filter(stock_quantity__gt=0, stock_quantity__lte=__import__("django.db.models", fromlist=["F"]).F("low_stock_threshold")).count(),
    }
    return render(request, "dashboard/home.html", context)
