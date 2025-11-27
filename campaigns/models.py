"""
Models for SMS campaigns.
"""
from django.db import models
from leads.models import Lead, Seller
from django.utils import timezone


class SMSCampaign(models.Model):
    """Represents an SMS campaign for future implementation."""
    STATUS_CHOICES = [
        ('draft', 'Qoralama'),
        ('scheduled', 'Rejalashtirilgan'),
        ('running', 'Ishlamoqda'),
        ('completed', 'Tugallangan'),
        ('cancelled', 'Bekor qilingan'),
    ]
    
    name = models.CharField(max_length=255)
    message = models.TextField(help_text="SMS xabar matni")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Targeting
    target_sellers = models.ManyToManyField(Seller, blank=True, related_name='sms_campaigns')
    target_lead_status = models.CharField(
        max_length=20,
        choices=Lead.STATUS_CHOICES,
        blank=True,
        help_text="Ushbu holatdagi lidlarni nishonga oling"
    )
    
    # Scheduling
    scheduled_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Statistics
    total_recipients = models.IntegerField(default=0)
    sent_count = models.IntegerField(default=0)
    failed_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "SMS Kampaniyasi"
        verbose_name_plural = "SMS Kampaniyalari"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"


class SMSCampaignLog(models.Model):
    """Logs individual SMS sends for a campaign."""
    campaign = models.ForeignKey(SMSCampaign, on_delete=models.CASCADE, related_name='logs')
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='sms_logs')
    phone_number = models.CharField(max_length=20)
    status = models.CharField(max_length=20, default='pending')  # pending, sent, failed
    error_message = models.TextField(blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "SMS Kampaniya Jurnali"
        verbose_name_plural = "SMS Kampaniya Jurnallari"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['campaign', 'status']),
        ]

    def __str__(self):
        return f"{self.campaign.name} - {self.lead.name} ({self.status})"

