@echo off
echo Celery Beat ishga tushiryapman...
celery -A crm_project beat --loglevel=info

