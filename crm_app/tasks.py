from celery import shared_task
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
from .models import Lead, FollowUp, TrialLesson, Reactivation, Offer, User
from .services import FollowUpService, KPIService, ReactivationService, OfferService
from .telegram_bot import send_telegram_notification


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def create_followup_task(self, lead_id, delay_minutes=5):
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
        print(f"Lead {lead_id} topilmadi")
        return
    except Exception as e:
        print(f"create_followup_task xatolik: {e}")
        import traceback
        traceback.print_exc()
        # Retry qilish
        raise self.retry(exc=e, countdown=60)


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def check_overdue_followups_task(self):
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
                note = f"📝 {followup.notes[:100]}" if followup.notes else ""
                message = (
                    f"⚠️ OVERDUE FOLLOW-UP\n"
                    f"👤 {followup.lead.name} | 📞 {followup.lead.phone}\n"
                    f"⏰ Reja: {due_date_str}\n"
                    f"{note}\n"
                    f"🔴 Darhol qo'ng'iroq qiling"
                )
                
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
        # Retry qilish
        raise self.retry(exc=e, countdown=300)


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def auto_reschedule_overdue_followups_task(self):
    """Overdue follow-up'larni avtomatik qayta rejalashtirish"""
    try:
        print(f"[{timezone.now()}] auto_reschedule_overdue_followups_task ishga tushdi")
        from .services import FollowUpService
        
        # Grace period o'tgan overdue'larni olish
        overdue = FollowUpService.get_overdue_followups()
        
        # Faqat 1-6 soat overdue bo'lganlarni avtomatik reschedule qilish
        now = timezone.now()
        auto_reschedule_count = 0
        
        for followup in overdue:
            hours_overdue = (now - followup.due_date).total_seconds() / 3600
            
            # 1-6 soat overdue bo'lsa, avtomatik reschedule
            if 1 <= hours_overdue <= 6:
                # Keyingi ish vaqtiga o'tkazish (2 soatdan keyin)
                if FollowUpService.auto_reschedule_overdue(followup, hours_ahead=2):
                    auto_reschedule_count += 1
                    print(f"Auto-rescheduled follow-up {followup.id} (overdue: {hours_overdue:.1f} hours)")
        
        print(f"[{timezone.now()}] auto_reschedule_overdue_followups_task yakunlandi: {auto_reschedule_count} ta follow-up qayta rejalashtirildi")
        return auto_reschedule_count
    except Exception as e:
        print(f"[{timezone.now()}] auto_reschedule_overdue_followups_task xatolik: {e}")
        import traceback
        traceback.print_exc()
        # Retry qilish
        raise self.retry(exc=e, countdown=300)


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def send_trial_reminder_task(self):
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
                        f"🔔 Sinov eslatmasi\n"
                        f"👤 {trial.lead.name} | 📞 {trial.lead.phone}\n"
                        f"📆 {trial.date.strftime('%d.%m.%Y')} 🕐 {trial.time.strftime('%H:%M')}\n"
                        f"⏱️ Qolgan vaqt: {time_str}\n"
                        f"👥 Guruh: {trial.group.name if trial.group else 'N/A'} | 🏢 Xona: {trial.room.name if trial.room else 'N/A'}\n"
                        f"💡 Sinovdan oldin bog'laning"
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
        raise self.retry(exc=e, countdown=300)


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def send_followup_reminders_task(self):
    """Follow-up eslatmalari yuborish - aloqa qilish kerak vaqtda (ish vaqtlarini tekshirish bilan)"""
    try:
        print(f"[{timezone.now()}] send_followup_reminders_task ishga tushdi")
        now = timezone.now()
        
        # Bugun bajarilishi kerak bo'lgan follow-up'lar
        today = now.date()
        tomorrow = today + timedelta(days=1)
        
        # Bugun va ertaga bajarilishi kerak bo'lgan follow-up'lar
        upcoming_followups = FollowUp.objects.filter(
            due_date__date__gte=today,
            due_date__date__lt=tomorrow,
            completed=False,
            reminder_sent=False,
            sales__isnull=False
        ).select_related('lead', 'sales')
        
        notifications_sent = 0
        for followup in upcoming_followups:
            # Aloqa qilish kerak vaqt
            due_datetime = followup.due_date
            
            # Agar hozirgi vaqt due_date ga yetgan bo'lsa va ish vaqtida bo'lsa
            if now >= due_datetime:
                # Sotuvchi ish vaqtida ekanligini tekshirish
                if followup.sales.is_available_for_leads:
                    if followup.sales and followup.sales.telegram_chat_id:
                        due_date_str = followup.due_date.strftime('%d.%m.%Y %H:%M')
                        
                        # Qancha vaqt o'tganini hisoblash
                        time_passed = now - due_datetime
                        minutes_passed = int(time_passed.total_seconds() / 60)
                        
                        if minutes_passed < 60:
                            time_str = f"{minutes_passed} daqiqa oldin"
                        else:
                            hours = minutes_passed // 60
                            mins = minutes_passed % 60
                            time_str = f"{hours} soat {mins} daqiqa oldin"
                        
                        note = f"📝 {followup.notes[:100]}" if followup.notes else ""
                        message = (
                            f"📞 Aloqa vaqti keldi\n"
                            f"👤 {followup.lead.name} | 📞 {followup.lead.phone}\n"
                            f"⏰ Reja: {due_date_str}\n"
                            f"⏱️ {time_str}\n"
                            f"{note}\n"
                            f"🔴 Darhol qo'ng'iroq qiling"
                        )
                        
                        if send_telegram_notification(
                            followup.sales.telegram_chat_id,
                            message
                        ):
                            followup.reminder_sent = True
                            followup.save()
                            notifications_sent += 1
                else:
                    # Agar ish vaqti tashqarisida bo'lsa, keyingi ish vaqtida eslatma yuborish
                    next_work_time = FollowUpService.calculate_work_hours_due_date(
                        followup.sales,
                        now,
                        timedelta(0)  # Keyingi ish vaqti
                    )
                    # Agar keyingi ish vaqti aniq bo'lsa va hali eslatma yuborilmagan bo'lsa
                    if next_work_time > now and not followup.reminder_sent:
                        # Keyingi ish vaqtida eslatma yuborish uchun task yaratish
                        send_followup_reminder_at_time.delay(
                            followup.id,
                            next_work_time.isoformat()
                        )
        
        print(f"[{timezone.now()}] send_followup_reminders_task yakunlandi: {notifications_sent} ta notification yuborildi")
    except Exception as e:
        print(f"[{timezone.now()}] send_followup_reminders_task xatolik: {e}")
        import traceback
        traceback.print_exc()
        raise self.retry(exc=e, countdown=300)


