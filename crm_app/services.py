from django.utils import timezone
from django.db import models
from datetime import timedelta
from .models import User, Lead, FollowUp, Group, TrialLesson, KPI, Reactivation, Offer


class LeadDistributionService:
    """Lid taqsimlash xizmati"""
    
    @staticmethod
    def distribute_leads(leads):
        """Lidlarni faol va ishda bo'lgan sotuvchilar orasida teng taqsimlash"""
        from .tasks import send_new_lead_notification
        
        # Faqat mavjud va ishda bo'lgan sotuvchilarni olish
        active_sales = [sales for sales in User.objects.filter(role='sales', is_active_sales=True) 
                       if sales.is_available_for_leads]
        
        if not active_sales:
            return None
        
        # Har bir sotuvchining lidlari sonini hisoblash
        sales_lead_counts = {}
        for sales in active_sales:
            sales_lead_counts[sales.id] = Lead.objects.filter(
                assigned_sales=sales,
                status__in=['new', 'contacted', 'interested', 'trial_registered']
            ).count()
        
        # Lidlarni taqsimlash
        for lead in leads:
            # Eski assigned_sales ni saqlash (notification uchun)
            old_assigned_sales_id = lead.assigned_sales_id if lead.pk else None
            was_new_lead = not lead.pk  # Lid yangi ekanligini tekshirish
            
            if not sales_lead_counts:
                # Agar barcha sotuvchilar ishda bo'lmasa, eng kam lidga ega bo'lganiga berish
                active_sales = [sales for sales in User.objects.filter(role='sales', is_active_sales=True)]
                if active_sales:
                    min_sales = min(active_sales, key=lambda s: Lead.objects.filter(
                        assigned_sales=s,
                        status__in=['new', 'contacted', 'interested', 'trial_registered']
                    ).count())
                    lead.assigned_sales = min_sales
                    lead.save()
                    # Notification yuborish
                    # Agar lid yangi bo'lsa yoki assigned_sales o'zgarganda notification yuborish
                    if was_new_lead or (not old_assigned_sales_id or old_assigned_sales_id != min_sales.id):
                        send_new_lead_notification.delay(lead.id)
                continue
            
            # Eng kam lidga ega sotuvchini topish
            min_sales_id = min(sales_lead_counts.items(), key=lambda x: x[1])[0]
            lead.assigned_sales_id = min_sales_id
            lead.save()
            
            # Notification yuborish
            # Agar lid yangi bo'lsa yoki assigned_sales o'zgarganda notification yuborish
            if was_new_lead or (not old_assigned_sales_id or old_assigned_sales_id != min_sales_id):
                send_new_lead_notification.delay(lead.id)
            
            sales_lead_counts[min_sales_id] += 1
        
        return len(active_sales)


