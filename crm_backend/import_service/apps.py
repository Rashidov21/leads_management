"""Import service app configuration."""
from django.apps import AppConfig


class ImportServiceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'import_service'