@shared_task
def send_followup_reminder_at_time(followup_id, reminder_time_iso):
    """
    Belgilangan vaqtda follow-up eslatmasi yuborish
    """
    try:
        from datetime import datetime
        
        followup = FollowUp.objects.get(id=followup_id)
        if followup.completed or followup.reminder_sent:
            return
        
        reminder_time = datetime.fromisoformat(reminder_time_iso)
        if timezone.is_naive(reminder_time):
            reminder_time = timezone.make_aware(reminder_time)
        
        now = timezone.now()
        
        # Agar vaqt kelgan bo'lsa va sotuvchi ish vaqtida bo'lsa
        if now >= reminder_time and followup.sales.is_available_for_leads:
            if followup.sales and followup.sales.telegram_chat_id:
                due_date_str = followup.due_date.strftime('%d.%m.%Y %H:%M')
                
                message = (
                    f"📞 <b>ALOQA QILISH VAQTI!</b>\n"
                    f"{'=' * 25}\n\n"
                    f"👤 <b>Lid:</b> {followup.lead.name}\n"
                    f"📞 <b>Telefon:</b> <code>{followup.lead.phone}</code>\n\n"
                    f"⏰ <b>Rejalashtirilgan vaqt:</b> {due_date_str}\n\n"
                )
                
                if followup.notes:
                    message += f"📝 <b>Eslatma:</b>\n{followup.notes[:100]}\n\n"
                
                message += "🔴 <b>DARHOL ALOQA QILING!</b>"
                
                if send_telegram_notification(followup.sales.telegram_chat_id,message):
                    followup.reminder_sent = True
                    followup.save()
    except FollowUp.DoesNotExist:
        pass
    except Exception as e:
        print(f"send_followup_reminder_at_time xatolik (followup_id={followup_id}): {e}")
        import traceback
        traceback.print_exc()


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def send_post_trial_sales_reminder_task(self):
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
        raise self.retry(exc=e, countdown=300)


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def calculate_daily_kpi_task(self):
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
        raise self.retry(exc=e, countdown=300)


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def reactivation_task(self):
    """Reaktivatsiya tekshirish"""
    try:
        print(f"[{timezone.now()}] reactivation_task ishga tushdi")
        ReactivationService.check_and_reactivate()
        print(f"[{timezone.now()}] reactivation_task yakunlandi")
    except Exception as e:
        print(f"[{timezone.now()}] reactivation_task xatolik: {e}")
        import traceback
        traceback.print_exc()
        raise self.retry(exc=e, countdown=300)


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
def create_followup_after_trial_end_task():
    """Sinov darsi tugagandan keyin (90 minutdan keyin) follow-up yaratish"""
    try:
        print(f"[{timezone.now()}] create_followup_after_trial_end_task ishga tushdi")
        from datetime import timedelta
        from .models import TrialLesson, Lead, FollowUp
        from .services import FollowUpService
        
        now = timezone.now()
        LESSON_DURATION_MINUTES = 90
        
        # Sinov darslari tugagan, lekin natija kiritilmagan trial'lar
        trials = TrialLesson.objects.filter(
            result__in=['', None],  # Natija kiritilmagan
            lead__status='trial_registered',  # Hali sinovga yozilgan statusida
            lead__assigned_sales__isnull=False  # Assigned sales bo'lishi kerak
        ).select_related('lead', 'lead__assigned_sales')
        
        followups_created = 0
        for trial in trials:
            # Sinov darsi tugash vaqti
            trial_datetime = timezone.make_aware(
                timezone.datetime.combine(trial.date, trial.time)
            )
            trial_end_time = trial_datetime + timedelta(minutes=LESSON_DURATION_MINUTES)
            
            # Agar sinov darsi tugagan bo'lsa (90 minutdan keyin)
            if now >= trial_end_time:
                # Follow-up allaqachon yaratilganligini tekshirish
                existing = FollowUp.objects.filter(
                    lead=trial.lead,
                    notes__contains="Sinov darsi tugadi",
                    completed=False
                ).exists()
                
                if not existing and trial.lead.assigned_sales:
                    # Darhol follow-up yaratish
                    due_date = FollowUpService.calculate_work_hours_due_date(
                        trial.lead.assigned_sales,
                        now,
                        timedelta(0)  # Darhol
                    )
                    followup = FollowUp.objects.create(
                        lead=trial.lead,
                        sales=trial.lead.assigned_sales,
                        due_date=due_date,
                        notes="Sinov darsi tugadi - natija kiritish va aloqa qilish kerak (keldi/kelmadi)"
                    )
                    send_followup_created_notification.delay(followup.id)
                    followups_created += 1
        
        print(f"[{timezone.now()}] create_followup_after_trial_end_task yakunlandi: {followups_created} ta follow-up yaratildi")
    except Exception as e:
        print(f"[{timezone.now()}] create_followup_after_trial_end_task xatolik: {e}")
        import traceback
        traceback.print_exc()


