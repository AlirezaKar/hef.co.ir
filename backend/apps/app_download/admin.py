from django.contrib import admin

from .models import DownloadCategory, DownloadFile, DownloadReport


@admin.register(DownloadCategory)
class DownloadCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "slug")


@admin.register(DownloadFile)
class DownloadFileAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "file_type",
        "category",
        "visibility",
        "download_count",
        "is_active",
        "created_at",
    )
    list_filter = ("visibility", "file_type", "category", "is_active")
    search_fields = ("title", "original_name", "tags")
    readonly_fields = ("download_count", "size_bytes", "file_type", "created_at", "updated_at")


@admin.register(DownloadReport)
class DownloadReportAdmin(admin.ModelAdmin):
    list_display = ("id", "file", "reason", "reporter", "created_at")
    list_filter = ("reason", "created_at")
    search_fields = ("reason", "details", "file__title")
    readonly_fields = ("created_at",)
