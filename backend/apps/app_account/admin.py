from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.contrib.auth.models import Group
from .models import LoginAttempt, SiteContent, User, UserScanSetting


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
    list_filter = ("successful", "created_at")
    search_fields = ("username_tried", "ip_address", "user__username")
    readonly_fields = (
        "user",
        "username_tried",
        "ip_address",
        "successful",
        "created_at",
    )

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


@admin.register(SiteContent)
class SiteContentAdmin(admin.ModelAdmin):
    list_display = ("page", "key", "order", "is_active", "icon")
    list_filter = ("page", "is_active")
    search_fields = ("key", "value")
    list_editable = ("order", "is_active")


@admin.register(UserScanSetting)
class UserScanSettingAdmin(admin.ModelAdmin):
    list_display = ("user", "interval", "last_scan_at", "scan_version")
    list_filter = ("interval",)
    search_fields = ("user__username",)
    readonly_fields = ("last_scan_at", "scan_version", "last_fingerprint")
