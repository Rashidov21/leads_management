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
        from .services import FollowUpService
        
        lead = Lead.objects.get(id=lead_id)
        if not lead.assigned_sales:
            return
        
        base_time = timezone.now()
        delay = timedelta(minutes=delay_minutes)
        # Ish vaqtiga moslashtirish
        due_date = FollowUpService.calculate_work_hours_due_date(
            lead.assigned_sales,
            base_time,
            delay
        )
        followup = FollowUp.objects.create(
            lead=lead,
            sales=lead.assigned_sales,
            due_date=due_date,
            notes="Qo'lda yaratilgan follow-up"
        )
        # Notification yuborish (qo'lda yaratilgan follow-up uchun)
        send_followup_created_notification.delay(followup.id)
    except Lead.DoesNotExist:
        pass


@shared_task
def check_overdue_followups_task():
    """Overdue follow-uplarni tekshirish va notification yuborish"""
    try:
        print(f"[{timezone.now()}] check_overdue_followups_task ishga tushdi")
        overdue_followups = FollowUpService.get_overdue_followups().select_related('lead', 'sales')
        
        # Har bir sotuvchi uchun overdue sonini hisoblash
        sales_overdue_count = {}
        notifications_sent = 0
        
        for followup in overdue_followups:
            # Overdue flag'ni o'rnatish
            if not followup.is_overdue:
                followup.is_overdue = True
                followup.save()
            
            # Sotuvchiga xabar (faqat birinchi marta)
            if followup.sales and followup.sales.telegram_chat_id:
                due_date_str = followup.due_date.strftime('%d.%m.%Y %H:%M')
                message = (
                    f"⚠️ <b>OVERDUE FOLLOW-UP!</b>\n"
                    f"{'=' * 25}\n\n"
                    f"👤 <b>Lid:</b> {followup.lead.name}\n"
                    f"📞 <b>Telefon:</b> <code>{followup.lead.phone}</code>\n\n"
                    f"⏰ <b>Vaqt:</b> {due_date_str}\n"
                    f"❌ <b>Vaqt o'tib ketdi!</b>\n\n"
                )
                
                if followup.notes:
                    message += f"📝 <b>Eslatma:</b>\n{followup.notes[:100]}\n\n"
                
                message += "🔴 <b>DARHOL ALOQA QILING!</b>"
                
                if send_telegram_notification(
                    followup.sales.telegram_chat_id,
                    message
                ):
                    notifications_sent += 1
            
            # Sotuvchi uchun overdue sonini hisoblash
            if followup.sales:
                sales_id = followup.sales.id
                if sales_id not in sales_overdue_count:
                    sales_overdue_count[sales_id] = {
                        'sales': followup.sales,
                        'count': 0
                    }
                sales_overdue_count[sales_id]['count'] += 1
        
        # Manager/Admin ga xabar (5+ overdue bo'lsa)
        if settings.TELEGRAM_ADMIN_CHAT_ID:
            for sales_id, data in sales_overdue_count.items():
                if data['count'] >= 5:
                    send_telegram_notification(
                        settings.TELEGRAM_ADMIN_CHAT_ID,
                        f"⚠️ Sotuvchi {data['sales'].username} da {data['count']} ta overdue follow-up bor!\n"
                        f"Darhol tekshirish kerak."
                    )
        
        print(f"[{timezone.now()}] check_overdue_followups_task yakunlandi: {notifications_sent} ta notification yuborildi")
    except Exception as e:
        print(f"[{timezone.now()}] check_overdue_followups_task xatolik: {e}")
        import traceback
        traceback.print_exc()


