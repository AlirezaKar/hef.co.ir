"""User-facing error pages that never expose source code or internals."""

from __future__ import annotations

import logging
import re

from django.shortcuts import render

logger = logging.getLogger(__name__)

_UNSAFE = re.compile(
    r"(\.py\b|\\|traceback|exception|middleware|settings|/backend/|/apps/|File \"|Resolver404|No .+ matches)",
    re.IGNORECASE,
)


def _safe_404_message(exception) -> tuple[str, str]:
    """Return (title, message) for a 404 response."""
    raw = str(exception or "").strip()
    if raw and not _UNSAFE.search(raw) and ("گزارش" in raw or "تاریخچه" in raw):
        title = "فایل تاریخچه یافت نشد" if "تاریخچه" in raw else "گزارش یافت نشد"
        return title, raw.rstrip(".") + "."
    return "صفحه یافت نشد", "صفحه مورد نظر یافت نشد."


def render_error(request, *, status: int, title: str, message: str, template_name: str):
    return render(
        request,
        template_name,
        {
            "status_code": status,
            "title": title,
            "message": message,
        },
        status=status,
    )


def not_found(request, exception=None):
    title, message = _safe_404_message(exception)
    return render_error(
        request,
        status=404,
        title=title,
        message=message,
        template_name="errors/404.html",
    )


def server_error(request):
    return render_error(
        request,
        status=500,
        title="خطای سرور",
        message="مشکلی پیش آمد. لطفاً کمی بعد دوباره تلاش کنید.",
        template_name="errors/500.html",
    )


def permission_denied(request, exception=None):
    return render_error(
        request,
        status=403,
        title="دسترسی مجاز نیست",
        message="شما اجازه مشاهده این بخش را ندارید.",
        template_name="errors/403.html",
    )


def bad_request(request, exception=None):
    return render_error(
        request,
        status=400,
        title="درخواست نامعتبر",
        message="درخواست ارسال‌شده معتبر نیست.",
        template_name="errors/400.html",
    )


def csrf_failure(request, reason=""):
    return render_error(
        request,
        status=403,
        title="نشست نامعتبر",
        message="لطفاً صفحه را تازه کنید و دوباره تلاش کنید.",
        template_name="errors/403.html",
    )