@shared_task
def check_expired_leaves_task():
    """Ruxsat tugagan sotuvchilarning is_on_leave holatini yangilash"""
    try:
        print(f"[{timezone.now()}] check_expired_leaves_task ishga tushdi")
        from .models import LeaveRequest, User
        from datetime import date, time as dt_time
        
        now = timezone.now()
        today = now.date()
        current_time = now.time()
        
        # Ruxsat tugagan, lekin hali is_on_leave True bo'lgan sotuvchilar
        expired_leaves = LeaveRequest.objects.filter(
            status='approved',
            sales__is_on_leave=True
        ).select_related('sales')
        
        updated_count = 0
        for leave in expired_leaves:
            # Agar ruxsat tugagan bo'lsa
            if leave.end_date < today:
                # Ruxsat tugagan
                leave.sales.is_on_leave = False
                leave.sales.save()
                updated_count += 1
            elif leave.end_date == today:
                # Agar bugun ruxsat tugashi kerak bo'lsa
                if leave.end_time:
                    # Agar soat belgilangan bo'lsa
                    if current_time > leave.end_time:
                        leave.sales.is_on_leave = False
                        leave.sales.save()
                        updated_count += 1
                else:
                    # Agar butun kun ruxsat bo'lsa, kun oxirida o'chirish
                    # (bu yerda end_time yo'q, shuning uchun kun oxirida o'chirish kerak)
                    # Lekin hozircha o'chirmaymiz, chunki kun hali tugamagan bo'lishi mumkin
                    pass
        
        print(f"[{timezone.now()}] check_expired_leaves_task yakunlandi: {updated_count} ta sotuvchi yangilandi")
    except Exception as e:
        print(f"[{timezone.now()}] check_expired_leaves_task xatolik: {e}")
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
                f"🆕 Yangi lid\n"
                f"👤 {lead.name} | 📞 {lead.phone}\n"
                f"{course_info}\n"
                f"📊 Manba: {lead.get_source_display()} | Status: {lead.get_status_display()}\n"
                f"⏰ {lead.created_at.strftime('%d.%m.%Y %H:%M')}\n"
                f"⚠️ Darhol bog'laning (5 daqiqada follow-up yaratiladi)"
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
            
            course_info = f"📚 Kurs: {lead.interested_course.name}" if lead.interested_course else ""
            next_step = f"💬 Keyingi qadam: {action_message}" if action_message else ""
            message = (
                f"🔄 Status o'zgardi\n"
                f"👤 {lead.name} | 📞 {lead.phone}\n"
                f"{old_emoji} {old_status_display} → {new_emoji} {new_status_display}\n"
                f"{course_info}\n"
                f"{next_step}"
            )
            
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
            
            notes_part = f"📝 {followup.notes}" if followup.notes else ""
            course_part = f"📚 Kurs: {followup.lead.interested_course.name}" if followup.lead.interested_course else ""
            message = (
                f"{emoji} Yangi follow-up\n"
                f"👤 {followup.lead.name} | 📞 {followup.lead.phone}\n"
                f"⏰ {due_date_str} {due_time_str} | ⏱️ {time_left_str}\n"
                f"🎯 Prioritet: {priority}\n"
                f"{notes_part}\n"
                f"{course_part}\n"
                f"💡 1 soat oldin eslatma yuboriladi"
            )
            
            send_telegram_notification(
                followup.sales.telegram_chat_id,
                message
            )
    except FollowUp.DoesNotExist:
        pass
    except Exception as e:
        print(f"send_followup_created_notification xatolik (followup_id={followup_id}): {e}")


@shared_task
def create_next_contacted_followup(lead_id, sequence, delay_hours, base_time):
    """
    Contacted status uchun keyingi follow-up'ni yaratish
    sequence: Ketma-ketlik raqami (2, 3, ...)
    delay_hours: Kechikish (soat)
    base_time: Birinchi follow-up yaratilgan vaqt (ISO format)
    """
    try:
        from datetime import datetime
        
        lead = Lead.objects.get(id=lead_id)
        if not lead.assigned_sales or lead.status != 'contacted':
            return  # Agar status o'zgargandan bo'lsa, to'xtatish
        
        # Allaqachon bu sequence uchun follow-up borligini tekshirish
        existing = FollowUp.objects.filter(
            lead=lead,
            followup_sequence=sequence,
            completed=False
        ).exists()
        
        if existing:
            return  # Agar allaqachon bor bo'lsa, yaratmaymiz
        
        # Base time ni parse qilish
        if isinstance(base_time, str):
            base_datetime = datetime.fromisoformat(base_time)
            if timezone.is_naive(base_datetime):
                base_datetime = timezone.make_aware(base_datetime)
        else:
            base_datetime = base_time
        
        delay = timedelta(hours=delay_hours)
        due_date = FollowUpService.calculate_work_hours_due_date(
            lead.assigned_sales,
            base_datetime,
            delay
        )
        
        notes_map = {
            2: "Contacted - 3 kundan keyin aloqa (qo'shimcha ma'lumot, bonuslar, chegirmalar)",
            3: "Contacted - 7 kundan keyin aloqa (yakuniy taklif, qaror qabul qilish)",
        }
        
        followup = FollowUp.objects.create(
            lead=lead,
            sales=lead.assigned_sales,
            due_date=due_date,
            notes=notes_map.get(sequence, f"Contacted - {delay_hours} soatdan keyin aloqa"),
            followup_sequence=sequence
        )
        send_followup_created_notification.delay(followup.id)
    except Lead.DoesNotExist:
        pass
    except Exception as e:
        print(f"create_next_contacted_followup xatolik (lead_id={lead_id}, sequence={sequence}): {e}")
        import traceback
        traceback.print_exc()


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
                f"{reactivation_info['emoji']} Reaktivatsiya\n"
                f"👤 {lead.name} | 📞 {lead.phone}\n"
                f"📚 {lead.interested_course.name if lead.interested_course else 'Kurs tanlanmagan'}\n"
                f"📅 {reactivation.days_since_lost} kun bo'ldi\n"
                f"💬 Tavsiya: {reactivation_info['message']}\n"
                f"⚠️ Lid bilan qayta aloqa qiling"
            )
            
            send_telegram_notification(
                lead.assigned_sales.telegram_chat_id,
                message
            )
    except Reactivation.DoesNotExist:
        pass
    except Exception as e:
        print(f"send_reactivation_notification xatolik (reactivation_id={reactivation_id}): {e}")