class FollowUpService:
    """Follow-up xizmatlari"""
    
    @staticmethod
    def calculate_work_hours_due_date(sales, base_time, delay):
        """
        Follow-up vaqtini ish vaqtlariga moslashtirish
        Ruxsat so'rovlarini ham inobatga oladi
        
        Args:
            sales: User model instance (sotuvchi)
            base_time: datetime - boshlang'ich vaqt
            delay: timedelta - kechikish (masalan, timedelta(hours=24))
        
        Returns:
            datetime - ish vaqtiga moslashtirilgan follow-up vaqti
        """
        if not sales or not sales.is_active_sales:
            # Agar sotuvchi yo'q yoki faol emas bo'lsa, oddiy hisoblash
            return base_time + delay
        
        # Agar ish vaqtlari belgilanmagan bo'lsa, oddiy hisoblash
        if not sales.work_start_time or not sales.work_end_time:
            return base_time + delay
        
        # Ruxsat so'rovlarini tekshirish funksiyasi
        def is_on_leave_at_time(check_datetime):
            """Belgilangan vaqtda ruxsat olganligini tekshirish"""
            from .models import LeaveRequest
            check_date = check_datetime.date()
            check_time = check_datetime.time()
            
            active_leave = LeaveRequest.objects.filter(
                sales=sales,
                status='approved',
                start_date__lte=check_date,
                end_date__gte=check_date
            ).first()
            
            if active_leave:
                # Agar soatlar belgilangan bo'lsa
                if active_leave.start_time and active_leave.end_time:
                    if active_leave.start_time <= check_time <= active_leave.end_time:
                        return True
                else:
                    # Butun kun ruxsat
                    return True
            return False
        
        # Hisoblangan vaqt
        calculated_time = base_time + delay
        
        # Ish kunlari
        work_days = {
            0: sales.work_monday,      # Dushanba
            1: sales.work_tuesday,     # Seshanba
            2: sales.work_wednesday,   # Chorshanba
            3: sales.work_thursday,    # Payshanba
            4: sales.work_friday,      # Juma
            5: sales.work_saturday,    # Shanba
            6: sales.work_sunday,      # Yakshanba
        }
        
        # Hisoblangan vaqtning kuni va vaqti
        calculated_weekday = calculated_time.weekday()
        calculated_time_only = calculated_time.time()
        calculated_date = calculated_time.date()
        
        # Ish kuni va ish vaqti ichida ekanligini tekshirish
        is_work_day = work_days.get(calculated_weekday, False)
        is_work_hours = sales.work_start_time <= calculated_time_only <= sales.work_end_time
        is_on_leave = is_on_leave_at_time(calculated_time)
        
        # Agar ish vaqti ichida va ruxsat olmagan bo'lsa
        if is_work_day and is_work_hours and not is_on_leave:
            return calculated_time
        
        # Agar ish vaqti tashqarisida yoki ruxsat olgan bo'lsa, keyingi ish kunini topish
        # Hisoblangan kundan boshlab keyingi ish kunini topish
        max_days_to_check = 30  # 1 oy tekshirish (ruxsatlar uzoq bo'lishi mumkin)
        
        for day_offset in range(max_days_to_check):
            check_date = calculated_date + timedelta(days=day_offset)
            check_weekday = check_date.weekday()
            
            # Agar bu ish kuni bo'lsa
            if work_days.get(check_weekday, False):
                # Bu kunning ish vaqti boshlanishini yaratish
                work_start_datetime = timezone.make_aware(
                    timezone.datetime.combine(check_date, sales.work_start_time)
                )
                
                # Agar ruxsat olmagan bo'lsa
                if not is_on_leave_at_time(work_start_datetime):
                    if check_date == calculated_date:
                        # Agar bu kun hisoblangan kun bo'lsa
                        if calculated_time_only < sales.work_start_time:
                            # Bugun ish vaqti boshlanishiga o'tkazish
                            return work_start_datetime
                        # Agar hisoblangan vaqt ish vaqti tugashidan keyin bo'lsa yoki ish kuni emas bo'lsa
                        # Keyingi ish kunining boshlanishiga o'tkazish
                        continue
                    
                    # Keyingi ish kunining boshlanish vaqtini qaytarish
                    return work_start_datetime
        
        # Agar ish kuni topilmasa, oddiy hisoblangan vaqtni qaytarish
        return calculated_time
    
    @staticmethod
    def get_today_followups(sales=None):
        """Bugungi va o'tgan barcha bajarilmagan follow-uplarni olish"""
        today_end = timezone.now().replace(hour=23, minute=59, second=59, microsecond=999999)
        
        queryset = FollowUp.objects.select_related(
            'lead', 'sales', 'lead__assigned_sales', 'lead__interested_course'
        ).filter(
            due_date__lte=today_end,  # Bugun yoki undan oldin
            completed=False
        )
        
        if sales:
            queryset = queryset.filter(sales=sales)
        
        return queryset.order_by('due_date')
    
    @staticmethod
    def get_overdue_followups(sales=None):
        """Overdue follow-uplarni olish"""
        queryset = FollowUp.objects.select_related(
            'lead', 'sales', 'lead__assigned_sales', 'lead__interested_course'
        ).filter(
            due_date__lt=timezone.now(),
            completed=False
        )
        
        if sales:
            queryset = queryset.filter(sales=sales)
        
        return queryset.order_by('due_date')
    
    @staticmethod
    def check_sales_blocked(sales):
        """Sotuvchi bloklanganligini tekshirish (5+ overdue)"""
        overdue_count = FollowUpService.get_overdue_followups(sales).count()
        return overdue_count >= 5
    
    @staticmethod
    def get_overdue_followups_prioritized(sales=None):
        """Overdue'larni prioritet bo'yicha tartiblash"""
        from django.db.models import F, Case, When, IntegerField
        
        overdue = FollowUpService.get_overdue_followups(sales)
        
        # Prioritizatsiya:
        # 1. Eng qadimgi overdue (urgent)
        # 2. Lead status (interested > contacted > new)
        
        # Annotate qilish uchun status priority
        overdue = overdue.annotate(
            status_priority=Case(
                When(lead__status='interested', then=3),
                When(lead__status='trial_registered', then=2),
                When(lead__status='contacted', then=1),
                When(lead__status='new', then=0),
                default=0,
                output_field=IntegerField()
            )
        )
        
        return overdue.order_by('due_date', '-status_priority')
    
    @staticmethod
    def auto_reschedule_overdue(followup, hours_ahead=2):
        """Overdue follow-up'ni avtomatik qayta rejalashtirish"""
        if followup.completed:
            return False
        
        # Keyingi ish vaqtiga o'tkazish
        new_due_date = FollowUpService.calculate_work_hours_due_date(
            followup.sales,
            timezone.now(),
            timedelta(hours=hours_ahead)
        )
        
        followup.due_date = new_due_date
        followup.is_overdue = False
        followup.save()
        
        return True
    
    @staticmethod
    def escalate_overdue_followup(followup):
        """Overdue follow-up'ni manager'ga ko'tarish"""
        from .tasks import send_telegram_notification
        
        # Agar 24+ soat overdue bo'lsa, manager'ga xabar
        hours_overdue = (timezone.now() - followup.due_date).total_seconds() / 3600
        
        if hours_overdue >= 24:
            # Manager'larga notification
            managers = User.objects.filter(
                role__in=['admin', 'sales_manager']
            )
            for manager in managers:
                if manager.telegram_chat_id:
                    due_date_str = followup.due_date.strftime('%d.%m.%Y %H:%M')
                    message = (
                        f"🚨 <b>ESCALATION: Overdue Follow-up</b>\n"
                        f"{'=' * 30}\n\n"
                        f"👤 <b>Lid:</b> {followup.lead.name}\n"
                        f"📞 <b>Telefon:</b> <code>{followup.lead.phone}</code>\n"
                        f"👨‍💼 <b>Sotuvchi:</b> {followup.sales.username}\n\n"
                        f"⏰ <b>Vaqt:</b> {due_date_str}\n"
                        f"⏳ <b>Kechikish:</b> {hours_overdue:.1f} soat\n\n"
                        f"🔴 <b>24+ soat overdue - DARHOL TAXSIR QILING!</b>"
                    )
                    send_telegram_notification(
                        manager.telegram_chat_id,
                        message
                    )
            return True
        return False
    
    @staticmethod
    def reassign_overdue_followup(followup, new_sales=None):
        """Overdue follow-up'ni boshqa sotuvchiga o'tkazish"""
        if new_sales is None:
            # Eng kam overdue'ga ega sotuvchini topish
            sales_overdue = {}
            for sales in User.objects.filter(role='sales', is_active_sales=True):
                sales_overdue[sales] = FollowUpService.get_overdue_followups(sales).count()
            
            if not sales_overdue:
                return None
            
            new_sales = min(sales_overdue.items(), key=lambda x: x[1])[0]
        
        followup.sales = new_sales
        followup.save()
        
        return new_sales
    
    @staticmethod
    def get_overdue_statistics(sales=None, days=7):
        """Overdue statistikasi"""
        overdue = FollowUpService.get_overdue_followups(sales)
        now = timezone.now()
        
        from django.core.cache import cache
        
        # Cache key
        cache_key = f'overdue_stats_{sales.id if sales else "all"}'
        stats = cache.get(cache_key)
        
        if stats is None:
            stats = {
                'total': overdue.count(),
                'by_age': {
                    '< 1 hour': overdue.filter(
                        due_date__gte=now - timedelta(hours=1)
                    ).count(),
                    '1-6 hours': overdue.filter(
                        due_date__lt=now - timedelta(hours=1),
                        due_date__gte=now - timedelta(hours=6)
                    ).count(),
                    '6-24 hours': overdue.filter(
                        due_date__lt=now - timedelta(hours=6),
                        due_date__gte=now - timedelta(days=1)
                    ).count(),
                    '> 24 hours': overdue.filter(
                        due_date__lt=now - timedelta(days=1)
                    ).count(),
                },
                'by_sales': {}
            }
            
            # Har bir sotuvchi uchun overdue soni
            if not sales:
                for sales_user in User.objects.filter(role='sales', is_active_sales=True):
                    count = FollowUpService.get_overdue_followups(sales_user).count()
                    if count > 0:
                        stats['by_sales'][sales_user.username] = count
            
            # Cache for 5 minutes
            cache.set(cache_key, stats, 300)
        
        return stats


