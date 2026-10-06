# I3Center

A Persian (RTL, Jalali calendar) online shop and blog built with Django 5.2. It combines a product catalog with variants (color and size), a session-based cart, coupons, online payment through Zarinpal, OTP-verified login and registration, and a blog with comments and likes.

## Features

**Accounts**
- Custom user model that logs in with a phone number
- Registration and login with a two-step one-time password (OTP) sent by SMS (Kavenegar)
- Password reset by email, password change
- Admin panel with a custom user form
- Management command that removes expired OTP codes

**Products**
- Brands, materials and nested categories
- Products with variants (color + size), each with its own price, discount, stock and sales count
- Extra product images, rich-text descriptions (CKEditor)
- Comments with replies, likes and dislikes; product likes
- Unique-IP view counting
- Search, filtering (price range, brand, material, availability, discount), sorting and pagination
- Price history per variant (recorded automatically by a signal) shown as a line chart
- Home page carousels (all, discounted, best-selling, most-viewed, most-liked, newest products, popular articles)
- FAQ, About Us and Contact Us pages

**Orders**
- Session-based cart (add, remove one, delete)
- Order creation from the cart, editing and deleting unpaid orders
- Coupons with validity dates, usage limits and one use per user
- Payment request and verification through Zarinpal; stock and sales counts update after a successful payment

**Posts (blog)**
- Categories and posts with rich-text content
- Comments with replies, like/dislike on comments, likes on posts
- Unique-IP view counting, search, sorting and pagination

## Tech Stack

- Python 3 and Django 5.2 (`Django==5.2.17` in `requirements.txt`)
- PostgreSQL (`psycopg2`)
- Arvan Cloud S3-compatible object storage for media files (`django-storages`, `boto3`)
- `django-jalali` / `jdatetime` for Jalali dates
- `django-ckeditor` for rich text
- `django-filter` for filtering
- Kavenegar for SMS, Zarinpal for payments
- Bootstrap 5 (RTL), Bootstrap Icons and Chart.js on the front end

## Project Structure

### Root

```
I3Center/                      # project root
├── I3Center/                  # project package
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── accounts/                  # app (see below)
├── products/                  # app (see below)
├── orders/                    # app (see below)
├── posts/                     # app (see below)
├── utility/
│   ├── function.py            # SMS sending, client IP, unique OTP code
│   └── inheritance.py         # BaseModel (created/updated + Jalali dates)
├── templates/
│   ├── base.html
│   ├── 404.html
│   ├── 500.html
│   └── includes/
│       ├── header.html
│       ├── navbar.html
│       ├── footer.html
│       └── messages.html
├── static/
│   ├── CSS/
│   └── JS/
├── logs/                      # created automatically
├── manage.py
└── requirements.txt
```

---

### accounts

```
accounts/
├── management/
│   └── commands/
│       └── remove_expired_otp.py
├── migrations/
├── templates/
│   └── accounts/
│       ├── user_login.html
│       ├── user_login_verify.html
│       ├── user_password_change.html
│       ├── user_password_change_done.html
│       ├── user_password_reset_complete.html
│       ├── user_password_reset_confirm.html
│       ├── user_password_reset_done.html
│       ├── user_password_reset_email.html
│       ├── user_password_reset_form.html
│       ├── user_register.html
│       └── user_register_verify.html
├── __init__.py
├── admin.py
├── apps.py
├── forms.py
├── manager.py
├── model_field_validation.py
├── models.py
├── tests.py
├── urls.py
└── views.py
```

---

### products

```
products/
├── migrations/
├── templates/
│   └── products/
│       ├── about_us.html
│       ├── category_view.html
│       ├── contact_us.html
│       ├── faq.html
│       ├── home.html
│       ├── product_details.html
│       └── product_view.html
├── templatetags/
│   └── my_custom_tags.py
├── __init__.py
├── admin.py
├── apps.py
├── filters.py
├── forms.py
├── model_field_validation.py
├── models.py
├── signals.py
├── tests.py
├── urls.py
└── views.py
```

