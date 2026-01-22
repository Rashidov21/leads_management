from django.utils import timezone
from django.db import models
from datetime import timedelta
from .models import User, Lead, FollowUp, Group, TrialLesson, KPI, Reactivation, Offer,Course


class LeadDistributionService:
    """Lid taqsimlash xizmati"""
    
    @staticmethod
    def distribute_leads(leads):
        """Lidlarni kurs bo'yicha yoki teng taqsimlash"""
        from .tasks import send_new_lead_notification
        
        # Faqat mavjud va ishda bo'lgan sotuvchilarni olish
        active_sales = [sales for sales in User.objects.filter(role='sales', is_active_sales=True) 
                       if sales.is_available_for_leads]
        
        if not active_sales:
            return None
        
        # Lidlarni taqsimlash
        for lead in leads:
            # Eski assigned_sales ni saqlash (notification uchun)
            old_assigned_sales_id = lead.assigned_sales_id if lead.pk else None
            was_new_lead = not lead.pk  # Lid yangi ekanligini tekshirish
            
            assigned_sales = None
            
            # Agar lid kursga biriktirilgan bo'lsa, kurs bo'yicha taqsimlash
            if lead.interested_course:
                # Ushbu kursga biriktirilgan sotuvchilarni topish
                course_sales = [
                    sales for sales in active_sales 
                    if lead.interested_course in sales.assigned_courses.all()
                ]
                
                if course_sales:
                    # Kursga biriktirilgan sotuvchilar bor, ular orasida taqsimlash
                    sales_lead_counts = {}
                    for sales in course_sales:
                        sales_lead_counts[sales.id] = Lead.objects.filter(
                            assigned_sales=sales,
                            status__in=['new', 'contacted', 'interested', 'trial_registered']
                        ).count()
                    
                    if sales_lead_counts:
                        min_sales_id = min(sales_lead_counts.items(), key=lambda x: x[1])[0]
                        assigned_sales = User.objects.get(id=min_sales_id)
            
            # Agar kursga biriktirilgan sotuvchi topilmasa yoki kurs belgilanmagan bo'lsa
            # Oddiy teng taqsimlash
            if not assigned_sales:
                sales_lead_counts = {}
                for sales in active_sales:
                    sales_lead_counts[sales.id] = Lead.objects.filter(
                        assigned_sales=sales,
                        status__in=['new', 'contacted', 'interested', 'trial_registered']
                    ).count()
                
                if not sales_lead_counts:
                    # Agar barcha sotuvchilar ishda bo'lmasa, eng kam lidga ega bo'lganiga berish
                    all_sales = User.objects.filter(role='sales', is_active_sales=True)
                    if all_sales:
                        assigned_sales = min(all_sales, key=lambda s: Lead.objects.filter(
                            assigned_sales=s,
                            status__in=['new', 'contacted', 'interested', 'trial_registered']
                        ).count())
                else:
                    min_sales_id = min(sales_lead_counts.items(), key=lambda x: x[1])[0]
                    assigned_sales = User.objects.get(id=min_sales_id)
            
            # Lidni biriktirish va saqlash
            if assigned_sales:
                lead.assigned_sales = assigned_sales
                lead.save()
                
                # Notification yuborish
                if was_new_lead or (not old_assigned_sales_id or old_assigned_sales_id != assigned_sales.id):
                    send_new_lead_notification.delay(lead.id)
        
        return len(active_sales)


