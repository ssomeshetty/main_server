from django.apps import AppConfig


class CoreConfig(AppConfig):
    """
    Core application configuration for the Karnataka Politicians Tracker.
    
    This app contains all the models, serializers, views, and utilities
    for the main functionality of the public tracker.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'politicians_tracker.apps.core'
    verbose_name = 'Karnataka Politicians Tracker Core'
    
    def ready(self):
        """Import signals when app is ready."""
        # Import signals (if any)
        # import politicians_tracker.apps.core.signals
        pass
