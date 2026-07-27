from django.apps import AppConfig


class AppAccountConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.app_account"
    label = "app_account"
    verbose_name = "حساب کاربری"

    def ready(self):
        from . import signals  # noqa: F401
