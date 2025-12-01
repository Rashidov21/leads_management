from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User, Course, Room, Group, Lead, FollowUp, 
    TrialLesson, KPI, Reactivation
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'role', 'is_active_sales', 'phone']
    list_filter = ['role', 'is_active_sales']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('CRM Fields', {'fields': ('role', 'phone', 'telegram_chat_id', 'is_active_sales')}),
    )


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'duration_minutes', 'lessons_per_week', 'is_active']
    list_filter = ['is_active']


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['name', 'capacity', 'is_active']


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'course', 'days', 'time', 'room', 'capacity', 'current_students', 'is_full']
    list_filter = ['course', 'is_active', 'days']


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'interested_course', 'source', 'assigned_sales', 'status', 'created_at']
    list_filter = ['status', 'source', 'assigned_sales', 'created_at']
    search_fields = ['name', 'phone']


@admin.register(FollowUp)
class FollowUpAdmin(admin.ModelAdmin):
    list_display = ['lead', 'sales', 'due_date', 'completed', 'is_overdue']
    list_filter = ['completed', 'is_overdue', 'due_date']


@admin.register(TrialLesson)
class TrialLessonAdmin(admin.ModelAdmin):
    list_display = ['lead', 'group', 'date', 'time', 'result']
    list_filter = ['date', 'result']


@admin.register(KPI)
class KPIAdmin(admin.ModelAdmin):
    list_display = ['sales', 'date', 'daily_contacts', 'conversion_rate', 'overdue_count']
    list_filter = ['date', 'sales']


@admin.register(Reactivation)
class ReactivationAdmin(admin.ModelAdmin):
    list_display = ['lead', 'reactivation_type', 'days_since_lost', 'sent_at', 'result']
    list_filter = ['reactivation_type', 'result']

