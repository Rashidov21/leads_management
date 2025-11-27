# Archived API: reminders/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReminderViewSet

router = DefaultRouter()
router.register(r'', ReminderViewSet, basename='reminder')

urlpatterns = [
    path('', include(router.urls)),
    path('pending/', ReminderViewSet.as_view({'get': 'pending'}), name='pending-reminders'),
    path('overdue/', ReminderViewSet.as_view({'get': 'overdue'}), name='overdue-reminders'),
]
