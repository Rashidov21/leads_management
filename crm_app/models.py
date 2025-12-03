from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta


class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('sales_manager', 'Sales Manager'),
        ('sales', 'Sales'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='sales')
    phone = models.CharField(max_length=20, blank=True)
    telegram_chat_id = models.CharField(max_length=100, blank=True, null=True)
    is_active_sales = models.BooleanField(default=True)
    is_on_leave = models.BooleanField(default=False, help_text="Ishdan ruxsat olgan")
    is_absent = models.BooleanField(default=False, help_text="Manager tomonidan ishda emasligi belgilangan")
    absent_reason = models.TextField(blank=True, help_text="Ishda emaslik sababi")
    absent_from = models.DateTimeField(null=True, blank=True, help_text="Ishda emaslik boshlanish vaqti")
    absent_until = models.DateTimeField(null=True, blank=True, help_text="Ishda emaslik tugash vaqti")
    
    # Ish vaqtlari
    work_start_time = models.TimeField(null=True, blank=True, help_text="Ish boshlanish vaqti (masalan: 09:00)")
    work_end_time = models.TimeField(null=True, blank=True, help_text="Ish tugash vaqti (masalan: 18:00)")
    work_monday = models.BooleanField(default=True, help_text="Dushanba ish kuni")
    work_tuesday = models.BooleanField(default=True, help_text="Seshanba ish kuni")
    work_wednesday = models.BooleanField(default=True, help_text="Chorshanba ish kuni")
    work_thursday = models.BooleanField(default=True, help_text="Payshanba ish kuni")
    work_friday = models.BooleanField(default=True, help_text="Juma ish kuni")
    work_saturday = models.BooleanField(default=False, help_text="Shanba ish kuni")
    work_sunday = models.BooleanField(default=False, help_text="Yakshanba ish kuni")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    @property
    def is_admin(self):
        return self.role == 'admin'
    
    @property
    def is_sales_manager(self):
        return self.role == 'sales_manager'
    
    @property
    def is_sales(self):
        return self.role == 'sales'
    
    def is_working_at_time(self, check_time=None):
        """Belgilangan vaqtda ishlayotganligini tekshirish"""
        if not self.is_active_sales:
            return False
        
        if check_time is None:
            check_time = timezone.now()
        
        # Kunni tekshirish
        weekday = check_time.weekday()  # 0 = Monday, 6 = Sunday
        work_days = {
            0: self.work_monday,
            1: self.work_tuesday,
            2: self.work_wednesday,
            3: self.work_thursday,
            4: self.work_friday,
            5: self.work_saturday,
            6: self.work_sunday,
        }
        
        if not work_days.get(weekday, False):
            return False
        
        # Vaqtni tekshirish
        if self.work_start_time and self.work_end_time:
            current_time = check_time.time()
            if not (self.work_start_time <= current_time <= self.work_end_time):
                return False
        
        return True
    
    @property
    def is_available_for_leads(self):
        """Lidlar uchun mavjudligini tekshirish"""
        if not self.is_active_sales:
            return False
        
        now = timezone.now()
        
        # Ruxsat so'rovlarini tekshirish
        # Circular importdan qochish uchun bu yerda tekshiramiz
        try:
            from django.apps import apps
            LeaveRequest = apps.get_model('crm_app', 'LeaveRequest')
            active_leave = LeaveRequest.objects.filter(
                sales=self,
                status='approved',
                start_date__lte=now.date(),
                end_date__gte=now.date()
            ).first()
            
            if active_leave:
                # Agar soatlar belgilangan bo'lsa, ularni tekshirish
                if active_leave.start_time and active_leave.end_time:
                    current_time = now.time()
                    if active_leave.start_time <= current_time <= active_leave.end_time:
                        return False
                else:
                    # Butun kun ruxsat
                    return False
        except:
            # Agar model topilmasa, is_on_leave ni tekshiramiz
            if self.is_on_leave:
                return False
        
        # Manager tomonidan belgilangan ishda emaslik
        if self.is_absent:
            if self.absent_from and self.absent_until:
                if self.absent_from <= now <= self.absent_until:
                    return False
            elif self.is_absent:
                return False
        
        # Ish vaqtini tekshirish
        return self.is_working_at_time(now)
    
    @property
    def is_working_now(self):
        """Hozir ishlayotganligini tekshirish"""
        return self.is_available_for_leads


