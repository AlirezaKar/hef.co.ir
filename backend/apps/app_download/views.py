from __future__ import annotations

import json
from pathlib import Path

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Count, Q, Sum
from django.http import FileResponse, Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from .models import DownloadCategory, DownloadFile, DownloadReport


def _is_superuser(user) -> bool:
    return bool(user.is_authenticated and user.is_active and user.is_superuser)


superuser_required = user_passes_test(_is_superuser)


def _client_ip(request) -> str | None:
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def _visible_files_qs(request):
    qs = (
        DownloadFile.objects.filter(is_active=True)
        .select_related("category")
        .order_by("-created_at")
    )
    if request.user.is_authenticated:
        return qs
    return qs.filter(visibility=DownloadFile.VISIBILITY_PUBLIC)


def _files_payload(qs):
    return [f.to_portal_dict() for f in qs]


def _categories_payload():
    return list(
        DownloadCategory.objects.filter(is_active=True)
        .order_by("sort_order", "name")
        .values("id", "name", "slug")
    )


@require_GET
def index_view(request):
    files = _files_payload(_visible_files_qs(request))
    categories = _categories_payload()
    return render(
        request,
        "download/index.html",
        {
            "files_json": json.dumps(files, ensure_ascii=False),
            "categories_json": json.dumps(categories, ensure_ascii=False),
            "manage_url": reverse("download:manage") if _is_superuser(request.user) else "",
        },
    )


@superuser_required
@require_GET
def manage_view(request):
    qs = DownloadFile.objects.select_related("category").order_by("-created_at")
    files = _files_payload(qs)
    categories = _categories_payload()
    stats = qs.aggregate(
        total=Count("id"),
        public_count=Count("id", filter=Q(visibility=DownloadFile.VISIBILITY_PUBLIC)),
        private_count=Count("id", filter=Q(visibility=DownloadFile.VISIBILITY_PRIVATE)),
        downloads_sum=Sum("download_count"),
    )
    return render(
        request,
        "download/manage.html",
        {
            "files_json": json.dumps(files, ensure_ascii=False),
            "categories_json": json.dumps(categories, ensure_ascii=False),
            "stats": {
                "total": stats["total"] or 0,
                "public": stats["public_count"] or 0,
                "private": stats["private_count"] or 0,
                "downloads": stats["downloads_sum"] or 0,
            },
        },
    )


@superuser_required
@require_POST
def upload_view(request):
    title = (request.POST.get("title") or "").strip()
    category_id = request.POST.get("category_id") or ""
    tags = (request.POST.get("tags") or "").strip()
    visibility = request.POST.get("visibility") or DownloadFile.VISIBILITY_PUBLIC
    if visibility not in dict(DownloadFile.VISIBILITY_CHOICES):
        visibility = DownloadFile.VISIBILITY_PUBLIC
    password_enabled = request.POST.get("password_enabled") in ("1", "true", "on", "yes")
    password = (request.POST.get("password") or "").strip()

    category = None
    if category_id:
        category = DownloadCategory.objects.filter(pk=category_id, is_active=True).first()

    uploads = request.FILES.getlist("files")
    if not uploads:
        messages.error(request, "هیچ فایلی انتخاب نشده است.")
        return redirect("download:manage")

    created = 0
    for upload in uploads:
        item = DownloadFile(
            title=title or Path(upload.name).stem,
            original_name=Path(upload.name).name,
            file=upload,
            category=category,
            tags=tags,
            visibility=visibility,
            uploaded_by=request.user if request.user.is_authenticated else None,
        )
        if password_enabled and password:
            item.set_password(password)
        item.save()
        created += 1

    messages.success(request, f"{created} فایل با موفقیت آپلود شد.")
    return redirect("download:manage")


@superuser_required
@require_POST
def update_view(request, pk: int):
    item = get_object_or_404(DownloadFile, pk=pk)
    title = (request.POST.get("title") or "").strip()
    category_id = request.POST.get("category_id") or ""
    tags = (request.POST.get("tags") or "").strip()
    visibility = request.POST.get("visibility") or item.visibility
    if visibility not in dict(DownloadFile.VISIBILITY_CHOICES):
        visibility = item.visibility
    password_enabled = request.POST.get("password_enabled") in ("1", "true", "on", "yes")
    password = (request.POST.get("password") or "").strip()

    if title:
        item.title = title
    item.tags = tags
    item.visibility = visibility
    item.category = (
        DownloadCategory.objects.filter(pk=category_id, is_active=True).first()
        if category_id
        else None
    )

    if password_enabled:
        if password:
            item.set_password(password)
        # keep existing hash if enabled but password left blank
    else:
        item.password_hash = ""

    replace = request.FILES.get("file")
    if replace:
        if item.file:
            item.file.delete(save=False)
        item.file = replace
        item.original_name = Path(replace.name).name

    item.save()
    messages.success(request, "تغییرات فایل ذخیره شد.")
    return redirect("download:manage")


@superuser_required
@require_POST
def delete_view(request, pk: int):
    item = get_object_or_404(DownloadFile, pk=pk)
    if item.file:
        item.file.delete(save=False)
    item.delete()
    messages.success(request, "فایل حذف شد.")
    return redirect("download:manage")


@require_http_methods(["GET", "POST"])
def download_file_view(request, pk: int):
    item = get_object_or_404(DownloadFile, pk=pk, is_active=True)

    if item.visibility == DownloadFile.VISIBILITY_PRIVATE and not request.user.is_authenticated:
        return redirect(f"{reverse('account:login')}?next={request.path}")

    password = ""
    if request.method == "POST":
        password = (request.POST.get("password") or "").strip()
    elif request.GET.get("password"):
        password = request.GET.get("password") or ""

    if item.has_password and not item.check_file_password(password):
        if request.method == "POST" or request.GET.get("password") is not None:
            messages.error(request, "رمز عبور فایل نادرست است.")
        return render(
            request,
            "download/password.html",
            {"item": item},
        )

    if not item.file:
        raise Http404("File missing")

    item.download_count = (item.download_count or 0) + 1
    item.save(update_fields=["download_count", "updated_at"])

    try:
        handle = item.file.open("rb")
    except FileNotFoundError as exc:
        raise Http404("File missing") from exc

    filename = item.original_name or Path(item.file.name).name
    return FileResponse(handle, as_attachment=True, filename=filename)


@require_POST
def report_view(request):
    file_id = request.POST.get("file_id")
    reason = (request.POST.get("reason") or "").strip()
    details = (request.POST.get("details") or "").strip()
    item = get_object_or_404(DownloadFile, pk=file_id, is_active=True)

    if not reason:
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"ok": False, "error": "reason_required"}, status=400)
        messages.error(request, "لطفاً دلیل گزارش را انتخاب کنید.")
        return redirect("download:index")

    DownloadReport.objects.create(
        file=item,
        reason=reason,
        details=details,
        reporter=request.user if request.user.is_authenticated else None,
        reporter_ip=_client_ip(request),
    )

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"ok": True})

    messages.success(request, "گزارش شما ثبت شد.")
    return redirect("download:index")