class GroupService:
    """Guruh xizmatlari"""
    
    @staticmethod
    def get_available_groups(course=None, days=None, time=None):
        """Mavjud guruhlarni olish"""
        queryset = Group.objects.filter(is_active=True)
        
        if course:
            queryset = queryset.filter(course=course)
        if days:
            queryset = queryset.filter(days=days)
        if time:
            queryset = queryset.filter(time=time)
        
        # Faqat to'liq bo'lmagan guruhlarni qaytarish
        available = queryset.filter(current_students__lt=models.F('capacity'))
        
        # Agar mavjud guruhlar bo'lmasa, barcha faol guruhlarni qaytarish (to'liq bo'lsa ham)
        if not available.exists() and queryset.exists():
            return queryset.order_by('name')
        
        return available.order_by('name')
    
    @staticmethod
    def get_room_occupancy(room, date_obj, time_slot):
        """Xona bandligini olish"""
        # Bu yerda dars jadvali asosida hisoblash kerak
        # Soddalashtirilgan versiya
        groups = Group.objects.filter(room=room, time=time_slot, is_active=True)
        total_students = sum(group.current_students for group in groups)
        total_capacity = sum(group.capacity for group in groups)
        
        if total_capacity == 0:
            return 0
        
        return (total_students / total_capacity) * 100
    
    @staticmethod
    def can_enroll_to_group(group):
        """Guruhga yozish mumkinligini tekshirish"""
        return not group.is_full


