from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from .models import Lead, FollowUp, TrialLesson, KPI, LeaveRequest
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
    from .services import FollowUpService
    
    if created:
        # Yangi lid - 5 daqiqada qo'ng'iroq
        # Agar assigned_sales bo'lsa, follow-up yaratish va notification yuborish
        if instance.assigned_sales:
            base_time = timezone.now()
            delay = timedelta(minutes=5)
            # Ish vaqtiga moslashtirish (5 daqiqa juda qisqa, lekin ish vaqti tashqarisida bo'lsa keyingi kun boshlanishiga)
            due_date = FollowUpService.calculate_work_hours_due_date(
                instance.assigned_sales, 
                base_time, 
                delay
            )
            followup = FollowUp.objects.create(
                lead=instance,
                sales=instance.assigned_sales,
                due_date=due_date,
                notes="Yangi lid - darhol aloqa qilish kerak"
            )
            # Telegram xabarlar
            # Notification faqat bir marta yuborilishi kerak
            # Agar distribute_leads ichida yuborilgan bo'lsa, bu yerda yubormaslik
            # Lekin agar qo'lda assigned_sales biriktirilgan bo'lsa, bu yerda yuborish
            # Bu muammoni hal qilish uchun, notification yuborishni faqat distribute_leads ichida qilamiz
            # Yoki bu yerda ham yuborish, lekin dublikatsiyani oldini olish
            send_followup_created_notification.delay(followup.id)
        # Eslatma: send_new_lead_notification distribute_leads ichida yuboriladi
        # Agar qo'lda assigned_sales biriktirilgan bo'lsa, views.py da yuboriladi
    else:
        # Status o'zgarishi
        if not instance.assigned_sales:
            return
        
        # Status o'zgarganda notification yuborish
        old_status = getattr(instance, '_old_status', None)
        if old_status and old_status != instance.status:
            send_status_change_notification.delay(instance.id, old_status, instance.status)
        
        # Contacted status uchun ko'p bosqichli follow-up
        if instance.status == 'contacted':
            delays = [
                timedelta(hours=24),   # 1-aloqa
                timedelta(hours=48),   # 2-aloqa
                timedelta(hours=72),   # 3-aloqa
            ]
            base_time = timezone.now()
            for delay in delays:
                due_date = FollowUpService.calculate_work_hours_due_date(
                    instance.assigned_sales,
                    base_time,
                    delay
                )
                hours = int(delay.total_seconds() / 3600)
                followup = FollowUp.objects.create(
                    lead=instance,
                    sales=instance.assigned_sales,
                    due_date=due_date,
                    notes=f"Contacted - {hours} soatdan keyin aloqa (ko'proq ma'lumot, kurs narxi, jadval, guruhlar)"
                )
                send_followup_created_notification.delay(followup.id)
        
        # Interested status uchun ko'p bosqichli follow-up
        elif instance.status == 'interested':
            delays = [
                timedelta(days=1),   # 1-kun: qo'shimcha ma'lumot
                timedelta(days=3),   # 3-kun: guruhlar bandligi haqida xabar
                timedelta(days=5),   # 5-kun: oxirgi joylar haqida eslatma
                timedelta(days=7),   # 7-kun: "qaror qilishga yordam berish" qo'ng'irog'i
            ]
            base_time = timezone.now()
            notes_map = {
                1: "Qo'shimcha ma'lumot",
                3: "Guruhlar bandligi haqida xabar",
                5: "Oxirgi joylar haqida eslatma",
                7: "Qaror qilishga yordam berish",
            }
            for delay in delays:
                due_date = FollowUpService.calculate_work_hours_due_date(
                    instance.assigned_sales,
                    base_time,
                    delay
                )
                days = delay.days
                followup = FollowUp.objects.create(
                    lead=instance,
                    sales=instance.assigned_sales,
                    due_date=due_date,
                    notes=f"Interested - {days} kundan keyin: {notes_map.get(days, 'Follow-up')}"
                )
                send_followup_created_notification.delay(followup.id)
        
        # Trial Registered uchun 1 kun va 2 soat oldin eslatma
        elif instance.status == 'trial_registered':
            # Sinov sanasini topish
            trial = instance.trials.filter(result__in=['', 'attended', 'not_attended']).order_by('date', 'time').first()
            if trial:
                trial_datetime = timezone.make_aware(
                    timezone.datetime.combine(trial.date, trial.time)
                )
                now = timezone.now()
                
                # 1 kun oldin eslatma
                one_day_before = trial_datetime - timedelta(days=1)
                if one_day_before > now:
                    due_date = FollowUpService.calculate_work_hours_due_date(
                        instance.assigned_sales,
                        one_day_before,
                        timedelta(0)
                    )
                    # Follow-up allaqachon yaratilganligini tekshirish
                    existing = FollowUp.objects.filter(
                        lead=instance,
                        notes__contains="Sinovdan 1 kun oldin",
                        completed=False
                    ).exists()
                    if not existing:
                        followup = FollowUp.objects.create(
                            lead=instance,
                            sales=instance.assigned_sales,
                            due_date=due_date,
                            notes="Sinovdan 1 kun oldin eslatma"
                        )
                        send_followup_created_notification.delay(followup.id)
                
                # 2 soat oldin eslatma + lokatsiya
                two_hours_before = trial_datetime - timedelta(hours=2)
                if two_hours_before > now:
                    due_date = FollowUpService.calculate_work_hours_due_date(
                        instance.assigned_sales,
                        two_hours_before,
                        timedelta(0)
                    )
                    existing = FollowUp.objects.filter(
                        lead=instance,
                        notes__contains="Sinovdan 2 soat oldin",
                        completed=False
                    ).exists()
                    if not existing:
                        followup = FollowUp.objects.create(
                            lead=instance,
                            sales=instance.assigned_sales,
                            due_date=due_date,
                            notes="Sinovdan 2 soat oldin eslatma + lokatsiya"
                        )
                        send_followup_created_notification.delay(followup.id)
        
        # Trial Attended - follow-up yaratmaymiz (offline taklif beriladi)
        # Lekin agar 24 soatdan keyin enrolled bo'lmagan bo'lsa, follow-up yaratamiz
        # Bu Celery task orqali tekshiriladi (check_trial_attended_not_enrolled_task)
        
        # Trial Not Attended uchun follow-up
        elif instance.status == 'trial_not_attended':
            delays = [
                timedelta(minutes=30),  # 30 daqiqa
                timedelta(hours=24),    # 24 soat
                timedelta(days=3),      # 3-kun
            ]
            base_time = timezone.now()
            notes_map = {
                timedelta(minutes=30): "Sinovga kelmadi - 30 daqiqadan keyin qayta yozish",
                timedelta(hours=24): "Sinovga kelmadi - 24 soatdan keyin qayta taklif",
                timedelta(days=3): "Sinovga kelmadi - 3 kundan keyin uzr va qayta imkon taklifi",
            }
            for delay in delays:
                due_date = FollowUpService.calculate_work_hours_due_date(
                    instance.assigned_sales,
                    base_time,
                    delay
                )
                followup = FollowUp.objects.create(
                    lead=instance,
                    sales=instance.assigned_sales,
                    due_date=due_date,
                    notes=notes_map.get(delay, f"Trial Not Attended - {delay}")
                )
                send_followup_created_notification.delay(followup.id)
        
        # Lost uchun reactivation (mavjud ReactivationService orqali boshqariladi)
        elif instance.status == 'lost':
            pass  # ReactivationService orqali boshqariladi


