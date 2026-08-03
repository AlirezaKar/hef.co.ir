from django.contrib.auth import get_user_model
from django.db.models import F
from django.urls import Resolver404, resolve
from django.utils.deprecation import MiddlewareMixin

from .models import PageVisit
from .utils import get_client_ip, _mac_from_ip

# Persian labels for known named routes (namespace:name)
PAGE_LABELS = {
    "account:landing": "صفحه اصلی (لندینگ)",
    "account:login": "ورود",
    "account:signup": "ثبت‌نام",
    "account:logout": "خروج",
    "account:profile": "پروفایل",
    "account:about": "درباره ما",
    "account:faq": "سؤالات متداول",
    "account:contact": "تماس با ما",
    "account:tinymce_upload": "آپلود TinyMCE",
    "report:home": "خانه",
    "report:index": "تاریخچه",
    "report:trading_account_create": "ایجاد حساب ترید",
    "report:history_account": "حساب ترید (تاریخچه)",
    "report:history_file": "فایل تاریخچه",
}


def resolve_page_location(path: str) -> tuple[str, str]:
    """Return (url_name, page_label) for a request path."""
    try:
        match = resolve(path)
    except Resolver404:
        return "", path[:200]

    if match.namespaces:
        url_name = f"{':'.join(match.namespaces)}:{match.url_name}"
    else:
        url_name = match.url_name or ""

    label = PAGE_LABELS.get(url_name, "")
    if not label:
        label = url_name or path[:200]
    return url_name[:200], label[:200]


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
        url_name, page_label = resolve_page_location(path)

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
            url_name=url_name,
            page_label=page_label,
            user_agent=ua,
        )
        return None
