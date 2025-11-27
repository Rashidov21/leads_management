"""
Celery configuration for leads_management project.
"""
import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'leads_management.settings')

app = Celery('leads_management')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Celery Beat schedule
app.conf.beat_schedule = {
    'sync-google-sheets': {
        'task': 'leads.tasks.sync_google_sheets',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
    },
    'calculate-kpis': {
        'task': 'kpi.tasks.calculate_kpis',
        'schedule': crontab(hour='*/6'),  # Every 6 hours
    },
    'calculate-monthly-summaries': {
        'task': 'leads.tasks.calculate_monthly_kpi_summaries',
        'schedule': crontab(hour=0, minute=0),  # Daily at midnight
    },
    'send-lead-reminders': {
        'task': 'leads.tasks.send_lead_reminders',
        'schedule': crontab(hour='*/4'),  # Every 4 hours
    },
}
