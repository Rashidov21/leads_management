from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    
    # Leads
    path('leads/', views.leads_list, name='leads_list'),
    path('leads/create/', views.lead_create, name='lead_create'),
    path('leads/<int:pk>/', views.lead_detail, name='lead_detail'),
    path('leads/<int:pk>/assign/', views.lead_assign, name='lead_assign'),
    path('leads/import/', views.excel_import, name='excel_import'),
    
    # Follow-ups
    path('followups/today/', views.followups_today, name='followups_today'),
    
    # Trials
    path('trials/register/<int:lead_pk>/', views.trial_register, name='trial_register'),
    path('trials/<int:trial_pk>/result/', views.trial_result, name='trial_result'),
    
    # Courses & Groups
    path('courses/', views.courses_list, name='courses_list'),
    path('groups/', views.groups_list, name='groups_list'),
    
    # Analytics
    path('analytics/', views.analytics, name='analytics'),
]

