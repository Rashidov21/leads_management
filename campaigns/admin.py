"""
Admin configuration for campaigns app.
"""
from django.contrib import admin
from .models import SMSCampaign, SMSCampaignLog


@admin.register(SMSCampaign)
class SMSCampaignAdmin(admin.ModelAdmin):
    list_display = ['name', 'status', 'scheduled_at', 'total_recipients', 'sent_count', 'failed_count', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'message']
    filter_horizontal = ['target_sellers']
    readonly_fields = ['started_at', 'completed_at', 'total_recipients', 'sent_count', 'failed_count', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'


@admin.register(SMSCampaignLog)
class SMSCampaignLogAdmin(admin.ModelAdmin):
    list_display = ['campaign', 'lead', 'phone_number', 'status', 'sent_at', 'created_at']
    list_filter = ['status', 'campaign', 'created_at']
    search_fields = ['lead__name', 'phone_number', 'campaign__name']
    raw_id_fields = ['campaign', 'lead']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'