class KPIService:
    """KPI hisoblash xizmati"""
    
    @staticmethod
    def calculate_daily_kpi(sales, date):
        """Kunlik KPI hisoblash (ishda bo'lmagan vaqtlarni hisobga o'tkazmaslik)"""
        from django.db.models import Count, Avg, Q
        from datetime import datetime, time as dt_time
        
        # Sotuvchi o'sha kuni ishda bo'lganligini tekshirish
        date_start = timezone.make_aware(datetime.combine(date, dt_time.min))
        date_end = timezone.make_aware(datetime.combine(date, dt_time.max))
        
        # Agar sotuvchi o'sha kuni ishda bo'lmagan bo'lsa, KPI'ni 0 qilib qaytaramiz
        if sales.is_on_leave:
            # Ruxsat so'rovlarini tekshirish
            from .models import LeaveRequest
            leave_request = LeaveRequest.objects.filter(
                sales=sales,
                start_date__lte=date,
                end_date__gte=date,
                status='approved'
            ).first()
            if leave_request:
                # KPI'ni 0 qilib qaytaramiz
                kpi, created = KPI.objects.update_or_create(
                    sales=sales,
                    date=date,
                    defaults={
                        'daily_contacts': 0,
                        'daily_followups': 0,
                        'followup_completion_rate': 0,
                        'trials_registered': 0,
                        'trials_to_sales': 0,
                        'conversion_rate': 0,
                        'response_time_minutes': 0,
                        'overdue_count': 0,
                    }
                )
                return kpi
        
        # Agar sotuvchi o'sha kuni ishda emas bo'lsa
        if sales.is_absent and sales.absent_from and sales.absent_until:
            if sales.absent_from <= date_end and sales.absent_until >= date_start:
                # KPI'ni 0 qilib qaytaramiz
                kpi, created = KPI.objects.update_or_create(
                    sales=sales,
                    date=date,
                    defaults={
                        'daily_contacts': 0,
                        'daily_followups': 0,
                        'followup_completion_rate': 0,
                        'trials_registered': 0,
                        'trials_to_sales': 0,
                        'conversion_rate': 0,
                        'response_time_minutes': 0,
                        'overdue_count': 0,
                    }
                )
                return kpi
        
        # Kunlik aloqa (faqat ishda bo'lgan vaqtlarda)
        daily_contacts = Lead.objects.filter(
            assigned_sales=sales,
            updated_at__date=date,
            status__in=['contacted', 'interested']
        ).count()
        
        # Kunlik follow-up (faqat ishda bo'lgan vaqtlarda)
        daily_followups = FollowUp.objects.filter(
            sales=sales,
            due_date__date=date
        ).count()
        
        # Follow-up bajarilganligi
        completed_followups = FollowUp.objects.filter(
            sales=sales,
            due_date__date=date,
            completed=True
        ).count()
        followup_completion_rate = (completed_followups / daily_followups * 100) if daily_followups > 0 else 0
        
        # Sinovga yozilganlar
        trials_registered = Lead.objects.filter(
            assigned_sales=sales,
            status='trial_registered',
            updated_at__date=date
        ).count()
        
        # Sinovdan sotuv
        trials_to_sales = Lead.objects.filter(
            assigned_sales=sales,
            status='enrolled',
            enrolled_at__date=date
        ).count()
        
        # Kunlik konversiya: shu kunda enrolled bo'lganlar / shu kunda berilgan lidlar
        total_assigned_today = Lead.objects.filter(
            assigned_sales=sales,
            created_at__date=date
        ).count()
        enrolled_today = Lead.objects.filter(
            assigned_sales=sales,
            status='enrolled',
            enrolled_at__date=date
        ).count()
        conversion_rate = (enrolled_today / total_assigned_today * 100) if total_assigned_today > 0 else 0
        
        # Response time (o'rtacha)
        # Soddalashtirilgan - lead yaratilgan vaqt va birinchi follow-up orasidagi vaqt
        response_times = []
        leads = Lead.objects.filter(assigned_sales=sales, created_at__date=date)
        for lead in leads:
            first_followup = FollowUp.objects.filter(lead=lead).order_by('due_date').first()
            if first_followup:
                response_time = (first_followup.due_date - lead.created_at).total_seconds() / 60
                response_times.append(response_time)
        
        response_time_minutes = sum(response_times) / len(response_times) if response_times else 0
        
        # Overdue soni
        overdue_count = FollowUp.objects.filter(
            sales=sales,
            is_overdue=True,
            completed=False
        ).count()
        
        # KPI yaratish yoki yangilash
        kpi, created = KPI.objects.update_or_create(
            sales=sales,
            date=date,
            defaults={
                'daily_contacts': daily_contacts,
                'daily_followups': daily_followups,
                'followup_completion_rate': followup_completion_rate,
                'trials_registered': trials_registered,
                'trials_to_sales': trials_to_sales,
                'conversion_rate': conversion_rate,
                'response_time_minutes': response_time_minutes,
                'overdue_count': overdue_count,
            }
        )
        
        return kpi
    
    @staticmethod
    def calculate_monthly_conversion_rate(sales, year, month):
        """Oylik konversiya hisoblash: oy davomida enrolled bo'lganlar / oy davomida berilgan lidlar"""
        from datetime import datetime
        from calendar import monthrange
        
        # Oyning birinchi va oxirgi kuni
        month_start = datetime(year, month, 1).date()
        last_day = monthrange(year, month)[1]
        month_end = datetime(year, month, last_day).date()
        
        # Oy davomida berilgan barcha lidlar
        total_assigned_monthly = Lead.objects.filter(
            assigned_sales=sales,
            created_at__date__gte=month_start,
            created_at__date__lte=month_end
        ).count()
        
        # Oy davomida enrolled bo'lgan lidlar
        enrolled_monthly = Lead.objects.filter(
            assigned_sales=sales,
            status='enrolled',
            enrolled_at__date__gte=month_start,
            enrolled_at__date__lte=month_end
        ).count()
        
        # Oylik konversiya
        monthly_conversion_rate = (enrolled_monthly / total_assigned_monthly * 100) if total_assigned_monthly > 0 else 0
        
        return {
            'total_assigned': total_assigned_monthly,
            'enrolled': enrolled_monthly,
            'conversion_rate': monthly_conversion_rate
        }