---

### orders

```
orders/
├── context_processors/
│   └── processors.py
├── migrations/
├── templates/
│   └── orders/
│       ├── cart_view.html
│       ├── order_details.html
│       ├── order_form.html
│       ├── order_modify.html
│       ├── order_pay.html
│       └── order_view.html
├── __init__.py
├── admin.py
├── apps.py
├── cart.py
├── forms.py
├── models.py
├── tests.py
├── urls.py
└── views.py
```

---

### posts

```
posts/
├── migrations/
├── templates/
│   └── posts/
│       ├── category_view.html
│       ├── post_details.html
│       └── post_view.html
├── __init__.py
├── admin.py
├── apps.py
├── filters.py
├── forms.py
├── models.py
├── tests.py
├── urls.py
└── views.py
```

## URL Overview

The project `urls.py` includes each app under its own prefix:

| Prefix | Included from |
|---|---|
| `/admin/` | Django admin |
| `/accounts/` | `accounts.urls` |
| `/` | `products.urls` |
| `/orders/` | `orders.urls` |
| `/posts/` | `posts.urls` |
| `/ckeditor/` | `ckeditor_uploader.urls` |

All routes of each app are listed below. Names are used with the app namespace, for example `accounts:user_login`.

---

### accounts  (prefix `/accounts/`)

| URL | Name | Purpose |
|---|---|---|
| `/accounts/user-register/` | `user_register` | Registration form |
| `/accounts/user-register-verify/` | `user_register_verify` | Confirm registration with OTP |
| `/accounts/user-login/` | `user_login` | Login form |
| `/accounts/user-login-verify/` | `user_login_verify` | Confirm login with OTP |
| `/accounts/user-logout/` | `user_logout` | Log out |
| `/accounts/user-password-reset/` | `user_password_reset` | Password reset, step 1 (email) |
| `/accounts/user-password-reset-done/` | `user_password_reset_done` | Password reset, step 2 (check email) |
| `/accounts/user-password-reset-confirm/<uidb64>/<token>/` | `user_password_reset_confirm` | Password reset, step 3 (new password) |
| `/accounts/user-password-reset-complete/` | `user_password_reset_complete` | Password reset, step 4 (done) |
| `/accounts/user-password-change/` | `user_password_change` | Change password (login required) |
| `/accounts/user-password-change-done/` | `user_password_change_done` | Password change confirmation |

---

### products  (prefix `/`)

| URL | Name | Purpose |
|---|---|---|
| `/` | `home` | Home page with carousels |
| `/products/` | `view` | Product list with search, filters, pagination |
| `/products/<pk>/<slug>/` | `view_from_category` | Product list of one category |
| `/product/details/<pk>/<slug>/` | `details` | Product details, variants, comments |
| `/category/` | `category_view` | Parent categories |
| `/category/<pk>/<slug>/` | `category_sub` | Sub-categories of a category |
| `/products/like/<pk>/` | `product_like` | Like / unlike a product |
| `/products/comment-like/<pk>/` | `comment_like` | Like a comment |
| `/products/comment-dislike/<pk>/` | `comment_dislike` | Dislike a comment |
| `/faq/` | `faq` | Frequently asked questions |
| `/about-us/` | `about_us` | About us |
| `/contact-us/` | `contact_us` | Contact form |

---

### orders  (prefix `/orders/`)

| URL | Name | Purpose |
|---|---|---|
| `/orders/cart/view/` | `cart_view` | Show the cart |
| `/orders/cart/add/<pk>/` | `cart_add` | Add a variant to the cart |
| `/orders/cart/update/<pk>/` | `cart_update` | Add one, remove one or delete a cart item |
| `/orders/form/` | `order_form` | Shipping information form (creates the order) |
| `/orders/view/` | `order_view` | List of the user's orders |
| `/orders/modify/<id>/` | `order_modify` | Edit an unpaid order |
| `/orders/update-quantity/<id>/` | `update_quantity` | Change the quantity of an order item |
| `/orders/details/<id>/` | `order_details` | Order details and coupon code |
| `/orders/pay/<id>/` | `order_pay` | Payment summary |
| `/orders/zp-request/<id>/` | `zp_request` | Send the payment request to Zarinpal |
| `/orders/zp-verify/` | `zp_verify` | Zarinpal callback and verification |