class Course(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sales_script = models.TextField(help_text="Sotuv scripti va bonus eslatmalar")
    duration_minutes = models.IntegerField(help_text="Dars davomiyligi (daqiqa)")
    lessons_per_week = models.IntegerField(help_text="Haftasiga darslar soni")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name


class Room(models.Model):
    name = models.CharField(max_length=100)
    capacity = models.IntegerField()
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} (Sig'im: {self.capacity})"


class Group(models.Model):
    DAY_CHOICES = [
        ('odd', 'Toq kunlar'),
        ('even', 'Juft kunlar'),
        ('daily', 'Har kuni'),
    ]
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    days = models.CharField(max_length=10, choices=DAY_CHOICES)
    time = models.TimeField()
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True)
    capacity = models.IntegerField()
    current_students = models.IntegerField(default=0)
    trial_students = models.ManyToManyField('Lead', related_name='trial_groups', blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.course.name} - {self.name}"
    
    @property
    def available_spots(self):
        # Trial students ham hisobga olinadi
        total_students = self.current_students + self.trial_students.count()
        return max(0, self.capacity - total_students)
    
    @property
    def is_full(self):
        # Trial students ham hisobga olinadi
        total_students = self.current_students + self.trial_students.count()
        return total_students >= self.capacity
    
    @property
    def occupancy_percentage(self):
        if self.capacity == 0:
            return 0
        # Trial students ham hisobga olinadi
        total_students = self.current_students + self.trial_students.count()
        return (total_students / self.capacity) * 100
    
    @property
    def total_students_with_trials(self):
        """Jami o'quvchilar (enrolled + trial)"""
        return self.current_students + self.trial_students.count()


class Lead(models.Model):
    STATUS_CHOICES = [
        ('new', 'Yangi'),
        ('contacted', 'Aloqa qilindi'),
        ('interested', 'Qiziqmoqda'),
        ('trial_registered', 'Sinovga yozildi'),
        ('trial_attended', 'Sinovga keldi'),
        ('trial_not_attended', 'Sinovga kelmadi'),
        ('offer_sent', 'Sotuv taklifi'),
        ('enrolled', 'Kursga yozildi'),
        ('lost', "Yo'qotilgan lid"),
        ('reactivation', 'Qayta aloqa lid'),
    ]
    
    SOURCE_CHOICES = [
        ('instagram', 'Instagram'),
        ('telegram', 'Telegram'),
        ('youtube', 'Youtube'),
        ('organic', 'Organic'),
        ('form', 'Forma'),
        ('excel', 'Excel'),
        ('google_sheets', 'Google Sheets'),
    ]
    
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    interested_course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='form')
    assigned_sales = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                      related_name='assigned_leads', limit_choices_to={'role': 'sales'})
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    lost_at = models.DateTimeField(null=True, blank=True)
    enrolled_at = models.DateTimeField(null=True, blank=True)
    enrolled_group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['status', 'assigned_sales'], name='lead_status_sales_idx'),
            models.Index(fields=['created_at'], name='lead_created_at_idx'),
            models.Index(fields=['phone'], name='lead_phone_idx'),
            models.Index(fields=['source'], name='lead_source_idx'),
            models.Index(fields=['assigned_sales', 'status'], name='lead_sales_status_idx'),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.phone}"
    
    def save(self, *args, **kwargs):
        # Eski statusni saqlash (signals uchun)
        old_status = None
        old_enrolled_group = None
        if self.pk:
            try:
                old_instance = Lead.objects.get(pk=self.pk)
                old_status = old_instance.status
                old_enrolled_group = old_instance.enrolled_group
            except Lead.DoesNotExist:
                pass
        
        if self.status == 'lost' and not self.lost_at:
            self.lost_at = timezone.now()
        
        if self.status == 'enrolled' and not self.enrolled_at:
            self.enrolled_at = timezone.now()
            
            # Agar enrolled_group o'zgarganda, eski guruhdan olib tashlash
            if old_enrolled_group and old_enrolled_group != self.enrolled_group:
                old_enrolled_group.current_students = max(0, old_enrolled_group.current_students - 1)
                old_enrolled_group.save()
            
            # Yangi guruhga qo'shish
            if self.enrolled_group:
                # Agar status 'enrolled' dan boshqa statusga o'zgarganda, guruhdan olib tashlash
                if old_status == 'enrolled' and self.status != 'enrolled':
                    if old_enrolled_group:
                        old_enrolled_group.current_students = max(0, old_enrolled_group.current_students - 1)
                        old_enrolled_group.save()
                # Agar yangi enrolled_group bo'lsa va oldin enrolled bo'lmagan bo'lsa
                elif old_status != 'enrolled' and self.enrolled_group:
                    self.enrolled_group.current_students += 1
                    self.enrolled_group.save()
                    # Trial students dan olib tashlash
                    self.enrolled_group.trial_students.remove(self)
        
        # Agar status enrolled dan boshqa statusga o'zgarganda
        if old_status == 'enrolled' and self.status != 'enrolled':
            if old_enrolled_group:
                old_enrolled_group.current_students = max(0, old_enrolled_group.current_students - 1)
                old_enrolled_group.save()
        
        super().save(*args, **kwargs)


