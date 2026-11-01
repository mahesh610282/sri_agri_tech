from django import forms
from .models import Customer

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        exclude = ["customer_id", "outstanding_balance", "user"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "mobile": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "address": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "village": forms.TextInput(attrs={"class": "form-control"}),
            "mandal": forms.TextInput(attrs={"class": "form-control"}),
            "district": forms.TextInput(attrs={"class": "form-control"}),
            "state": forms.TextInput(attrs={"class": "form-control"}),
            "active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def clean_mobile(self):
        mobile = self.cleaned_data["mobile"].strip()
        if not mobile.isdigit() or len(mobile) != 10 or mobile[0] not in "6789":
            raise forms.ValidationError("Enter a valid 10-digit Indian mobile number.")
        return mobile
