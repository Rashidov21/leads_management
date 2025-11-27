@echo off
REM Windows batch script to setup the CRM backend

echo ========================================
echo Education Center CRM - Setup Script
echo ========================================
echo.

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv
call venv\Scripts\activate

echo Installing dependencies...
pip install -r requirements.txt

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Create .env file from .env.example
echo 2. Configure your database
echo 3. Run migrations: python manage.py migrate
echo 4. Create superuser: python manage.py createsuperuser
echo 5. Start Redis: redis-server
echo 6. Start Celery: celery -A crm_project worker -l info
echo 7. Start Beat: celery -A crm_project beat -l info
echo 8. Start Django: python manage.py runserver
echo.
pause
