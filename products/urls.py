from django.urls import path
from .views import product_list, product_create, product_edit, category_list

app_name = "products"

urlpatterns = [
    path("", product_list, name="list"),
    path("add/", product_create, name="create"),
    path("<int:pk>/edit/", product_edit, name="edit"),
    path("categories/", category_list, name="categories"),
]
