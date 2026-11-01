from django.urls import path
from .views import stock_list, stock_adjust

app_name = "inventory"

urlpatterns = [
    path("", stock_list, name="list"),
    path("adjust/", stock_adjust, name="adjust"),
]
