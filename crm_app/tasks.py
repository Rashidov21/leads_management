from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import Lead, FollowUp, TrialLesson, Reactivation
from .services import FollowUpService, KPIService, ReactivationService
from .telegram_bot import send_telegram_notification


@shared_task
def create_followup_task(lead_id, delay_minutes=5):
    """Follow-up yaratish task"""
    try:
        lead = Lead.objects.get(id=lead_id)
        due_date = timezone.now() + timedelta(minutes=delay_minutes)
        FollowUp.objects.create(
            lead=lead,
            sales=lead.assigned_sales,
            due_date=due_date
        )
    except Lead.DoesNotExist:
        pass


@shared_task
def check_overdue_followups_task():
    """Overdue follow-uplarni tekshirish"""
    overdue_followups = FollowUpService.get_overdue_followups()
    
    for followup in overdue_followups:
        followup.is_overdue = True
        followup.save()
        
        # Sotuvchiga xabar
        if followup.sales.telegram_chat_id:
            send_telegram_notification(
                followup.sales.telegram_chat_id,
                f"⚠️ Overdue follow-up!\n"
                f"Lid: {followup.lead.name}\n"
                f"Vaqt: {followup.due_date.strftime('%Y-%m-%d %H:%M')}"
            )
        
        # Manager/Admin ga xabar
        overdue_count = FollowUpService.get_overdue_followups(followup.sales).count()
        if overdue_count >= 5:
            # Manager ga xabar yuborish
            send_telegram_notification(
                settings.TELEGRAM_ADMIN_CHAT_ID,
                f"⚠️ Sotuvchi {followup.sales.username} da 5+ overdue follow-up bor!"
            )


@shared_task
def send_trial_reminder_task():
    """Sinov oldidan eslatma yuborish (2 soat oldin)"""
    two_hours_later = timezone.now() + timedelta(hours=2)
    tomorrow = timezone.now().date() + timedelta(days=1)
    
    trials = TrialLesson.objects.filter(
        date=timezone.now().date(),
        reminder_sent=False
    )
    
    for trial in trials:
        trial_time = timezone.datetime.combine(trial.date, trial.time)
        if trial_time <= two_hours_later:
            # Telegram xabar yuborish
            if trial.lead.assigned_sales.telegram_chat_id:
                send_telegram_notification(
                    trial.lead.assigned_sales.telegram_chat_id,
                    f"🔔 Sinov eslatmasi!\n"
                    f"Lid: {trial.lead.name}\n"
                    f"Vaqt: {trial.date} {trial.time}\n"
                    f"Xona: {trial.room.name if trial.room else 'N/A'}"
                )
            trial.reminder_sent = True
            trial.save()


@shared_task
def calculate_daily_kpi_task():
    """Kunlik KPI hisoblash"""
    from .models import User
    
    today = timezone.now().date()
    sales_users = User.objects.filter(role='sales', is_active_sales=True)
    
    for sales in sales_users:
        try:
            KPIService.calculate_daily_kpi(sales, today)
        except Exception as e:
            print(f"KPI hisoblashda xatolik ({sales.username}): {e}")


@shared_task
def reactivation_task():
    """Reaktivatsiya tekshirish"""
    ReactivationService.check_and_reactivate()


@shared_task
def send_new_lead_notification(lead_id):
    """Yangi lid haqida xabar"""
    try:
        lead = Lead.objects.get(id=lead_id)
        if lead.assigned_sales and lead.assigned_sales.telegram_chat_id:
            send_telegram_notification(
                lead.assigned_sales.telegram_chat_id,
                f"🆕 Yangi lid!\n"
                f"Ism: {lead.name}\n"
                f"Telefon: {lead.phone}\n"
                f"Kurs: {lead.interested_course.name if lead.interested_course else 'N/A'}\n"
                f"Manba: {lead.get_source_display()}"
            )
    except Lead.DoesNotExist:
        pass

