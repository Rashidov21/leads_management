"""URL configuration for analytics module."""
from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('dashboard/', views.analytics_dashboard, name='dashboard'),
    path('leads/', views.lead_analytics, name='lead_analytics'),
    path('sales/', views.sales_analytics, name='sales_analytics'),
    path('groups/', views.group_analytics, name='group_analytics'),
    path('marketing/', views.marketing_analytics, name='marketing_analytics'),
]