class ReactivationService:
    """Reaktivatsiya xizmati"""
    
    @staticmethod
    def check_and_reactivate():
        """Yo'qotilgan lidlarni reaktivatsiya qilish"""
        from .tasks import send_reactivation_notification
        
        lost_leads = Lead.objects.filter(status='lost', lost_at__isnull=False)
        
        for lead in lost_leads:
            days_since_lost = (timezone.now().date() - lead.lost_at.date()).days
            
            # 7 kun
            if days_since_lost == 7:
                reactivation, created = Reactivation.objects.get_or_create(
                    lead=lead,
                    reactivation_type='7_days',
                    defaults={'days_since_lost': 7}
                )
                if created:
                    send_reactivation_notification.delay(reactivation.id)
            
            # 14 kun
            elif days_since_lost == 14:
                reactivation, created = Reactivation.objects.get_or_create(
                    lead=lead,
                    reactivation_type='14_days',
                    defaults={'days_since_lost': 14}
                )
                if created:
                    send_reactivation_notification.delay(reactivation.id)
            
            # 30 kun
            elif days_since_lost == 30:
                reactivation, created = Reactivation.objects.get_or_create(
                    lead=lead,
                    reactivation_type='30_days',
                    defaults={'days_since_lost': 30}
                )
                if created:
                    send_reactivation_notification.delay(reactivation.id)


