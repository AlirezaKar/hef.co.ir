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


class PageVisit(models.Model):
    """Visit log for every page load — authenticated user or anonymous."""

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="page_visits",
        verbose_name="کاربر",
    )
    visitor_label = models.CharField(
        "برچسب بازدیدکننده",
        max_length=150,
        default="anonymous",
        help_text="نام کاربری یا anonymous",
    )
    ip_address = models.GenericIPAddressField("آدرس IP", blank=True, null=True)
    mac_address = models.CharField("آدرس MAC", max_length=32, blank=True)
    path = models.CharField("مسیر", max_length=500)
    url_name = models.CharField("نام مسیر URL", max_length=200, blank=True)
    page_label = models.CharField("برچسب صفحه", max_length=200, blank=True)
    user_agent = models.CharField("User-Agent", max_length=500, blank=True)
    created_at = models.DateTimeField("زمان", default=timezone.now, db_index=True)

    class Meta:
        verbose_name = "بازدید صفحه"
        verbose_name_plural = "بازدیدهای صفحه"
        ordering = ["-created_at"]

    def __str__(self):
        where = self.page_label or self.path
        return f"{self.visitor_label} — {where}"


class TradingAccount(models.Model):
    trading_acc_username = models.CharField(
        "شماره حساب",
        max_length=150,
        unique=True,
    )
    broker = models.CharField("نام کارگزاری", max_length=200)
    users = models.ManyToManyField(
        User,
        related_name="trading_accounts",
        blank=True,
        verbose_name="کاربران",
    )
    created_at = models.DateTimeField("زمان ایجاد", default=timezone.now)
    updated_at = models.DateTimeField("زمان به‌روزرسانی", auto_now=True)

    class Meta:
        verbose_name = "حساب ترید"
        verbose_name_plural = "حساب‌های ترید"
        ordering = ["trading_acc_username"]

    def __str__(self):
        return f"{self.trading_acc_username} — {self.broker}"
