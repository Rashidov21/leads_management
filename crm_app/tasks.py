from celery import shared_task
from django.utils import timezone
from django.conf import settings
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
            if trial.lead.assigned_sales and trial.lead.assigned_sales.telegram_chat_id:
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
def send_followup_reminders_task():
    """Follow-up eslatmalari yuborish (1 soat oldin)"""
    now = timezone.now()
    one_hour_later = now + timedelta(hours=1)
    
    # 1 soat ichida bajarilishi kerak bo'lgan follow-up'lar
    upcoming_followups = FollowUp.objects.filter(
        due_date__gte=now,
        due_date__lte=one_hour_later,
        completed=False,
        reminder_sent=False
    )
    
    for followup in upcoming_followups:
        if followup.sales and followup.sales.telegram_chat_id:
            due_date_str = followup.due_date.strftime('%d.%m.%Y %H:%M')
            minutes_left = int((followup.due_date - now).total_seconds() / 60)
            
            send_telegram_notification(
                followup.sales.telegram_chat_id,
                f"⏰ Follow-up eslatmasi!\n"
                f"Lid: {followup.lead.name}\n"
                f"Vaqt: {due_date_str}\n"
                f"Qolgan vaqt: {minutes_left} daqiqa\n"
                f"Eslatma: {followup.notes[:50] if followup.notes else 'Yo\'q'}"
            )
            followup.reminder_sent = True
            followup.save()


@shared_task
def send_post_trial_sales_reminder_task():
    """Sinovdan keyin sotuv taklifi eslatmasi"""
    # Sinovdan keyin 3 daqiqada follow-up yaratiladi, lekin alohida eslatma ham yuboramiz
    # Sinovga keldi va natija 'attended' bo'lgan, lekin hali 'enrolled' bo'lmagan lidlar
    from datetime import date
    
    today = timezone.now().date()
    yesterday = today - timedelta(days=1)
    
    # Kechagi va bugungi sinovlar
    recent_trials = TrialLesson.objects.filter(
        date__gte=yesterday,
        result='attended',
        sales_reminder_sent=False
    )
    
    for trial in recent_trials:
        # Agar lid hali 'enrolled' bo'lmagan bo'lsa
        if trial.lead.status != 'enrolled' and trial.lead.assigned_sales:
            if trial.lead.assigned_sales.telegram_chat_id:
                send_telegram_notification(
                    trial.lead.assigned_sales.telegram_chat_id,
                    f"💰 Sotuv taklifi!\n"
                    f"Lid: {trial.lead.name}\n"
                    f"Telefon: {trial.lead.phone}\n"
                    f"Sinovga keldi: {trial.date}\n"
                    f"Kurs: {trial.lead.interested_course.name if trial.lead.interested_course else 'N/A'}\n"
                    f"⚠️ Sotuv taklifi berish vaqt keldi!"
                )
            trial.sales_reminder_sent = True
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


@shared_task
def send_status_change_notification(lead_id, old_status, new_status):
    """Status o'zgarishi haqida xabar"""
    try:
        lead = Lead.objects.get(id=lead_id)
        if lead.assigned_sales and lead.assigned_sales.telegram_chat_id:
            status_display = lead.get_status_display()
            send_telegram_notification(
                lead.assigned_sales.telegram_chat_id,
                f"📊 Status o'zgardi!\n"
                f"Lid: {lead.name}\n"
                f"Eski status: {dict(Lead.STATUS_CHOICES).get(old_status, old_status)}\n"
                f"Yangi status: {status_display}\n"
                f"Telefon: {lead.phone}"
            )
    except Lead.DoesNotExist:
        pass


@shared_task
def send_followup_created_notification(followup_id):
    """Follow-up yaratilganda xabar"""
    try:
        followup = FollowUp.objects.get(id=followup_id)
        if followup.sales and followup.sales.telegram_chat_id:
            due_date_str = followup.due_date.strftime('%d.%m.%Y %H:%M')
            send_telegram_notification(
                followup.sales.telegram_chat_id,
                f"📋 Yangi follow-up!\n"
                f"Lid: {followup.lead.name}\n"
                f"Vaqt: {due_date_str}\n"
                f"Eslatma: {followup.notes[:50] if followup.notes else 'Yo\'q'}"
            )
    except FollowUp.DoesNotExist:
        pass


@shared_task
def send_reactivation_notification(reactivation_id):
    """Reaktivatsiya haqida xabar"""
    try:
        reactivation = Reactivation.objects.get(id=reactivation_id)
        lead = reactivation.lead
        if lead.assigned_sales and lead.assigned_sales.telegram_chat_id:
            reactivation_type_map = {
                '7_days': '7 kun o\'tdi - qayta taklif qilish',
                '14_days': '14 kun o\'tdi - boshqa kurs tavsiyasi',
                '30_days': '30 kun o\'tdi - yangi guruhlar haqida xabar',
            }
            message = reactivation_type_map.get(reactivation.reactivation_type, 'Reaktivatsiya')
            
            send_telegram_notification(
                lead.assigned_sales.telegram_chat_id,
                f"🔄 Reaktivatsiya!\n"
                f"Lid: {lead.name}\n"
                f"Telefon: {lead.phone}\n"
                f"Tavsiya: {message}\n"
                f"Kurs: {lead.interested_course.name if lead.interested_course else 'N/A'}"
            )
    except Reactivation.DoesNotExist:
        pass

