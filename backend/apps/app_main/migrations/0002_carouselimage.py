# Generated manually for CarouselImage model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app_main", "0001_cms_from_account"),
    ]

    operations = [
        migrations.CreateModel(
            name="CarouselImage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("image", models.ImageField(help_text="تصویر اسلایدر صفحه اصلی", upload_to="carousel/", verbose_name="تصویر")),
                ("title", models.CharField(blank=True, help_text="عنوان اختیاری برای تصویر", max_length=200, verbose_name="عنوان")),
                ("order", models.PositiveIntegerField(default=0, help_text="ترتیب نمایش (اعداد کوچکتر اول نمایش داده می‌شوند)", verbose_name="ترتیب")),
                ("is_active", models.BooleanField(default=True, help_text="آیا این تصویر در اسلایدر نمایش داده شود", verbose_name="فعال")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="تاریخ به‌روزرسانی")),
            ],
            options={
                "verbose_name": "تصویر اسلایدر",
                "verbose_name_plural": "تصاویر اسلایدر",
                "ordering": ["order", "created_at"],
            },
        ),
    ]
