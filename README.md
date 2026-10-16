# HEF Portal — [hef.co.ir](https://hef.co.ir)

A full-stack Persian (RTL) web portal for **HEF**, an educational and financial holding specializing in trading market instruction and account history tracking. Built with Django, it provides authentication, a multi-language CMS, a download center, a ticketing system, and a finance dashboard for per-user trading history reports.

---

## Features

- **Authentication & profiles** — signup, login (username or email), session management, profile editing with avatar cropping (WebP), and MAC/IP identity capture
- **Notification center** — bell icon in the navbar with real-time unread badge, dropdown for recent notifications, and a dedicated tickets page (PENDING / APPROVED / REJECTED)
- **Ticketing system** — contact form submissions create tickets; admins review, approve, or reject with reasons; users are notified automatically
- **Multi-language CMS** — About, Resume, FAQ, and Contact pages editable per-language (FA / EN / FR / AR) via Django admin with django-parler
- **Adobe Connect page** — dedicated product page for private Adobe Connect server deployments, with pricing and consultation routed to a "Coming Soon" stub
- **Download center** — file upload, tagging, password protection, and visibility control (public/private), with per-file download tracking
- **Finance hub** — trading account linking and per-user trading history reports generated from pre-processed `.htm` files
- **Admin dashboard** — full Django admin with ticket management, page-visit analytics, login-attempt audit logs, and TinyMCE rich-text editing

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Django 5.2, Gunicorn |
| **Database** | PostgreSQL (production), SQLite (local dev) |
| **Cache** | Redis / django-redis (production), LocMem (local dev) |
| **Frontend** | Django templates, Bootstrap 5.3 (RTL), Tailwind CSS (CDN) |
| **Reverse proxy** | Caddy (auto TLS via Let's Encrypt) |
| **Image processing** | Pillow (profile pictures → WebP) |
| **Rich text** | django-tinymce (About/Resume admin editors) |
| **i18n CMS** | django-parler (per-language content) |
| **Containerization** | Docker + Docker Compose |

---

## Project Layout

```
hef.co.ir/
├── backend/                # Django project root
│   ├── apps/
│   │   ├── app_main/       # Public pages, CMS, i18n chrome, Adobe Connect
│   │   ├── app_account/    # Users, auth, tickets, notifications, trading accounts
│   │   ├── app_finance/    # Trading history viewer
│   │   ├── app_learn/      # Learning section
│   │   └── app_download/   # Download center
│   ├── config/             # Django settings, URLs, middleware, error views
│   ├── templates/          # HTML templates (Jinja2/Django templates)
│   ├── static/             # CSS, JS, fonts, images
│   ├── media/              # User uploads (profile pictures)
│   └── manage.py
├── data/History/           # Trading history .htm files per account
├── scripts/                # Entrypoint, update, dev/prod helpers
├── docker-compose.yml      # Local Docker (HTTP)
├── docker-compose.caddy.yml # Production Docker (Caddy + Gunicorn + Postgres + Redis)
├── Caddyfile               # Caddy config for production TLS
├── Dockerfile              # Application container image
└── README.md
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- pip

### Local Development (without Docker)

```bash
cd backend
python -m venv .venv

# Activate
# Windows:
.venv\Scripts\activate
# Linux / macOS:
source .venv/bin/activate

pip install -r requirements.txt
cp .env.sample .env          # edit .env — set DJANGO_SECRET_KEY (required)
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

> **Note:** When `DJANGO_DEBUG=True`, Django's default yellow debug pages appear on errors. When `DJANGO_DEBUG=False`, custom error pages (404, 403, 400, 500) are displayed instead.

### Local Docker (HTTP only, no TLS)

```bash
cp backend/.env.sample backend/.env
# Set at least: DJANGO_SECRET_KEY, POSTGRES_PASSWORD
docker compose up -d --build
# Site available at http://localhost/
```

---

## Production Deployment

### Stack

| Service | Role |
|---------|------|
| **Caddy** | Reverse proxy, HTTP → HTTPS, Let's Encrypt certificates |
| **Gunicorn** | WSGI application server (port 8000 internally) |
| **PostgreSQL** | Primary database |
| **Redis** | Cache backend + cached_db sessions |

### Steps

#### 1. Install Docker on Ubuntu

```bash
sudo apt update
sudo apt install -y ca-certificates curl git
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
  sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io \
  docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker "$USER"
# Log out and back in
```

#### 2. Clone the Repository

```bash
sudo mkdir -p /opt/hef && sudo chown "$USER":"$USER" /opt/hef
cd /opt/hef
git clone <YOUR_REPO_URL> .
```

#### 3. Configure Environment

```bash
cp backend/.env.sample backend/.env
nano backend/.env
```

Required settings:

| Variable | Example |
|----------|---------|
| `MY_DOMAIN` | `portal.example.com` |
| `DJANGO_SECRET_KEY` | *(long random string)* |
| `POSTGRES_PASSWORD` | *(strong password)* |
| `DJANGO_ALLOWED_HOSTS` | `portal.example.com,www.portal.example.com` |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | `https://portal.example.com` |
| `DJANGO_DEBUG` | `False` |

Generate a secret key:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

#### 4. DNS & Firewall

Point your domain's A/AAAA records to the server's public IP, then:

```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

#### 5. Start the Stack

```bash
cd /opt/hef
docker compose -f docker-compose.caddy.yml up -d --build
```

Caddy obtains and renews Let's Encrypt certificates automatically.

#### 6. Create Superuser

```bash
docker compose -f docker-compose.caddy.yml exec django python manage.py createsuperuser
```

#### 7. Trading History Files

Place files on the host at:

```
/opt/hef/data/History/History-{trading_acc_username}/
```

Expected files per account:

```
Index_{username}.htm
Daily_{username}_{YYYY-MM-DD}_to_{YYYY-MM-DD}.htm
Weekly_{username}_Week{N}_{YYYY-MM-DD}_to_{YYYY-MM-DD}.htm
Monthly_{username}_{YYYY-MM-DD}_to_{YYYY-MM-DD}.htm
Yearly_{username}_{YYYY-MM-DD}_to_{YYYY-MM-DD}.htm    # optional
```

---

## Updating the Application

```bash
cd /opt/hef
chmod +x scripts/update.sh
./scripts/update.sh
```

The update script pulls the latest code from `main` and rebuilds the Docker containers.

Manual equivalent:

```bash
git pull origin main
docker compose -f docker-compose.caddy.yml up -d --build
```

---

## Useful Commands

```bash
# View logs
docker compose -f docker-compose.caddy.yml logs -f django
docker compose -f docker-compose.caddy.yml logs -f caddy
docker compose -f docker-compose.caddy.yml logs -f redis

# Django shell
docker compose -f docker-compose.caddy.yml exec django python manage.py shell

# Run migrations
docker compose -f docker-compose.caddy.yml exec django python manage.py migrate

# Stop / start
docker compose -f docker-compose.caddy.yml stop
docker compose -f docker-compose.caddy.yml start
```

---

## Content Management

All editable content is managed through Django admin at `/admin/`:

| Content | Admin Section | Notes |
|---------|--------------|-------|
| About page | **صفحه درباره ما** | TinyMCE rich editor, per-language tabs |
| Resume page | **صفحه رزومه** | TinyMCE rich editor, per-language tabs |
| FAQ items | **محتوای سایت** (page=FAQ) | Translate key/value per language |
| Contact cards | **محتوای سایت** (page=CONTACT) | Translate key/value per language |
| Tickets | **تیکت‌ها** | Approve or reject with reason; user notified automatically |
| Navigation strings | `app_main/i18n_chrome.py` | Hardcoded per-language dicts (FA/EN/FR/AR) |

---

## Configuration Reference

All settings are controlled via `backend/.env`. See [`.env.sample`](backend/.env.sample) for the full list with descriptions.

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DJANGO_SECRET_KEY` | ✅ | — | Django secret key |
| `DJANGO_DEBUG` | ✅ | `False` | Debug mode (`True` shows Django debug pages) |
| `DJANGO_ALLOWED_HOSTS` | ✅ | — | Comma-separated hostnames |
| `POSTGRES_PASSWORD` | ✅ (Docker) | — | Database password |
| `MY_DOMAIN` | ✅ (Caddy) | — | Public domain for TLS |
| `REDIS_URL` | — | — | Redis connection string |
| `HISTORY_ROOT` | — | `<project>/data/History` | Path to trading history files |

---

## License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

<p align="center">
  Built with ❤️ for the Persian trading community.
</p>
