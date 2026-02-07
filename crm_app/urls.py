from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Public landing
    path('landing/', views.landing_page, name='landing'),
    
    # Leads
    path('leads/', views.leads_list, name='leads_list'),
    path('leads/create/', views.lead_create, name='lead_create'),
    path('leads/<int:pk>/', views.lead_detail, name='lead_detail'),
    path('leads/<int:pk>/assign/', views.lead_assign, name='lead_assign'),
    path('leads/import/', views.excel_import, name='excel_import'),
    path('leads/import/google-sheets/', views.google_sheets_manual_import, name='google_sheets_manual_import'),
    path('leads/table/', views.leads_table, name='leads_table'),
    
    # Follow-ups
    path('followups/today/', views.followups_today, name='followups_today'),
    path('followups/overdue/', views.overdue_followups_list, name='overdue_followups_list'),
    path('followups/overdue/<int:followup_id>/complete/', views.overdue_followup_complete, name='overdue_followup_complete'),
    path('followups/overdue/bulk/reschedule/', views.bulk_reschedule_overdue, name='bulk_reschedule_overdue'),
    path('followups/overdue/bulk/reassign/', views.bulk_reassign_overdue, name='bulk_reassign_overdue'),
    path('followups/overdue/bulk/complete/', views.bulk_complete_overdue, name='bulk_complete_overdue'),
    path('followups/overdue/bulk/delete/', views.bulk_delete_overdue, name='bulk_delete_overdue'),
    
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
    path('users/me/', views.manager_self_edit, name='manager_self_edit'),
    
    # Analytics
    path('analytics/', views.analytics, name='analytics'),
    path('analytics/my-kpi/<int:sales_id>/', views.sales_kpi, name='sales_kpi_sales'),
    path('analytics/my-kpi/', views.sales_kpi, name='sales_kpi'),
    path('analytics/export-excel/', views.export_analytics_excel, name='export_analytics_excel'),
    path('analytics/send-telegram/', views.send_kpi_report_telegram, name='send_kpi_report_telegram'),
    
    # Leave Requests (Sales)
    path('leaves/create/', views.leave_request_create, name='leave_request_create'),
    path('leaves/', views.leave_request_list, name='leave_request_list'),
    
    # Leave Requests (Manager/Admin)
    path('leaves/pending/', views.leave_request_pending_list, name='leave_request_pending_list'),
    path('leaves/<int:pk>/approve/', views.leave_request_approve, name='leave_request_approve'),
    
    # Sales Absence (Manager/Admin)
    path('users/sales/<int:pk>/absence/', views.sales_absence_set, name='sales_absence_set'),
    
    # Sales Messages (Manager/Admin)
    path('messages/create/', views.sales_message_create, name='sales_message_create'),
    path('messages/', views.sales_message_list, name='sales_message_list'),
    path('messages/<int:pk>/delete/', views.sales_message_delete, name='sales_message_delete'),
    
    # Sales Messages (Sales)
    path('messages/inbox/', views.sales_message_inbox, name='sales_message_inbox'),
    path('messages/<int:pk>/', views.sales_message_detail, name='sales_message_detail'),

    # Offers
    path('offers/', views.offers_list, name='offers_list'),
    path('offers/create/', views.offer_create, name='offer_create'),
    path('offers/<int:pk>/edit/', views.offer_edit, name='offer_edit'),
    path('offers/<int:pk>/delete/', views.offer_delete, name='offer_delete'),
]