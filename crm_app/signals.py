from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from .models import Lead, FollowUp, TrialLesson, KPI
from .tasks import (
    send_new_lead_notification,
    send_status_change_notification,
    send_followup_created_notification,
)


@receiver(pre_save, sender=Lead)
def store_old_status(sender, instance, **kwargs):
    """Status o'zgarishini aniqlash uchun eski statusni saqlash"""
    if instance.pk:
        try:
            old_instance = Lead.objects.get(pk=instance.pk)
            instance._old_status = old_instance.status
        except Lead.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender=Lead)
def create_followup_on_status_change(sender, instance, created, **kwargs):
    """Avtomatik follow-up yaratish status o'zgarishi bilan"""
    if created:
        # Yangi lid - 5 daqiqada qo'ng'iroq
        if instance.assigned_sales:
            due_date = timezone.now() + timedelta(minutes=5)
            followup = FollowUp.objects.create(
                lead=instance,
                sales=instance.assigned_sales,
                due_date=due_date,
                notes="Yangi lid - darhol aloqa qilish kerak"
            )
            # Telegram xabarlar
            send_new_lead_notification.delay(instance.id)
            send_followup_created_notification.delay(followup.id)
    else:
        # Status o'zgarishi
        if not instance.assigned_sales:
            return
        
        # Status o'zgarganda notification yuborish
        old_status = getattr(instance, '_old_status', None)
        if old_status and old_status != instance.status:
            send_status_change_notification.delay(instance.id, old_status, instance.status)
            
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
                followup = FollowUp.objects.create(
                    lead=instance,
                    sales=instance.assigned_sales,
                    due_date=due_date,
                    notes=f"Status: {instance.get_status_display()}"
                )
                # Follow-up yaratilganda notification
                send_followup_created_notification.delay(followup.id)


@receiver(post_save, sender=TrialLesson)
def create_followup_after_trial(sender, instance, created, **kwargs):
    """Sinovdan keyin follow-up yaratish"""
    if not created and instance.result == 'attended':
        # Sinovga keldi - 3 daqiqada taklif
        due_date = timezone.now() + timedelta(minutes=3)
        followup = FollowUp.objects.create(
            lead=instance.lead,
            sales=instance.lead.assigned_sales,
            due_date=due_date,
            notes="Sinovga keldi - sotuv taklifi berish kerak"
        )
        # Follow-up yaratilganda notification
        send_followup_created_notification.delay(followup.id)


@receiver(pre_save, sender=FollowUp)
def check_overdue(sender, instance, **kwargs):
    """Follow-up overdue ekanligini tekshirish"""
    if instance.due_date and timezone.now() > instance.due_date and not instance.completed:
        instance.is_overdue = True


@receiver(post_save, sender=FollowUp)
def notify_followup_created(sender, instance, created, **kwargs):
    """Follow-up yaratilganda notification (agar boshqa joyda yaratilmagan bo'lsa)"""
    if created and instance.sales and instance.sales.telegram_chat_id:
        # Faqat boshqa signal'lar orqali yaratilmagan follow-up'lar uchun
        # (chunki boshqa joylarda allaqachon notification yuboriladi)
        # Bu yerda faqat qo'lda yaratilgan follow-up'lar uchun
        send_followup_created_notification.delay(instance.id)

