"""
Celery config for crm_project.
"""
import os
from celery import Celery
from celery.schedules import schedule

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_project.settings')

app = Celery('crm_project')

# Load configuration from Django settings with namespace
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all registered Django apps
app.autodiscover_tasks()

# Celery Beat Schedule for periodic tasks
app.conf.beat_schedule = {
    'import-from-google-sheets': {
        'task': 'import_service.tasks.import_from_google_sheets',
        'schedule': 300.0,  # Every 5 minutes
        'options': {'queue': 'imports'}
    },
    'check-reminder-deadlines': {
        'task': 'reminders.tasks.check_reminder_deadlines',
        'schedule': 60.0,  # Every 1 minute
        'options': {'queue': 'reminders'}
    },
}
