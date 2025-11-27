"""URL configuration for leads app (template views)."""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.leads_list, name='leads_list'),
    path('create/', views.create_lead, name='create_lead'),
    path('<int:pk>/', views.lead_detail, name='lead_detail'),
]
