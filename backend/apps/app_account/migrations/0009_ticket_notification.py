import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app_account", "0008_remove_cms_models"),
    ]

    operations = [
        migrations.CreateModel(
            name="Ticket",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("subject", models.CharField(max_length=200, verbose_name="موضوع")),
                ("message", models.TextField(verbose_name="پیام")),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "در انتظار بررسی"),
                            ("approved", "تأیید شده"),
                            ("rejected", "رد شده"),
                        ],
                        db_index=True,
                        default="pending",
                        max_length=20,
                        verbose_name="وضعیت",
                    ),
                ),
                (
                    "admin_reply",
                    models.TextField(blank=True, verbose_name="پاسخ ادمین"),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="زمان ایجاد"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="زمان به‌روزرسانی"),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tickets",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="کاربر",
                    ),
                ),
            ],
            options={
                "verbose_name": "تیکت",
                "verbose_name_plural": "تیکت‌ها",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="Notification",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "message",
                    models.CharField(max_length=300, verbose_name="پیام"),
                ),
                (
                    "is_read",
                    models.BooleanField(default=False, verbose_name="خوانده‌شده"),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="زمان"
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notifications",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="کاربر",
                    ),
                ),
                (
                    "ticket",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notifications",
                        to="app_account.ticket",
                        verbose_name="تیکت",
                    ),
                ),
            ],
            options={
                "verbose_name": "اعلان",
                "verbose_name_plural": "اعلان‌ها",
                "ordering": ["-created_at"],
            },
        ),
    ]
