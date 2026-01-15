from django.apps import AppConfig


class RobotsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'robots'
    verbose_name = 'AI Robots'

    def ready(self):
        import robots.signals  # noqa: F401
