"""
URL configuration for leads_management project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('leads.urls', namespace='leads')),
    path('kpi/', include('kpi.urls', namespace='kpi')),
    path('campaigns/', include('campaigns.urls', namespace='campaigns')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

