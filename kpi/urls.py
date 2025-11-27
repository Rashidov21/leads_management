"""
URLs for KPI app.
"""
from django.urls import path
from . import views

app_name = 'kpi'

urlpatterns = [
    path('', views.kpi_dashboard, name='kpi_dashboard'),
    # KPI Rule URLs
    path('rules/', views.rule_list, name='rule_list'),
    path('rules/create/', views.rule_create, name='rule_create'),
    path('rules/<int:rule_id>/', views.rule_detail, name='rule_detail'),
    path('rules/<int:rule_id>/edit/', views.rule_edit, name='rule_edit'),
    path('rules/<int:rule_id>/delete/', views.rule_delete, name='rule_delete'),
    # KPI Calculation URLs
    path('calculations/', views.calculation_list, name='calculation_list'),
    path('summaries/', views.summary_list, name='summary_list'),
    path('calculate/', views.trigger_calculation, name='trigger_calculation'),
]