@shared_task
def send_trial_reminder_task():
    """Sinov oldidan eslatma yuborish (2 soat oldin)"""
    try:
        print(f"[{timezone.now()}] send_trial_reminder_task ishga tushdi")
        now = timezone.now()
        two_hours_later = now + timedelta(hours=2)
        today = now.date()
        
        # Bugungi sinovlar
        trials = TrialLesson.objects.filter(
            date=today,
            reminder_sent=False,
            lead__status__in=['trial_registered', 'trial_attended']  # Faqat sinovga yozilganlar
        ).select_related('lead', 'lead__assigned_sales', 'group', 'room')
        
        notifications_sent = 0
        for trial in trials:
            # Timezone aware datetime yaratish
            trial_datetime = timezone.make_aware(
                timezone.datetime.combine(trial.date, trial.time)
            )
            
            # Agar sinov 2 soat ichida bo'lsa, eslatma yuborish
            if now <= trial_datetime <= two_hours_later:
                # Telegram xabar yuborish
                if trial.lead.assigned_sales and trial.lead.assigned_sales.telegram_chat_id:
                    hours_left = int((trial_datetime - now).total_seconds() / 3600)
                    minutes_left = int(((trial_datetime - now).total_seconds() % 3600) / 60)
                    
                    time_str = f"{hours_left} soat {minutes_left} daqiqa" if hours_left > 0 else f"{minutes_left} daqiqa"
                    
                    message = (
                        f"🔔 <b>SINOV ESLATMASI</b>\n"
                        f"{'=' * 25}\n\n"
                        f"👤 <b>Lid:</b> {trial.lead.name}\n"
                        f"📞 <b>Telefon:</b> <code>{trial.lead.phone}</code>\n\n"
                        f"📅 <b>Sinov vaqti:</b>\n"
                        f"📆 {trial.date.strftime('%d.%m.%Y')}\n"
                        f"🕐 {trial.time.strftime('%H:%M')}\n\n"
                        f"⏱️ <b>Qolgan vaqt:</b> {time_str}\n\n"
                        f"👥 <b>Guruh:</b> {trial.group.name if trial.group else 'N/A'}\n"
                        f"🏢 <b>Xona:</b> {trial.room.name if trial.room else 'N/A'}\n\n"
                        f"💡 <b>Eslatma:</b> Sinovdan oldin lid bilan aloqa qiling!"
                    )
                    
                    if send_telegram_notification(
                        trial.lead.assigned_sales.telegram_chat_id,
                        message
                    ):
                        notifications_sent += 1
                trial.reminder_sent = True
                trial.save()
        
        print(f"[{timezone.now()}] send_trial_reminder_task yakunlandi: {notifications_sent} ta notification yuborildi")
    except Exception as e:
        print(f"[{timezone.now()}] send_trial_reminder_task xatolik: {e}")
        import traceback
        traceback.print_exc()


@shared_task
def send_followup_reminders_task():
    """Follow-up eslatmalari yuborish (1 soat oldin)"""
    try:
        print(f"[{timezone.now()}] send_followup_reminders_task ishga tushdi")
        now = timezone.now()
        one_hour_later = now + timedelta(hours=1)
        
        # 1 soat ichida bajarilishi kerak bo'lgan follow-up'lar
        upcoming_followups = FollowUp.objects.filter(
            due_date__gte=now,
            due_date__lte=one_hour_later,
            completed=False,
            reminder_sent=False,
            sales__isnull=False  # Faqat assigned sales bo'lganlar
        ).select_related('lead', 'sales')
        
        notifications_sent = 0
        for followup in upcoming_followups:
            if followup.sales and followup.sales.telegram_chat_id:
                due_date_str = followup.due_date.strftime('%d.%m.%Y %H:%M')
                minutes_left = int((followup.due_date - now).total_seconds() / 60)
                
                # Vaqt formatlash
                if minutes_left >= 60:
                    hours = minutes_left // 60
                    mins = minutes_left % 60
                    time_left = f"{hours} soat {mins} daqiqa"
                else:
                    time_left = f"{minutes_left} daqiqa"
                
                message = (
                    f"⏰ <b>FOLLOW-UP ESLATMASI</b>\n"
                    f"{'=' * 25}\n\n"
                    f"👤 <b>Lid:</b> {followup.lead.name}\n"
                    f"📞 <b>Telefon:</b> <code>{followup.lead.phone}</code>\n\n"
                    f"⏰ <b>Vaqt:</b> {due_date_str}\n"
                    f"⏱️ <b>Qolgan vaqt:</b> {time_left}\n\n"
                )
                
                if followup.notes:
                    message += f"📝 <b>Eslatma:</b>\n{followup.notes[:100]}\n\n"
                
                message += "⚠️ <b>TEZKOR HARAKAT QILING!</b>"
                
                if send_telegram_notification(
                    followup.sales.telegram_chat_id,
                    message
                ):
                    notifications_sent += 1
                followup.reminder_sent = True
                followup.save()
        
        print(f"[{timezone.now()}] send_followup_reminders_task yakunlandi: {notifications_sent} ta notification yuborildi")
    except Exception as e:
        print(f"[{timezone.now()}] send_followup_reminders_task xatolik: {e}")
        import traceback
        traceback.print_exc()


