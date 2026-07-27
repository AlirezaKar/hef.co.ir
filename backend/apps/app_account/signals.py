from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import User, UserScanSetting


@receiver(post_save, sender=User)
def on_user_created(sender, instance, created, **kwargs):
    """Create scan settings and report folder for every new user."""
    if not created:
        return

    UserScanSetting.objects.get_or_create(user=instance)

    # Avoid circular import at module load
    from apps.app_report.services import ensure_user_report_dir

    ensure_user_report_dir(instance.username)