@shared_task
def expire_offers_task():
    """Muddatidan o'tgan takliflarni avtomatik o'chirish"""
    today = timezone.now().date()
    expired = Offer.objects.filter(
        is_active=True,
        valid_until__lt=today
    )
    count = expired.update(is_active=False)
    if count:
        print(f"[offers] {count} ta taklif muddati tugagani uchun o'chirildi")


@shared_task
def send_daily_sales_summary_task():
    """
    Har ish kuni oxirida (kechqurun) sotuv statistikalarini admin/sales_manager guruhlariga yuborish.
    Guruh ID admin/sales_manager profilinga kiritiladi (telegram_group_id).
    """
    today = timezone.localdate()
    sales_users = User.objects.filter(role='sales', is_active_sales=True)

    # KPI'larni hisoblash va agregat
    per_sales_lines = []
    totals = {
        'contacts': 0,
        'followups': 0,
        'trials': 0,
        'sales': 0,
        'overdue': 0,
    }

    for sales in sales_users:
        kpi = KPIService.calculate_daily_kpi(sales, today)
        totals['contacts'] += kpi.daily_contacts
        totals['followups'] += kpi.daily_followups
        totals['trials'] += kpi.trials_registered
        totals['sales'] += kpi.trials_to_sales
        totals['overdue'] += kpi.overdue_count

        line = (
            f"• {sales.username}: "
            f"aloqa {kpi.daily_contacts}, fu {kpi.daily_followups}, "
            f"trial {kpi.trials_registered}, sotuv {kpi.trials_to_sales}, "
            f"overdue {kpi.overdue_count}"
        )
        per_sales_lines.append(line)

    # Guruhlar ro'yxati (takrorlanmasin)
    group_ids = set(
        User.objects.filter(
            role__in=['admin', 'sales_manager'],
            telegram_group_id__isnull=False
        ).values_list('telegram_group_id', flat=True)
    )

    if not group_ids:
        print("[daily summary] Hech qaysi guruh ID topilmadi.")
        return

    header = f"📊 Kunlik sotuv hisobot ({today.strftime('%d.%m.%Y')})"
    totals_line = (
        f"Jami: aloqa {totals['contacts']}, fu {totals['followups']}, "
        f"trial {totals['trials']}, sotuv {totals['sales']}, overdue {totals['overdue']}"
    )
    body = "\n".join(per_sales_lines) if per_sales_lines else "Ma'lumot topilmadi."
    message = f"{header}\n{totals_line}\n\n{body}"

    sent = 0
    for gid in group_ids:
        if gid:
            if send_telegram_notification(gid, message):
                sent += 1

    print(f"[daily summary] {sent} ta guruhga yuborildi.")


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def import_leads_from_google_sheets(self):
    """
    Google Sheets'dan avtomatik ravishda lidlarni import qilish
    Har 5 daqiqada ishga tushadi
    """
    from django.conf import settings
    from .services import GoogleSheetsService
    
    try:
        print(f"[{timezone.now()}] Google Sheets import task ishga tushdi")
        
        # .env fayldan Google Sheets konfiguratsiyasini olish
        spreadsheet_id = getattr(settings, 'GOOGLE_SHEETS_SPREADSHEET_ID', None)
        worksheets = getattr(settings, 'GOOGLE_SHEETS_WORKSHEETS', [getattr(settings, 'GOOGLE_SHEETS_WORKSHEET_NAME', 'Sheet1')])
        
        if not spreadsheet_id:
            print("GOOGLE_SHEETS_SPREADSHEET_ID sozlanmagan! Task o'tkazib yuborildi.")
            return {
                'success': False,
                'error': 'GOOGLE_SHEETS_SPREADSHEET_ID sozlanmagan'
            }
        
        summary = {'imported': 0, 'skipped': 0, 'errors': []}
        
        for worksheet_name in worksheets:
            result = GoogleSheetsService.import_new_leads(
                spreadsheet_id=spreadsheet_id,
                worksheet_name=worksheet_name
            )
            summary['imported'] += result.get('imported', 0)
            summary['skipped'] += result.get('skipped', 0)
            summary['errors'].extend([f"{worksheet_name}: {err}" for err in result.get('errors', [])])
        
        # Log
        if summary['imported'] > 0:
            print(f"[{timezone.now()}] Google Sheets: {summary['imported']} ta yangi lid import qilindi (multi-sheet)")
            
            # Admin/Manager'larga xabar
            if settings.TELEGRAM_ADMIN_CHAT_ID:
                message = (
                    f"📊 <b>Google Sheets Auto-Import</b>\n"
                    f"{'=' * 30}\n\n"
                    f"✅ <b>Import qilindi:</b> {summary['imported']} ta lid\n"
                    f"⏭ <b>O'tkazib yuborildi:</b> {summary['skipped']} ta\n"
                )
                
                if summary['errors']:
                    message += f"\n⚠️ <b>Xatoliklar:</b> {len(summary['errors'])} ta\n"
                
                send_telegram_notification(
                    settings.TELEGRAM_ADMIN_CHAT_ID,
                    message
                )
            
            # Manager/Admin telegram group'lariga ham yuborish
            managers = User.objects.filter(role__in=['admin', 'sales_manager'])
            for manager in managers:
                if manager.telegram_group_id:
                    short_message = (
                        f"📊 <b>Google Sheets Import</b>\n"
                        f"✅ {summary['imported']} ta yangi lid\n"
                        f"⏭ {summary['skipped']} ta o'tkazib yuborildi"
                    )
                    send_telegram_notification(
                        manager.telegram_group_id,
                        short_message
                    )
        else:
            print(f"[{timezone.now()}] Google Sheets: Yangi lid topilmadi (multi-sheet)")
        
        if summary['errors']:
            print(f"[{timezone.now()}] Google Sheets xatoliklar: {summary['errors']}")
        
        return summary
        
    except Exception as e:
        print(f"[{timezone.now()}] Google Sheets import xatolik: {e}")
        import traceback
        traceback.print_exc()
        # Retry qilish (faqat connection xatolari uchun)
        error_str = str(e).lower()
        if any(keyword in error_str for keyword in ['connection', 'network', 'timeout', 'getaddrinfo', 'failed to establish']):
            raise self.retry(exc=e, countdown=300)
        return {
            'success': False,
            'error': str(e)
        }


