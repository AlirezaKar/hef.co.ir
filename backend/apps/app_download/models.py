from __future__ import annotations

from pathlib import Path

from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.db import models
from django.utils.text import slugify

from .storage import get_cdn_storage


class DownloadCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("sort_order", "name")
        verbose_name = "Download category"
        verbose_name_plural = "Download categories"

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name, allow_unicode=True) or "category"
            slug = base
            n = 2
            while DownloadCategory.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{n}"
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)


class DownloadFile(models.Model):
    VISIBILITY_PUBLIC = "public"
    VISIBILITY_PRIVATE = "private"
    VISIBILITY_CHOICES = (
        (VISIBILITY_PUBLIC, "Public"),
        (VISIBILITY_PRIVATE, "Private"),
    )

    title = models.CharField(max_length=255)
    original_name = models.CharField(max_length=255, blank=True)
    file = models.FileField(upload_to="downloads/%Y/%m/", storage=get_cdn_storage)
    file_type = models.CharField(max_length=20, blank=True)
    size_bytes = models.BigIntegerField(default=0)
    category = models.ForeignKey(
        DownloadCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="files",
    )
    tags = models.CharField(max_length=255, blank=True)
    visibility = models.CharField(
        max_length=20,
        choices=VISIBILITY_CHOICES,
        default=VISIBILITY_PUBLIC,
    )
    password_hash = models.CharField(max_length=128, blank=True)
    download_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_download_files",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Download file"
        verbose_name_plural = "Download files"

    def __str__(self) -> str:
        return self.title

    @property
    def has_password(self) -> bool:
        return bool(self.password_hash)

    @property
    def size_display(self) -> str:
        size = float(self.size_bytes or 0)
        if size < 1024:
            return f"{int(size)} B"
        if size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        if size < 1024 * 1024 * 1024:
            return f"{size / (1024 * 1024):.1f} MB"
        return f"{size / (1024 * 1024 * 1024):.1f} GB"

    def set_password(self, raw: str | None) -> None:
        raw = (raw or "").strip()
        self.password_hash = make_password(raw) if raw else ""

    def check_file_password(self, raw: str | None) -> bool:
        if not self.password_hash:
            return True
        return check_password(raw or "", self.password_hash)

    def refresh_file_meta(self) -> None:
        if self.file and self.file.name:
            self.original_name = self.original_name or Path(self.file.name).name
            ext = Path(self.file.name).suffix.lstrip(".").upper() or "FILE"
            self.file_type = ext
            try:
                self.size_bytes = self.file.size
            except Exception:
                self.size_bytes = self.size_bytes or 0

    def save(self, *args, **kwargs):
        if self.file and not self.original_name:
            self.original_name = Path(self.file.name).name
        if self.file:
            self.refresh_file_meta()
        super().save(*args, **kwargs)

    def to_portal_dict(self) -> dict:
        return {
            "id": self.pk,
            "title": self.title,
            "name": self.original_name or Path(self.file.name).name if self.file else "",
            "type": self.file_type or "FILE",
            "size": self.size_display,
            "size_bytes": self.size_bytes,
            "date": self.created_at.strftime("%Y-%m-%d") if self.created_at else "",
            "downloads": self.download_count,
            "category": self.category.name if self.category_id else "",
            "category_id": self.category_id,
            "tags": self.tags,
            "visibility": self.visibility,
            "password": self.has_password,
            "download_url": f"/download/file/{self.pk}/",
        }


class DownloadReport(models.Model):
    file = models.ForeignKey(
        DownloadFile,
        on_delete=models.CASCADE,
        related_name="reports",
    )
    reason = models.CharField(max_length=120)
    details = models.TextField(blank=True)
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="download_reports",
    )
    reporter_ip = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Download report"
        verbose_name_plural = "Download reports"

    def __str__(self) -> str:
        return f"Report #{self.pk} · {self.file_id}"
