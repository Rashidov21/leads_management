"""
Scheduling module: Course, Group, Room, and Timetable models.
Handles course database, group management, room occupancy, and availability.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError


class Course(models.Model):
    """Course information with teacher, price, duration, and frequency."""
    
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='courses_taught')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_minutes = models.IntegerField(default=90)  # 1.5 hours = 90 minutes
    frequency_per_week = models.IntegerField(default=3)  # 3 times per week
    room_capacity = models.IntegerField(default=10)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
        ]
    
    def __str__(self):
        return f"{self.name} (${self.price})"


class Room(models.Model):
    """Physical room/classroom information."""
    
    name = models.CharField(max_length=255, unique=True)
    capacity = models.IntegerField()
    location = models.CharField(max_length=255, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
        ]
    
    def __str__(self):
        return f"{self.name} (cap: {self.capacity})"


class Group(models.Model):
    """Course group with schedule, room, students, and capacity."""
    
    DAYS_CHOICES = [
        ('odd', 'Odd days'),
        ('even', 'Even days'),
        ('mon', 'Monday'),
        ('tue', 'Tuesday'),
        ('wed', 'Wednesday'),
        ('thu', 'Thursday'),
        ('fri', 'Friday'),
        ('sat', 'Saturday'),
        ('sun', 'Sunday'),
        ('mon_wed_fri', 'Mon/Wed/Fri'),
        ('tue_thu', 'Tue/Thu'),
    ]
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='groups')
    name = models.CharField(max_length=255)
    days = models.CharField(max_length=20, choices=DAYS_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True)
    capacity = models.IntegerField()
    current_students = models.IntegerField(default=0)
    trial_students = models.IntegerField(default=0)
    assigned_teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='groups_assigned')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['course', 'start_time']
        unique_together = ['course', 'name', 'days', 'start_time']
        indexes = [
            models.Index(fields=['course']),
            models.Index(fields=['days']),
            models.Index(fields=['start_time']),
        ]
    
    def __str__(self):
        return f"{self.course.name} - {self.name} ({self.days} {self.start_time})"
    
    @property
    def free_slots(self):
        """Calculate number of free slots in the group."""
        return max(0, self.capacity - self.current_students - self.trial_students)
    
    @property
    def occupancy_percent(self):
        """Calculate occupancy percentage."""
        if self.capacity == 0:
            return 0
        return int((self.current_students / self.capacity) * 100)
    
    @property
    def is_full(self):
        """Check if group is at capacity."""
        return self.current_students >= self.capacity
    
    def clean(self):
        """Validate group data."""
        if self.current_students < 0:
            raise ValidationError("Current students cannot be negative.")
        if self.capacity < 1:
            raise ValidationError("Capacity must be at least 1.")


class RoomOccupancy(models.Model):
    """Track room occupancy by time slot for availability grid."""
    
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='occupancy')
    date = models.DateField()
    time_start = models.TimeField()
    time_end = models.TimeField()
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True)
    occupancy_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['date', 'time_start']
        unique_together = ['room', 'date', 'time_start', 'time_end']
        indexes = [
            models.Index(fields=['room', 'date']),
            models.Index(fields=['date', 'time_start']),
        ]
    
    def __str__(self):
        return f"{self.room.name} - {self.date} {self.time_start}-{self.time_end}"
    
    @property
    def occupancy_percent(self):
        """Calculate occupancy percentage for the room."""
        if self.room.capacity == 0:
            return 0
        return int((self.occupancy_count / self.room.capacity) * 100)
    
    @property
    def availability_color(self):
        """Return color code for occupancy: green (free), yellow (50%+), red (full)."""
        percent = self.occupancy_percent
        if percent < 50:
            return 'green'
        elif percent < 100:
            return 'yellow'
        else:
            return 'red'
