from django.contrib.auth import get_user_model
from django.db.models import F
from django.utils.deprecation import MiddlewareMixin


class ClickTrackingMiddleware(MiddlewareMixin):
    """Increment click_count for authenticated users on meaningful GETs."""

    SKIP_PREFIXES = (
        "/static/",
        "/media/",
        "/admin/",
        "/reports/scan-version/",
        "/reports/raw/",
    )

    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.method != "GET":
            return None
        user = getattr(request, "user", None)
        if user is None or not user.is_authenticated:
            return None
        path = request.path
        if any(path.startswith(prefix) for prefix in self.SKIP_PREFIXES):
            return None
        get_user_model().objects.filter(pk=user.pk).update(
            click_count=F("click_count") + 1
        )
        return None
