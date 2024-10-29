from django.apps import AppConfig


class AppConfig(AppConfig):
    """Configuration for the 'app' Django application."""
    default_auto_field = "django.db.models.BigAutoField"
    name = "app"

    def ready(self):
        """Import the app's signals when the application is ready."""
        import app.signals
