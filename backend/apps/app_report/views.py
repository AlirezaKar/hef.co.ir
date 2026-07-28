from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.views.decorators.http import require_GET

from apps.app_account.models import UserScanSetting

from .services import (
    classify_filename,
    maybe_rescan,
    read_report_html,
    rewrite_index_hrefs,
    rewrite_report_home_button,
    safe_resolve_report,
    scan_user_reports,
    user_report_dir,
)


def _file_url(filename: str) -> str:
    return reverse("report:report_file", kwargs={"filename": filename})


def _raw_url(filename: str) -> str:
    return reverse("report:report_raw", kwargs={"filename": filename})


def _home_url() -> str:
    return reverse("report:home")


def _load_report_html(username: str, filename: str) -> str:
    path = safe_resolve_report(username, filename)
    if path is None:
        raise Http404("گزارش یافت نشد")
    html = read_report_html(path)
    if classify_filename(filename, username) == "index":
        html = rewrite_index_hrefs(html, username, _file_url)
    else:
        # Wire the native report header button to the portal home page
        html = rewrite_report_home_button(html, _home_url())
    return html


@login_required
def home_view(request):
    return render(request, "report/home.html")


@login_required
@require_GET
def reports_index_view(request):
    username = request.user.username
    maybe_rescan(request.user)

    index_name = f"Index_{username}.htm"
    path = safe_resolve_report(username, index_name)
    if path is None:
        files = scan_user_reports(username)
        index_files = [f for f in files if f.report_type == "index"]
        if not index_files:
            return render(
                request,
                "report/missing.html",
                {
                    "title": "گزارش یافت نشد",
                    "message": (
                        f"فایل فهرست گزارش‌ها برای کاربر «{username}» پیدا نشد."
                    ),
                },
            )
        index_name = index_files[0].filename

    setting = UserScanSetting.objects.filter(user=request.user).first()
    return render(
        request,
        "report/embed.html",
        {
            "iframe_src": _raw_url(index_name),
            "filename": index_name,
            "scan_version": setting.scan_version if setting else 0,
            "page_title": "گزارش‌ها",
        },
    )


@login_required
@require_GET
def report_file_view(request, filename: str):
    """
    Open the matching report as a full page at a dynamic URL.
    Avoids iframe X-Frame-Options blocking (ERR_BLOCKED_BY_RESPONSE).
    """
    username = request.user.username
    maybe_rescan(request.user)
    html = _load_report_html(username, filename)
    return HttpResponse(html, content_type="text/html; charset=utf-8")


@login_required
@require_GET
@xframe_options_sameorigin
def report_raw_view(request, filename: str):
    """Serve report HTML for the index iframe embed (same-origin only)."""
    html = _load_report_html(request.user.username, filename)
    return HttpResponse(html, content_type="text/html; charset=utf-8")


@login_required
@require_GET
def scan_version_view(request):
    version = maybe_rescan(request.user)
    setting = UserScanSetting.objects.filter(user=request.user).first()
    folder = user_report_dir(request.user.username)
    return JsonResponse(
        {
            "scan_version": version,
            "interval": setting.interval if setting else "1h",
            "folder_exists": folder.is_dir(),
        }
    )
