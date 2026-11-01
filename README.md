# Sri Mathre Agri Clinics

Django application for:
- Admin and Customer roles
- Customer management
- Product/category management
- Inventory and stock transactions
- POS-style billing
- Payments and outstanding balance
- Invoice/print view
- Customer portal
- Admin dashboard
- Reports
- Store/product gallery

## Architecture

Each major business section is a separate Django app:

```text
core/
accounts/
customers/
products/
inventory/
billing/
payments/
dashboard/
reports/
gallery/
```

## Setup

```bash
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate # Linux/macOS

pip install -r requirements.txt
copy .env.example .env     # Windows
# cp .env.example .env     # Linux/macOS
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_demo
python manage.py runserver
```

For MySQL, update `.env` with DB_NAME, DB_USER, DB_PASSWORD, DB_HOST and DB_PORT.

## Important

The core bill workflow is implemented inside `billing/services.py` with `transaction.atomic()`:
1. lock customer/products
2. validate stock
3. create bill
4. create bill items
5. reduce stock
6. create stock transactions
7. update outstanding balance

Payment recording is also atomic in `payments/services.py`.

## Production

Before deployment:
- use a strong SECRET_KEY
- DEBUG=False
- configure ALLOWED_HOSTS
- configure MySQL
- run collectstatic
- use Gunicorn + Nginx + HTTPS
- keep credentials in environment variables
- validate uploaded files
- add automated tests and backups
