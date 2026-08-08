@echo off
setlocal EnableExtensions EnableDelayedExpansion
title HEF Django Menu
color 0A

cd /d "%~dp0.."
cd backend

if not exist ".venv\Scripts\activate.bat" (
  echo.
  echo  Virtual environment not found at backend\.venv
  echo  Create it with:
  echo    python -m venv .venv
  echo    .venv\Scripts\activate
  echo    pip install -r requirements.txt
  echo.
  pause
  exit /b 1
)

call ".venv\Scripts\activate.bat"
if errorlevel 1 (
  echo Failed to activate virtual environment.
  pause
  exit /b 1
)

:MENU
cls
echo.
echo  ============================================================
echo                     HEF Django CLI Menu
echo  ============================================================
echo.
echo    [1]  runserver              Start development server
echo    [2]  makemigrations         Create new migrations
echo    [3]  migrate                Apply migrations
echo    [4]  showmigrations         List migration status
echo    [5]  createsuperuser        Create admin user
echo    [6]  collectstatic          Collect static files
echo    [7]  shell                  Open Django shell
echo    [8]  dbshell                Open database shell
echo    [9]  check                  Run Django system checks
echo   [10]  flush                  Wipe DB data ^(keep schema^)
echo   [11]  seed_data              Create dummy / demo data
echo   [12]  custom command         Type any manage.py args
echo.
echo    [0]  Exit
echo.
echo  ------------------------------------------------------------
set "CHOICE="
set /p CHOICE=  Enter option number: 

if "%CHOICE%"=="1"  goto RUNSERVER
if "%CHOICE%"=="2"  goto MAKEMIGRATIONS
if "%CHOICE%"=="3"  goto MIGRATE
if "%CHOICE%"=="4"  goto SHOWMIGRATIONS
if "%CHOICE%"=="5"  goto CREATESUPERUSER
if "%CHOICE%"=="6"  goto COLLECTSTATIC
if "%CHOICE%"=="7"  goto SHELL
if "%CHOICE%"=="8"  goto DBSHELL
if "%CHOICE%"=="9"  goto CHECK
if "%CHOICE%"=="10" goto FLUSH
if "%CHOICE%"=="11" goto SEED
if "%CHOICE%"=="12" goto CUSTOM
if "%CHOICE%"=="0"  goto EXIT

echo.
echo  Invalid option. Try again.
timeout /t 2 >nul
goto MENU

:RUNSERVER
cls
echo.
set "PORT=8000"
set /p PORT=  Port [8000]: 
if "!PORT!"=="" set "PORT=8000"
echo.
echo  Starting: python manage.py runserver !PORT!
echo  Press Ctrl+C to stop the server.
echo.
python manage.py runserver !PORT!
goto PAUSE_BACK

:MAKEMIGRATIONS
cls
echo.
echo  Leave blank to make migrations for all apps.
set "APP="
set /p APP=  App name ^(optional^): 
echo.
if "!APP!"=="" (
  echo  Running: python manage.py makemigrations
  python manage.py makemigrations
) else (
  echo  Running: python manage.py makemigrations !APP!
  python manage.py makemigrations !APP!
)
goto PAUSE_BACK

:MIGRATE
cls
echo.
echo  Leave blank to migrate all apps.
set "APP="
set /p APP=  App name ^(optional^): 
echo.
if "!APP!"=="" (
  echo  Running: python manage.py migrate
  python manage.py migrate
) else (
  echo  Running: python manage.py migrate !APP!
  python manage.py migrate !APP!
)
goto PAUSE_BACK

:SHOWMIGRATIONS
cls
echo.
echo  Running: python manage.py showmigrations
echo.
python manage.py showmigrations
goto PAUSE_BACK

:CREATESUPERUSER
cls
echo.
echo  Running: python manage.py createsuperuser
echo.
python manage.py createsuperuser
goto PAUSE_BACK

:COLLECTSTATIC
cls
echo.
echo  [1] collectstatic --noinput  ^(recommended^)
echo  [2] collectstatic            ^(ask for each file^)
echo  [0] Back
echo.
set "CS="
set /p CS=  Enter option: 
if "!CS!"=="0" goto MENU
if "!CS!"=="2" (
  echo.
  echo  Running: python manage.py collectstatic
  python manage.py collectstatic
  goto PAUSE_BACK
)
echo.
echo  Running: python manage.py collectstatic --noinput
python manage.py collectstatic --noinput
goto PAUSE_BACK

:SHELL
cls
echo.
echo  Running: python manage.py shell
echo  Type exit^(^) or Ctrl+Z then Enter to leave.
echo.
python manage.py shell
goto PAUSE_BACK

:DBSHELL
cls
echo.
echo  Running: python manage.py dbshell
echo.
python manage.py dbshell
goto PAUSE_BACK

:CHECK
cls
echo.
echo  Running: python manage.py check
echo.
python manage.py check
goto PAUSE_BACK

:FLUSH
cls
echo.
echo  WARNING: This deletes ALL data from the database.
echo  Schema / migrations stay. This cannot be undone easily.
echo.
set "CONFIRM="
set /p CONFIRM=  Type YES to continue: 
if /I not "!CONFIRM!"=="YES" (
  echo.
  echo  Cancelled.
  goto PAUSE_BACK
)
echo.
echo  Running: python manage.py flush --no-input
python manage.py flush --no-input
goto PAUSE_BACK

:SEED
cls
echo.
echo  Interactive seed — pick models and row counts.
echo  Running: python manage.py seed_data
echo.
python manage.py seed_data
goto PAUSE_BACK

:CUSTOM
cls
echo.
echo  Examples:
echo    showmigrations app_account
echo    migrate app_account 0005
echo    dumpdata app_account.User --indent 2
echo.
set "ARGS="
set /p ARGS=  manage.py  
if "!ARGS!"=="" (
  echo.
  echo  No args provided.
  goto PAUSE_BACK
)
echo.
echo  Running: python manage.py !ARGS!
python manage.py !ARGS!
goto PAUSE_BACK

:PAUSE_BACK
echo.
echo  ------------------------------------------------------------
pause
goto MENU

:EXIT
echo.
echo  Bye.
endlocal
exit /b 0
