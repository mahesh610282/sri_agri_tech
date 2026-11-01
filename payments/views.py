from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from accounts.decorators import admin_required
from billing.models import Bill
from .services import record_payment

@admin_required
def payment_create(request, bill_id):
    bill = get_object_or_404(Bill, pk=bill_id)
    if request.method == "POST":
        try:
            record_payment(
                bill_id=bill_id,
                amount=request.POST["amount"],
                method=request.POST["payment_method"],
                reference_number=request.POST.get("reference_number", ""),
                notes=request.POST.get("notes", ""),
                user=request.user,
            )
            messages.success(request, "Payment recorded successfully.")
            return redirect("billing:detail", pk=bill_id)
        except Exception as exc:
            messages.error(request, str(exc))
    return render(request, "payments/form.html", {"bill": bill})