@shared_task
def send_post_trial_sales_reminder_task():
    """Sinovdan keyin sotuv taklifi eslatmasi"""
    try:
        print(f"[{timezone.now()}] send_post_trial_sales_reminder_task ishga tushdi")
        # Sinovdan keyin 3 daqiqada follow-up yaratiladi, lekin alohida eslatma ham yuboramiz
        # Sinovga keldi va natija 'attended' bo'lgan, lekin hali 'enrolled' bo'lmagan lidlar
        now = timezone.now()
        today = now.date()
        yesterday = today - timedelta(days=1)
        
        # Kechagi va bugungi sinovlar (faqat 'attended' natijali)
        recent_trials = TrialLesson.objects.filter(
            date__gte=yesterday,
            result='attended',
            sales_reminder_sent=False,
            lead__status__in=['trial_attended', 'interested', 'contacted']  # Faqat sinovga kelgan, lekin hali yozilmagan
        ).select_related('lead', 'lead__assigned_sales', 'lead__interested_course')
        
        notifications_sent = 0
        for trial in recent_trials:
            # Agar lid hali 'enrolled' bo'lmagan bo'lsa
            if trial.lead.status != 'enrolled' and trial.lead.assigned_sales:
                if trial.lead.assigned_sales.telegram_chat_id:
                    # Sinovdan keyin necha vaqt o'tganini hisoblash
                    trial_datetime = timezone.make_aware(
                        timezone.datetime.combine(trial.date, trial.time)
                    )
                    time_since_trial = now - trial_datetime
                    hours_since = int(time_since_trial.total_seconds() / 3600)
                    
                    message = (
                        f"💰 <b>SOTUV TAKLIFI ESLATMASI</b>\n"
                        f"{'=' * 25}\n\n"
                        f"👤 <b>Lid:</b> {trial.lead.name}\n"
                        f"📞 <b>Telefon:</b> <code>{trial.lead.phone}</code>\n\n"
                        f"📅 <b>Sinov sanasi:</b> {trial.date.strftime('%d.%m.%Y')} {trial.time.strftime('%H:%M')}\n"
                        f"📚 <b>Kurs:</b> {trial.lead.interested_course.name if trial.lead.interested_course else 'N/A'}\n"
                        f"⏱️ <b>Sinovdan keyin:</b> {hours_since} soat o'tdi\n\n"
                        f"⚠️ <b>Sotuv taklifi berish vaqt keldi!</b>"
                    )
                    
                    if send_telegram_notification(
                        trial.lead.assigned_sales.telegram_chat_id,
                        message
                    ):
                        notifications_sent += 1
                trial.sales_reminder_sent = True
                trial.save()
        
        print(f"[{timezone.now()}] send_post_trial_sales_reminder_task yakunlandi: {notifications_sent} ta notification yuborildi")
    except Exception as e:
        print(f"[{timezone.now()}] send_post_trial_sales_reminder_task xatolik: {e}")
        import traceback
        traceback.print_exc()


@shared_task
def calculate_daily_kpi_task():
    """Kunlik KPI hisoblash"""
    try:
        print(f"[{timezone.now()}] calculate_daily_kpi_task ishga tushdi")
        from .models import User
        
        today = timezone.now().date()
        sales_users = User.objects.filter(role='sales', is_active_sales=True)
        
        calculated_count = 0
        for sales in sales_users:
            try:
                KPIService.calculate_daily_kpi(sales, today)
                calculated_count += 1
            except Exception as e:
                print(f"KPI hisoblashda xatolik ({sales.username}): {e}")
        
        print(f"[{timezone.now()}] calculate_daily_kpi_task yakunlandi: {calculated_count} ta sotuvchi uchun KPI hisoblandi")
    except Exception as e:
        print(f"[{timezone.now()}] calculate_daily_kpi_task xatolik: {e}")
        import traceback
        traceback.print_exc()


@shared_task
def reactivation_task():
    """Reaktivatsiya tekshirish"""
    try:
        print(f"[{timezone.now()}] reactivation_task ishga tushdi")
        ReactivationService.check_and_reactivate()
        print(f"[{timezone.now()}] reactivation_task yakunlandi")
    except Exception as e:
        print(f"[{timezone.now()}] reactivation_task xatolik: {e}")
        import traceback
        traceback.print_exc()


