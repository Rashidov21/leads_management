"""URL configuration for reminders app (template views)."""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.pending_reminders, name='pending_reminders'),
    path('pending/', views.pending_reminders, name='pending_reminders'),
    path('overdue/', views.overdue_reminders, name='overdue_reminders'),
    path('<int:pk>/mark_contacted/', views.mark_contacted, name='mark_contacted'),
    path('<int:pk>/snooze/', views.snooze_reminder, name='snooze_reminder'),
]
