from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from accounts.decorators import admin_required
from .forms import CategoryForm, ProductForm
from .models import Category, Product

@admin_required
def product_list(request):
    q = request.GET.get("q", "").strip()
    category = request.GET.get("category", "").strip()
    products = Product.objects.select_related("category").order_by("name")
    if q:
        products = products.filter(Q(name__icontains=q) | Q(product_code__icontains=q))
    if category:
        products = products.filter(category_id=category)
    return render(request, "products/list.html", {
        "products": products,
        "categories": Category.objects.filter(active=True),
        "q": q,
        "selected_category": category,
    })

@admin_required
def product_create(request):
    form = ProductForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Product created successfully.")
        return redirect("products:list")
    return render(request, "products/form.html", {"form": form, "title": "Add Product"})

@admin_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, request.FILES or None, instance=product)
    if form.is_valid():
        form.save()
        messages.success(request, "Product updated successfully.")
        return redirect("products:list")
    return render(request, "products/form.html", {"form": form, "title": "Edit Product"})

@admin_required
def category_list(request):
    categories = Category.objects.order_by("name")
    form = CategoryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("products:categories")
    return render(request, "products/categories.html", {"categories": categories, "form": form})
