"""Admin datetime range filters."""

from datetime import datetime, time

from django.contrib import admin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class DateTimeFromToFilter(admin.SimpleListFilter):
    """Filter by created_at date range via query params (from/to date)."""

    title = _("بازه تاریخ و زمان")
    parameter_name = "created_range"

    # Used with DateFieldListFilter-style params via template; we use
    # created_at__date__gte / created_at__date__lte via this filter's lookups.
    # Simpler approach: expose Today / Yesterday / This week / This month.

    def lookups(self, request, model_admin):
        return (
            ("today", "امروز"),
            ("yesterday", "دیروز"),
            ("week", "۷ روز اخیر"),
            ("month", "۳۰ روز اخیر"),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if not value:
            return queryset
        now = timezone.localtime(timezone.now())
        today_start = timezone.make_aware(datetime.combine(now.date(), time.min))
        if value == "today":
            return queryset.filter(created_at__gte=today_start)
        if value == "yesterday":
            from datetime import timedelta

            yesterday = today_start - timedelta(days=1)
            return queryset.filter(created_at__gte=yesterday, created_at__lt=today_start)
        if value == "week":
            from datetime import timedelta

            return queryset.filter(created_at__gte=today_start - timedelta(days=7))
        if value == "month":
            from datetime import timedelta

            return queryset.filter(created_at__gte=today_start - timedelta(days=30))
        return queryset


class CreatedAtDateFilter(admin.DateFieldListFilter):
    """Date filter for DateTimeField created_at (day granularity)."""

    def __init__(self, field, request, params, model, model_admin, field_path):
        super().__init__(field, request, params, model, model_admin, field_path)
        self.title = "تاریخ"
