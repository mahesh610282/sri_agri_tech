from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from customers.models import Customer
from products.models import Category, Product
from decimal import Decimal

class Command(BaseCommand):
    help = "Create safe demo data for local development."

    def handle(self, *args, **options):
        User = get_user_model()
        admin, _ = User.objects.get_or_create(
            username="admin",
            defaults={"role": User.Role.ADMIN, "is_staff": True, "is_superuser": True},
        )
        admin.role = User.Role.ADMIN
        admin.is_staff = True
        admin.is_superuser = True
        admin.set_password("Admin@12345")
        admin.save()

        category, _ = Category.objects.get_or_create(name="Seeds", defaults={"description": "Agricultural seeds"})
        products = [
            ("SEED-001", "Cotton Seeds", Decimal("450"), Decimal("550"), Decimal("100")),
            ("SEED-002", "Paddy Seeds", Decimal("300"), Decimal("380"), Decimal("150")),
            ("FERT-001", "NPK Fertilizer", Decimal("900"), Decimal("1050"), Decimal("80")),
        ]
        for code, name, purchase, selling, stock in products:
            Product.objects.get_or_create(
                product_code=code,
                defaults={
                    "name": name, "category": category, "unit": "Bag",
                    "purchase_price": purchase, "selling_price": selling,
                    "stock_quantity": stock, "low_stock_threshold": Decimal("20")
                }
            )

        self.stdout.write(self.style.SUCCESS("Demo data created. Login: admin / Admin@12345"))
