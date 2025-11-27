"""
URLs for leads app.
"""
from django.urls import path
from . import views

app_name = 'leads'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    # Lead URLs
    path('leads/', views.lead_list, name='lead_list'),
    path('leads/create/', views.lead_create, name='lead_create'),
    path('leads/<int:lead_id>/', views.lead_detail, name='lead_detail'),
    path('leads/<int:lead_id>/edit/', views.lead_edit, name='lead_edit'),
    path('leads/<int:lead_id>/delete/', views.lead_delete, name='lead_delete'),
    path('leads/export/', views.lead_export, name='lead_export'),
    # Seller URLs
    path('sellers/', views.seller_list, name='seller_list'),
    path('sellers/create/', views.seller_create, name='seller_create'),
    path('sellers/<int:seller_id>/edit/', views.seller_edit, name='seller_edit'),
    path('sellers/<int:seller_id>/delete/', views.seller_delete, name='seller_delete'),
]

