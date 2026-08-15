# HEF History Portal

Persian Django portal for viewing pre-generated trading history `.htm` files.

## Stack

- Django 5.2 + Django templates
- Tailwind CSS (CDN) + Bootstrap RTL (CDN)
- PostgreSQL in Docker (SQLite still works for local non-Docker dev)
- Redis in Docker (Django cache + cached_db sessions; LocMem without Redis)
- Gunicorn + Caddy (HTTPS / Let's Encrypt)
- Pillow (profile pictures → WebP)
- django-tinymce (rich About page editor in admin)
- django-parler (per-language About / Resume / FAQ / Contact CMS content)

## Project layout

```
hef.co.ir/
  backend/           # Django project
    apps/
      app_account/   # users, auth, landing/about, FAQ, contact, visits, trading accounts
      app_report/    # home + history loading
    media/
    templates/
  data/History/History-{trading_acc_username}/
  scripts/           # entrypoint.sh, update.sh
  docker-compose.yml
  docker-compose.caddy.yml
  Caddyfile
  Dockerfile
  example/           # UI / sample references (local only)
```

---

## Local development (without Docker)

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

Open `http://127.0.0.1:8000/` — public landing. After login you land on `/home/`.

Sensitive settings live in `backend/.env` — never commit that file. Docker Compose reads the same file.

---

## Ubuntu server deployment (Docker + Caddy + Gunicorn + Postgres + Redis)

Containers use `restart: unless-stopped`, so after a crash or a VM / VMware reboot Docker brings the stack back up automatically (as long as the Docker daemon itself is enabled: `sudo systemctl enable --now docker`).

Stack roles:

| Service | Role |
|---------|------|
| **Caddy** | Reverse proxy, HTTP→HTTPS, Let's Encrypt certificates, `/static` + `/media` |
| **Gunicorn** (`django`) | Runs the Django app; talks to Caddy on internal port 8000 |
| **Postgres** | Primary database |
| **Redis** | Cache (and session cache via `cached_db`) |

### 1. Install Docker on Ubuntu

```bash
sudo apt update
sudo apt install -y ca-certificates curl git
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker "$USER"
# log out and back in so the docker group applies
```

### 2. Clone the repository (once)

```bash
cd /opt   # or any directory you prefer
sudo mkdir -p /opt/hef && sudo chown "$USER":"$USER" /opt/hef
cd /opt/hef
git clone <YOUR_GITHUB_REPO_URL> .
# example: git clone https://github.com/your-org/hef.co.ir.git .
```

### 3. Configure environment

```bash
cp backend/.env.sample backend/.env
nano backend/.env
```

Set at least:

| Variable | Notes |
|----------|--------|
| `MY_DOMAIN` | Your public domain (e.g. `portal.example.com`). Use this placeholder name until DNS is ready. |
| `DJANGO_SECRET_KEY` | Long random secret |
| `POSTGRES_PASSWORD` | Strong password |
| `DJANGO_ALLOWED_HOSTS` | Should include `MY_DOMAIN` |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | `https://` + your domain (production) |

Generate a secret key:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

### 4. DNS and firewall

- Point `MY_DOMAIN` A/AAAA records to this server’s public IP.
- Open ports **80** and **443**:

```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 5. Start production stack (Caddy TLS)

```bash
cd /opt/hef
docker compose -f docker-compose.caddy.yml up -d --build
```

Caddy obtains and renews Let's Encrypt certificates automatically for `MY_DOMAIN`.

Wait a few seconds, then open `https://MY_DOMAIN`.

### 6. Create a Django superuser

```bash
docker compose -f docker-compose.caddy.yml exec django python manage.py createsuperuser
```

### 7. History files

Put account folders on the host under:

```text
/opt/hef/data/History/History-{trading_acc_username}/
```

This path is mounted into the container as `/data/History`.

### 8. Updating code after you push to GitHub

You do **not** need to re-clone. On the server:

```bash
cd /opt/hef
chmod +x scripts/update.sh
./scripts/update.sh
```

That script runs:

1. `git pull` (fast-forward) from `main`
2. `docker compose -f docker-compose.caddy.yml up -d --build`

Manual equivalent:

```bash
cd /opt/hef
git pull origin main
docker compose -f docker-compose.caddy.yml up -d --build
```

### 9. Useful commands

```bash
# logs
docker compose -f docker-compose.caddy.yml logs -f redis
docker compose -f docker-compose.caddy.yml logs -f django
docker compose -f docker-compose.caddy.yml logs -f caddy

# Django shell / migrate
docker compose -f docker-compose.caddy.yml exec django python manage.py shell
docker compose -f docker-compose.caddy.yml exec django python manage.py migrate

# stop / start
docker compose -f docker-compose.caddy.yml stop
docker compose -f docker-compose.caddy.yml start
```

### Local Docker (HTTP only, no TLS)

```bash
cp backend/.env.sample backend/.env
# set DJANGO_SECRET_KEY, POSTGRES_PASSWORD; MY_DOMAIN can be localhost
docker compose up -d --build
# site on http://localhost/
```

### Migrating existing SQLite data to Postgres (optional, one-time)

On a machine that still has `backend/db.sqlite3`:

```bash
cd backend
python manage.py dumpdata --natural-foreign --natural-primary \
  -e contenttypes -e auth.permission -e sessions \
  -o ../data_dump.json
```

Copy `data_dump.json` to the server, then:

```bash
docker compose -f docker-compose.caddy.yml exec -T django \
  python manage.py loaddata /usr/src/backend/data_dump.json
```

(Place the dump inside the image/build context or mount it before loading.)

---

## History files

Place files under `data/History/History-{trading_acc_username}/` matching:

- `Index_{trading_acc_username}.htm`
- `Daily_{trading_acc_username}_{YYYY-MM-DD}_to_{YYYY-MM-DD}.htm`
- `Weekly_{trading_acc_username}_Week{N}_{YYYY-MM-DD}_to_{YYYY-MM-DD}.htm`
- `Monthly_{trading_acc_username}_{YYYY-MM-DD}_to_{YYYY-MM-DD}.htm`
- `Yearly_{trading_acc_username}_{YYYY-MM-DD}_to_{YYYY-MM-DD}.htm` (optional)

Users create or link **trading accounts**. Superusers see **all** trading accounts on the History page.

## Content & tracking

- **About / Resume / FAQ / Contact cards**: editable per language (FA / EN / FR / AR) in Django admin via **django-parler** language tabs. Existing Persian content was migrated as the default (`fa`). Adobe Connect and Download Center are separate (chrome strings / download app) and are not managed by parler.
- **About (landing + `/about/`)**: Django admin → **صفحه درباره ما** (TinyMCE per language).
- **FAQ / Contact**: **Site content** items (translate `key` / `value` per language).
- **Page visits**: path, URL name, and Persian page label are stored (`PageVisit`).
- **Login**: optional «مرا به خاطر بسپار» — checked ≈ 1 year session; unchecked = 30-minute idle logout.

## Notes

- UI language is Persian (RTL). Dates stay Gregorian. Django CLI commands stay in English.
- Signup requires: username, email, password, confirm password, phone number.
- Login accepts username **or** email.
- Profile picture uploads are stored as `.webp` in `backend/media/profile_picture/`.
