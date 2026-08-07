# Generated manually for ResumePage singleton

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app_account", "0005_pagevisit_location"),
    ]

    operations = [
        migrations.CreateModel(
            name="ResumePage",
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
                    "title",
                    models.CharField(
                        default="رزومه", max_length=200, verbose_name="عنوان"
                    ),
                ),
                (
                    "body",
                    models.TextField(
                        blank=True,
                        help_text="محتوای HTML با TinyMCE",
                        verbose_name="محتوا",
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True, verbose_name="زمان به‌روزرسانی"
                    ),
                ),
            ],
            options={
                "verbose_name": "صفحه رزومه",
                "verbose_name_plural": "صفحه رزومه",
            },
        ),
    ]
