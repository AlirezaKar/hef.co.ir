# HEF History Portal

Persian Django portal for viewing pre-generated trading history `.htm` files.

## Stack

- Django 5.2 + Django templates
- Tailwind CSS (CDN) + Bootstrap RTL (CDN)
- SQLite (development)
- Pillow (profile pictures → WebP)

## Project layout

```
hef.co.ir/
  backend/           # Django project
    apps/
      app_account/   # users, auth, profile, trading accounts, about, contact
      app_report/    # home + history loading
    media/profile_picture/
    templates/
  data/History/History-{trading_acc_username}/   # Index/Daily/Weekly/Monthly .htm files
  example/           # UI / sample references
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

Open `http://127.0.0.1:8000/`.

Sensitive settings (`DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`) live in `backend/.env` only — never commit that file.

## History files

Place files under `data/History/History-{trading_acc_username}/` matching:

- `Index_{trading_acc_username}.htm`
- `Daily_{trading_acc_username}_{YYYY-MM-DD}_to_{YYYY-MM-DD}.htm`
- `Weekly_{trading_acc_username}_Week{N}_{YYYY-MM-DD}_to_{YYYY-MM-DD}.htm`
- `Monthly_{trading_acc_username}_{YYYY-MM-DD}_to_{YYYY-MM-DD}.htm`
- `Yearly_{trading_acc_username}_{YYYY-MM-DD}_to_{YYYY-MM-DD}.htm` (optional)

Users create or link **trading accounts** (شماره حساب + نام کارگزاری). History is scanned on demand when a trading account is opened — there is no timed scheduler.

The site **loads** these files; it does not generate history HTML. Filenames are case-sensitive.

## Notes

- UI language is Persian (RTL). Dates stay Gregorian. Django CLI commands stay in English.
- Signup requires: username, email, password, confirm password, phone number.
- Login accepts username **or** email.
- Profile picture uploads are stored as `.webp` in `backend/media/profile_picture/`.
- About / Contact content is managed in Django admin via **Site content** key/value items.
