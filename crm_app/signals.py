from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from .models import Lead, FollowUp, TrialLesson, KPI
from .tasks import create_followup_task, send_trial_reminder_task, check_overdue_followups_task


@receiver(post_save, sender=Lead)
def create_followup_on_status_change(sender, instance, created, **kwargs):
    """Avtomatik follow-up yaratish status o'zgarishi bilan"""
    if created:
        # Yangi lid - 5 daqiqada qo'ng'iroq
        due_date = timezone.now() + timedelta(minutes=5)
        FollowUp.objects.create(
            lead=instance,
            sales=instance.assigned_sales,
            due_date=due_date,
            notes="Yangi lid - darhol aloqa qilish kerak"
        )
    else:
        # Status o'zgarishi
        status_followup_map = {
            'contacted': timedelta(hours=24),
            'interested': timedelta(hours=48),
            'trial_registered': timedelta(hours=2),  # Sinov oldidan 2 soat
            'trial_attended': timedelta(minutes=3),  # Sinovdan keyin 3 daqiqa
            'lost': None,  # Lost uchun reactivation
        }
        
        if instance.status in status_followup_map:
            delay = status_followup_map[instance.status]
            if delay:
                due_date = timezone.now() + delay
                FollowUp.objects.create(
                    lead=instance,
                    sales=instance.assigned_sales,
                    due_date=due_date,
                    notes=f"Status: {instance.get_status_display()}"
                )


@receiver(post_save, sender=TrialLesson)
def create_followup_after_trial(sender, instance, created, **kwargs):
    """Sinovdan keyin follow-up yaratish"""
    if not created and instance.result == 'attended':
        # Sinovga keldi - 3 daqiqada taklif
        due_date = timezone.now() + timedelta(minutes=3)
        FollowUp.objects.create(
            lead=instance.lead,
            sales=instance.lead.assigned_sales,
            due_date=due_date,
            notes="Sinovga keldi - sotuv taklifi berish kerak"
        )


@receiver(pre_save, sender=FollowUp)
def check_overdue(sender, instance, **kwargs):
    """Follow-up overdue ekanligini tekshirish"""
    if instance.due_date and timezone.now() > instance.due_date and not instance.completed:
        instance.is_overdue = True

