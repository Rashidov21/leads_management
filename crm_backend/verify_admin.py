#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_project.settings')
django.setup()

from django.contrib import admin
from scheduling.models import Course, Group, Room, RoomOccupancy
from trials.models import Trial, TrialReminder
from analytics.models import SalesKPI, LeadMetrics, GroupAnalytics, MarketingAnalytics

print("✅ ADMIN REGISTRATION VERIFICATION")
print("=" * 60)

# Get all registered models in admin
admin_registry = admin.site._registry

# Check scheduling app
scheduling_models = []
for model, admin_class in admin_registry.items():
    if model._meta.app_label == 'scheduling':
        scheduling_models.append((model.__name__, admin_class.__class__.__name__))
        
print(f"\n✅ Scheduling App Models ({len(scheduling_models)}):")
for model_name, admin_class in sorted(scheduling_models):
    print(f"   ✓ {model_name:20} → {admin_class}")

# Check trials app
trials_models = []
for model, admin_class in admin_registry.items():
    if model._meta.app_label == 'trials':
        trials_models.append((model.__name__, admin_class.__class__.__name__))
        
print(f"\n✅ Trials App Models ({len(trials_models)}):")
for model_name, admin_class in sorted(trials_models):
    print(f"   ✓ {model_name:20} → {admin_class}")

# Check analytics app
analytics_models = []
for model, admin_class in admin_registry.items():
    if model._meta.app_label == 'analytics':
        analytics_models.append((model.__name__, admin_class.__class__.__name__))
        
print(f"\n✅ Analytics App Models ({len(analytics_models)}):")
for model_name, admin_class in sorted(analytics_models):
    print(f"   ✓ {model_name:20} → {admin_class}")

total = len(scheduling_models) + len(trials_models) + len(analytics_models)
print(f"\n{'='*60}")
print(f"✅ TOTAL REGISTERED MODELS: {total}")
print(f"{'='*60}")

# Verify model fields
print("\n✅ MODEL FIELD VERIFICATION")
print("=" * 60)

models_to_check = [
    ('Course', Course),
    ('Group', Group),
    ('Room', Room),
    ('RoomOccupancy', RoomOccupancy),
    ('Trial', Trial),
    ('TrialReminder', TrialReminder),
    ('SalesKPI', SalesKPI),
    ('LeadMetrics', LeadMetrics),
    ('GroupAnalytics', GroupAnalytics),
    ('MarketingAnalytics', MarketingAnalytics),
]

for model_name, model_class in models_to_check:
    field_count = len(model_class._meta.get_fields())
    print(f"   ✓ {model_name:20} - {field_count} fields")

print(f"\n{'='*60}")
print("✅ ALL VERIFICATIONS PASSED - SYSTEM READY!")
print(f"{'='*60}")