class OfferService:
    """Takliflar (chegirma/bonus) xizmati"""

    @staticmethod
    def active_offers(channel=None, audience=None, course=None, date=None):
        """
        Faol va amaldagi takliflar ro'yxati
        channel: 'followup', 'reactivation', 'trial', 'general', 'all'
        audience: 'new', 'lost', 'reactivation', 'trial', 'all'
        course: Course instance yoki None
        """
        today = date or timezone.now().date()

        qs = Offer.objects.filter(is_active=True)

        # Sana bo'yicha filtr
        qs = qs.filter(
            models.Q(valid_from__isnull=True) | models.Q(valid_from__lte=today),
            models.Q(valid_until__isnull=True) | models.Q(valid_until__gte=today),
        )

        # Kanal bo'yicha filtr
        if channel and channel != 'all':
            qs = qs.filter(models.Q(channel='general') | models.Q(channel=channel))

        # Auditoriya bo'yicha filtr
        if audience and audience != 'all':
            qs = qs.filter(models.Q(audience='any') | models.Q(audience=audience))

        # Kurs bo'yicha filtr
        if course:
            qs = qs.filter(models.Q(course__isnull=True) | models.Q(course=course))

        return qs.order_by('-priority', 'valid_until', '-created_at')

    @staticmethod
    def active_for_lead(lead, channel=None):
        """Lead kontekstida mos takliflar"""
        audience = 'all'
        if lead:
            if lead.status in ['lost', 'reactivation']:
                audience = 'reactivation'
            elif lead.status == 'trial_registered':
                audience = 'trial'
            elif lead.status in ['new', 'contacted', 'interested']:
                audience = 'new'
        return OfferService.active_offers(
            channel=channel or 'all',
            audience=audience,
            course=getattr(lead, 'interested_course', None)
        )


