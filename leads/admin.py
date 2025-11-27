"""
Admin configuration for leads app.
"""
from django.contrib import admin
from .models import Lead, Seller


@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display = ['user', 'telegram_id', 'phone_number', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['user__username', 'user__email', 'telegram_id', 'phone_number']
    raw_id_fields = ['user']


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'seller', 'status', 'source', 'created_at']
    list_filter = ['status', 'source', 'created_at', 'seller']
    search_fields = ['name', 'email', 'phone', 'company']
    raw_id_fields = ['seller']
    readonly_fields = ['created_at', 'updated_at', 'last_synced_at']
    date_hierarchy = 'created_at'

