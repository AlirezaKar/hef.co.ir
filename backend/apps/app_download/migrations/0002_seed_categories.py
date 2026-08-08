from django.db import migrations


CATEGORIES = (
    ("مستندات", "documents", 10),
    ("نرم‌افزار", "software", 20),
    ("آموزشی", "training", 30),
    ("عمومی", "general", 40),
)


def seed_categories(apps, schema_editor):
    DownloadCategory = apps.get_model("app_download", "DownloadCategory")
    for name, slug, sort_order in CATEGORIES:
        DownloadCategory.objects.get_or_create(
            slug=slug,
            defaults={"name": name, "sort_order": sort_order, "is_active": True},
        )


def unseed_categories(apps, schema_editor):
    DownloadCategory = apps.get_model("app_download", "DownloadCategory")
    DownloadCategory.objects.filter(slug__in=[c[1] for c in CATEGORIES]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("app_download", "0001_initial_download_center"),
    ]

    operations = [
        migrations.RunPython(seed_categories, unseed_categories),
    ]
