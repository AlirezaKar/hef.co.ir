from django.contrib.auth import get_user_model
from django.db.models import F
from django.utils.deprecation import MiddlewareMixin

from .models import PageVisit
from .utils import get_client_ip, _mac_from_ip


class ClickTrackingMiddleware(MiddlewareMixin):
    """
    Record a PageVisit for every meaningful GET (auth + anonymous),
    and bump click_count for authenticated users.
    """

    SKIP_PREFIXES = (
        "/static/",
        "/media/",
        "/admin/",
        "/favicon",
    )

    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.method != "GET":
            return None
        path = request.path or "/"
        if any(path.startswith(prefix) for prefix in self.SKIP_PREFIXES):
            return None

        user = getattr(request, "user", None)
        authenticated = bool(user and user.is_authenticated)
        ip = get_client_ip(request)

        if authenticated:
            visitor_label = user.username
            get_user_model().objects.filter(pk=user.pk).update(
                click_count=F("click_count") + 1
            )
            user_fk = user
            mac = user.mac_address or (_mac_from_ip(ip) or "")
        else:
            visitor_label = "anonymous"
            user_fk = None
            mac = _mac_from_ip(ip) or ""

        ua = (request.META.get("HTTP_USER_AGENT") or "")[:500]
        PageVisit.objects.create(
            user=user_fk,
            visitor_label=visitor_label,
            ip_address=ip,
            mac_address=mac,
            path=path[:500],
            user_agent=ua,
        )
        return None
