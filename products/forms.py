from django import forms
from .models import Category, Product

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "description", "active"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["product_code", "name", "category", "description", "image", "unit", "purchase_price", "selling_price", "stock_quantity", "low_stock_threshold", "active"]
        widgets = {
            "product_code": forms.TextInput(attrs={"class": "form-control"}),
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "unit": forms.TextInput(attrs={"class": "form-control"}),
            "purchase_price": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "selling_price": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "stock_quantity": forms.NumberInput(attrs={"class": "form-control", "step": "0.001"}),
            "low_stock_threshold": forms.NumberInput(attrs={"class": "form-control", "step": "0.001"}),
            "active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
