#!/bin/bash
# HEF Production Deployment Script
# This script automates the production deployment process

set -e

echo "==================================="
echo "HEF Production Deployment"
echo "==================================="
echo

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (use sudo)"
    exit 1
fi

# Configuration
APP_DIR="/opt/hef"
SERVICE_NAME="hef"
LOG_DIR="/var/log/hef"

echo "1. Installing system dependencies..."
apt update
apt install -y python3.11 python3.11-venv python3-pip \
    postgresql postgresql-contrib redis-server \
    caddy

echo
echo "2. Setting up application directory..."
mkdir -p $APP_DIR
chown $SUDO_USER:$SUDO_USER $APP_DIR

echo
echo "3. Cloning repository..."
if [ -d "$APP_DIR/.git" ]; then
    echo "Repository already exists, pulling latest changes..."
    cd $APP_DIR
    git pull origin main
else
    echo "Please clone your repository to $APP_DIR manually"
    echo "Then re-run this script"
    exit 1
fi

echo
echo "4. Setting up Python virtual environment..."
cd $APP_DIR
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r backend/requirements.txt

echo
echo "5. Configuring environment..."
if [ ! -f backend/.env ]; then
    cp backend/.env.sample backend/.env
    echo "Please edit backend/.env with your settings"
    nano backend/.env
fi

echo
echo "6. Setting up PostgreSQL..."
echo "Please manually configure PostgreSQL:"
echo "  - Create database: hef"
echo "  - Create user: hef with password"
echo "  - Grant privileges"
echo
echo "Then run: python backend/manage.py migrate"

echo
echo "7. Creating log directory..."
mkdir -p $LOG_DIR
chown www-data:www-data $LOG_DIR

echo
echo "8. Installing systemd service..."
cp scripts/hef.service /etc/systemd/system/$SERVICE_NAME.service
systemctl daemon-reload
systemctl enable $SERVICE_NAME

echo
echo "9. Configuring Caddy..."
cp Caddyfile /etc/caddy/Caddyfile
echo "Please update /etc/caddy/Caddyfile with your domain"
echo "Then run: systemctl restart caddy"

echo
echo "10. Setting permissions..."
chown -R www-data:www-data backend/media backend/staticfiles
chown -R www-data:www-data data/History cdn

echo
echo "==================================="
echo "Deployment Complete!"
echo "==================================="
echo
echo "Next steps:"
echo "1. Configure PostgreSQL database"
echo "2. Run: cd $APP_DIR && source venv/bin/activate && python backend/manage.py migrate"
echo "3. Run: python backend/manage.py createsuperuser"
echo "4. Update /etc/caddy/Caddyfile with your domain"
echo "5. Run: systemctl start $SERVICE_NAME"
echo "6. Run: systemctl restart caddy"
echo
echo "View logs:"
echo "  sudo journalctl -u $SERVICE_NAME -f"
echo "  sudo tail -f $LOG_DIR/error.log"
