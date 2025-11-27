"""Import service URL configuration for template views."""
from django.urls import path
from . import views

urlpatterns = [
    path('upload-excel/', views.upload_excel, name='upload-excel'),
    path('upload-csv/', views.upload_csv, name='upload-csv'),
    path('status/', views.import_status, name='import-status'),
]
