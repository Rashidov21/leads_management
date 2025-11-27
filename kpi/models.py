"""
Models for KPI tracking and bonus/penalty rules.
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from leads.models import Seller, Lead
from django.utils import timezone
from decimal import Decimal


class KPIRule(models.Model):
    """Defines a KPI rule that can trigger bonuses or penalties."""
    RULE_TYPE_CHOICES = [
        ('conversion_rate', 'Aylanish darajasi'),
        ('response_time', 'Javob berish vaqti'),
        ('leads_contacted', 'Bog\'langan lidlar'),
        ('leads_converted', 'Aylantirilgan lidlar'),
        ('revenue', 'Daromad'),
    ]
    
    COMPARISON_CHOICES = [
        ('gte', 'Katta yoki teng'),
        ('lte', 'Kichik yoki teng'),
        ('eq', 'Teng'),
        ('between', 'Oraliqda'),
    ]
    
    name = models.CharField(max_length=255, unique=True)
    rule_type = models.CharField(max_length=50, choices=RULE_TYPE_CHOICES)
    comparison = models.CharField(max_length=10, choices=COMPARISON_CHOICES)
    
    # Threshold values
    threshold_value = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Bitta chegaraviy qiymat"
    )
    threshold_min = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Minimal chegaraviy qiymat ('oraliqda' taqqoslash uchun)"
    )
    threshold_max = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Maksimal chegaraviy qiymat ('oraliqda' taqqoslash uchun)"
    )
    
    # Bonus/Penalty configuration
    bonus_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Qoida bajarilganda bonus miqdori"
    )
    penalty_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Qoida bajarilmasa jarima miqdori"
    )
    
    # Time period for evaluation
    evaluation_period_days = models.IntegerField(
        default=30,
        validators=[MinValueValidator(1)],
        help_text="Baholash uchun qaytib ko'riladigan kunlar soni"
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "KPI Qoidasi"
        verbose_name_plural = "KPI Qoidalari"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.get_rule_type_display()})"

    def clean(self):
        """Validate rule configuration."""
        from django.core.exceptions import ValidationError
        
        if self.comparison == 'between':
            if not self.threshold_min or not self.threshold_max:
                raise ValidationError("'oraliqda' taqqoslash uchun threshold_min va threshold_max talab qilinadi.")
            if self.threshold_min >= self.threshold_max:
                raise ValidationError("threshold_min threshold_max dan kichik bo'lishi kerak.")
        elif not self.threshold_value:
            raise ValidationError("Ushbu taqqoslash turi uchun threshold_value talab qilinadi.")


class KPICalculation(models.Model):
    """Stores calculated KPI results for sellers."""
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='kpi_calculations')
    rule = models.ForeignKey(KPIRule, on_delete=models.CASCADE, related_name='calculations')
    
    # Calculated values
    actual_value = models.DecimalField(max_digits=10, decimal_places=2)
    threshold_value = models.DecimalField(max_digits=10, decimal_places=2)
    rule_met = models.BooleanField(default=False)
    
    # Financial impact
    bonus_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    penalty_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    net_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    # Period
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    calculated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "KPI Hisobi"
        verbose_name_plural = "KPI Hisoblari"
        ordering = ['-calculated_at']
        unique_together = [['seller', 'rule', 'period_start', 'period_end']]
        indexes = [
            models.Index(fields=['seller', 'calculated_at']),
            models.Index(fields=['rule', 'calculated_at']),
        ]

    def __str__(self):
        status = "✓" if self.rule_met else "✗"
        return f"{self.seller} - {self.rule.name} {status} ({self.period_start.date()} to {self.period_end.date()})"


class SellerKPISummary(models.Model):
    """Monthly summary of KPI performance for a seller."""
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='kpi_summaries')
    month = models.DateField(help_text="Oyning birinchi kuni")
    
    # Aggregated values
    total_bonus = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_penalty = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    net_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    # Statistics
    total_leads = models.IntegerField(default=0)
    converted_leads = models.IntegerField(default=0)
    conversion_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    
    calculated_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Sotuvchi KPI Xulosa"
        verbose_name_plural = "Sotuvchi KPI Xulosalari"
        ordering = ['-month', '-seller']
        unique_together = [['seller', 'month']]
        indexes = [
            models.Index(fields=['seller', 'month']),
        ]

    def __str__(self):
        return f"{self.seller} - {self.month.strftime('%B %Y')} (Net: {self.net_amount})"

