# Remove CMS models from app_account state (tables kept for app_main).

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("app_account", "0007_parler_cms_translations"),
        ("app_main", "0001_cms_from_account"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.DeleteModel(name="AboutPageTranslation"),
                migrations.DeleteModel(name="ResumePageTranslation"),
                migrations.DeleteModel(name="SiteContentTranslation"),
                migrations.DeleteModel(name="AboutPage"),
                migrations.DeleteModel(name="ResumePage"),
                migrations.DeleteModel(name="SiteContent"),
            ],
            database_operations=[],
        ),
    ]
