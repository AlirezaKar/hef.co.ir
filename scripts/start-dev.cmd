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
echo Starting Django development server on http://127.0.0.1:8000 ...
python manage.py runserver 8000
