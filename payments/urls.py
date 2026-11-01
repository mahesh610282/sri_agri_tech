from django.urls import path
from .views import payment_create

app_name = "payments"

urlpatterns = [
    path("bill/<int:bill_id>/add/", payment_create, name="create"),
]
