from django.contrib import admin
from django.utils.html import format_html
from .models import Course, Room, Group, RoomOccupancy


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'teacher', 'price', 'duration_minutes', 'frequency_per_week', 'room_capacity')
    list_filter = ('created_at', 'teacher', 'frequency_per_week')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Course Information', {
            'fields': ('name', 'description', 'teacher', 'price')
        }),
        ('Schedule Details', {
            'fields': ('duration_minutes', 'frequency_per_week', 'room_capacity')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'capacity', 'location')
    list_filter = ('created_at',)
    search_fields = ('name', 'location')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Room Information', {
            'fields': ('name', 'capacity', 'location')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'course', 'days', 'start_time', 'end_time', 'room', 'capacity_status', 'occupancy_percent')
    list_filter = ('course', 'days', 'start_time', 'created_at')
    search_fields = ('name', 'course__name')
    readonly_fields = ('created_at', 'updated_at', 'display_occupancy')
    fieldsets = (
        ('Group Information', {
            'fields': ('course', 'name', 'room')
        }),
        ('Schedule', {
            'fields': ('days', 'start_time', 'end_time')
        }),
        ('Capacity', {
            'fields': ('capacity', 'current_students', 'trial_students')
        }),
        ('Assignment', {
            'fields': ('assigned_teacher',)
        }),
        ('Status', {
            'fields': ('display_occupancy',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def capacity_status(self, obj):
        """Display capacity status with color coding."""
        if obj.is_full:
            color = 'red'
            status = 'FULL'
        elif obj.occupancy_percent >= 80:
            color = 'orange'
            status = f'{obj.occupancy_percent}%'
        else:
            color = 'green'
            status = f'{obj.occupancy_percent}%'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            status
        )
    capacity_status.short_description = 'Capacity Status'

    def display_occupancy(self, obj):
        """Display occupancy information."""
        free = obj.free_slots
        return f"{obj.current_students}/{obj.capacity} students ({free} free slots, {obj.trial_students} trial)"
    display_occupancy.short_description = 'Occupancy Info'


@admin.register(RoomOccupancy)
class RoomOccupancyAdmin(admin.ModelAdmin):
    list_display = ('room', 'date', 'time_start', 'time_end', 'occupancy_count', 'occupancy_status')
    list_filter = ('room', 'date')
    search_fields = ('room__name',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Room Occupancy', {
            'fields': ('room', 'date', 'time_start', 'time_end', 'group')
        }),
        ('Metrics', {
            'fields': ('occupancy_count',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def occupancy_status(self, obj):
        """Display occupancy status with color coding."""
        color = obj.availability_color
        percent = obj.occupancy_percent
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            f'{percent}%'
        )
    occupancy_status.short_description = 'Occupancy Status'