@shared_task
def send_google_sheets_import_summary_task():
    """
    Google Sheets import natijalarini har 2 soatda admin/manager'larga yuborish
    """
    try:
        from django.conf import settings
        from .services import GoogleSheetsService
        
        spreadsheet_id = getattr(settings, 'GOOGLE_SHEETS_SPREADSHEET_ID', None)
        if not spreadsheet_id:
            return
        
        worksheets = getattr(settings, 'GOOGLE_SHEETS_WORKSHEETS', 
                           [getattr(settings, 'GOOGLE_SHEETS_WORKSHEET_NAME', 'Sheet1')])
        
        summary = {'imported': 0, 'skipped': 0, 'errors': []}
        
        for worksheet_name in worksheets:
            result = GoogleSheetsService.import_new_leads(
                spreadsheet_id=spreadsheet_id,
                worksheet_name=worksheet_name
            )
            summary['imported'] += result.get('imported', 0)
            summary['skipped'] += result.get('skipped', 0)
            summary['errors'].extend([f"{worksheet_name}: {err}" for err in result.get('errors', [])])
        
        # Admin/Manager'larga xabar
        if summary['imported'] > 0 or summary['errors']:
            message = (
                f"📊 <b>Google Sheets Import (2 soatlik)</b>\n"
                f"{'=' * 30}\n\n"
                f"✅ <b>Import qilindi:</b> {summary['imported']} ta lid\n"
                f"⏭ <b>O'tkazib yuborildi:</b> {summary['skipped']} ta\n"
            )
            
            if summary['errors']:
                message += f"\n⚠️ <b>Xatoliklar:</b> {len(summary['errors'])} ta\n"
                if len(summary['errors']) <= 5:
                    for err in summary['errors'][:5]:
                        message += f"  • {err}\n"
                else:
                    message += f"  ... va yana {len(summary['errors']) - 5} ta xatolik\n"
            
            # Admin ga yuborish
            if settings.TELEGRAM_ADMIN_CHAT_ID:
                send_telegram_notification(
                    settings.TELEGRAM_ADMIN_CHAT_ID,
                    message
                )
            
            # Manager/Admin telegram group'lariga ham yuborish
            managers = User.objects.filter(role__in=['admin', 'sales_manager'])
            for manager in managers:
                if manager.telegram_group_id:
                    send_telegram_notification(
                        manager.telegram_group_id,
                        message
                    )
        
        print(f"[google sheets summary] {summary['imported']} ta lid, {summary['skipped']} ta o'tkazib yuborildi")
        
    except Exception as e:
        print(f"[google sheets summary] xatolik: {e}")
        import traceback
        traceback.print_exc()


@shared_task
def send_critical_alerts_task():
    """
    Kritik ogohlantirishlarni darhol admin/manager'larga yuborish
    """
    try:
        from django.conf import settings
        from .services import FollowUpService
        
        alerts = []
        
        # 1. Sotuvchilar bloklanganligini tekshirish
        sales_users = User.objects.filter(role='sales', is_active_sales=True)
        for sales in sales_users:
            if FollowUpService.check_sales_blocked(sales):
                overdue_count = FollowUpService.get_overdue_followups(sales).count()
                alerts.append(
                    f"🔴 <b>Sotuvchi bloklangan!</b>\n"
                    f"👤 {sales.username}\n"
                    f"⚠️ Overdue: {overdue_count} ta\n"
                    f"Darhol tekshirish kerak!"
                )
        
        # 2. Katta import xatoliklari (10+)
        # Bu Google Sheets import task'da tekshiriladi, lekin bu yerda ham tekshirish mumkin
        
        # 3. Tizim xatoliklari (database, API) - bu yerda tekshirish qiyin, lekin struktura qoldiramiz
        
        if alerts:
            message = (
                f"🚨 <b>KRITIK OGOHLANTIRISHLAR</b>\n"
                f"{'=' * 30}\n\n"
            )
            message += "\n\n".join(alerts)
            
            # Admin ga yuborish
            if settings.TELEGRAM_ADMIN_CHAT_ID:
                send_telegram_notification(
                    settings.TELEGRAM_ADMIN_CHAT_ID,
                    message
                )
            
            # Manager/Admin telegram group'lariga ham yuborish
            managers = User.objects.filter(role__in=['admin', 'sales_manager'])
            for manager in managers:
                if manager.telegram_group_id:
                    send_telegram_notification(
                        manager.telegram_group_id,
                        message
                    )
        
        print(f"[critical alerts] {len(alerts)} ta kritik ogohlantirish yuborildi")
        
    except Exception as e:
        print(f"[critical alerts] xatolik: {e}")
        import traceback
        traceback.print_exc()


