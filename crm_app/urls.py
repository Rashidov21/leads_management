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
    
    # Courses (Admin only)
    path('courses/', views.courses_list, name='courses_list'),
    path('courses/create/', views.course_create, name='course_create'),
    path('courses/<int:pk>/edit/', views.course_edit, name='course_edit'),
    path('courses/<int:pk>/delete/', views.course_delete, name='course_delete'),
    
    # Rooms (Admin only)
    path('rooms/', views.rooms_list, name='rooms_list'),
    path('rooms/create/', views.room_create, name='room_create'),
    path('rooms/<int:pk>/edit/', views.room_edit, name='room_edit'),
    path('rooms/<int:pk>/delete/', views.room_delete, name='room_delete'),
    
    # Groups (Admin only)
    path('groups/', views.groups_list, name='groups_list'),
    path('groups/create/', views.group_create, name='group_create'),
    path('groups/<int:pk>/edit/', views.group_edit, name='group_edit'),
    path('groups/<int:pk>/delete/', views.group_delete, name='group_delete'),
    
    # User Management - Sales (Manager & Admin)
    path('users/sales/', views.sales_list, name='sales_list'),
    path('users/sales/create/', views.sales_create, name='sales_create'),
    path('users/sales/<int:pk>/edit/', views.sales_edit, name='sales_edit'),
    path('users/sales/<int:pk>/delete/', views.sales_delete, name='sales_delete'),
    
    # User Management - Managers (Admin only)
    path('users/managers/', views.managers_list, name='managers_list'),
    path('users/managers/create/', views.manager_create, name='manager_create'),
    path('users/managers/<int:pk>/edit/', views.manager_edit, name='manager_edit'),
    path('users/managers/<int:pk>/delete/', views.manager_delete, name='manager_delete'),
    
    # Analytics
    path('analytics/', views.analytics, name='analytics'),
    path('analytics/my-kpi/', views.sales_kpi, name='sales_kpi'),
    
    # Leave Requests (Sales)
    path('leaves/create/', views.leave_request_create, name='leave_request_create'),
    path('leaves/', views.leave_request_list, name='leave_request_list'),
    
    # Leave Requests (Manager/Admin)
    path('leaves/pending/', views.leave_request_pending_list, name='leave_request_pending_list'),
    path('leaves/<int:pk>/approve/', views.leave_request_approve, name='leave_request_approve'),
    
    # Sales Absence (Manager/Admin)
    path('users/sales/<int:pk>/absence/', views.sales_absence_set, name='sales_absence_set'),
]
