# HEF History Portal

Persian Django portal for viewing pre-generated trading history `.htm` files.

## Stack

- Django 5.2 + Django templates
- Tailwind CSS (CDN) + Bootstrap RTL (CDN)
- SQLite (development)
- Pillow (profile pictures → WebP)
- django-tinymce (rich About page editor in admin)

## Project layout

```
hef.co.ir/
  backend/           # Django project
    apps/
      app_account/   # users, auth, landing/about, FAQ, contact, visits, trading accounts
      app_report/    # home + history loading
    media/
      profile_picture/
      about_uploads/   # TinyMCE uploads
    templates/
  data/History/History-{trading_acc_username}/   # Index/Daily/Weekly/Monthly .htm files
  example/           # UI / sample references (local only)
```

## Setup

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt
copy .env.sample .env   # or: cp .env.sample .env
# Edit backend/.env — set DJANGO_SECRET_KEY (required). Keep DEBUG=True only for local use.
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open `http://127.0.0.1:8000/` — public **About** landing (not logged in). Login/signup from there. After login you land on `/home/`.

Sensitive settings (`DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`) live in `backend/.env` only — never commit that file.

## History files

Place files under `data/History/History-{trading_acc_username}/` matching:

- `Index_{trading_acc_username}.htm`
- `Daily_{trading_acc_username}_{YYYY-MM-DD}_to_{YYYY-MM-DD}.htm`
- `Weekly_{trading_acc_username}_Week{N}_{YYYY-MM-DD}_to_{YYYY-MM-DD}.htm`
- `Monthly_{trading_acc_username}_{YYYY-MM-DD}_to_{YYYY-MM-DD}.htm`
- `Yearly_{trading_acc_username}_{YYYY-MM-DD}_to_{YYYY-MM-DD}.htm` (optional)

Users create or link **trading accounts** (شماره حساب + نام کارگزاری). History is scanned on demand when a trading account is opened — there is no timed scheduler.

Opening a trading account loads its Index in a **new tab** as plain HTML. Daily/Weekly/… links also open in new tabs; their return button goes back to that account’s Index. The Index return button (top) goes to the portal home.

## Content & tracking

- **About (landing + `/about/`)**: rich HTML via Django admin → **صفحه درباره ما** (TinyMCE). Optional key/value extras still via **Site content** (`about`).
- **FAQ (`/faq/`)** and **Contact**: **Site content** key/value items (`faq`, `contact`).
- **Page visits**: every meaningful GET is stored (`PageVisit`) — authenticated users linked to their User; anonymous visitors labeled `anonymous`. Login attempts support date/time filters in admin.

## Notes

- UI language is Persian (RTL). Dates stay Gregorian. Django CLI commands stay in English.
- Signup requires: username, email, password, confirm password, phone number.
- Login accepts username **or** email.
- Profile picture uploads are stored as `.webp` in `backend/media/profile_picture/`.
