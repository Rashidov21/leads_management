"""Views for scheduling module: groups, rooms, occupancy grid."""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Group, Course, Room, RoomOccupancy


@login_required
def groups_list(request):
    """Display all course groups with capacity info."""
    groups = Group.objects.select_related('course', 'room').all()
    return render(request, 'scheduling/groups.html', {'groups': groups})


@login_required
def filter_groups(request):
    """Filter groups by course, days, time, room availability, capacity."""
    groups = Group.objects.select_related('course', 'room').all()
    
    # Apply filters
    course_id = request.GET.get('course_id')
    if course_id:
        groups = groups.filter(course_id=course_id)
    
    days = request.GET.get('days')
    if days:
        groups = groups.filter(days=days)
    
    # Room availability (free slots)
    min_free_slots = request.GET.get('min_free_slots')
    if min_free_slots:
        min_free_slots = int(min_free_slots)
        # Filter in Python since we use a property
        groups = [g for g in groups if g.free_slots >= min_free_slots]
    
    # Not full groups
    not_full = request.GET.get('not_full')
    if not_full == 'true':
        groups = [g for g in groups if not g.is_full]
    
    return render(request, 'scheduling/groups.html', {'groups': groups, 'filtered': True})


@login_required
def room_occupancy_grid(request):
    """Display room occupancy grid: time vs room, color-coded by availability."""
    date = request.GET.get('date')  # YYYY-MM-DD
    occupancy = RoomOccupancy.objects.select_related('room').filter(date=date) if date else RoomOccupancy.objects.none()
    
    rooms = Room.objects.all()
    time_slots = ['08:00', '09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00']
    
    # Build grid: {room_id: {time: occupancy_record}}
    grid = {}
    for room in rooms:
        grid[room.id] = {}
        for time_slot in time_slots:
            # Find occupancy for this slot (simplified: assuming each slot is 1 hour)
            occupancy_record = occupancy.filter(room=room, time_start=time_slot).first()
            grid[room.id][time_slot] = occupancy_record
    
    return render(request, 'scheduling/room_occupancy.html', {
        'grid': grid,
        'rooms': rooms,
        'time_slots': time_slots,
        'date': date,
    })


@login_required
def courses_list(request):
    """Display all courses."""
    courses = Course.objects.select_related('teacher').all()
    return render(request, 'scheduling/courses.html', {'courses': courses})
