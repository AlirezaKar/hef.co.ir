@echo off
setlocal
cd /d "%~dp0.."
cd backend

if not exist ".venv\Scripts\activate.bat" (
  echo Virtual environment not found at backend\.venv
  echo Create it with: python -m venv .venv ^& .venv\Scripts\activate ^& pip install -r requirements.txt
  exit /b 1
)

call ".venv\Scripts\activate.bat"

where gunicorn >nul 2>&1
if errorlevel 1 (
  echo gunicorn not found in the virtual environment.
  echo Install with: pip install gunicorn
  exit /b 1
)

echo Starting Gunicorn on 0.0.0.0:80 ^(for external reverse proxy^)...
echo Note: binding port 80 on Windows usually requires running this script as Administrator.
gunicorn config.wsgi:application --bind 0.0.0.0:80 --workers 2 --timeout 60 --access-logfile - --error-logfile -
