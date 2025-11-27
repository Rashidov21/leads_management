"""
Trial lessons module: Trial scheduling, reminders, and result tracking.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from leads.models import Lead
from scheduling.models import Group


class Trial(models.Model):
    """Trial lesson scheduling and result tracking."""
    
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('attended', 'Attended'),
        ('no_show', 'No-show'),
        ('cancelled', 'Cancelled'),
    ]
    
    RESULT_CHOICES = [
        ('pending', 'Pending'),
        ('sales_offer', 'Sales Offer Made'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='trials')
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True)
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    result = models.CharField(max_length=20, choices=RESULT_CHOICES, default='pending')
    
    # Trial execution tracking
    actual_attendance_time = models.DateTimeField(null=True, blank=True)
    trial_completed_at = models.DateTimeField(null=True, blank=True)
    
    # Follow-up after trial
    sales_offer_made_at = models.DateTimeField(null=True, blank=True)
    salesperson_notes = models.TextField(blank=True)
    
    # Reminders
    pre_trial_reminder_sent_at = models.DateTimeField(null=True, blank=True)
    post_trial_reminder_sent_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-scheduled_date', 'scheduled_time']
        indexes = [
            models.Index(fields=['lead']),
            models.Index(fields=['scheduled_date']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Trial {self.lead.name} - {self.scheduled_date} {self.scheduled_time}"
    
    @property
    def is_overdue(self):
        """Check if trial is overdue."""
        now = timezone.now()
        trial_datetime = timezone.make_aware(
            timezone.datetime.combine(self.scheduled_date, self.scheduled_time)
        )
        return now > trial_datetime and self.status == 'scheduled'
    
    @property
    def is_upcoming_today(self):
        """Check if trial is today."""
        return self.scheduled_date == timezone.now().date()
    
    @property
    def hours_until_trial(self):
        """Calculate hours until trial."""
        now = timezone.now()
        trial_datetime = timezone.make_aware(
            timezone.datetime.combine(self.scheduled_date, self.scheduled_time)
        )
        if trial_datetime > now:
            delta = trial_datetime - now
            return delta.total_seconds() / 3600
        return 0


class TrialReminder(models.Model):
    """Track trial reminders sent to salesperson."""
    
    trial = models.OneToOneField(Trial, on_delete=models.CASCADE, related_name='reminder')
    pre_trial_reminder_scheduled_at = models.DateTimeField()  # 2 hours before
    pre_trial_reminder_sent = models.BooleanField(default=False)
    post_trial_reminder_scheduled_at = models.DateTimeField()  # 3 minutes after trial
    post_trial_reminder_sent = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['pre_trial_reminder_scheduled_at']
        indexes = [
            models.Index(fields=['pre_trial_reminder_sent']),
            models.Index(fields=['post_trial_reminder_sent']),
        ]
    
    def __str__(self):
        return f"Reminder for {self.trial}"