@shared_task
def send_morning_daily_report_task():
    """
    Ertalabki kunlik hisobot (09:00)
    """
    try:
        from django.conf import settings
        from .services import FollowUpService, KPIService
        
        today = timezone.localdate()
        sales_users = User.objects.filter(role='sales', is_active_sales=True)
        
        # Bugungi follow-up'lar
        today_followups = FollowUpService.get_today_followups()
        total_followups = today_followups.count()
        completed_followups = today_followups.filter(completed=True).count()
        pending_followups = today_followups.filter(completed=False).count()
        overdue_followups = FollowUpService.get_overdue_followups().count()
        
        # Bugungi maqsadlar (har bir sotuvchi uchun)
        per_sales_lines = []
        for sales in sales_users:
            kpi = KPIService.calculate_daily_kpi(sales, today)
            per_sales_lines.append(
                f"• {sales.username}: "
                f"aloqa {kpi.daily_contacts}, "
                f"trial {kpi.trials_registered}, "
                f"sotuv {kpi.trials_to_sales}, "
                f"overdue {kpi.overdue_count}"
            )
        
        message = (
            f"🌅 <b>Ertalabki Briefing ({today.strftime('%d.%m.%Y')})</b>\n"
            f"{'=' * 30}\n\n"
            f"📋 <b>Bugungi Follow-up'lar:</b>\n"
            f"  • Jami: {total_followups} ta\n"
            f"  • Bajarilgan: {completed_followups} ta\n"
            f"  • Kutilmoqda: {pending_followups} ta\n"
            f"  • Overdue: {overdue_followups} ta\n\n"
            f"🎯 <b>Bugungi Maqsadlar:</b>\n"
            f"{chr(10).join(per_sales_lines) if per_sales_lines else 'Ma\'lumot topilmadi'}\n\n"
            f"💪 Yaxshi ish kuni tilaymiz!"
        )
        
        # Admin ga yuborish
        if settings.TELEGRAM_ADMIN_CHAT_ID:
            send_telegram_notification(
                settings.TELEGRAM_ADMIN_CHAT_ID,
                message
            )
        
        # Manager/Admin telegram group'lariga ham yuborish
        managers = User.objects.filter(role__in=['admin', 'sales_manager'])
        for manager in managers:
            if manager.telegram_group_id:
                send_telegram_notification(
                    manager.telegram_group_id,
                    message
                )
        
        print(f"[morning report] Ertalabki hisobot yuborildi")
        
    except Exception as e:
        print(f"[morning report] xatolik: {e}")
        import traceback
        traceback.print_exc()


