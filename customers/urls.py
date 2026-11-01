from django.urls import path
from .views import customer_list, customer_create, customer_edit, customer_detail, portal

app_name = "customers"

urlpatterns = [
    path("", customer_list, name="list"),
    path("add/", customer_create, name="create"),
    path("<int:pk>/", customer_detail, name="detail"),
    path("<int:pk>/edit/", customer_edit, name="edit"),
    path("portal/", portal, name="portal"),
]
