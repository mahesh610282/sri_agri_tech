from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render
)

from accounts.decorators import admin_required
from customers.models import Customer
from products.models import Product

from .models import Bill
from .services import (
    create_bill,
    pay_bill,
    allocate_customer_payment,
)


# ============================================================
# BILL LIST
# ============================================================

@admin_required
def bill_list(request):

    q = request.GET.get(
        "q",
        ""
    ).strip()

    bills = (
        Bill.objects
        .select_related("customer")
        .all()
    )

    if q:
        bills = bills.filter(
            Q(customer__name__icontains=q)
            |
            Q(customer__mobile__icontains=q)
            |
            Q(bill_number__icontains=q)
        )

    return render(
        request,
        "billing/list.html",
        {
            "bills": bills.distinct(),
            "q": q,
        }
    )


# ============================================================
# CREATE BILL
# ============================================================

@admin_required
def create_bill_view(request):

    if request.method == "POST":

        try:

            product_ids = request.POST.getlist(
                "product_id[]"
            )

            quantities = request.POST.getlist(
                "quantity[]"
            )

            items = []

            for product_id, quantity in zip(
                product_ids,
                quantities
            ):

                if product_id and quantity:

                    items.append(
                        {
                            "product_id": product_id,
                            "quantity": quantity,
                        }
                    )

            bill = create_bill(
                customer_id=request.POST[
                    "customer_id"
                ],
                items=items,
                discount=request.POST.get(
                    "discount",
                    0
                ),
                paid_amount=request.POST.get(
                    "paid_amount",
                    0
                ),
                payment_method=request.POST.get(
                    "payment_method",
                    "CASH"
                ),
                reference_number=request.POST.get(
                    "reference_number",
                    ""
                ),
                notes=request.POST.get(
                    "notes",
                    ""
                ),
                user=request.user,
            )

            messages.success(
                request,
                (
                    f"Bill {bill.bill_number} "
                    f"created successfully."
                )
            )

            return redirect(
                "billing:detail",
                pk=bill.pk
            )

        except Exception as exc:

            messages.error(
                request,
                str(exc)
            )

    customers = (
        Customer.objects
        .filter(active=True)
        .order_by("name")
    )

    products = (
        Product.objects
        .filter(active=True)
        .order_by("name")
    )

    return render(
        request,
        "billing/create.html",
        {
            "customers": customers,
            "products": products,
        }
    )


# ============================================================
# BILL DETAIL
# ============================================================

@admin_required
def bill_detail(request, pk):

    bill = get_object_or_404(
        Bill.objects
        .select_related("customer")
        .prefetch_related(
            "items__product",
            "payment_allocations__payment"
        ),
        pk=pk
    )

    return render(
        request,
        "billing/detail.html",
        {
            "bill": bill
        }
    )


# ============================================================
# CUSTOMER PAYMENT
# ============================================================

@admin_required
def customer_payment(request):

    if request.method == "POST":

        try:

            payment = allocate_customer_payment(
                customer_id=request.POST[
                    "customer_id"
                ],
                amount=request.POST[
                    "amount"
                ],
                payment_method=request.POST.get(
                    "payment_method",
                    "CASH"
                ),
                reference_number=request.POST.get(
                    "reference_number",
                    ""
                ),
                notes=request.POST.get(
                    "notes",
                    ""
                ),
                user=request.user,
            )

            messages.success(
                request,
                (
                    f"Payment of ₹{payment.amount} "
                    f"recorded successfully."
                )
            )

            return redirect(
                "billing:payment"
            )

        except Exception as exc:

            messages.error(
                request,
                str(exc)
            )

    customers = (
        Customer.objects
        .filter(
            active=True,
            outstanding_balance__gt=0
        )
        .order_by("name")
    )

    return render(
        request,
        "billing/payment.html",
        {
            "customers": customers
        }
    )


# ============================================================
# PAY PARTICULAR BILL
# ============================================================

@admin_required
def bill_payment(request, pk):

    bill = get_object_or_404(
        Bill,
        pk=pk
    )

    if request.method == "POST":

        try:

            pay_bill(
                bill_id=bill.pk,
                amount=request.POST[
                    "amount"
                ],
                payment_method=request.POST.get(
                    "payment_method",
                    "CASH"
                ),
                reference_number=request.POST.get(
                    "reference_number",
                    ""
                ),
                notes=request.POST.get(
                    "notes",
                    ""
                ),
                user=request.user,
            )

            messages.success(
                request,
                "Payment recorded successfully."
            )

            return redirect(
                "billing:detail",
                pk=bill.pk
            )

        except Exception as exc:

            messages.error(
                request,
                str(exc)
            )

    return render(
        request,
        "billing/bill_payment.html",
        {
            "bill": bill
        }
    )