@shared_task
def send_weekly_report_task():
    """
    Haftalik hisobot (Dushanba ertalab)
    """
    try:
        from django.conf import settings
        from django.db.models import Count, Sum, Avg, Q
        from datetime import timedelta
        
        today = timezone.localdate()
        
        # O'tgan hafta (Dushanba - Yakshanba)
        # Dushanbani topish
        days_since_monday = today.weekday()
        week_start = today - timedelta(days=days_since_monday + 7)  # O'tgan hafta dushanba
        week_end = week_start + timedelta(days=6)  # O'tgan hafta yakshanba
        
        # Statistikalar
        total_leads = Lead.objects.filter(
            created_at__date__gte=week_start,
            created_at__date__lte=week_end
        ).count()
        
        total_trials = TrialLesson.objects.filter(
            date__gte=week_start,
            date__lte=week_end
        ).count()
        
        total_sales = Lead.objects.filter(
            status='enrolled',
            enrolled_at__date__gte=week_start,
            enrolled_at__date__lte=week_end
        ).count()
        
        # Sotuvchilar reytingi
        sales_users = User.objects.filter(role='sales', is_active_sales=True)
        sales_ratings = []
        
        for sales in sales_users:
            sales_leads = Lead.objects.filter(
                assigned_sales=sales,
                created_at__date__gte=week_start,
                created_at__date__lte=week_end
            ).count()
            
            sales_trials = TrialLesson.objects.filter(
                lead__assigned_sales=sales,
                date__gte=week_start,
                date__lte=week_end
            ).count()
            
            sales_enrolled = Lead.objects.filter(
                assigned_sales=sales,
                status='enrolled',
                enrolled_at__date__gte=week_start,
                enrolled_at__date__lte=week_end
            ).count()
            
            conversion_rate = (sales_enrolled / sales_trials * 100) if sales_trials > 0 else 0
            
            sales_ratings.append({
                'sales': sales,
                'leads': sales_leads,
                'trials': sales_trials,
                'sales_count': sales_enrolled,
                'conversion': conversion_rate
            })
        
        # Konversiya bo'yicha tartiblash
        sales_ratings.sort(key=lambda x: x['conversion'], reverse=True)
        
        # Top 3 sotuvchi
        top_sales_lines = []
        for i, rating in enumerate(sales_ratings[:3], 1):
            top_sales_lines.append(
                f"{i}. {rating['sales'].username}: "
                f"{rating['sales_count']} ta sotuv, "
                f"{rating['conversion']:.1f}% konversiya"
            )
        
        # Umumiy konversiya
        total_trials_converted = sum(r['trials'] for r in sales_ratings)
        total_sales_converted = sum(r['sales_count'] for r in sales_ratings)
        overall_conversion = (total_sales_converted / total_trials_converted * 100) if total_trials_converted > 0 else 0
        
        message = (
            f"📈 <b>Haftalik Hisobot</b>\n"
            f"{week_start.strftime('%d.%m')} - {week_end.strftime('%d.%m.%Y')}\n"
            f"{'=' * 30}\n\n"
            f"📊 <b>Umumiy Statistikalar:</b>\n"
            f"  • Jami lidlar: {total_leads} ta\n"
            f"  • Trial darslar: {total_trials} ta\n"
            f"  • Sotuvlar: {total_sales} ta\n"
            f"  • Konversiya: {overall_conversion:.1f}%\n\n"
            f"🏆 <b>Top 3 Sotuvchi:</b>\n"
            f"{chr(10).join(top_sales_lines) if top_sales_lines else 'Ma\'lumot topilmadi'}\n\n"
            f"📅 Keyingi hafta uchun omad!"
        )
        
        # Admin ga yuborish
        if settings.TELEGRAM_ADMIN_CHAT_ID:
            send_telegram_notification(
                settings.TELEGRAM_ADMIN_CHAT_ID,
                message
            )
        
        # Manager/Admin telegram group'lariga ham yuborish
        managers = User.objects.filter(role__in=['admin', 'sales_manager'])
        for manager in managers:
            if manager.telegram_group_id:
                send_telegram_notification(
                    manager.telegram_group_id,
                    message
                )
        
        print(f"[weekly report] Haftalik hisobot yuborildi ({week_start} - {week_end})")
        
    except Exception as e:
        print(f"[weekly report] xatolik: {e}")
        import traceback
        traceback.print_exc()


@shared_task
def send_monthly_report_task():
    """
    Oylik hisobot (Oyning 1-kuni)
    """
    try:
        from django.conf import settings
        from django.db.models import Count, Sum, Avg, Q
        from datetime import timedelta
        import calendar
        
        today = timezone.localdate()
        
        # O'tgan oy
        if today.month == 1:
            last_month = 12
            last_year = today.year - 1
        else:
            last_month = today.month - 1
            last_year = today.year
        
        month_start = today.replace(year=last_year, month=last_month, day=1)
        days_in_month = calendar.monthrange(last_year, last_month)[1]
        month_end = month_start.replace(day=days_in_month)
        
        month_name = calendar.month_name[last_month]
        
        # Statistikalar
        total_leads = Lead.objects.filter(
            created_at__date__gte=month_start,
            created_at__date__lte=month_end
        ).count()
        
        total_trials = TrialLesson.objects.filter(
            date__gte=month_start,
            date__lte=month_end
        ).count()
        
        total_sales = Lead.objects.filter(
            status='enrolled',
            enrolled_at__date__gte=month_start,
            enrolled_at__date__lte=month_end
        ).count()
        
        # Sotuvchilar reytingi
        sales_users = User.objects.filter(role='sales', is_active_sales=True)
        sales_ratings = []
        
        for sales in sales_users:
            sales_leads = Lead.objects.filter(
                assigned_sales=sales,
                created_at__date__gte=month_start,
                created_at__date__lte=month_end
            ).count()
            
            sales_trials = TrialLesson.objects.filter(
                lead__assigned_sales=sales,
                date__gte=month_start,
                date__lte=month_end
            ).count()
            
            sales_enrolled = Lead.objects.filter(
                assigned_sales=sales,
                status='enrolled',
                enrolled_at__date__gte=month_start,
                enrolled_at__date__lte=month_end
            ).count()
            
            conversion_rate = (sales_enrolled / sales_trials * 100) if sales_trials > 0 else 0
            
            sales_ratings.append({
                'sales': sales,
                'leads': sales_leads,
                'trials': sales_trials,
                'sales_count': sales_enrolled,
                'conversion': conversion_rate
            })
        
        # Konversiya bo'yicha tartiblash
        sales_ratings.sort(key=lambda x: x['conversion'], reverse=True)
        
        # Top 3 sotuvchi
        top_sales_lines = []
        for i, rating in enumerate(sales_ratings[:3], 1):
            top_sales_lines.append(
                f"{i}. {rating['sales'].username}: "
                f"{rating['sales_count']} ta sotuv, "
                f"{rating['conversion']:.1f}% konversiya"
            )
        
        # Umumiy konversiya
        total_trials_converted = sum(r['trials'] for r in sales_ratings)
        total_sales_converted = sum(r['sales_count'] for r in sales_ratings)
        overall_conversion = (total_sales_converted / total_trials_converted * 100) if total_trials_converted > 0 else 0
        
        # O'rtacha kunlik ko'rsatkichlar
        days_in_month_count = (month_end - month_start).days + 1
        avg_daily_leads = total_leads / days_in_month_count if days_in_month_count > 0 else 0
        avg_daily_sales = total_sales / days_in_month_count if days_in_month_count > 0 else 0
        
        message = (
            f"📊 <b>Oylik Hisobot</b>\n"
            f"{month_name} {last_year}\n"
            f"{'=' * 30}\n\n"
            f"📈 <b>Umumiy Statistikalar:</b>\n"
            f"  • Jami lidlar: {total_leads} ta\n"
            f"  • Trial darslar: {total_trials} ta\n"
            f"  • Sotuvlar: {total_sales} ta\n"
            f"  • Konversiya: {overall_conversion:.1f}%\n"
            f"  • O'rtacha kunlik lidlar: {avg_daily_leads:.1f} ta\n"
            f"  • O'rtacha kunlik sotuvlar: {avg_daily_sales:.1f} ta\n\n"
            f"🏆 <b>Top 3 Sotuvchi:</b>\n"
            f"{chr(10).join(top_sales_lines) if top_sales_lines else 'Ma\'lumot topilmadi'}\n\n"
            f"📅 Keyingi oy uchun omad!"
        )
        
        # Admin ga yuborish
        if settings.TELEGRAM_ADMIN_CHAT_ID:
            send_telegram_notification(
                settings.TELEGRAM_ADMIN_CHAT_ID,
                message
            )
        
        # Manager/Admin telegram group'lariga ham yuborish
        managers = User.objects.filter(role__in=['admin', 'sales_manager'])
        for manager in managers:
            if manager.telegram_group_id:
                send_telegram_notification(
                    manager.telegram_group_id,
                    message
                )
        
        print(f"[monthly report] Oylik hisobot yuborildi ({month_name} {last_year})")
        
    except Exception as e:
        print(f"[monthly report] xatolik: {e}")
        import traceback
        traceback.print_exc()


