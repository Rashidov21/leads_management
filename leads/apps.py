from django.apps import AppConfig


class LeadsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'leads'
    
    def ready(self):
        """Configure admin site after apps are loaded."""
        # Prevent multiple calls in development
        if hasattr(self, '_admin_configured'):
            return
        
        from django.contrib import admin
        from django.conf import settings
        
        # Customize admin site
        admin.site.site_header = settings.ADMIN_SITE_HEADER
        admin.site.site_title = settings.ADMIN_SITE_TITLE
        admin.site.index_title = settings.ADMIN_INDEX_TITLE
        
        self._admin_configured = True

