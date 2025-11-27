# Archived API: leads/serializers.py
# Copied here before removing DRF serializers

from rest_framework import serializers
from .models import Lead, ImportLog, LeadReminder


class LeadSerializer(serializers.ModelSerializer):
    """Serializer for Lead model."""
    assigned_to_username = serializers.CharField(
        source='assigned_to.username',
        read_only=True
    )
    
    class Meta:
        model = Lead
        fields = [
            'id', 'name', 'phone', 'source', 'status',
            'assigned_to', 'assigned_to_username',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class LeadCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating leads."""
    
    class Meta:
        model = Lead
        fields = ['name', 'phone', 'source', 'status', 'assigned_to']
    
    def validate_phone(self, value):
        """Validate phone number format."""
        if not value or len(value) < 10:
            raise serializers.ValidationError("Phone number must be at least 10 digits.")
        return value


class ImportLogSerializer(serializers.ModelSerializer):
    """Serializer for ImportLog model."""
    imported_by_username = serializers.CharField(
        source='imported_by.username',
        read_only=True
    )
    
    class Meta:
        model = ImportLog
        fields = [
            'id', 'import_type', 'status', 'total_records',
            'imported_count', 'duplicate_count', 'error_count',
            'imported_by', 'imported_by_username', 'file_name',
            'google_sheet_id', 'started_at', 'completed_at'
        ]
        read_only_fields = [
            'id', 'imported_count', 'duplicate_count', 'error_count',
            'started_at', 'completed_at'
        ]


class LeadReminderSerializer(serializers.ModelSerializer):
    """Serializer for LeadReminder model."""
    lead_name = serializers.CharField(source='lead.name', read_only=True)
    lead_phone = serializers.CharField(source='lead.phone', read_only=True)
    assigned_to_username = serializers.CharField(
        source='lead.assigned_to.username',
        read_only=True
    )
    
    class Meta:
        model = LeadReminder
        fields = [
            'id', 'lead', 'lead_name', 'lead_phone',
            'assigned_to_username', 'status',
            'contact_deadline', 'last_reminder_at',
            'contacted_at', 'reminder_count'
        ]
        read_only_fields = [
            'id', 'contact_deadline', 'last_reminder_at',
            'contacted_at', 'reminder_count'
        ]
