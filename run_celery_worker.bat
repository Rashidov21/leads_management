@echo off
echo Celery Worker ishga tushiryapman...
celery -A crm_project worker --loglevel=info

