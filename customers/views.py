from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from accounts.decorators import admin_required, customer_required
from .forms import CustomerForm
from .models import Customer

@admin_required
def customer_list(request):
    q = request.GET.get("q", "").strip()
    qs = Customer.objects.all().order_by("-created_at")
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(mobile__icontains=q))
    return render(request, "customers/list.html", {"customers": qs, "q": q})

@admin_required
def customer_create(request):
    form = CustomerForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Customer created successfully.")
        return redirect("customers:list")
    return render(request, "customers/form.html", {"form": form, "title": "Add Customer"})

@admin_required
def customer_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    form = CustomerForm(request.POST or None, instance=customer)
    if form.is_valid():
        form.save()
        messages.success(request, "Customer updated successfully.")
        return redirect("customers:list")
    return render(request, "customers/form.html", {"form": form, "title": "Edit Customer"})

@admin_required
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    bills = customer.bills.select_related("customer").order_by("-created_at")
    return render(request, "customers/detail.html", {"customer": customer, "bills": bills})

@customer_required
def portal(request):
    customer = get_object_or_404(Customer, user=request.user)
    bills = customer.bills.order_by("-created_at")[:20]
    return render(request, "customers/portal.html", {"customer": customer, "bills": bills})
