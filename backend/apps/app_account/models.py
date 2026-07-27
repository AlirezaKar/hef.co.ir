import re
import uuid
from io import BytesIO
from pathlib import Path

from django.contrib.auth.models import AbstractUser
from django.core.files.base import ContentFile
from django.db import models
from django.utils import timezone
from PIL import Image


def profile_picture_upload_to(instance, filename):
    name = Path(filename).name
    if not name.lower().endswith(".webp"):
        stem = re.sub(r"[^a-zA-Z0-9_-]", "_", Path(name).stem)[:40] or "profile"
        name = f"{instance.username}_{stem}.webp"
    return f"profile_picture/{name}"


class User(AbstractUser):
    class MacSource(models.TextChoices):
        IP = "ip", "IP"
        HDD = "hdd", "HDD"
        GENERATED = "generated", "تولیدشده"

    email = models.EmailField("email address", unique=True)
    phone_number = models.CharField("phone number", max_length=11)
    picture = models.ImageField(
        "profile picture",
        upload_to=profile_picture_upload_to,
        blank=True,
        null=True,
    )
    national_id = models.CharField("national ID", max_length=10, blank=True)
    ip_address = models.GenericIPAddressField("IP address", blank=True, null=True)
    mac_address = models.CharField("MAC address", max_length=32, blank=True)
    mac_source = models.CharField(
        "MAC source",
        max_length=16,
        choices=MacSource.choices,
        blank=True,
    )
    click_count = models.PositiveIntegerField("click count", default=0)
    login_attempt_count = models.PositiveIntegerField("login attempt count", default=0)

    REQUIRED_FIELDS = ["email", "phone_number"]

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"

    def __str__(self):
        return self.username

    def save_picture_as_webp(self, uploaded_file):
        """Validate and convert an uploaded image to WebP."""
        image = Image.open(uploaded_file)
        image = image.convert("RGB")
        buffer = BytesIO()
        image.save(buffer, format="WEBP", quality=85)
        buffer.seek(0)
        filename = f"{self.username}_{uuid.uuid4().hex[:8]}.webp"
        if self.picture:
            self.picture.delete(save=False)
        self.picture.save(filename, ContentFile(buffer.read()), save=False)


class LoginAttempt(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="login_attempts",
        verbose_name="کاربر",
    )
    username_tried = models.CharField("نام کاربری تلاش‌شده", max_length=150)
    ip_address = models.GenericIPAddressField("آدرس IP", blank=True, null=True)
    successful = models.BooleanField("موفق", default=False)
    created_at = models.DateTimeField("زمان", default=timezone.now)

    class Meta:
        verbose_name = "تلاش ورود"
        verbose_name_plural = "تلاش‌های ورود"
        ordering = ["-created_at"]

    def __str__(self):
        status = "موفق" if self.successful else "ناموفق"
        return f"{self.username_tried} — {status}"


class SiteContent(models.Model):
    class Page(models.TextChoices):
        ABOUT = "about", "درباره ما"
        CONTACT = "contact", "تماس با ما"

    page = models.CharField("صفحه", max_length=20, choices=Page.choices)
    key = models.CharField("کلید", max_length=100)
    value = models.TextField("مقدار")
    icon = models.CharField("آیکون (اختیاری)", max_length=50, blank=True)
    order = models.PositiveIntegerField("ترتیب", default=0)
    is_active = models.BooleanField("فعال", default=True)

    class Meta:
        verbose_name = "محتوای سایت"
        verbose_name_plural = "محتوای سایت"
        ordering = ["page", "order", "id"]

    def __str__(self):
        return f"{self.get_page_display()}: {self.key}"


class UserScanSetting(models.Model):
    class Interval(models.TextChoices):
        HOUR_1 = "1h", "هر ۱ ساعت"
        HOUR_3 = "3h", "هر ۳ ساعت"
        HOUR_6 = "6h", "هر ۶ ساعت"
        DAY_1 = "1d", "هر روز"

    INTERVAL_SECONDS = {
        "1h": 3600,
        "3h": 10800,
        "6h": 21600,
        "1d": 86400,
    }

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="scan_setting",
        verbose_name="کاربر",
    )
    interval = models.CharField(
        "بازه به‌روزرسانی",
        max_length=8,
        choices=Interval.choices,
        default=Interval.HOUR_1,
    )
    last_scan_at = models.DateTimeField("آخرین اسکن", blank=True, null=True)
    scan_version = models.PositiveIntegerField("نسخه اسکن", default=0)
    last_fingerprint = models.CharField("اثرانگشت پوشه", max_length=64, blank=True)

    class Meta:
        verbose_name = "تنظیمات اسکن"
        verbose_name_plural = "تنظیمات اسکن"

    def __str__(self):
        return f"{self.user.username} — {self.get_interval_display()}"

    @property
    def interval_seconds(self):
        return self.INTERVAL_SECONDS.get(self.interval, 3600)

    def mark_scanned(self):
        self.last_scan_at = timezone.now()
        self.scan_version = models.F("scan_version") + 1
        self.save(update_fields=["last_scan_at", "scan_version"])
        self.refresh_from_db(fields=["scan_version"])