class FollowUp(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='followups')
    sales = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followups')
    due_date = models.DateTimeField()
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    is_overdue = models.BooleanField(default=False)
    reminder_sent = models.BooleanField(default=False)  # Follow-up eslatmasi yuborilganligi
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['due_date']
        indexes = [
            models.Index(fields=['due_date', 'completed'], name='followup_due_completed_idx'),
            models.Index(fields=['sales', 'completed'], name='followup_sales_completed_idx'),
            models.Index(fields=['lead', 'completed'], name='followup_lead_completed_idx'),
            models.Index(fields=['is_overdue', 'completed'], name='followup_overdue_completed_idx'),
            models.Index(fields=['due_date'], name='followup_due_date_idx'),
        ]
    
    def __str__(self):
        return f"Follow-up: {self.lead.name} - {self.due_date}"
    
    def mark_completed(self):
        self.completed = True
        self.completed_at = timezone.now()
        self.save()


class TrialLesson(models.Model):
    RESULT_CHOICES = [
        ('attended', 'Keldi'),
        ('not_attended', 'Kelmadi'),
        ('offer_sent', 'Sotuv taklifi'),
        ('accepted', 'Qabul qildi'),
        ('rejected', 'Rad etdi'),
    ]
    
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='trials')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='trials')
    date = models.DateField()
    time = models.TimeField()
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True)
    result = models.CharField(max_length=20, choices=RESULT_CHOICES, blank=True)
    notes = models.TextField(blank=True)
    reminder_sent = models.BooleanField(default=False)  # Sinov oldi eslatmasi
    sales_reminder_sent = models.BooleanField(default=False)  # Sinovdan keyin sotuv eslatmasi
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['date', 'time'], name='trial_date_time_idx'),
            models.Index(fields=['lead', 'date'], name='trial_lead_date_idx'),
            models.Index(fields=['result'], name='trial_result_idx'),
            models.Index(fields=['date', 'result'], name='trial_date_result_idx'),
        ]
    
    def __str__(self):
        return f"Sinov: {self.lead.name} - {self.date}"


