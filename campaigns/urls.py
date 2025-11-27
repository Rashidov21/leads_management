"""
URLs for campaigns app.
"""
from django.urls import path
from . import views

app_name = 'campaigns'

urlpatterns = [
    path('', views.campaign_list, name='campaign_list'),
    path('create/', views.campaign_create, name='campaign_create'),
    path('<int:campaign_id>/', views.campaign_detail, name='campaign_detail'),
    path('api/send/', views.api_send_sms, name='api_send_sms'),
    path('api/status/', views.api_campaign_status, name='api_campaign_status'),
]

