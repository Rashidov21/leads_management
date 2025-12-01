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
    
    @property
    def is_available_for_leads(self):
        """Lidlar uchun mavjudligini tekshirish"""
        if not self.is_active_sales:
            return False
        if self.is_on_leave:
            return False
        if self.is_absent:
            # Vaqt oralig'ini tekshirish
            now = timezone.now()
            if self.absent_from and self.absent_until:
                if self.absent_from <= now <= self.absent_until:
                    return False
            elif self.is_absent:
                return False
        return True
    
    @property
    def is_working_now(self):
        """Hozir ishlayotganligini tekshirish"""
        if not self.is_active_sales:
            return False
        if self.is_on_leave:
            return False
        if self.is_absent:
            now = timezone.now()
            if self.absent_from and self.absent_until:
                if self.absent_from <= now <= self.absent_until:
                    return False
            elif self.is_absent:
                return False
        return True


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
        return self.capacity - self.current_students
    
    @property
    def is_full(self):
        return self.current_students >= self.capacity
    
    @property
    def occupancy_percentage(self):
        if self.capacity == 0:
            return 0
        return (self.current_students / self.capacity) * 100


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
    
    def __str__(self):
        return f"{self.name} - {self.phone}"
    
    def save(self, *args, **kwargs):
        if self.status == 'lost' and not self.lost_at:
            self.lost_at = timezone.now()
        if self.status == 'enrolled' and not self.enrolled_at:
            self.enrolled_at = timezone.now()
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
    reason = models.TextField(help_text="Ruxsat sababi")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_leaves')
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, help_text="Rad etish sababi")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Ruxsat: {self.sales.username} - {self.start_date} to {self.end_date}"
    
    def approve(self, approved_by_user):
        """Ruxsatni tasdiqlash"""
        self.status = 'approved'
        self.approved_by = approved_by_user
        self.approved_at = timezone.now()
        self.save()
        # Sotuvchini ishdan ruxsat holatiga o'tkazish
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

