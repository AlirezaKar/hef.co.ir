from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.db import models
from django.utils.html import format_html

from .admin_filters import DateTimeFromToFilter
from .models import LoginAttempt, Notification, PageVisit, Ticket, TradingAccount, User


admin.site.unregister(Group)


class LoginAttemptInline(admin.TabularInline):
    model = LoginAttempt
    extra = 0
    can_delete = False
    readonly_fields = (
        "username_tried",
        "ip_address",
        "successful_badge",
        "created_at",
    )
    fields = readonly_fields

    def has_add_permission(self, request, obj=None):
        return False

    @admin.display(description="وضعیت")
    def successful_badge(self, obj):
        if obj.successful:
            return format_html(
                '<span style="color:#0a7;font-weight:600;">موفق</span>'
            )
        return format_html(
            '<span style="color:#c00;font-weight:600;">ناموفق</span>'
        )


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "username",
        "email",
        "phone_number",
        "ip_address",
        "mac_address",
        "mac_source_hint",
        "click_count",
        "login_attempt_count",
        "is_staff",
    )
    list_filter = ("is_staff", "is_superuser", "is_active", "mac_source")
    search_fields = ("username", "email", "phone_number", "national_id")
    readonly_fields = (
        "ip_address",
        "mac_address",
        "mac_source",
        "mac_source_hint",
        "click_count",
        "login_attempt_count",
        "date_joined",
        "last_login",
    )
    inlines = [LoginAttemptInline]

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            "اطلاعات شخصی",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "phone_number",
                    "national_id",
                    "picture",
                )
            },
        ),
        (
            "اطلاعات شبکه (فقط خواندنی)",
            {
                "fields": (
                    "ip_address",
                    "mac_address",
                    "mac_source",
                    "mac_source_hint",
                    "click_count",
                    "login_attempt_count",
                )
            },
        ),
        (
            "دسترسی‌ها",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("تاریخ‌ها", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "phone_number",
                    "password1",
                    "password2",
                ),
            },
        ),
    )

    @admin.display(description="راهنمای منبع MAC")
    def mac_source_hint(self, obj):
        labels = {
            "ip": "IP — از آدرس MAC مرتبط با IP کاربر",
            "hdd": "HDD — از شناسه سخت‌افزار/دیسک",
            "generated": "تولیدشده — به‌صورت تصادفی تولید شده",
        }
        return labels.get(obj.mac_source, "—")


