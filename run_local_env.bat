@echo off
setlocal

REM Project and venv paths
set PROJECT_DIR=%~dp0
if "%PROJECT_DIR:~-1%"=="\" set PROJECT_DIR=%PROJECT_DIR:~0,-1%
set VENV_DIR=%PROJECT_DIR%\.venv

cd /d "%PROJECT_DIR%"

if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo [!] Virtualenv topilmadi: %VENV_DIR%
    echo Avval ^"python -m venv .venv && .venv\Scripts\pip install -r requirements.txt^" bajarib oling.
    exit /b 1
)

REM Redis xizmat sifatida ishlayotgan bo'lsa, quyidagini o'chirmang; aks holda yo'lini moslang.
REM start "redis" "C:\path\to\redis-server.exe"

REM Celery worker
start "celery-worker" cmd /k "call "%VENV_DIR%\Scripts\activate" && python -m dotenv run -- celery -A crm_project worker -l info"

REM Celery beat
start "celery-beat" cmd /k "call "%VENV_DIR%\Scripts\activate" && python -m dotenv run -- celery -A crm_project beat -l info"

REM Django runserver
start "django" cmd /k "call "%VENV_DIR%\Scripts\activate" && python -m dotenv run -- python manage.py runserver 0.0.0.0:8000"

endlocal

