"""
Admin configuration for KPI app.
"""
from django.contrib import admin
from .models import KPIRule, KPICalculation, SellerKPISummary


@admin.register(KPIRule)
class KPIRuleAdmin(admin.ModelAdmin):
    list_display = ['name', 'rule_type', 'comparison', 'threshold_value', 'bonus_amount', 'penalty_amount', 'is_active', 'created_at']
    list_filter = ['rule_type', 'is_active', 'created_at']
    search_fields = ['name']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'rule_type', 'is_active')
        }),
        ('Threshold Configuration', {
            'fields': ('comparison', 'threshold_value', 'threshold_min', 'threshold_max', 'evaluation_period_days')
        }),
        ('Financial Impact', {
            'fields': ('bonus_amount', 'penalty_amount')
        }),
    )


@admin.register(KPICalculation)
class KPICalculationAdmin(admin.ModelAdmin):
    list_display = ['seller', 'rule', 'actual_value', 'threshold_value', 'rule_met', 'net_amount', 'calculated_at']
    list_filter = ['rule_met', 'rule', 'calculated_at']
    search_fields = ['seller__user__username', 'rule__name']
    raw_id_fields = ['seller', 'rule']
    readonly_fields = ['calculated_at']
    date_hierarchy = 'calculated_at'


@admin.register(SellerKPISummary)
class SellerKPISummaryAdmin(admin.ModelAdmin):
    list_display = ['seller', 'month', 'total_bonus', 'total_penalty', 'net_amount', 'conversion_rate', 'updated_at']
    list_filter = ['month', 'updated_at']
    search_fields = ['seller__user__username']
    raw_id_fields = ['seller']
    readonly_fields = ['calculated_at', 'updated_at']
    date_hierarchy = 'month'

