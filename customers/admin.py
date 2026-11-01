from django.contrib import admin
from .models import Customer

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("customer_id", "name", "mobile", "outstanding_balance", "active")
    search_fields = ("name", "mobile", "customer_id")
    list_filter = ("active", "district", "state")
