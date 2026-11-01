from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class UserAdminConfig(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Business Role", {"fields": ("role", "mobile")}),
    )
    list_display = ("username", "mobile", "role", "is_active", "is_staff")
    list_filter = ("role", "is_active", "is_staff")