@shared_task
def check_trial_attended_not_enrolled_task():
    """Sinovga kelgan, lekin enrolled bo'lmagan lidlar uchun follow-up"""
    try:
        print(f"[{timezone.now()}] check_trial_attended_not_enrolled_task ishga tushdi")
        
        # Sinovga kelgan, lekin enrolled bo'lmagan lidlar
        trial_attended_leads = Lead.objects.filter(
            status='trial_attended',
            assigned_sales__isnull=False
        ).select_related('assigned_sales')
        
        now = timezone.now()
        notifications_sent = 0
        
        for lead in trial_attended_leads:
            # Eng so'nggi sinovni topish
            last_trial = lead.trials.filter(result='attended').order_by('-date', '-time').first()
            if not last_trial:
                continue
            
            trial_datetime = timezone.make_aware(
                timezone.datetime.combine(last_trial.date, last_trial.time)
            )
            time_since_trial = now - trial_datetime
            
            # 24 soatdan keyin follow-up yaratish
            if timedelta(hours=23) < time_since_trial < timedelta(hours=25):
                # Follow-up allaqachon yaratilganligini tekshirish
                existing = FollowUp.objects.filter(
                    lead=lead,
                    notes__contains="Sinovdan keyin 24 soat",
                    completed=False
                ).exists()
                
                if not existing:
                    due_date = FollowUpService.calculate_work_hours_due_date(
                        lead.assigned_sales,
                        now,
                        timedelta(0)
                    )
                    followup = FollowUp.objects.create(
                        lead=lead,
                        sales=lead.assigned_sales,
                        due_date=due_date,
                        notes="Sinovdan keyin 24 soat - qayta aloqa"
                    )
                    send_followup_created_notification.delay(followup.id)
                    notifications_sent += 1
            
            # 3-kundan keyin follow-up
            elif timedelta(days=2, hours=23) < time_since_trial < timedelta(days=3, hours=1):
                existing = FollowUp.objects.filter(
                    lead=lead,
                    notes__contains="Sinovdan keyin 3-kun",
                    completed=False
                ).exists()
                
                if not existing:
                    due_date = FollowUpService.calculate_work_hours_due_date(
                        lead.assigned_sales,
                        now,
                        timedelta(0)
                    )
                    followup = FollowUp.objects.create(
                        lead=lead,
                        sales=lead.assigned_sales,
                        due_date=due_date,
                        notes="Sinovdan keyin 3-kun - yakuniy follow-up"
                    )
                    send_followup_created_notification.delay(followup.id)
                    notifications_sent += 1
            
            # 7-kundan keyin follow-up
            elif timedelta(days=6, hours=23) < time_since_trial < timedelta(days=7, hours=1):
                existing = FollowUp.objects.filter(
                    lead=lead,
                    notes__contains="Sinovdan keyin 7-kun",
                    completed=False
                ).exists()
                
                if not existing:
                    due_date = FollowUpService.calculate_work_hours_due_date(
                        lead.assigned_sales,
                        now,
                        timedelta(0)
                    )
                    followup = FollowUp.objects.create(
                        lead=lead,
                        sales=lead.assigned_sales,
                        due_date=due_date,
                        notes="Sinovdan keyin 7-kun - qayta muloqot"
                    )
                    send_followup_created_notification.delay(followup.id)
                    notifications_sent += 1
            
            # 14-kundan keyin follow-up
            elif timedelta(days=13, hours=23) < time_since_trial < timedelta(days=14, hours=1):
                existing = FollowUp.objects.filter(
                    lead=lead,
                    notes__contains="Sinovdan keyin 14-kun",
                    completed=False
                ).exists()
                
                if not existing:
                    due_date = FollowUpService.calculate_work_hours_due_date(
                        lead.assigned_sales,
                        now,
                        timedelta(0)
                    )
                    followup = FollowUp.objects.create(
                        lead=lead,
                        sales=lead.assigned_sales,
                        due_date=due_date,
                        notes="Sinovdan keyin 14-kun - re-engagement"
                    )
                    send_followup_created_notification.delay(followup.id)
                    notifications_sent += 1
        
        print(f"[{timezone.now()}] check_trial_attended_not_enrolled_task yakunlandi: {notifications_sent} ta follow-up yaratildi")
    except Exception as e:
        print(f"[{timezone.now()}] check_trial_attended_not_enrolled_task xatolik: {e}")
        import traceback
        traceback.print_exc()


