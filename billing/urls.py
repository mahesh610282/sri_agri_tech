from django.urls import path

from .views import (
    bill_list,
    create_bill_view,
    bill_detail,
    customer_payment,
    bill_payment,
)

app_name = "billing"


urlpatterns = [

    path(
        "",
        bill_list,
        name="list"
    ),

    path(
        "create/",
        create_bill_view,
        name="create"
    ),

    path(
        "payment/",
        customer_payment,
        name="payment"
    ),

    path(
        "<int:pk>/",
        bill_detail,
        name="detail"
    ),

    path(
        "<int:pk>/payment/",
        bill_payment,
        name="bill_payment"
    ),
]