@shared_task
def send_trial_results_summary_task():
    """
    Trial dars natijalari hisoboti (har kuni kechqurun)
    """
    try:
        from django.conf import settings
        
        today = timezone.localdate()
        
        # Bugungi trial'lar
        today_trials = TrialLesson.objects.filter(date=today).select_related('lead', 'lead__assigned_sales')
        
        total_trials = today_trials.count()
        attended_trials = today_trials.filter(lead__status='trial_attended').count()
        not_attended_trials = today_trials.filter(lead__status='trial_not_attended').count()
        # Bugungi trial'dan keyin enrolled bo'lganlar
        trial_lead_ids = [t.lead.id for t in today_trials]
        enrolled_after_trial = Lead.objects.filter(
            status='enrolled',
            enrolled_at__date=today,
            id__in=trial_lead_ids
        ).count() if trial_lead_ids else 0
        
        # Konversiya
        conversion_rate = (enrolled_after_trial / attended_trials * 100) if attended_trials > 0 else 0
        
        # Sotuvchilar bo'yicha
        sales_summary = {}
        for trial in today_trials:
            sales = trial.lead.assigned_sales
            if not sales:
                continue
            
            if sales.username not in sales_summary:
                sales_summary[sales.username] = {
                    'total': 0,
                    'attended': 0,
                    'not_attended': 0,
                    'enrolled': 0
                }
            
            sales_summary[sales.username]['total'] += 1
            if trial.lead.status == 'trial_attended':
                sales_summary[sales.username]['attended'] += 1
            elif trial.lead.status == 'trial_not_attended':
                sales_summary[sales.username]['not_attended'] += 1
        
        # Enrolled'lar (bugungi trial'dan keyin)
        enrolled_today = Lead.objects.filter(
            status='enrolled',
            enrolled_at__date=today
        ).select_related('assigned_sales')
        
        for lead in enrolled_today:
            # Agar bugungi trial'lar ro'yxatida bo'lsa
            if lead.id in [t.lead.id for t in today_trials]:
                if lead.assigned_sales and lead.assigned_sales.username in sales_summary:
                    sales_summary[lead.assigned_sales.username]['enrolled'] += 1
        
        # Sotuvchilar bo'yicha qatorlar
        sales_lines = []
        for sales_name, data in sales_summary.items():
            sales_conversion = (data['enrolled'] / data['attended'] * 100) if data['attended'] > 0 else 0
            sales_lines.append(
                f"• {sales_name}: "
                f"jami {data['total']}, "
                f"keldi {data['attended']}, "
                f"kelmadi {data['not_attended']}, "
                f"yozildi {data['enrolled']} "
                f"({sales_conversion:.1f}%)"
            )
        
        message = (
            f"📊 <b>Trial Dars Natijalari</b>\n"
            f"{today.strftime('%d.%m.%Y')}\n"
            f"{'=' * 30}\n\n"
            f"📈 <b>Umumiy:</b>\n"
            f"  • Jami trial'lar: {total_trials} ta\n"
            f"  • Kelganlar: {attended_trials} ta\n"
            f"  • Kelmaganlar: {not_attended_trials} ta\n"
            f"  • Kursga yozilganlar: {enrolled_after_trial} ta\n"
            f"  • Konversiya: {conversion_rate:.1f}%\n\n"
        )
        
        if sales_lines:
            message += f"👥 <b>Sotuvchilar bo'yicha:</b>\n{chr(10).join(sales_lines)}\n"
        
        # Admin ga yuborish
        if settings.TELEGRAM_ADMIN_CHAT_ID:
            send_telegram_notification(
                settings.TELEGRAM_ADMIN_CHAT_ID,
                message
            )
        
        # Manager/Admin telegram group'lariga ham yuborish
        managers = User.objects.filter(role__in=['admin', 'sales_manager'])
        for manager in managers:
            if manager.telegram_group_id:
                send_telegram_notification(
                    manager.telegram_group_id,
                    message
                )
        
        print(f"[trial results] Trial natijalari yuborildi ({today})")
        
    except Exception as e:
        print(f"[trial results] xatolik: {e}")
        import traceback
        traceback.print_exc()
