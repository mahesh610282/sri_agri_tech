from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from .forms import LoginForm
from .models import User

class UserLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = LoginForm

def logout_view(request):
    logout(request)
    return redirect("accounts:login")

def dashboard(request):
    if not request.user.is_authenticated:
        return redirect("accounts:login")
    if request.user.is_superuser or request.user.role == User.Role.ADMIN:
        return redirect("dashboard:home")
    return redirect("customers:portal")
