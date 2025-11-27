# Archived API: leads/views.py
# Copied here before removing DRF-based API implementation.

"""Views for leads API (archived)."""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import Lead, ImportLog, LeadReminder
from .serializers import (
    LeadSerializer,
    LeadCreateUpdateSerializer,
    ImportLogSerializer,
    LeadReminderSerializer
)


class LeadViewSet(viewsets.ModelViewSet):
    """ViewSet for Lead model."""
    queryset = Lead.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return LeadCreateUpdateSerializer
        return LeadSerializer
    
    @action(detail=False, methods=['get'])
    def by_status(self, request):
        """Get leads filtered by status."""
        status_filter = request.query_params.get('status')
        if status_filter:
            leads = Lead.objects.filter(status=status_filter)
            serializer = self.get_serializer(leads, many=True)
            return Response(serializer.data)
        return Response({'error': 'status parameter required'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def by_salesperson(self, request):
        """Get leads assigned to a specific salesperson."""
        salesperson_id = request.query_params.get('salesperson_id')
        if salesperson_id:
            leads = Lead.objects.filter(assigned_to_id=salesperson_id)
            serializer = self.get_serializer(leads, many=True)
            return Response(serializer.data)
        return Response({'error': 'salesperson_id parameter required'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def mark_contacted(self, request, pk=None):
        """Mark a lead as contacted."""
        lead = self.get_object()
        lead.status = 'contacted'
        lead.save()
        
        # Update reminder if exists
        if hasattr(lead, 'reminder'):
            lead.reminder.status = 'contacted'
            lead.reminder.contacted_at = timezone.now()
            lead.reminder.save()
        
        return Response({'status': 'Lead marked as contacted'})
    
    @action(detail=True, methods=['post'])
    def assign_to_salesperson(self, request, pk=None):
        """Assign a lead to a salesperson."""
        lead = self.get_object()
        salesperson_id = request.data.get('salesperson_id')
        
        if not salesperson_id:
            return Response(
                {'error': 'salesperson_id required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        lead.assigned_to_id = salesperson_id
        lead.save()
        serializer = self.get_serializer(lead)
        return Response(serializer.data)


class ImportLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for ImportLog model."""
    queryset = ImportLog.objects.all()
    serializer_class = ImportLogSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Get import logs filtered by type."""
        import_type = request.query_params.get('type')
        if import_type:
            logs = ImportLog.objects.filter(import_type=import_type)
            serializer = self.get_serializer(logs, many=True)
            return Response(serializer.data)
        return Response({'error': 'type parameter required'}, status=status.HTTP_400_BAD_REQUEST)


class LeadReminderViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for LeadReminder model."""
    queryset = LeadReminder.objects.all()
    serializer_class = LeadReminderSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def pending_reminders(self, request):
        """Get all pending reminders."""
        reminders = LeadReminder.objects.filter(status='pending').order_by('contact_deadline')
        serializer = self.get_serializer(reminders, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def snooze(self, request, pk=None):
        """Snooze a reminder."""
        reminder = self.get_object()
        snooze_minutes = request.data.get('snooze_minutes', 5)
        
        reminder.status = 'snoozed'
        reminder.contact_deadline = timezone.now() + timezone.timedelta(minutes=snooze_minutes)
        reminder.save()
        
        return Response({'status': 'Reminder snoozed'})
