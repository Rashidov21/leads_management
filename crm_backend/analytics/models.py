"""
Sales KPI and Analytics module: Track salesperson metrics and provide insights.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Count, Q
from leads.models import Lead


class SalesKPI(models.Model):
    """Daily KPI metrics per salesperson."""
    
    salesperson = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_kpis')
    date = models.DateField()
    
    # Contacts and follow-ups
    new_contacts = models.IntegerField(default=0)
    followups_completed = models.IntegerField(default=0)
    followups_overdue = models.IntegerField(default=0)
    
    # Trials
    trials_scheduled = models.IntegerField(default=0)
    trials_attended = models.IntegerField(default=0)
    trials_no_show = models.IntegerField(default=0)
    
    # Conversions
    sales_offers_made = models.IntegerField(default=0)
    enrollments = models.IntegerField(default=0)
    lost_leads = models.IntegerField(default=0)
    
    # Time metrics (in seconds)
    avg_response_time = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date']
        unique_together = ['salesperson', 'date']
        indexes = [
            models.Index(fields=['salesperson', 'date']),
            models.Index(fields=['date']),
        ]
    
    def __str__(self):
        return f"{self.salesperson.username} - {self.date}"
    
    @property
    def followup_completion_percent(self):
        """Calculate follow-up completion percentage."""
        total = self.followups_completed + self.followups_overdue
        if total == 0:
            return 0
        return int((self.followups_completed / total) * 100)
    
    @property
    def trial_to_conversion_percent(self):
        """Calculate trial-to-conversion rate."""
        total_trials = self.trials_attended + self.trials_no_show
        if total_trials == 0:
            return 0
        return int((self.enrollments / total_trials) * 100)
    
    @property
    def overall_conversion_percent(self):
        """Calculate overall conversion rate."""
        total_contacts = self.new_contacts
        if total_contacts == 0:
            return 0
        return int((self.enrollments / total_contacts) * 100)


class LeadMetrics(models.Model):
    """Aggregated lead metrics for analytics dashboard."""
    
    date = models.DateField(unique=True)
    
    # Lead acquisition
    new_leads_total = models.IntegerField(default=0)
    new_leads_instagram = models.IntegerField(default=0)
    new_leads_telegram = models.IntegerField(default=0)
    new_leads_whatsapp = models.IntegerField(default=0)
    new_leads_landing = models.IntegerField(default=0)
    new_leads_google_sheets = models.IntegerField(default=0)
    new_leads_excel = models.IntegerField(default=0)
    new_leads_csv = models.IntegerField(default=0)
    new_leads_call = models.IntegerField(default=0)
    
    # Lead status breakdown
    leads_contacted = models.IntegerField(default=0)
    leads_interested = models.IntegerField(default=0)
    leads_trial_scheduled = models.IntegerField(default=0)
    leads_trial_attended = models.IntegerField(default=0)
    leads_sales_offer = models.IntegerField(default=0)
    leads_enrolled = models.IntegerField(default=0)
    leads_lost = models.IntegerField(default=0)
    
    # Distribution metrics
    leads_assigned_total = models.IntegerField(default=0)
    leads_unassigned = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date']
        indexes = [
            models.Index(fields=['date']),
        ]
    
    def __str__(self):
        return f"Lead Metrics - {self.date}"
    
    @property
    def source_breakdown(self):
        """Return breakdown of leads by source."""
        return {
            'instagram': self.new_leads_instagram,
            'telegram': self.new_leads_telegram,
            'whatsapp': self.new_leads_whatsapp,
            'landing': self.new_leads_landing,
            'google_sheets': self.new_leads_google_sheets,
            'excel': self.new_leads_excel,
            'csv': self.new_leads_csv,
            'call': self.new_leads_call,
        }
    
    @property
    def conversion_rate_percent(self):
        """Calculate overall conversion rate."""
        if self.new_leads_total == 0:
            return 0
        return int((self.leads_enrolled / self.new_leads_total) * 100)
    
    @property
    def trial_to_conversion_percent(self):
        """Calculate trial-to-conversion rate."""
        total_trials = self.leads_trial_attended
        if total_trials == 0:
            return 0
        return int((self.leads_enrolled / total_trials) * 100)


class GroupAnalytics(models.Model):
    """Analytics for course groups: capacity usage, recommendations."""
    
    date = models.DateField()
    
    # Capacity metrics
    total_groups = models.IntegerField(default=0)
    full_groups = models.IntegerField(default=0)
    near_full_groups = models.IntegerField(default=0)  # 80%+ capacity
    empty_groups = models.IntegerField(default=0)
    
    # Room usage
    total_rooms = models.IntegerField(default=0)
    rooms_in_use = models.IntegerField(default=0)
    avg_room_occupancy = models.IntegerField(default=0)  # percentage
    
    # Trial students
    total_trial_students = models.IntegerField(default=0)
    expected_enrollments = models.IntegerField(default=0)
    
    # Recommendations
    new_groups_recommended = models.IntegerField(default=0)
    groups_to_combine = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date']
        unique_together = ['date']
        indexes = [
            models.Index(fields=['date']),
        ]
    
    def __str__(self):
        return f"Group Analytics - {self.date}"


class MarketingAnalytics(models.Model):
    """Marketing channel performance analytics."""
    
    date = models.DateField()
    channel = models.CharField(
        max_length=50,
        choices=[
            ('instagram', 'Instagram Ads'),
            ('telegram', 'Telegram Bot'),
            ('whatsapp', 'WhatsApp'),
            ('landing', 'Landing Page'),
            ('google_sheets', 'Google Sheets'),
            ('call', 'Call Tracking'),
        ]
    )
    
    # Cost and lead metrics
    impressions = models.IntegerField(default=0)
    clicks = models.IntegerField(default=0)
    leads_generated = models.IntegerField(default=0)
    cost_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # KPIs
    ctr = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Click-through rate %")
    cpl = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Cost per lead")
    cpa = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Cost per acquisition")
    enrollments_from_channel = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date']
        unique_together = ['date', 'channel']
        indexes = [
            models.Index(fields=['date', 'channel']),
        ]
    
    def __str__(self):
        return f"{self.get_channel_display()} - {self.date}"
