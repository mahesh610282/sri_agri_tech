from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        CUSTOMER = "CUSTOMER", "Customer"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CUSTOMER)
    mobile = models.CharField(max_length=15, blank=True)

    def is_admin_user(self):
        return self.is_superuser or self.role == self.Role.ADMIN