class GoogleSheetsService:
    """Google Sheets integratsiyasi - Avtomatik lid import"""
    
    @staticmethod
    def get_credentials():
        """Google Sheets kredensiallarini olish"""
        import json
        from google.oauth2.service_account import Credentials
        from django.conf import settings
        
        # .env fayldan credentials JSON'ni olish
        creds_json = settings.GOOGLE_SHEETS_CREDENTIALS
        
        if not creds_json:
            raise ValueError("GOOGLE_SHEETS_CREDENTIALS sozlanmagan!")
        
        # JSON string'ni dict'ga o'tkazish
        try:
            creds_dict = json.loads(creds_json)
        except json.JSONDecodeError:
            # Agar fayl yo'li bo'lsa
            with open(creds_json, 'r') as f:
                creds_dict = json.load(f)
        
        # Credentials yaratish
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
        credentials = Credentials.from_service_account_info(
            creds_dict,
            scopes=SCOPES
        )
        
        return credentials
    
    @staticmethod
    def connect_to_sheet(spreadsheet_id, worksheet_name='Sheet1'):
        """Google Sheets'ga ulanish"""
        import gspread
        
        try:
            credentials = GoogleSheetsService.get_credentials()
            client = gspread.authorize(credentials)
            spreadsheet = client.open_by_key(spreadsheet_id)
            worksheet = spreadsheet.worksheet(worksheet_name)
            return worksheet
        except Exception as e:
            print(f"Google Sheets'ga ulanishda xatolik: {e}")
            raise
    
    @staticmethod
    def import_new_leads(spreadsheet_id, worksheet_name='Sheet1', 
                        name_column='name', phone_column='phone', 
                        source_column='source', interested_course_column='course',
                        secondary_phone_column='secondary_phone'):
        """
        Google Sheets'dan yangi lidlarni import qilish
        
        Args:
            spreadsheet_id: Google Sheets ID (URL'dan)
            worksheet_name: Sheet nomi (default: 'Sheet1')
            name_column: Ism ustuni nomi (default: 'name')
            phone_column: Telefon ustuni nomi (default: 'phone')
            source_column: Manba ustuni nomi (default: 'source')
            interested_course_column: Qiziqayotgan kurs ustuni nomi (default: 'course')
            secondary_phone_column: Qo'shimcha telefon ustuni nomi (default: 'secondary_phone')
        
        Returns:
            dict: {'imported': count, 'skipped': count, 'errors': []}
        """
        from django.core.cache import cache
        
        result = {
            'imported': 0,
            'skipped': 0,
            'errors': [],
            'leads': []
        }
        
        try:
            # Google Sheets'ga ulanish
            worksheet = GoogleSheetsService.connect_to_sheet(
                spreadsheet_id, 
                worksheet_name
            )
            
            # Barcha qatorlarni olish (dictionary formatda)
            all_records = worksheet.get_all_records()
            
            if not all_records:
                return result
            
            # Cache'dan oxirgi import qilingan qator raqamini olish
            cache_key = f'google_sheets_last_row_{spreadsheet_id}_{worksheet_name}'
            last_imported_row = cache.get(cache_key, 0)  # 0 = hech narsa import qilinmagan
            
            # Faqat yangi qatorlarni import qilish
            new_records = all_records[last_imported_row:]
            
            if not new_records:
                return result
            
            # Har bir yangi qatorni qayta ishlash
            leads_to_import = []
            
            for idx, record in enumerate(new_records, start=last_imported_row + 1):
                try:
                    # Ma'lumotlarni olish (case-insensitive)
                    name = str(record.get(name_column, record.get(name_column.title(), ''))).strip()
                    phone = str(record.get(phone_column, record.get(phone_column.title(), ''))).strip()
                    
                    # Bo'sh yoki noto'g'ri ma'lumotlarni o'tkazib yuborish
                    if not name or not phone:
                        result['skipped'] += 1
                        continue
                    
                    # Telefon raqamni tozalash
                    phone = phone.replace('+', '').replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
                    
                    # Duplicate tekshirish
                    if Lead.objects.filter(phone=phone).exists():
                        result['skipped'] += 1
                        continue
                    
                    # Source
                    source_value = str(record.get(source_column, record.get(source_column.title(), 'instagram'))).strip().lower()
                    source_mapping = {
                        'instagram': 'instagram',
                        'telegram': 'telegram',
                        'youtube': 'youtube',
                        'organic': 'organic',
                        'form': 'form',
                        'excel': 'excel',
                        'google_sheets': 'google_sheets',
                    }
                    source = source_mapping.get(source_value, 'google_sheets')
                    
                    # Qo'shimcha telefon
                    secondary_phone = str(record.get(secondary_phone_column, 
                                         record.get(secondary_phone_column.title(), ''))).strip()
                    if secondary_phone:
                        secondary_phone = secondary_phone.replace('+', '').replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
                    
                    # Interested course
                    interested_course = None
                    course_name = str(record.get(interested_course_column, 
                                     record.get(interested_course_column.title(), ''))).strip()
                    if course_name:
                        try:
                            interested_course = Course.objects.filter(
                                name__icontains=course_name
                            ).first()
                        except:
                            pass
                    
                    # Lead yaratish
                    lead = Lead(
                        name=name,
                        phone=phone,
                        secondary_phone=secondary_phone if secondary_phone else None,
                        source=source,
                        interested_course=interested_course,
                        notes=f"Google Sheets'dan avtomatik import (row {idx + 1})"
                    )
                    leads_to_import.append(lead)
                    
                except Exception as e:
                    result['errors'].append(f"Row {idx + 1}: {str(e)}")
                    continue
            
            # Bulk yaratish va taqsimlash
            if leads_to_import:
                # Taqsimlash (ichida save va notification bo'ladi)
                # MUHIM: Lidlarni avval save qilmaslik! 
                # distribute_leads ichida assigned_sales bilan birga save qiladi
                # Bu signal'ni to'g'ri ishlashi uchun zarur
                from .services import LeadDistributionService
                LeadDistributionService.distribute_leads(leads_to_import)
                
                result['imported'] = len(leads_to_import)
                result['leads'] = [lead.id for lead in leads_to_import]
                
                # Cache'ni yangilash
                cache.set(
                    cache_key, 
                    last_imported_row + len(new_records),
                    timeout=None  # Hech qachon expire bo'lmaydi
                )
            
        except Exception as e:
            result['errors'].append(f"Umumiy xatolik: {str(e)}")
            print(f"Google Sheets import xatolik: {e}")
            import traceback
            traceback.print_exc()
        
        return result
    
    @staticmethod
    def test_connection(spreadsheet_id, worksheet_name='Sheet1'):
        """Google Sheets ulanishini test qilish"""
        try:
            worksheet = GoogleSheetsService.connect_to_sheet(
                spreadsheet_id,
                worksheet_name
            )
            row_count = worksheet.row_count
            col_count = worksheet.col_count
            
            return {
                'success': True,
                'message': f'Ulanish muvaffaqiyatli! {row_count} qator, {col_count} ustun',
                'row_count': row_count,
                'col_count': col_count
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Xatolik: {str(e)}'
            }