from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Lead(models.Model):
    """Model for storing lead information."""
    
    STATUS_CHOICES = [
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('interested', 'Interested'),
        ('trial_scheduled', 'Trial Scheduled'),
        ('trial_attended', 'Trial Attended'),
        ('trial_no_show', 'Trial No-show'),
        ('sales_offer', 'Sales Offer'),
        ('decision_pending', 'Decision Pending'),
        ('enrolled', 'Enrolled'),
        ('lost', 'Lost'),
        ('reactivation', 'Reactivation'),
    ]
    
    SOURCE_CHOICES = [
        ('instagram_ads', 'Instagram Ads'),
        ('telegram_bot', 'Telegram Bot'),
        ('whatsapp', 'WhatsApp'),
        ('landing_page', 'Landing Page'),
        ('google_sheets', 'Google Sheets'),
        ('excel_upload', 'Excel Upload'),
        ('csv_upload', 'CSV Upload'),
        ('call_tracking', 'Call Tracking'),
        ('manual', 'Manual Entry'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, unique=True)
    interested_course = models.CharField(max_length=255, null=True, blank=True)
    source = models.CharField(
        max_length=20,
        choices=SOURCE_CHOICES,
        default='manual'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new'
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_leads'
    )
    # Follow-up automation fields
    follow_up_plan = models.JSONField(default=dict, blank=True)
    last_contacted_at = models.DateTimeField(null=True, blank=True)
    next_followup_at = models.DateTimeField(null=True, blank=True)
    followup_count = models.IntegerField(default=0)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['phone']),
            models.Index(fields=['status']),
            models.Index(fields=['assigned_to']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.phone}"

    def set_status(self, new_status: str, by_user: User = None):
        """
        Change lead status and compute next follow-up/deadline according to rules.

        This implements the basic follow-up rules used elsewhere. More
        advanced scheduling (trials, snooze, notifications) is handled by
        Celery tasks and the reminders app.
        """
        self.status = new_status
        now = timezone.now()

        # Basic automation rules (can be extended)
        if new_status == 'new':
            # Contact within 5 minutes
            self.next_followup_at = now + timezone.timedelta(minutes=5)
        elif new_status == 'contacted':
            self.next_followup_at = now + timezone.timedelta(hours=24)
        elif new_status == 'interested':
            self.next_followup_at = now + timezone.timedelta(hours=48)
        elif new_status == 'trial_scheduled':
            # Expect trial scheduling system to set exact reminder
            self.next_followup_at = None
        elif new_status == 'trial_attended':
            # Sales offer shortly after trial
            self.next_followup_at = now + timezone.timedelta(minutes=3)
        elif new_status == 'decision_pending':
            self.next_followup_at = now + timezone.timedelta(days=3)
        elif new_status == 'lost':
            # schedule reactivation flows externally
            self.next_followup_at = None
        elif new_status == 'reactivation':
            self.next_followup_at = now + timezone.timedelta(days=7)

        # update last_contacted_at where appropriate
        if new_status in ('contacted', 'trial_attended'):
            self.last_contacted_at = now

        self.save()


class ImportLog(models.Model):
    """Model for tracking import operations."""
    
    IMPORT_TYPE_CHOICES = [
        ('google_sheets', 'Google Sheets'),
        ('excel', 'Excel'),
        ('csv', 'CSV'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    import_type = models.CharField(max_length=20, choices=IMPORT_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    total_records = models.IntegerField(default=0)
    imported_count = models.IntegerField(default=0)
    duplicate_count = models.IntegerField(default=0)
    error_count = models.IntegerField(default=0)
    
    error_details = models.JSONField(default=dict, blank=True)
    
    imported_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='import_logs'
    )
    
    file_name = models.CharField(max_length=255, blank=True, null=True)
    google_sheet_id = models.CharField(max_length=255, blank=True, null=True)
    
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['import_type']),
        ]
    
    def __str__(self):
        return f"{self.get_import_type_display()} - {self.started_at.strftime('%Y-%m-%d %H:%M')}"


class LeadReminder(models.Model):
    """Model for tracking reminders for new leads."""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('notified', 'Notified'),
        ('contacted', 'Contacted'),
        ('snoozed', 'Snoozed'),
    ]
    
    lead = models.OneToOneField(Lead, on_delete=models.CASCADE, related_name='reminder')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    created_at = models.DateTimeField(auto_now_add=True)
    contact_deadline = models.DateTimeField()
    last_reminder_at = models.DateTimeField(null=True, blank=True)
    contacted_at = models.DateTimeField(null=True, blank=True)
    
    reminder_count = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['contact_deadline']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['contact_deadline']),
        ]
    
    def __str__(self):
        return f"Reminder for {self.lead.name} - {self.status}"
