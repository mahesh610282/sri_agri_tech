from functools import wraps
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied

def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        if not request.user.is_superuser and getattr(request.user, "role", None) != "ADMIN":
            raise PermissionDenied("Admin access required.")
        return view_func(request, *args, **kwargs)
    return wrapper

def customer_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        if getattr(request.user, "role", None) != "CUSTOMER":
            raise PermissionDenied("Customer access required.")
        return view_func(request, *args, **kwargs)
    return wrapper