@receiver(post_save, sender=TrialLesson)
def create_followup_after_trial(sender, instance, created, **kwargs):
    """
    Sinovdan keyin follow-up yaratish
    Eslatma: Trial Attended bo'lganda offline taklif beriladi,
    shuning uchun 3 daqiqada follow-up yaratmaymiz.
    Agar 24 soatdan keyin enrolled bo'lmagan bo'lsa, 
    check_trial_attended_not_enrolled_task orqali follow-up yaratiladi.
    Sinov darsi tugagandan keyin (90 minutdan keyin) follow-up 
    create_followup_after_trial_end_task orqali yaratiladi.
    """
    # Trial Attended uchun follow-up yaratmaymiz (offline taklif)
    # Sinov darsi tugagandan keyin follow-up create_followup_after_trial_end_task orqali yaratiladi
    pass


@receiver(pre_save, sender=FollowUp)
def check_overdue(sender, instance, **kwargs):
    """Follow-up overdue ekanligini tekshirish"""
    if instance.due_date and timezone.now() > instance.due_date and not instance.completed:
        instance.is_overdue = True


# @receiver(post_save, sender=FollowUp)
# def notify_followup_created(sender, instance, created, **kwargs):
#     """Follow-up yaratilganda notification (agar boshqa joyda yaratilmagan bo'lsa)"""
#     # Bu signal olib tashlandi, chunki dublikatsiya muammosiga olib keladi
#     # Barcha follow-up'lar allaqachon boshqa signal'lar orqali yuboriladi:
#     # - create_followup_on_status_change (yangi lid va status o'zgarishi)
#     # - create_followup_after_trial (sinovdan keyin)
#     # Qo'lda yaratilgan follow-up'lar uchun alohida notification kerak bo'lsa,
#     # views.py da yuborish kerak
#     pass


@receiver(post_save, sender=LeaveRequest)
def handle_leave_request_status_change(sender, instance, created, **kwargs):
    """Ruxsat so'rovi statusi o'zgarganda ishdan ruxsat holatini yangilash"""
    from .models import User
    
    # Agar ruxsat tasdiqlangan bo'lsa
    if instance.status == 'approved':
        # Agar butun kun ruxsat bo'lsa, is_on_leave ni True qilish
        if not instance.start_time and not instance.end_time:
            instance.sales.is_on_leave = True
            instance.sales.save()
    
    # Agar ruxsat rad etilgan bo'lsa yoki ruxsat tugagan bo'lsa
    elif instance.status == 'rejected':
        # is_on_leave ni False qilish
        if instance.sales.is_on_leave:
            instance.sales.is_on_leave = False
            instance.sales.save()
    
    # Ruxsat tugagandan keyin is_on_leave ni o'chirish
    # Bu Celery task orqali tekshiriladi (check_expired_leaves_task)

