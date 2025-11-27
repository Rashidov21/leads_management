"""Serializers for leads API."""
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
        """DRF serializers removed — project uses template views now.

        This file retained as a placeholder in case DRF endpoints are restored.
        """
        from django.utils.translation import gettext_lazy as _

        __all__ = []
        read_only_fields = ['id', 'created_at', 'updated_at']
