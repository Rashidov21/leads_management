"""Django admin configuration for leads app."""
from django.contrib import admin
from .models import Lead, ImportLog, LeadReminder


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'source', 'status', 'assigned_to', 'created_at']
    list_filter = ['status', 'source', 'created_at']
    search_fields = ['name', 'phone']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'phone')
        }),
        ('Lead Management', {
            'fields': ('source', 'status', 'assigned_to')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ImportLog)
class ImportLogAdmin(admin.ModelAdmin):
    list_display = ['import_type', 'status', 'imported_count', 'duplicate_count', 'started_at']
    list_filter = ['import_type', 'status', 'started_at']
    search_fields = ['file_name', 'google_sheet_id']
    readonly_fields = ['started_at', 'completed_at']


@admin.register(LeadReminder)
class LeadReminderAdmin(admin.ModelAdmin):
    list_display = ['lead', 'status', 'contact_deadline', 'reminder_count']
    list_filter = ['status', 'contact_deadline']
    search_fields = ['lead__name', 'lead__phone']
