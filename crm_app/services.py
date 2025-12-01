from django.utils import timezone
from django.db import models
from datetime import timedelta
from .models import User, Lead, FollowUp, Group, TrialLesson, KPI, Reactivation


class LeadDistributionService:
    """Lid taqsimlash xizmati"""
    
    @staticmethod
    def distribute_leads(leads):
        """Lidlarni faol sotuvchilar orasida teng taqsimlash"""
        active_sales = User.objects.filter(role='sales', is_active_sales=True)
        
        if not active_sales.exists():
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
            # Eng kam lidga ega sotuvchini topish
            min_sales_id = min(sales_lead_counts.items(), key=lambda x: x[1])[0]
            lead.assigned_sales_id = min_sales_id
            lead.save()
            sales_lead_counts[min_sales_id] += 1
        
        return active_sales.count()


class FollowUpService:
    """Follow-up xizmatlari"""
    
    @staticmethod
    def get_today_followups(sales=None):
        """Bugungi follow-uplarni olish"""
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        
        queryset = FollowUp.objects.filter(
            due_date__gte=today_start,
            due_date__lt=today_end,
            completed=False
        )
        
        if sales:
            queryset = queryset.filter(sales=sales)
        
        return queryset.order_by('due_date')
    
    @staticmethod
    def get_overdue_followups(sales=None):
        """Overdue follow-uplarni olish"""
        queryset = FollowUp.objects.filter(
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
        
        return queryset.filter(current_students__lt=models.F('capacity'))
    
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
        """Kunlik KPI hisoblash"""
        from django.db.models import Count, Avg, Q
        
        # Kunlik aloqa
        daily_contacts = Lead.objects.filter(
            assigned_sales=sales,
            updated_at__date=date,
            status__in=['contacted', 'interested']
        ).count()
        
        # Kunlik follow-up
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
        
        # Konversiya
        total_trials = TrialLesson.objects.filter(
            lead__assigned_sales=sales,
            date=date
        ).count()
        conversion_rate = (trials_to_sales / total_trials * 100) if total_trials > 0 else 0
        
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


class ReactivationService:
    """Reaktivatsiya xizmati"""
    
    @staticmethod
    def check_and_reactivate():
        """Yo'qotilgan lidlarni reaktivatsiya qilish"""
        from django.db.models import F
        
        lost_leads = Lead.objects.filter(status='lost', lost_at__isnull=False)
        
        for lead in lost_leads:
            days_since_lost = (timezone.now().date() - lead.lost_at.date()).days
            
            # 7 kun
            if days_since_lost == 7:
                Reactivation.objects.get_or_create(
                    lead=lead,
                    reactivation_type='7_days',
                    defaults={'days_since_lost': 7}
                )
            
            # 14 kun
            elif days_since_lost == 14:
                Reactivation.objects.get_or_create(
                    lead=lead,
                    reactivation_type='14_days',
                    defaults={'days_since_lost': 14}
                )
            
            # 30 kun
            elif days_since_lost == 30:
                Reactivation.objects.get_or_create(
                    lead=lead,
                    reactivation_type='30_days',
                    defaults={'days_since_lost': 30}
                )

