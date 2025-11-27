"""
URL configuration for crm_project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/leads/', include('leads.urls')),
    path('api/imports/', include('import_service.urls')),
    path('api/reminders/', include('reminders.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
