# Archived API: leads/urls.py
# Copied before removing API router
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LeadViewSet, ImportLogViewSet, LeadReminderViewSet

router = DefaultRouter()
router.register(r'', LeadViewSet, basename='lead')
router.register(r'import-logs', ImportLogViewSet, basename='import-log')
router.register(r'reminders', LeadReminderViewSet, basename='reminder')

urlpatterns = [
    path('', include(router.urls)),
]