class LeaveRequest(models.Model):
    """Ishdan ruxsat so'rovlari"""
    STATUS_CHOICES = [
        ('pending', 'Kutilmoqda'),
        ('approved', 'Tasdiqlandi'),
        ('rejected', 'Rad etildi'),
    ]
    
    sales = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leave_requests')
    start_date = models.DateField()
    end_date = models.DateField()
    start_time = models.TimeField(null=True, blank=True, help_text="Ruxsat boshlanish vaqti (bo'sh bo'lsa butun kun)")
    end_time = models.TimeField(null=True, blank=True, help_text="Ruxsat tugash vaqti (bo'sh bo'lsa butun kun)")
    reason = models.TextField(help_text="Ruxsat sababi")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_leaves')
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, help_text="Rad etish sababi")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['sales', 'status'], name='leave_sales_status_idx'),
            models.Index(fields=['start_date', 'end_date'], name='leave_dates_idx'),
            models.Index(fields=['status', 'start_date'], name='leave_status_start_idx'),
        ]
    
    def __str__(self):
        return f"Ruxsat: {self.sales.username} - {self.start_date} to {self.end_date}"
    
    def approve(self, approved_by_user):
        """Ruxsatni tasdiqlash"""
        self.status = 'approved'
        self.approved_by = approved_by_user
        self.approved_at = timezone.now()
        self.save()
        # Agar butun kun ruxsat bo'lsa, sotuvchini ishdan ruxsat holatiga o'tkazish
        if not self.start_time and not self.end_time:
            self.sales.is_on_leave = True
            self.sales.save()
    
    def reject(self, rejected_by_user, reason=''):
        """Ruxsatni rad etish"""
        self.status = 'rejected'
        self.approved_by = rejected_by_user
        self.approved_at = timezone.now()
        self.rejection_reason = reason
        self.save()


class KPI(models.Model):
    sales = models.ForeignKey(User, on_delete=models.CASCADE, related_name='kpis')
    date = models.DateField()
    daily_contacts = models.IntegerField(default=0)
    daily_followups = models.IntegerField(default=0)
    followup_completion_rate = models.FloatField(default=0.0)
    trials_registered = models.IntegerField(default=0)
    trials_to_sales = models.IntegerField(default=0)
    conversion_rate = models.FloatField(default=0.0)
    response_time_minutes = models.FloatField(default=0.0)
    overdue_count = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ['sales', 'date']
        ordering = ['-date']
        indexes = [
            models.Index(fields=['sales', 'date'], name='kpi_sales_date_idx'),
            models.Index(fields=['date'], name='kpi_date_idx'),
        ]
    
    def __str__(self):
        return f"KPI: {self.sales.username} - {self.date}"


class Reactivation(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='reactivations')
    days_since_lost = models.IntegerField()
    reactivation_type = models.CharField(max_length=20, choices=[
        ('7_days', '7 kun'),
        ('14_days', '14 kun'),
        ('30_days', '30 kun'),
    ])
    sent_at = models.DateTimeField(auto_now_add=True)
    result = models.CharField(max_length=20, blank=True, choices=[
        ('contacted', 'Aloqa qilindi'),
        ('interested', 'Qiziqmoqda'),
        ('no_response', 'Javob yo\'q'),
    ])
    
    def __str__(self):
        return f"Reactivation: {self.lead.name} - {self.reactivation_type}"


class SalesMessage(models.Model):
    """Sotuvchilarga yuboriladigan xabarlar"""
    PRIORITY_CHOICES = [
        ('urgent', 'Shoshilinch'),
        ('high', 'Yuqori'),
        ('normal', 'Oddiy'),
        ('low', 'Past'),
    ]
    
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages', limit_choices_to={'role__in': ['admin', 'sales_manager']})
    recipients = models.ManyToManyField(User, related_name='received_messages', limit_choices_to={'role': 'sales'})
    subject = models.CharField(max_length=200, help_text="Xabar mavzusi")
    message = models.TextField(help_text="Xabar matni")
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='normal')
    telegram_sent = models.BooleanField(default=False, help_text="Telegram orqali yuborilganligi")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Xabar: {self.subject} - {self.created_at.strftime('%d.%m.%Y %H:%M')}"
    
    def get_priority_display_class(self):
        """Priority uchun CSS class"""
        classes = {
            'urgent': 'bg-red-100 text-red-800',
            'high': 'bg-orange-100 text-orange-800',
            'normal': 'bg-blue-100 text-blue-800',
            'low': 'bg-gray-100 text-gray-800',
        }
        return classes.get(self.priority, 'bg-gray-100 text-gray-800')


class SalesMessageRead(models.Model):
    """Xabarlarni o'qilganligini kuzatish"""
    message = models.ForeignKey(SalesMessage, on_delete=models.CASCADE, related_name='reads')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='read_messages')
    read_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['message', 'user']
    
    def __str__(self):
        return f"{self.user.username} - {self.message.subject}"

