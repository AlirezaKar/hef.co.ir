# Production Deployment Guide (Without Docker)

This guide explains how to deploy HEF in production using systemd for auto-start, Caddy for reverse proxy and TLS, and Gunicorn for the Django application.

## Prerequisites

- Ubuntu 22.04 or Debian 11+
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Caddy 2.x
- Domain name pointing to your server

## 1. Install System Dependencies

```bash
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3-pip \
    postgresql postgresql-contrib redis-server \
    nginx supervisor
```

## 2. Install Caddy

```bash
# Install Caddy
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https curl
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | \
    sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | \
    sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update
sudo apt install caddy
```

## 3. Clone Repository

```bash
sudo mkdir -p /opt/hef
sudo chown $USER:$USER /opt/hef
cd /opt/hef
git clone <your-repo-url> .
```

## 4. Configure Environment

```bash
cd /opt/hef
cp backend/.env.sample backend/.env
nano backend/.env
```

Set the following variables:
```
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
MY_DOMAIN=yourdomain.com
POSTGRES_HOST=localhost
POSTGRES_DB=hef
POSTGRES_USER=hef
POSTGRES_PASSWORD=your-db-password
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```

## 5. Setup Python Virtual Environment

```bash
cd /opt/hef
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r backend/requirements.txt
```

## 6. Configure PostgreSQL

```bash
sudo -u postgres psql

CREATE DATABASE hef;
CREATE USER hef WITH PASSWORD 'your-db-password';
ALTER ROLE hef SET client_encoding TO 'utf8';
ALTER ROLE hef SET default_transaction_isolation TO 'read committed';
ALTER ROLE hef SET timezone TO 'Asia/Tehran';
GRANT ALL PRIVILEGES ON DATABASE hef TO hef;
\q
```

## 7. Run Migrations and Collect Static Files

```bash
cd /opt/hef
source venv/bin/activate

# Run migrations
python backend/manage.py migrate

# Collect static files
python backend/manage.py collectstatic --noinput

# Create superuser
python backend/manage.py createsuperuser

# Generate fake data (optional)
python scripts/generate_fake_data.py
```

## 8. Configure Gunicorn with Systemd

Create systemd service file:

```bash
sudo nano /etc/systemd/system/hef.service
```

Add the following content:

```ini
[Unit]
Description=HEF Django Application
After=network.target postgresql.service redis.service

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/opt/hef
Environment="DJANGO_SETTINGS_MODULE=config.settings"
Environment="PATH=/opt/hef/venv/bin"
ExecStart=/opt/hef/venv/bin/gunicorn config.wsgi:application \
    --bind 127.0.0.1:8000 \
    --workers 4 \
    --timeout 120 \
    --access-logfile /var/log/hef/access.log \
    --error-logfile /var/log/hef/error.log
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

Create log directory:

```bash
sudo mkdir -p /var/log/hef
sudo chown www-data:www-data /var/log/hef
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable hef
sudo systemctl start hef
sudo systemctl status hef
```

## 9. Configure Caddy

```bash
sudo nano /etc/caddy/Caddyfile
```

Replace with the production Caddyfile from this repository:

```bash
sudo cp /opt/hef/Caddyfile /etc/caddy/Caddyfile
sudo nano /etc/caddy/Caddyfile
```

Update `{$MY_DOMAIN}` with your actual domain or set it in environment:

```bash
sudo nano /etc/environment
```

Add:
```
MY_DOMAIN=yourdomain.com
```

Restart Caddy:

```bash
sudo systemctl restart caddy
sudo systemctl status caddy
```

Caddy will automatically:
- Obtain TLS certificate from Let's Encrypt
- Renew certificates automatically
- Redirect HTTP to HTTPS
- Serve as reverse proxy to Gunicorn

## 10. Set File Permissions

```bash
cd /opt/hef
sudo chown -R www-data:www-data backend/media backend/staticfiles
sudo chown -R www-data:www-data /opt/hef/data/History
sudo chown -R www-data:www-data /opt/hef/cdn
```

## 11. Verify Deployment

1. Open https://yourdomain.com in your browser
2. Check that TLS certificate is valid
3. Test admin panel at https://yourdomain.com/admin/
4. Verify static and media files are served correctly

## 12. Maintenance Commands

```bash
# View logs
sudo journalctl -u hef -f
sudo tail -f /var/log/hef/error.log

# Restart application
sudo systemctl restart hef

# Update application
cd /opt/hef
git pull origin main
source venv/bin/activate
pip install -r backend/requirements.txt
python backend/manage.py migrate
python backend/manage.py collectstatic --noinput
sudo systemctl restart hef

# Backup database
sudo -u postgres pg_dump hef > hef_backup_$(date +%Y%m%d).sql
```

## Troubleshooting

### Caddy not obtaining certificate
```bash
sudo systemctl stop caddy
sudo caddy run --config /etc/caddy/Caddyfile
```

### Gunicorn not starting
```bash
sudo journalctl -u hef -n 50 --no-pager
```

### Static files not loading
```bash
cd /opt/hef
source venv/bin/activate
python backend/manage.py collectstatic --noinput
sudo systemctl restart caddy
```

## Security Checklist

- [ ] Change default Django secret key
- [ ] Set DEBUG=False
- [ ] Configure ALLOWED_HOSTS
- [ ] Set strong database password
- [ ] Enable firewall (ufw)
- [ ] Setup regular backups
- [ ] Monitor logs regularly
- [ ] Keep system updated
