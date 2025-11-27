"""
Models for the leads app.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Seller(models.Model):
    """Represents a seller who manages leads."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='seller_profile')
    telegram_id = models.BigIntegerField(unique=True, null=True, blank=True, help_text="Telegram foydalanuvchi ID")
    phone_number = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Sotuvchi"
        verbose_name_plural = "Sotuvchilar"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} (ID: {self.telegram_id})"


class Lead(models.Model):
    """Represents a lead from Google Sheets or manual entry."""
    STATUS_CHOICES = [
        ('new', 'Yangi'),
        ('contacted', 'Bog\'langan'),
        ('qualified', 'Sifatli'),
        ('converted', 'Aylantirilgan'),
        ('lost', 'Yo\'qotilgan'),
    ]

    # Basic information
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    company = models.CharField(max_length=255, blank=True)
    
    # Assignment and status
    seller = models.ForeignKey(Seller, on_delete=models.SET_NULL, null=True, blank=True, related_name='leads')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    
    # Additional data
    notes = models.TextField(blank=True)
    source = models.CharField(max_length=100, default='google_sheets', help_text="Lid manbasi")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    contacted_at = models.DateTimeField(null=True, blank=True)
    converted_at = models.DateTimeField(null=True, blank=True)
    
    # Google Sheets sync
    sheets_row_id = models.IntegerField(null=True, blank=True, unique=True, help_text="Google Sheets dagi qator ID")
    last_synced_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Lid"
        verbose_name_plural = "Lidlar"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['seller', 'status']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.name} - {self.get_status_display()}"

    def mark_contacted(self):
        """Mark lead as contacted."""
        self.status = 'contacted'
        self.contacted_at = timezone.now()
        self.save()

    def mark_converted(self):
        """Mark lead as converted."""
        self.status = 'converted'
        self.converted_at = timezone.now()
        self.save()

