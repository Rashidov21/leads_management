# Archived API: reminders/views.py
# Copied before removing API viewset

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from leads.models import LeadReminder
from leads.serializers import LeadReminderSerializer
from .tasks import mark_reminder_contacted


class ReminderViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for LeadReminder model."""
    queryset = LeadReminder.objects.all()
    serializer_class = LeadReminderSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get all pending reminders for current user's assigned leads."""
        if request.user.is_staff:
            reminders = LeadReminder.objects.filter(status='pending').order_by('contact_deadline')
        else:
            reminders = LeadReminder.objects.filter(
                status='pending',
                lead__assigned_to=request.user
            ).order_by('contact_deadline')
        
        serializer = self.get_serializer(reminders, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get all overdue reminders."""
        from django.utils import timezone
        
        now = timezone.now()
        
        if request.user.is_staff:
            reminders = LeadReminder.objects.filter(
                status__in=['pending', 'notified'],
                contact_deadline__lt=now
            ).order_by('contact_deadline')
        else:
            reminders = LeadReminder.objects.filter(
                status__in=['pending', 'notified'],
                contact_deadline__lt=now,
                lead__assigned_to=request.user
            ).order_by('contact_deadline')
        
        serializer = self.get_serializer(reminders, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_contacted(self, request, pk=None):
        """Mark reminder as contacted."""
        reminder = self.get_object()
        mark_reminder_contacted.delay(reminder.id)
        return Response({'status': 'Reminder marked as contacted'})
    
    @action(detail=True, methods=['post'])
    def snooze(self, request, pk=None):
        """Snooze reminder for specified minutes."""
        from django.utils import timezone
        
        reminder = self.get_object()
        snooze_minutes = request.data.get('snooze_minutes', 5)
        
        reminder.contact_deadline = timezone.now() + timezone.timedelta(minutes=snooze_minutes)
        reminder.save()
        
        return Response({'status': f'Reminder snoozed for {snooze_minutes} minutes'})