---

### posts  (prefix `/posts/`)

| URL | Name | Purpose |
|---|---|---|
| `/posts/` | `view` | Post list with search, sorting, pagination |
| `/posts/category/` | `category` | Post categories |
| `/posts/category/<pk>/<slug>/` | `view_from_category` | Post list of one category |
| `/posts/category/<category_pk>/<category_slug>/<post_pk>/<post_slug>/` | `details` | Post details and comments |
| `/posts/post-love/<pk>/` | `post_love` | Like / unlike a post |
| `/posts/comment-love/<pk>/` | `comment_love` | Like a comment |
| `/posts/comment-hate/<pk>/` | `comment_hate` | Dislike a comment |

## Getting Started

### 1. Requirements

- Python 3
- PostgreSQL
- An S3-compatible bucket (the project uses Arvan Cloud)
- Kavenegar (SMS) and Zarinpal (payments) accounts for those features

### 2. Install

```bash
git clone <your-repository-url>
cd I3Center
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure

Create a PostgreSQL database named `I3Center` and a user for it, then set the following in `I3Center/settings.py`:

| Setting | Purpose |
|---|---|
| `SECRET_KEY` | Django secret key |
| `DEBUG`, `ALLOWED_HOSTS` | Debug mode and allowed host names |
| `DATABASES` | PostgreSQL name, user, password, host, port |
| `AWS_STORAGE_BUCKET_NAME`, `AWS_S3_ENDPOINT_URL`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` | Object storage for uploaded media |
| `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` | SMTP account used for password-reset emails |
| `MERCHANT`, `SANDBOX` | Zarinpal merchant ID and sandbox switch |

The Kavenegar API key and sender number are set in `utility/function.py` (`send_sms`).

### 4. Prepare the database

```bash
python manage.py migrate
python manage.py createsuperuser
```

The superuser prompt asks for: phone number, email, password, first name, last name, state, city, address and zip code.

### 5. Static files

`base.html` expects these files inside the `static/` folder:

- `CSS/bootstrap.rtl.min.css`
- `CSS/bootstrap-icons/bootstrap-icons.min.css`
- `JS/bootstrap.bundle.min.js`
- `JS/chart.js`

### 6. Run

```bash
python manage.py runserver
```

Open http://127.0.0.1:8000/ for the shop and http://127.0.0.1:8000/admin/ for the admin panel.

## Typical Setup in the Admin Panel

1. Create brands, materials and categories (parent categories are used for the navbar).
2. Create colors and sizes, then products; each product needs at least one variant.
3. Optionally add coupons (set `available`, a discount percentage, maximum uses, start and end dates).
4. Add blog categories and posts.

## OTP Handling

- OTP codes are 5 digits and expire after 2 minutes.
- Expired codes can be removed with the management command (it can be scheduled with cron):

```bash
python manage.py remove_expired_otp
```

- In the current code the `send_sms(...)` calls in `accounts/views.py` are commented out, and the OTP is shown in a message on the page.

## Payments

Payments use the Zarinpal WebGate REST API. Prices are stored in Toman and converted to Rial (multiplied by 10) when sent to the gateway. The `SANDBOX` setting switches between the sandbox and the live endpoints. The callback URL is built dynamically from the current request (`orders:zp_verify`).

## Logging

Each app (`accounts`, `products`, `orders`, `posts`) logs to its own rotating file in `logs/` (5 MB each, 5 backups, WARNING level and above) and to the console.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
