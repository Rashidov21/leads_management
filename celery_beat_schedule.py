"""
Celery Beat schedule configuration
Bu fayl celery beat ishga tushirish uchun
"""
from celery.schedules import crontab

beat_schedule = {
    'check-overdue-followups': {
        'task': 'crm_app.tasks.check_overdue_followups_task',
        'schedule': crontab(minute='*/15'),  # Har 15 daqiqada
    },
    'send-trial-reminders': {
        'task': 'crm_app.tasks.send_trial_reminder_task',
        'schedule': crontab(minute='*/30'),  # Har 30 daqiqada
    },
    'calculate-daily-kpi': {
        'task': 'crm_app.tasks.calculate_daily_kpi_task',
        'schedule': crontab(hour=23, minute=59),  # Har kuni kechasi
    },
    'check-reactivation': {
        'task': 'crm_app.tasks.reactivation_task',
        'schedule': crontab(hour=9, minute=0),  # Har kuni ertalab
    },
}

