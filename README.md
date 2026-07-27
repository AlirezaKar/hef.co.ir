# HEF Report Portal

Persian Django portal for viewing pre-generated trading/report `.htm` files.

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
      app_account/   # users, auth, profile, settings, about, contact
      app_report/    # home + report loading
    media/profile_picture/
    templates/
  data/reports/{username}/   # pre-built Index/Daily/Weekly/Monthly .htm files
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
## Reports

Place files under `data/reports/{username}/` matching:

- `Index_{username}.htm`
- `Daily_{username}_{YYYY-MM-DD}_to_{YYYY-MM-DD}.htm`
- `Weekly_{username}_Week{N}_{YYYY-MM-DD}_to_{YYYY-MM-DD}.htm`
- `Monthly_{username}_{YYYY-MM-DD}_to_{YYYY-MM-DD}.htm`
- `Yearly_{username}_{YYYY-MM-DD}_to_{YYYY-MM-DD}.htm` (optional)

The site **loads** these files; it does not generate report HTML. Filenames are case-sensitive.

In **Settings**, choose how often the folder is re-scanned (1h / 3h / 6h / daily). Open report pages poll for a new scan version and reload when it changes.

## Notes

- UI language is Persian (RTL). Dates stay Gregorian. Django CLI commands stay in English.
- Signup requires: username, email, password, confirm password, phone number.
- Login accepts username **or** email.
- Profile picture uploads are stored as `.webp` in `backend/media/profile_picture/`.
- About / Contact content is managed in Django admin via **Site content** key/value items.