@shared_task
def send_new_lead_notification(lead_id):
    """Yangi lid haqida xabar"""
    try:
        lead = Lead.objects.select_related('assigned_sales', 'interested_course').get(id=lead_id)
        if lead.assigned_sales and lead.assigned_sales.telegram_chat_id:
            # Kurs nomi va narxi
            course_info = ""
            if lead.interested_course:
                course_info = f"📚 <b>{lead.interested_course.name}</b>"
                if lead.interested_course.price:
                    course_info += f" ({lead.interested_course.price:,.0f} so'm)"
            else:
                course_info = "📚 Kurs tanlanmagan"
            
            message = (
                f"🆕 <b>YANGI LID</b>\n"
                f"{'=' * 25}\n\n"
                f"👤 <b>Ism:</b> {lead.name}\n"
                f"📞 <b>Telefon:</b> <code>{lead.phone}</code>\n"
                f"{course_info}\n"
                f"📊 <b>Manba:</b> {lead.get_source_display()}\n"
                f"🏷️ <b>Status:</b> {lead.get_status_display()}\n"
                f"⏰ <b>Vaqt:</b> {lead.created_at.strftime('%d.%m.%Y %H:%M')}\n\n"
                f"⚠️ <b>DARHOL ALOQA QILISH KERAK!</b>\n"
                f"⏱️ 5 daqiqada follow-up yaratiladi"
            )
            
            send_telegram_notification(
                lead.assigned_sales.telegram_chat_id,
                message
            )
    except Lead.DoesNotExist:
        pass
    except Exception as e:
        print(f"send_new_lead_notification xatolik (lead_id={lead_id}): {e}")


@shared_task
def send_status_change_notification(lead_id, old_status, new_status):
    """Status o'zgarishi haqida xabar"""
    try:
        lead = Lead.objects.select_related('assigned_sales', 'interested_course').get(id=lead_id)
        if lead.assigned_sales and lead.assigned_sales.telegram_chat_id:
            old_status_display = dict(Lead.STATUS_CHOICES).get(old_status, old_status)
            new_status_display = lead.get_status_display()
            
            # Status o'zgarishiga qarab emoji va rang
            status_emojis = {
                'new': '🆕',
                'contacted': '📞',
                'interested': '💡',
                'trial_registered': '📅',
                'trial_attended': '✅',
                'enrolled': '🎓',
                'lost': '❌'
            }
            
            old_emoji = status_emojis.get(old_status, '📊')
            new_emoji = status_emojis.get(new_status, '📊')
            
            # Status o'zgarishiga qarab xabar
            status_messages = {
                'contacted': "✅ Aloqa o'rnatildi! 24 soatdan keyin follow-up yaratiladi.",
                'interested': "💡 Lid qiziqish bildirdi! 48 soatdan keyin follow-up yaratiladi.",
                'trial_registered': "📅 Sinovga yozildi! 2 soat oldin eslatma yuboriladi.",
                'trial_attended': "✅ Sinovga keldi! 3 daqiqadan keyin sotuv taklifi berish kerak.",
                'enrolled': "🎓 Lid o'quvchiga aylandi! Tabriklaymiz! 🎉",
                'lost': "❌ Lid qiziqish bildirmadi. Reaktivatsiya mexanizmi ishga tushadi."
            }
            
            action_message = status_messages.get(new_status, "")
            
            message = (
                f"🔄 <b>STATUS O'ZGARDI</b>\n"
                f"{'=' * 25}\n\n"
                f"👤 <b>Lid:</b> {lead.name}\n"
                f"📞 <b>Telefon:</b> <code>{lead.phone}</code>\n\n"
                f"📊 <b>Status o'zgarishi:</b>\n"
                f"{old_emoji} {old_status_display}\n"
                f"➡️\n"
                f"{new_emoji} <b>{new_status_display}</b>\n\n"
            )
            
            if lead.interested_course:
                message += f"📚 <b>Kurs:</b> {lead.interested_course.name}\n\n"
            
            if action_message:
                message += f"💬 <b>Keyingi qadam:</b>\n{action_message}"
            
            send_telegram_notification(
                lead.assigned_sales.telegram_chat_id,
                message
            )
    except Lead.DoesNotExist:
        pass
    except Exception as e:
        print(f"send_status_change_notification xatolik (lead_id={lead_id}): {e}")