class FollowUpService:
    """Follow-up xizmatlari"""
    
    @staticmethod
    def calculate_work_hours_due_date(sales, base_time, delay):
        """
        Follow-up vaqtini ish vaqtlariga moslashtirish
        Ruxsat so'rovlarini ham inobatga oladi
        MUHIM: Agar hisoblangan vaqt o'tgan bo'lsa, keyingi ish vaqtiga o'tkazadi
        
        Args:
            sales: User model instance (sotuvchi)
            base_time: datetime - boshlang'ich vaqt
            delay: timedelta - kechikish (masalan, timedelta(hours=24))
        
        Returns:
            datetime - ish vaqtiga moslashtirilgan follow-up vaqti (hech qachon o'tmagan bo'lmaydi)
        """
        # Hozirgi vaqt
        now = timezone.now()
        
        if not sales or not sales.is_active_sales:
            # Agar sotuvchi yo'q yoki faol emas bo'lsa, oddiy hisoblash
            calculated = base_time + delay
            # Agar o'tgan bo'lsa, hozirgi vaqtga o'tkazish
            return max(calculated, now)
        
        # Agar ish vaqtlari belgilanmagan bo'lsa, oddiy hisoblash
        if not sales.work_start_time or not sales.work_end_time:
            calculated = base_time + delay
            # Agar o'tgan bo'lsa, hozirgi vaqtga o'tkazish
            return max(calculated, now)
        
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
        
        # Agar hisoblangan vaqt o'tgan bo'lsa, hozirgi vaqtdan boshlash
        if calculated_time < now:
            # Agar delay juda qisqa bo'lsa (masalan, 15 daqiqa), hozirgi vaqtdan boshlash
            calculated_time = now + delay
        
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
        
        # Agar ish vaqti ichida va ruxsat olmagan bo'lsa va o'tmagan bo'lsa
        if is_work_day and is_work_hours and not is_on_leave and calculated_time >= now:
            return calculated_time
        
        # Agar ish vaqti tashqarisida yoki ruxsat olgan bo'lsa yoki o'tgan bo'lsa, keyingi ish kunini topish
        # Hozirgi kundan boshlab keyingi ish kunini topish
        max_days_to_check = 30  # 1 oy tekshirish (ruxsatlar uzoq bo'lishi mumkin)
        
        # Hozirgi kundan boshlash (o'tgan vaqtlar uchun)
        start_date = max(calculated_date, now.date())
        
        for day_offset in range(max_days_to_check):
            check_date = start_date + timedelta(days=day_offset)
            check_weekday = check_date.weekday()
            
            # Agar bu ish kuni bo'lsa
            if work_days.get(check_weekday, False):
                # Bu kunning ish vaqti boshlanishini yaratish
                work_start_datetime = timezone.make_aware(
                    timezone.datetime.combine(check_date, sales.work_start_time)
                )
                
                # Agar ruxsat olmagan bo'lsa va o'tmagan bo'lsa
                if not is_on_leave_at_time(work_start_datetime) and work_start_datetime >= now:
                    # Agar bu bugun bo'lsa va hozirgi vaqt ish vaqti ichida bo'lsa
                    if check_date == now.date():
                        current_time = now.time()
                        if sales.work_start_time <= current_time <= sales.work_end_time:
                            # Hozirgi vaqtdan keyin eng yaqin vaqtni qaytarish
                            # Agar delay juda qisqa bo'lsa, hozirgi vaqtga qo'shish
                            if delay.total_seconds() < 3600:  # 1 soatdan kam
                                return max(now + delay, now)
                            else:
                                # Keyingi ish vaqtiga o'tkazish
                                continue
                        elif current_time < sales.work_start_time:
                            # Ish vaqti boshlanishiga o'tkazish
                            return work_start_datetime
                        else:
                            # Ish vaqti tugagan, keyingi kunga o'tkazish
                            continue
                    
                    # Keyingi ish kunining boshlanish vaqtini qaytarish
                    return work_start_datetime
        
        # Agar ish kuni topilmasa, hozirgi vaqtga delay qo'shish
        return max(now + delay, now)
    
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
        
        return queryset.order_by('due_date').distinct()
    
    @staticmethod
    def get_overdue_followups(sales=None, grace_period_hours=2):
        """
        Overdue follow-uplarni olish (grace period bilan)
        
        Args:
            sales: User instance yoki None (barcha sotuvchilar uchun)
            grace_period_hours: Grace period (soat). Default: 2 soat
                              Follow-up due_date o'tgandan keyin ham 
                              grace period davomida overdue hisoblanmaydi
        """
        now = timezone.now()
        grace_threshold = now - timedelta(hours=grace_period_hours)
        
        queryset = FollowUp.objects.select_related(
            'lead', 'sales', 'lead__assigned_sales', 'lead__interested_course'
        ).filter(
            due_date__lt=grace_threshold,  # Grace period o'tgandan keyin overdue
            completed=False
        )
        
        if sales:
            queryset = queryset.filter(sales=sales)
        
        return queryset.order_by('due_date')
    
    @staticmethod
    def check_sales_blocked(sales):
        """
        Sotuvchi bloklanganligini tekshirish (dinamik threshold)
        
        Threshold dinamik: umumiy follow-up yukining 20% dan ko'p bo'lsa
        yoki minimum 8 ta overdue bo'lsa
        """
        overdue_count = FollowUpService.get_overdue_followups(sales).count()
        
        # Sotuvchining umumiy follow-up yukini hisoblash
        total_active_followups = FollowUp.objects.filter(
            sales=sales,
            completed=False
        ).count()
        
        # Threshold dinamik: umumiy yukning 20% dan ko'p bo'lsa yoki minimum 8 ta
        dynamic_threshold = max(8, int(total_active_followups * 0.2))
        
        return overdue_count >= dynamic_threshold
    
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
    
    @staticmethod
    def get_sales_overdue_summary(sales):
        """
        Sotuvchi uchun overdue xulosa (prioritet bo'yicha)
        
        Returns:
            dict: {
                'total': int,
                'by_urgency': {
                    'critical': int,  # 24+ soat overdue
                    'high': int,     # 6-24 soat overdue
                    'medium': int,   # 1-6 soat overdue
                    'low': int,      # Grace period ichida (1 soatdan kam)
                },
                'is_blocked': bool,
                'threshold': int,    # Dinamik threshold
            }
        """
        overdue = FollowUpService.get_overdue_followups(sales)
        now = timezone.now()
        
        # Grace period threshold (1 soat)
        grace_threshold = now - timedelta(hours=1)
        
        summary = {
            'total': overdue.count(),
            'by_urgency': {
                'critical': overdue.filter(
                    due_date__lt=now - timedelta(hours=24)
                ).count(),
                'high': overdue.filter(
                    due_date__gte=now - timedelta(hours=24),
                    due_date__lt=now - timedelta(hours=6)
                ).count(),
                'medium': overdue.filter(
                    due_date__gte=now - timedelta(hours=6),
                    due_date__lt=grace_threshold
                ).count(),
                'low': overdue.filter(
                    due_date__gte=grace_threshold
                ).count(),
            },
            'is_blocked': FollowUpService.check_sales_blocked(sales),
        }
        
        # Dinamik threshold'ni hisoblash
        total_active_followups = FollowUp.objects.filter(
            sales=sales,
            completed=False
        ).count()
        summary['threshold'] = max(8, int(total_active_followups * 0.2))
        
        return summary


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
        
        # Response time (o'rtacha) - lead yaratilgan vaqt va birinchi aloqa (contacted/interested) orasidagi vaqt
        response_times = []
        leads = Lead.objects.filter(assigned_sales=sales, created_at__date=date)
        for lead in leads:
            # Birinchi aloqa vaqtini topish (status contacted yoki interested bo'lgan vaqt)
            # Lead history yoki updated_at orqali
            if lead.status in ['contacted', 'interested']:
                # Agar lead shu kunda contacted yoki interested bo'lgan bo'lsa
                if lead.updated_at.date() == date:
                    response_time = (lead.updated_at - lead.created_at).total_seconds() / 60
                    # Faqat ijobiy response time (kelajakdagi vaqtlar emas)
                    if response_time >= 0:
                        response_times.append(response_time)
            else:
                # Agar hali contacted bo'lmagan bo'lsa, birinchi follow-up vaqtini olish
                first_followup = FollowUp.objects.filter(lead=lead).order_by('due_date').first()
                if first_followup:
                    response_time = (first_followup.due_date - lead.created_at).total_seconds() / 60
                    if response_time >= 0:
                        response_times.append(response_time)
        
        response_time_minutes = sum(response_times) / len(response_times) if response_times else 0
        
        # Overdue soni (faqat shu kundagi overdue'lar, lekin umumiy overdue soni)
        overdue_count = FollowUpService.get_overdue_followups(sales).count()
        
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
    def get_sales_ranking(sales, period='month', metric='conversion_rate'):
        """
        Sotuvchi reytingini hisoblash
        
        Args:
            sales: Sotuvchi
            period: 'day', 'week', 'month'
            metric: 'conversion_rate', 'daily_contacts', 'trials_to_sales', 'followup_completion_rate'
        
        Returns:
            dict: {
                'rank': int,
                'total_sales': int,
                'position': str,  # 'top', 'middle', 'bottom'
                'value': float,
                'average': float,
                'best': float,
                'worst': float
            }
        """
        from datetime import datetime, timedelta
        from django.db.models import Avg, Max, Min
        
        today = timezone.now().date()
        
        # Period bo'yicha sana oralig'ini aniqlash
        if period == 'day':
            start_date = today
            end_date = today
        elif period == 'week':
            start_date = today - timedelta(days=7)
            end_date = today
        elif period == 'month':
            start_date = datetime(today.year, today.month, 1).date()
            end_date = today
        else:
            start_date = today - timedelta(days=30)
            end_date = today
        
        # Barcha faol sotuvchilar
        all_sales = User.objects.filter(role='sales', is_active_sales=True)
        
        # Har bir sotuvchi uchun ko'rsatkichni hisoblash
        sales_metrics = []
        for s in all_sales:
            if period == 'day':
                kpi = KPI.objects.filter(sales=s, date=start_date).first()
                if not kpi:
                    kpi = KPIService.calculate_daily_kpi(s, start_date)
            else:
                # Period uchun o'rtacha yoki yig'indi
                kpis = KPI.objects.filter(sales=s, date__gte=start_date, date__lte=end_date)
                if not kpis.exists():
                    # Agar KPI'lar yo'q bo'lsa, hisoblaymiz
                    current_date = start_date
                    while current_date <= end_date:
                        KPIService.calculate_daily_kpi(s, current_date)
                        current_date += timedelta(days=1)
                    kpis = KPI.objects.filter(sales=s, date__gte=start_date, date__lte=end_date)
                
                if metric == 'conversion_rate':
                    value = kpis.aggregate(avg=Avg('conversion_rate'))['avg'] or 0
                elif metric == 'daily_contacts':
                    value = kpis.aggregate(avg=Avg('daily_contacts'))['avg'] or 0
                elif metric == 'trials_to_sales':
                    value = kpis.aggregate(avg=Avg('trials_to_sales'))['avg'] or 0
                elif metric == 'followup_completion_rate':
                    value = kpis.aggregate(avg=Avg('followup_completion_rate'))['avg'] or 0
                else:
                    value = 0
                
                sales_metrics.append({'sales': s, 'value': value})
                continue
            
            # Kunlik KPI uchun
            if metric == 'conversion_rate':
                value = kpi.conversion_rate
            elif metric == 'daily_contacts':
                value = kpi.daily_contacts
            elif metric == 'trials_to_sales':
                value = kpi.trials_to_sales
            elif metric == 'followup_completion_rate':
                value = kpi.followup_completion_rate
            else:
                value = 0
            
            sales_metrics.append({'sales': s, 'value': value})
        
        # Qiymat bo'yicha tartiblash (tushuvchi tartibda)
        sales_metrics.sort(key=lambda x: x['value'], reverse=True)
        
        # Sotuvchi o'rni
        rank = 1
        current_sales_value = None
        for idx, item in enumerate(sales_metrics):
            if item['sales'].id == sales.id:
                rank = idx + 1
                current_sales_value = item['value']
                break
        
        # O'rtacha, eng yaxshi, eng yomon
        if sales_metrics:
            values = [item['value'] for item in sales_metrics]
            average = sum(values) / len(values) if values else 0
            best = max(values) if values else 0
            worst = min(values) if values else 0
        else:
            average = best = worst = 0
        
        # Position
        if rank <= len(sales_metrics) * 0.33:
            position = 'top'
        elif rank <= len(sales_metrics) * 0.67:
            position = 'middle'
        else:
            position = 'bottom'
        
        return {
            'rank': rank,
            'total_sales': len(sales_metrics),
            'position': position,
            'value': current_sales_value or 0,
            'average': average,
            'best': best,
            'worst': worst
        }
    
    @staticmethod
    def get_trend_comparison(sales, days=7, metric='daily_contacts'):
        """
        O'sish/pasayish ko'rsatkichlari
        
        Args:
            sales: Sotuvchi
            days: Necha kunlik taqqoslash
            metric: Ko'rsatkich nomi
        
        Returns:
            dict: {
                'current': float,
                'previous': float,
                'change': float,  # foizda o'zgarish
                'trend': str,  # 'up', 'down', 'stable'
            }
        """
        from datetime import timedelta
        
        today = timezone.now().date()
        previous_date = today - timedelta(days=days)
        
        # Joriy kunlik KPI
        current_kpi = KPI.objects.filter(sales=sales, date=today).first()
        if not current_kpi:
            current_kpi = KPIService.calculate_daily_kpi(sales, today)
        
        # Oldingi kunlik KPI
        previous_kpi = KPI.objects.filter(sales=sales, date=previous_date).first()
        if not previous_kpi:
            previous_kpi = KPIService.calculate_daily_kpi(sales, previous_date)
        
        # Ko'rsatkichlarni olish
        if metric == 'daily_contacts':
            current_value = current_kpi.daily_contacts
            previous_value = previous_kpi.daily_contacts
        elif metric == 'conversion_rate':
            current_value = current_kpi.conversion_rate
            previous_value = previous_kpi.conversion_rate
        elif metric == 'trials_to_sales':
            current_value = current_kpi.trials_to_sales
            previous_value = previous_kpi.trials_to_sales
        elif metric == 'followup_completion_rate':
            current_value = current_kpi.followup_completion_rate
            previous_value = previous_kpi.followup_completion_rate
        else:
            current_value = previous_value = 0
        
        # O'zgarish
        if previous_value > 0:
            change = ((current_value - previous_value) / previous_value) * 100
        elif current_value > 0:
            change = 100
        else:
            change = 0
        
        # Trend
        if abs(change) < 5:
            trend = 'stable'
        elif change > 0:
            trend = 'up'
        else:
            trend = 'down'
        
        return {
            'current': current_value,
            'previous': previous_value,
            'change': change,
            'trend': trend
        }
    
    @staticmethod
    def get_comparison_data(sales, period='month'):
        """
        Boshqa sotuvchilar bilan taqqoslash
        
        Args:
            sales: Sotuvchi
            period: 'day', 'week', 'month'
        
        Returns:
            dict: {
                'sales_value': dict,  # Sotuvchi ko'rsatkichlari
                'average': dict,  # O'rtacha ko'rsatkichlar
                'best': dict,  # Eng yaxshi ko'rsatkichlar
                'worst': dict,  # Eng yomon ko'rsatkichlar
            }
        """
        from datetime import datetime, timedelta
        from django.db.models import Avg, Max, Min
        
        today = timezone.now().date()
        
        # Period bo'yicha sana oralig'ini aniqlash
        if period == 'day':
            start_date = today
            end_date = today
        elif period == 'week':
            start_date = today - timedelta(days=7)
            end_date = today
        elif period == 'month':
            start_date = datetime(today.year, today.month, 1).date()
            end_date = today
        else:
            start_date = today - timedelta(days=30)
            end_date = today
        
        # Barcha faol sotuvchilar
        all_sales = User.objects.filter(role='sales', is_active_sales=True)
        
        # Sotuvchi KPI'lari
        if period == 'day':
            sales_kpi = KPI.objects.filter(sales=sales, date=start_date).first()
            if not sales_kpi:
                sales_kpi = KPIService.calculate_daily_kpi(sales, start_date)
        else:
            sales_kpis = KPI.objects.filter(sales=sales, date__gte=start_date, date__lte=end_date)
            if not sales_kpis.exists():
                current_date = start_date
                while current_date <= end_date:
                    KPIService.calculate_daily_kpi(sales, current_date)
                    current_date += timedelta(days=1)
                sales_kpis = KPI.objects.filter(sales=sales, date__gte=start_date, date__lte=end_date)
            
            sales_kpi = {
                'daily_contacts': sales_kpis.aggregate(avg=Avg('daily_contacts'))['avg'] or 0,
                'conversion_rate': sales_kpis.aggregate(avg=Avg('conversion_rate'))['avg'] or 0,
                'trials_to_sales': sales_kpis.aggregate(avg=Avg('trials_to_sales'))['avg'] or 0,
                'followup_completion_rate': sales_kpis.aggregate(avg=Avg('followup_completion_rate'))['avg'] or 0,
            }
        
        # Barcha sotuvchilar uchun KPI'larni olish
        all_kpis = []
        for s in all_sales:
            if period == 'day':
                kpi = KPI.objects.filter(sales=s, date=start_date).first()
                if not kpi:
                    kpi = KPIService.calculate_daily_kpi(s, start_date)
                all_kpis.append(kpi)
            else:
                kpis = KPI.objects.filter(sales=s, date__gte=start_date, date__lte=end_date)
                if not kpis.exists():
                    current_date = start_date
                    while current_date <= end_date:
                        KPIService.calculate_daily_kpi(s, current_date)
                        current_date += timedelta(days=1)
                    kpis = KPI.objects.filter(sales=s, date__gte=start_date, date__lte=end_date)
                all_kpis.append(kpis)
        
        # O'rtacha, eng yaxshi, eng yomon
        if period == 'day':
            average = {
                'daily_contacts': sum(kpi.daily_contacts for kpi in all_kpis) / len(all_kpis) if all_kpis else 0,
                'conversion_rate': sum(kpi.conversion_rate for kpi in all_kpis) / len(all_kpis) if all_kpis else 0,
                'trials_to_sales': sum(kpi.trials_to_sales for kpi in all_kpis) / len(all_kpis) if all_kpis else 0,
                'followup_completion_rate': sum(kpi.followup_completion_rate for kpi in all_kpis) / len(all_kpis) if all_kpis else 0,
            }
            best = {
                'daily_contacts': max((kpi.daily_contacts for kpi in all_kpis), default=0),
                'conversion_rate': max((kpi.conversion_rate for kpi in all_kpis), default=0),
                'trials_to_sales': max((kpi.trials_to_sales for kpi in all_kpis), default=0),
                'followup_completion_rate': max((kpi.followup_completion_rate for kpi in all_kpis), default=0),
            }
            worst = {
                'daily_contacts': min((kpi.daily_contacts for kpi in all_kpis), default=0),
                'conversion_rate': min((kpi.conversion_rate for kpi in all_kpis), default=0),
                'trials_to_sales': min((kpi.trials_to_sales for kpi in all_kpis), default=0),
                'followup_completion_rate': min((kpi.followup_completion_rate for kpi in all_kpis), default=0),
            }
        else:
            # Period uchun o'rtacha
            all_contacts = []
            all_conversions = []
            all_trials = []
            all_completions = []
            
            for kpis in all_kpis:
                if hasattr(kpis, 'aggregate'):
                    all_contacts.append(kpis.aggregate(avg=Avg('daily_contacts'))['avg'] or 0)
                    all_conversions.append(kpis.aggregate(avg=Avg('conversion_rate'))['avg'] or 0)
                    all_trials.append(kpis.aggregate(avg=Avg('trials_to_sales'))['avg'] or 0)
                    all_completions.append(kpis.aggregate(avg=Avg('followup_completion_rate'))['avg'] or 0)
            
            average = {
                'daily_contacts': sum(all_contacts) / len(all_contacts) if all_contacts else 0,
                'conversion_rate': sum(all_conversions) / len(all_conversions) if all_conversions else 0,
                'trials_to_sales': sum(all_trials) / len(all_trials) if all_trials else 0,
                'followup_completion_rate': sum(all_completions) / len(all_completions) if all_completions else 0,
            }
            best = {
                'daily_contacts': max(all_contacts) if all_contacts else 0,
                'conversion_rate': max(all_conversions) if all_conversions else 0,
                'trials_to_sales': max(all_trials) if all_trials else 0,
                'followup_completion_rate': max(all_completions) if all_completions else 0,
            }
            worst = {
                'daily_contacts': min(all_contacts) if all_contacts else 0,
                'conversion_rate': min(all_conversions) if all_conversions else 0,
                'trials_to_sales': min(all_trials) if all_trials else 0,
                'followup_completion_rate': min(all_completions) if all_completions else 0,
            }
        
        # Sotuvchi ko'rsatkichlari
        if period == 'day':
            sales_value = {
                'daily_contacts': sales_kpi.daily_contacts,
                'conversion_rate': sales_kpi.conversion_rate,
                'trials_to_sales': sales_kpi.trials_to_sales,
                'followup_completion_rate': sales_kpi.followup_completion_rate,
            }
        else:
            sales_value = sales_kpi
        
        return {
            'sales_value': sales_value,
            'average': average,
            'best': best,
            'worst': worst
        }
    
    @staticmethod
    def get_weekly_kpi_summary(sales, week_start_date):
        """
        Haftalik KPI xulosa
        
        Args:
            sales: Sotuvchi
            week_start_date: Hafta boshlanish sanasi
        
        Returns:
            dict: Haftalik yig'indilar va o'rtachalar
        """
        from datetime import timedelta
        
        week_end_date = week_start_date + timedelta(days=6)
        
        kpis = KPI.objects.filter(
            sales=sales,
            date__gte=week_start_date,
            date__lte=week_end_date
        )
        
        # Agar KPI'lar yo'q bo'lsa, hisoblaymiz
        if not kpis.exists():
            current_date = week_start_date
            while current_date <= week_end_date:
                KPIService.calculate_daily_kpi(sales, current_date)
                current_date += timedelta(days=1)
            kpis = KPI.objects.filter(
                sales=sales,
                date__gte=week_start_date,
                date__lte=week_end_date
            )
        
        from django.db.models import Sum, Avg
        
        return {
            'total_contacts': kpis.aggregate(sum=Sum('daily_contacts'))['sum'] or 0,
            'total_followups': kpis.aggregate(sum=Sum('daily_followups'))['sum'] or 0,
            'avg_completion_rate': kpis.aggregate(avg=Avg('followup_completion_rate'))['avg'] or 0,
            'total_trials': kpis.aggregate(sum=Sum('trials_registered'))['sum'] or 0,
            'total_sales': kpis.aggregate(sum=Sum('trials_to_sales'))['sum'] or 0,
            'avg_conversion_rate': kpis.aggregate(avg=Avg('conversion_rate'))['avg'] or 0,
            'avg_response_time': kpis.aggregate(avg=Avg('response_time_minutes'))['avg'] or 0,
            'avg_overdue': kpis.aggregate(avg=Avg('overdue_count'))['avg'] or 0,
        }
    
    @staticmethod
    def get_accurate_conversion_rate(sales, start_date, end_date):
        """
        Aniq konversiya hisoblash
        
        Args:
            sales: Sotuvchi
            start_date: Boshlanish sanasi
            end_date: Tugash sanasi
        
        Returns:
            dict: {
                'total_assigned': int,
                'enrolled': int,
                'conversion_rate': float,
                'by_status': dict  # Status bo'yicha taqsimot
            }
        """
        # Berilgan lidlar
        total_assigned = Lead.objects.filter(
            assigned_sales=sales,
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        ).count()
        
        # Enrolled lidlar
        enrolled = Lead.objects.filter(
            assigned_sales=sales,
            status='enrolled',
            enrolled_at__date__gte=start_date,
            enrolled_at__date__lte=end_date
        ).count()
        
        # Status bo'yicha taqsimot
        from django.db.models import Count
        by_status = dict(
            Lead.objects.filter(
                assigned_sales=sales,
                created_at__date__gte=start_date,
                created_at__date__lte=end_date
            ).values('status').annotate(count=Count('id')).values_list('status', 'count')
        )
        
        conversion_rate = (enrolled / total_assigned * 100) if total_assigned > 0 else 0
        
        return {
            'total_assigned': total_assigned,
            'enrolled': enrolled,
            'conversion_rate': conversion_rate,
            'by_status': by_status
        }
    
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
            qs = qs.filter(models.Q(audience='all') | models.Q(audience=audience))

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
    def connect_to_sheet(spreadsheet_id, worksheet_name='Sheet1', max_retries=3):
        """Google Sheets'ga ulanish (retry bilan)"""
        import gspread
        import time
        
        for attempt in range(max_retries):
            try:
                credentials = GoogleSheetsService.get_credentials()
                client = gspread.authorize(credentials)
                spreadsheet = client.open_by_key(spreadsheet_id)
                worksheet = spreadsheet.worksheet(worksheet_name)
                return worksheet
            except Exception as e:
                error_str = str(e).lower()
                # Network xatolarini tekshirish
                if any(keyword in error_str for keyword in ['connection', 'network', 'timeout', 'getaddrinfo', 'failed to establish']):
                    if attempt < max_retries - 1:
                        wait_time = (attempt + 1) * 2  # Exponential backoff
                        print(f"Google Sheets'ga ulanishda network xatolik (qayta uriniladi {attempt + 1}/{max_retries}): {e}")
                        time.sleep(wait_time)
                        continue
                # Boshqa xatoliklar
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
                    
                    # Sheet nomidan kursni aniqlash (mapping)
                    from django.conf import settings
                    sheet_to_course_mapping = getattr(
                        settings, 
                        'GOOGLE_SHEETS_SHEET_COURSE_MAPPING', 
                        {
                            'Sheet1': 'Soft',
                            'Sheet2': 'Mobilografiya',
                            'Sheet3': 'Computer Science',
                        }
                    )
                    
                    # Sheet nomidan kursni topish
                    sheet_course_name = sheet_to_course_mapping.get(worksheet_name)
                    
                    # Interested course - avval sheet nomidan, keyin record'dan
                    interested_course = None
                    course_name = None
                    
                    # 1. Sheet nomidan kursni aniqlash
                    if sheet_course_name:
                        try:
                            interested_course = Course.objects.filter(
                                name__icontains=sheet_course_name
                            ).first()
                            if interested_course:
                                print(f"Sheet '{worksheet_name}' dan kurs topildi: {interested_course.name}")
                        except Exception as e:
                            print(f"Sheet nomidan kurs topishda xatolik: {e}")
                    
                    # 2. Agar sheet nomidan topilmasa, record'dan qidirish
                    if not interested_course:
                        # Barcha ustun nomlarini case-insensitive qilish
                        record_keys_lower = {str(k).lower().strip(): k for k in record.keys()}
                        
                        # Mumkin bo'lgan ustun nomlari
                        course_key_variants = [
                            interested_course_column.lower().strip(),
                            'course',
                            'kurs',
                            'interested_course',
                            'qiziqqan kurs'
                        ]
                        
                        # Ustunni topish
                        found_key = None
                        for variant in course_key_variants:
                            if variant in record_keys_lower:
                                found_key = record_keys_lower[variant]
                                break
                        
                        if found_key:
                            course_name = str(record.get(found_key, '')).strip()
                        else:
                            # Agar variantlardan topilmasa, default ustun nomidan qidirish
                            course_name = str(record.get(interested_course_column, '') or 
                                             record.get(interested_course_column.title(), '') or
                                             record.get(interested_course_column.upper(), '')).strip()
                        
                        if course_name:
                            try:
                                interested_course = Course.objects.filter(
                                    name__icontains=course_name
                                ).first()
                            except Exception as e:
                                print(f"Course biriktirishda xatolik (row {idx + 1}): {e}")
                                pass
                    
                    # Lead yaratish - notes'ga sheet nomini qo'shish
                    lead = Lead(
                        name=name,
                        phone=phone,
                        secondary_phone=secondary_phone if secondary_phone else None,
                        source=source,
                        interested_course=interested_course,
                        notes=(
                            f"Google Sheets'dan avtomatik import\n"
                            f"Sheet: {worksheet_name}\n"
                            f"Qator: {idx + 1}\n"
                            f"Qiziqish bildirgan kursi: {interested_course.name if interested_course else 'Belgilanmagan'}\n"
                            f"Manba: {source}"
                        )
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