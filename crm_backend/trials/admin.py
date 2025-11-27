from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Trial, TrialReminder


@admin.register(Trial)
class TrialAdmin(admin.ModelAdmin):
    list_display = ('trial_info', 'group', 'scheduled_datetime', 'status_badge', 'result_badge', 'is_overdue')
    list_filter = ('status', 'result', 'scheduled_date', 'created_at')
    search_fields = ('lead__name', 'lead__phone')
    readonly_fields = ('created_at', 'updated_at', 'is_overdue', 'is_upcoming_today', 'hours_until_trial')
    fieldsets = (
        ('Lead & Group Information', {
            'fields': ('lead', 'group')
        }),
        ('Trial Scheduling', {
            'fields': ('scheduled_date', 'scheduled_time')
        }),
        ('Trial Status', {
            'fields': ('status', 'result')
        }),
        ('Trial Execution', {
            'fields': ('actual_attendance_time', 'trial_completed_at')
        }),
        ('Follow-up', {
            'fields': ('sales_offer_made_at', 'salesperson_notes')
        }),
        ('Reminders', {
            'fields': ('pre_trial_reminder_sent_at', 'post_trial_reminder_sent_at')
        }),
        ('Status Information', {
            'fields': ('is_overdue', 'is_upcoming_today', 'hours_until_trial'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def trial_info(self, obj):
        """Display trial lead and date."""
        return f"{obj.lead.name} - {obj.scheduled_date}"
    trial_info.short_description = 'Trial Info'

    def scheduled_datetime(self, obj):
        """Display scheduled datetime."""
        return f"{obj.scheduled_date} {obj.scheduled_time}"
    scheduled_datetime.short_description = 'Scheduled'

    def status_badge(self, obj):
        """Display status with color coding."""
        colors = {
            'scheduled': '#3498db',
            'attended': '#27ae60',
            'no_show': '#e74c3c',
            'cancelled': '#95a5a6'
        }
        color = colors.get(obj.status, '#3498db')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def result_badge(self, obj):
        """Display result with color coding."""
        colors = {
            'pending': '#95a5a6',
            'sales_offer': '#f39c12',
            'accepted': '#27ae60',
            'rejected': '#e74c3c'
        }
        color = colors.get(obj.result, '#95a5a6')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_result_display()
        )
    result_badge.short_description = 'Result'


@admin.register(TrialReminder)
class TrialReminderAdmin(admin.ModelAdmin):
    list_display = ('trial', 'pre_trial_reminder_status', 'post_trial_reminder_status', 'pre_trial_reminder_scheduled_at')
    list_filter = ('pre_trial_reminder_sent', 'post_trial_reminder_sent', 'created_at')
    search_fields = ('trial__lead__name',)
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Trial Reference', {
            'fields': ('trial',)
        }),
        ('Pre-Trial Reminder', {
            'fields': ('pre_trial_reminder_scheduled_at', 'pre_trial_reminder_sent')
        }),
        ('Post-Trial Reminder', {
            'fields': ('post_trial_reminder_scheduled_at', 'post_trial_reminder_sent')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def pre_trial_reminder_status(self, obj):
        """Display pre-trial reminder status."""
        if obj.pre_trial_reminder_sent:
            return format_html('<span style="color: green;">✓ Sent</span>')
        return format_html('<span style="color: red;">✗ Pending</span>')
    pre_trial_reminder_status.short_description = 'Pre-Trial Reminder'

    def post_trial_reminder_status(self, obj):
        """Display post-trial reminder status."""
        if obj.post_trial_reminder_sent:
            return format_html('<span style="color: green;">✓ Sent</span>')
        return format_html('<span style="color: red;">✗ Pending</span>')
    post_trial_reminder_status.short_description = 'Post-Trial Reminder'