@shared_task
def send_followup_created_notification(followup_id):
    """Follow-up yaratilganda xabar"""
    try:
        followup = FollowUp.objects.select_related('lead', 'sales', 'lead__interested_course').get(id=followup_id)
        if followup.sales and followup.sales.telegram_chat_id:
            due_date_str = followup.due_date.strftime('%d.%m.%Y')
            due_time_str = followup.due_date.strftime('%H:%M')
            
            # Qolgan vaqtni hisoblash
            now = timezone.now()
            if followup.due_date > now:
                time_left = followup.due_date - now
                total_seconds = int(time_left.total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                
                if hours > 0:
                    time_left_str = f"{hours} soat {minutes} daqiqa"
                elif minutes > 0:
                    time_left_str = f"{minutes} daqiqa"
                else:
                    time_left_str = "Bir necha soniya"
            else:
                time_left_str = "⏰ Vaqt o'tib ketgan"
            
            # Follow-up turiga qarab emoji
            if "Yangi lid" in followup.notes:
                emoji = "🆕"
                priority = "🔴 YUQORI"
            elif "Sinov" in followup.notes:
                emoji = "📅"
                priority = "🟡 O'RTA"
            else:
                emoji = "📋"
                priority = "🟢 ODDIY"
            
            message = (
                f"{emoji} <b>YANGI FOLLOW-UP</b>\n"
                f"{'=' * 25}\n\n"
                f"👤 <b>Lid:</b> {followup.lead.name}\n"
                f"📞 <b>Telefon:</b> <code>{followup.lead.phone}</code>\n\n"
                f"⏰ <b>Bajarilishi kerak:</b>\n"
                f"📅 {due_date_str}\n"
                f"🕐 {due_time_str}\n\n"
                f"⏱️ <b>Qolgan vaqt:</b> {time_left_str}\n"
                f"🎯 <b>Prioritet:</b> {priority}\n\n"
            )
            
            if followup.notes:
                message += f"📝 <b>Eslatma:</b>\n{followup.notes}\n\n"
            
            if followup.lead.interested_course:
                message += f"📚 <b>Kurs:</b> {followup.lead.interested_course.name}\n\n"
            
            message += "💡 <b>Eslatma:</b> 1 soat oldin sizga eslatma yuboriladi."
            
            send_telegram_notification(
                followup.sales.telegram_chat_id,
                message
            )
    except FollowUp.DoesNotExist:
        pass
    except Exception as e:
        print(f"send_followup_created_notification xatolik (followup_id={followup_id}): {e}")


@shared_task
def send_reactivation_notification(reactivation_id):
    """Reaktivatsiya haqida xabar"""
    try:
        reactivation = Reactivation.objects.select_related(
            'lead', 'lead__assigned_sales', 'lead__interested_course'
        ).get(id=reactivation_id)
        lead = reactivation.lead
        
        if lead.assigned_sales and lead.assigned_sales.telegram_chat_id:
            reactivation_type_map = {
                '7_days': {
                    'message': '7 kun o\'tdi - qayta taklif qilish',
                    'emoji': '🔄'
                },
                '14_days': {
                    'message': '14 kun o\'tdi - boshqa kurs tavsiyasi',
                    'emoji': '💡'
                },
                '30_days': {
                    'message': '30 kun o\'tdi - yangi guruhlar haqida xabar',
                    'emoji': '📢'
                },
            }
            
            reactivation_info = reactivation_type_map.get(
                reactivation.reactivation_type,
                {'message': 'Reaktivatsiya', 'emoji': '🔄'}
            )
            
            message = (
                f"{reactivation_info['emoji']} <b>REAKTIVATSIYA</b>\n"
                f"{'=' * 25}\n\n"
                f"👤 <b>Lid:</b> {lead.name}\n"
                f"📞 <b>Telefon:</b> <code>{lead.phone}</code>\n"
                f"📚 <b>Kurs:</b> {lead.interested_course.name if lead.interested_course else 'N/A'}\n\n"
                f"📅 <b>Kunlar:</b> {reactivation.days_since_lost} kun o'tdi\n"
                f"💬 <b>Tavsiya:</b> {reactivation_info['message']}\n\n"
                f"⚠️ <b>Lid bilan qayta aloqa qilish kerak!</b>"
            )
            
            send_telegram_notification(
                lead.assigned_sales.telegram_chat_id,
                message
            )
    except Reactivation.DoesNotExist:
        pass
    except Exception as e:
        print(f"send_reactivation_notification xatolik (reactivation_id={reactivation_id}): {e}")