@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    list_display = (
        "username_tried",
        "user",
        "ip_address",
        "successful_badge",
        "created_at",
    )
    list_filter = (
        "successful",
        DateTimeFromToFilter,
        ("created_at", admin.DateFieldListFilter),
    )
    date_hierarchy = "created_at"
    search_fields = ("username_tried", "ip_address", "user__username")
    readonly_fields = (
        "user",
        "username_tried",
        "ip_address",
        "successful",
        "created_at",
    )
    ordering = ("-created_at",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    @admin.display(description="وضعیت", boolean=False)
    def successful_badge(self, obj):
        if obj.successful:
            return format_html(
                '<span style="color:#0a7;font-weight:600;">موفق</span>'
            )
        return format_html(
            '<span style="color:#c00;font-weight:600;">ناموفق</span>'
        )


@admin.register(PageVisit)
class PageVisitAdmin(admin.ModelAdmin):
    list_display = (
        "visitor_label",
        "user",
        "page_label",
        "url_name",
        "path",
        "ip_address",
        "mac_address",
        "created_at",
    )
    list_filter = (
        DateTimeFromToFilter,
        ("created_at", admin.DateFieldListFilter),
        "visitor_label",
        "page_label",
    )
    date_hierarchy = "created_at"
    search_fields = (
        "visitor_label",
        "ip_address",
        "mac_address",
        "path",
        "url_name",
        "page_label",
        "user__username",
    )
    readonly_fields = (
        "user",
        "visitor_label",
        "ip_address",
        "mac_address",
        "path",
        "url_name",
        "page_label",
        "user_agent",
        "created_at",
    )
    ordering = ("-created_at",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(TradingAccount)
class TradingAccountAdmin(admin.ModelAdmin):
    list_display = ("trading_acc_username", "broker", "created_at", "updated_at")
    search_fields = ("trading_acc_username", "broker", "users__username")
    filter_horizontal = ("users",)
    readonly_fields = ("created_at", "updated_at")
    list_filter = (("created_at", admin.DateFieldListFilter),)
    date_hierarchy = "created_at"


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "subject",
        "status_badge",
        "created_at",
        "updated_at",
    )
    list_filter = ("status", ("created_at", admin.DateFieldListFilter))
    search_fields = ("subject", "message", "user__username", "user__email")
    readonly_fields = ("user", "subject", "message", "created_at", "updated_at")
    ordering = (
        # PENDING first, then REJECTED, then APPROVED
        models.Case(
            models.When(status="pending", then=models.Value(0)),
            models.When(status="rejected", then=models.Value(1)),
            models.When(status="approved", then=models.Value(2)),
            output_field=models.IntegerField(),
        ),
        "-created_at",
    )
    fieldsets = (
        (None, {
            "fields": ("user", "subject", "message", "status"),
        }),
        ("پاسخ ادمین", {
            "description": (
                "برای وضعیت «رد شده» دلیل رد و برای «تأیید شده» پاسخ را بنویسید. "
                "در هر دو حالت فیلد پاسخ ادمین الزامی است."
            ),
            "fields": ("admin_reply",),
        }),
        ("زمان‌ها", {
            "fields": ("created_at", "updated_at"),
        }),
    )

    @admin.display(description="وضعیت")
    def status_badge(self, obj):
        colors = {
            "pending": "#e6a817",
            "approved": "#0a7",
            "rejected": "#c00",
        }
        labels = {
            "pending": "در انتظار",
            "approved": "تأیید",
            "rejected": "رد شده",
        }
        c = colors.get(obj.status, "#888")
        return format_html(
            '<span style="color:{};font-weight:600;">{}</span>',
            c,
            labels.get(obj.status, obj.status),
        )

    def save_model(self, request, obj, form, change):
        """Create a notification when admin changes ticket status."""
        from .models import Notification

        old_status = None
        if change:
            old_status = Ticket.objects.filter(pk=obj.pk).values_list(
                "status", flat=True
            ).first()
        super().save_model(request, obj, form, change)
        if change and old_status and old_status != obj.status:
            status_labels = {
                "pending": "در انتظار بررسی",
                "approved": "تأیید شده",
                "rejected": "رد شده",
            }
            if obj.status == "rejected":
                reason = obj.admin_reply or "(بدون دلیل مشخص)"
                Notification.objects.create(
                    user=obj.user,
                    ticket=obj,
                    message=f"تیکت «{obj.subject}» رد شد. دلیل: {reason}",
                )
            elif obj.status == "approved":
                reply = obj.admin_reply or ""
                Notification.objects.create(
                    user=obj.user,
                    ticket=obj,
                    message=f"تیکت «{obj.subject}» تأیید شد. پاسخ: {reply}",
                )

    def clean(self):
        """Validate at form level — admin_reply required for approved/rejected."""
        pass

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return form

    def save_form(self, request, form, change):
        obj = super().save_form(request, form, change)
        # Enforce: admin_reply required when status is approved or rejected
        if change and obj.status in ("approved", "rejected"):
            if not (obj.admin_reply or "").strip():
                label = "پاسخ" if obj.status == "approved" else "دلیل رد"
                from django.contrib import messages
                messages.error(
                    request,
                    f"لطفاً {label} را وارد کنید.",
                )
                # Revert status change to prevent saving without reply
                original = Ticket.objects.filter(pk=obj.pk).first()
                if original:
                    obj.status = original.status
                    obj.admin_reply = original.admin_reply
        return obj


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "message_short", "ticket", "is_read", "created_at")
    list_filter = ("is_read", ("created_at", admin.DateFieldListFilter))
    search_fields = ("message", "user__username")
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)

    @admin.display(description="پیام")
    def message_short(self, obj):
        return (obj.message[:80] + "…") if len(obj.message) > 80 else obj.message
