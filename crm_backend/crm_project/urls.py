"""
URL configuration for crm_project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    # Frontend pages served via Django templates
    path('', TemplateView.as_view(template_name='dashboard.html'), name='dashboard'),
    path('leads/', include('leads.urls')),
    path('import/', include('import_service.urls')),
    path('reminders/', include('reminders.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
