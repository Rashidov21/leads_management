"""
URL configuration for crm_project project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.defaults import page_not_found, server_error

# Custom error handlers
handler404 = 'crm_project.views.custom_404'
handler500 = 'crm_project.views.custom_500'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('crm_app.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

