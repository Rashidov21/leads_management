from django.contrib import admin
from django.utils.html import format_html
from .models import SalesKPI, LeadMetrics, GroupAnalytics, MarketingAnalytics


@admin.register(SalesKPI)
class SalesKPIAdmin(admin.ModelAdmin):
    list_display = ('salesperson', 'date', 'new_contacts', 'trials_attended', 'enrollments', 'conversion_percent')
    list_filter = ('date', 'salesperson', 'created_at')
    search_fields = ('salesperson__username', 'salesperson__first_name', 'salesperson__last_name')
    readonly_fields = ('created_at', 'updated_at', 'followup_completion_percent', 'trial_to_conversion_percent', 'overall_conversion_percent')
    fieldsets = (
        ('Salesperson & Date', {
            'fields': ('salesperson', 'date')
        }),
        ('Contacts & Follow-ups', {
            'fields': ('new_contacts', 'followups_completed', 'followups_overdue', 'followup_completion_percent')
        }),
        ('Trials', {
            'fields': ('trials_scheduled', 'trials_attended', 'trials_no_show')
        }),
        ('Conversions', {
            'fields': ('sales_offers_made', 'enrollments', 'lost_leads')
        }),
        ('Performance Metrics', {
            'fields': ('avg_response_time', 'trial_to_conversion_percent', 'overall_conversion_percent')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def conversion_percent(self, obj):
        """Display overall conversion percentage."""
        percent = obj.overall_conversion_percent
        color = 'green' if percent >= 20 else 'orange' if percent >= 10 else 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}%</span>',
            color,
            percent
        )
    conversion_percent.short_description = 'Conversion %'


@admin.register(LeadMetrics)
class LeadMetricsAdmin(admin.ModelAdmin):
    list_display = ('date', 'new_leads_total', 'leads_trial_attended', 'leads_enrolled', 'conversion_rate_badge')
    list_filter = ('date', 'created_at')
    readonly_fields = ('created_at', 'source_breakdown_display', 'conversion_rate_percent', 'trial_to_conversion_percent')
    fieldsets = (
        ('Date', {
            'fields': ('date',)
        }),
        ('Lead Acquisition by Source', {
            'fields': ('new_leads_total', 'new_leads_instagram', 'new_leads_telegram', 'new_leads_whatsapp', 
                      'new_leads_landing', 'new_leads_google_sheets', 'new_leads_excel', 'new_leads_csv', 'new_leads_call')
        }),
        ('Lead Status Breakdown', {
            'fields': ('leads_contacted', 'leads_interested', 'leads_trial_scheduled', 'leads_trial_attended', 
                      'leads_sales_offer', 'leads_enrolled', 'leads_lost')
        }),
        ('Distribution', {
            'fields': ('leads_assigned_total', 'leads_unassigned')
        }),
        ('Performance Metrics', {
            'fields': ('source_breakdown_display', 'conversion_rate_percent', 'trial_to_conversion_percent'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def source_breakdown_display(self, obj):
        """Display source breakdown as formatted text."""
        breakdown = obj.source_breakdown
        lines = [f"<strong>Source Breakdown:</strong><br>"]
        for source, count in breakdown.items():
            if count > 0:
                lines.append(f"{source.replace('_', ' ').title()}: {count}<br>")
        return format_html(''.join(lines))
    source_breakdown_display.short_description = 'Source Breakdown'

    def conversion_rate_badge(self, obj):
        """Display conversion rate with color coding."""
        percent = obj.conversion_rate_percent
        color = 'green' if percent >= 20 else 'orange' if percent >= 10 else 'red'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}%</span>',
            color,
            percent
        )
    conversion_rate_badge.short_description = 'Conversion Rate'


@admin.register(GroupAnalytics)
class GroupAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('date', 'total_groups', 'full_groups', 'capacity_status', 'avg_room_occupancy', 'total_trial_students')
    list_filter = ('date', 'created_at')
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Date', {
            'fields': ('date',)
        }),
        ('Group Capacity', {
            'fields': ('total_groups', 'full_groups', 'near_full_groups', 'empty_groups')
        }),
        ('Room Usage', {
            'fields': ('total_rooms', 'rooms_in_use', 'avg_room_occupancy')
        }),
        ('Trial Students', {
            'fields': ('total_trial_students', 'expected_enrollments')
        }),
        ('Recommendations', {
            'fields': ('new_groups_recommended', 'groups_to_combine')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def capacity_status(self, obj):
        """Display capacity status."""
        occupied = obj.total_groups - obj.empty_groups
        percent = int((occupied / obj.total_groups) * 100) if obj.total_groups > 0 else 0
        color = 'green' if percent >= 70 else 'orange' if percent >= 50 else 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}%</span>',
            color,
            percent
        )
    capacity_status.short_description = 'Overall Capacity'


@admin.register(MarketingAnalytics)
class MarketingAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('date', 'channel', 'leads_generated', 'cpl', 'enrollments_from_channel', 'cpa')
    list_filter = ('date', 'channel', 'created_at')
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Channel', {
            'fields': ('date', 'channel')
        }),
        ('Traffic Metrics', {
            'fields': ('impressions', 'clicks', 'ctr')
        }),
        ('Lead Metrics', {
            'fields': ('leads_generated', 'cost_total', 'cpl')
        }),
        ('Conversion Metrics', {
            'fields': ('enrollments_from_channel', 'cpa')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
