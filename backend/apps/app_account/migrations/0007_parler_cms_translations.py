# Convert AboutPage / ResumePage / SiteContent to django-parler.
# Historical model state must inherit TranslatableModel before translation FKs are created.

import django.db.models.deletion
import parler.fields
import parler.models
from django.db import migrations, models


def copy_content_to_fa(apps, schema_editor):
    """Copy pre-parler columns into fa translation rows via SQL (state already dropped those fields)."""
    connection = schema_editor.connection
    AboutPageTranslation = apps.get_model("app_account", "AboutPageTranslation")
    ResumePageTranslation = apps.get_model("app_account", "ResumePageTranslation")
    SiteContentTranslation = apps.get_model("app_account", "SiteContentTranslation")

    with connection.cursor() as cursor:
        cursor.execute("SELECT id, title, body FROM app_account_aboutpage")
        for pk, title, body in cursor.fetchall():
            AboutPageTranslation.objects.update_or_create(
                master_id=pk,
                language_code="fa",
                defaults={"title": title or "درباره ما", "body": body or ""},
            )

        cursor.execute("SELECT id, title, body FROM app_account_resumepage")
        for pk, title, body in cursor.fetchall():
            ResumePageTranslation.objects.update_or_create(
                master_id=pk,
                language_code="fa",
                defaults={"title": title or "رزومه", "body": body or ""},
            )

        cursor.execute("SELECT id, key, value FROM app_account_sitecontent")
        for pk, key, value in cursor.fetchall():
            SiteContentTranslation.objects.update_or_create(
                master_id=pk,
                language_code="fa",
                defaults={"key": key or f"item-{pk}", "value": value or ""},
            )


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("app_account", "0006_resumepage"),
    ]

    operations = [
        # --- Update state so shared models inherit TranslatableModel (DB unchanged) ---
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.DeleteModel(name="AboutPage"),
                migrations.CreateModel(
                    name="AboutPage",
                    fields=[
                        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                        ("updated_at", models.DateTimeField(auto_now=True, verbose_name="زمان به‌روزرسانی")),
                    ],
                    options={
                        "verbose_name": "صفحه درباره ما",
                        "verbose_name_plural": "صفحه درباره ما",
                    },
                    bases=(parler.models.TranslatableModel,),
                ),
                migrations.DeleteModel(name="ResumePage"),
                migrations.CreateModel(
                    name="ResumePage",
                    fields=[
                        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                        ("updated_at", models.DateTimeField(auto_now=True, verbose_name="زمان به‌روزرسانی")),
                    ],
                    options={
                        "verbose_name": "صفحه رزومه",
                        "verbose_name_plural": "صفحه رزومه",
                    },
                    bases=(parler.models.TranslatableModel,),
                ),
                migrations.DeleteModel(name="SiteContent"),
                migrations.CreateModel(
                    name="SiteContent",
                    fields=[
                        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                        (
                            "page",
                            models.CharField(
                                choices=[
                                    ("about", "درباره ما"),
                                    ("contact", "تماس با ما"),
                                    ("faq", "سؤالات متداول"),
                                ],
                                max_length=20,
                                verbose_name="صفحه",
                            ),
                        ),
                        ("icon", models.CharField(blank=True, max_length=50, verbose_name="آیکون (اختیاری)")),
                        ("order", models.PositiveIntegerField(default=0, verbose_name="ترتیب")),
                        ("is_active", models.BooleanField(default=True, verbose_name="فعال")),
                    ],
                    options={
                        "verbose_name": "محتوای سایت",
                        "verbose_name_plural": "محتوای سایت",
                        "ordering": ["page", "order", "id"],
                    },
                    bases=(parler.models.TranslatableModel,),
                ),
            ],
            database_operations=[],
        ),
        migrations.CreateModel(
            name="AboutPageTranslation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("language_code", models.CharField(db_index=True, max_length=15, verbose_name="Language")),
                ("title", models.CharField(default="درباره ما", max_length=200, verbose_name="عنوان")),
                ("body", models.TextField(blank=True, help_text="محتوای HTML با TinyMCE", verbose_name="محتوا")),
                (
                    "master",
                    parler.fields.TranslationsForeignKey(
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="translations",
                        to="app_account.aboutpage",
                    ),
                ),
            ],
            options={
                "verbose_name": "صفحه درباره ما Translation",
                "db_table": "app_account_aboutpage_translation",
                "db_tablespace": "",
                "managed": True,
                "default_permissions": (),
                "constraints": [
                    models.UniqueConstraint(
                        fields=("language_code", "master"),
                        name="app_account_aboutpage_translation_uniq_lang",
                    )
                ],
            },
            bases=(parler.models.TranslatedFieldsModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name="ResumePageTranslation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("language_code", models.CharField(db_index=True, max_length=15, verbose_name="Language")),
                ("title", models.CharField(default="رزومه", max_length=200, verbose_name="عنوان")),
                ("body", models.TextField(blank=True, help_text="محتوای HTML با TinyMCE", verbose_name="محتوا")),
                (
                    "master",
                    parler.fields.TranslationsForeignKey(
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="translations",
                        to="app_account.resumepage",
                    ),
                ),
            ],
            options={
                "verbose_name": "صفحه رزومه Translation",
                "db_table": "app_account_resumepage_translation",
                "db_tablespace": "",
                "managed": True,
                "default_permissions": (),
                "constraints": [
                    models.UniqueConstraint(
                        fields=("language_code", "master"),
                        name="app_account_resumepage_translation_uniq_lang",
                    )
                ],
            },
            bases=(parler.models.TranslatedFieldsModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name="SiteContentTranslation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("language_code", models.CharField(db_index=True, max_length=15, verbose_name="Language")),
                ("key", models.CharField(max_length=100, verbose_name="کلید")),
                ("value", models.TextField(verbose_name="مقدار")),
                (
                    "master",
                    parler.fields.TranslationsForeignKey(
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="translations",
                        to="app_account.sitecontent",
                    ),
                ),
            ],
            options={
                "verbose_name": "محتوای سایت Translation",
                "db_table": "app_account_sitecontent_translation",
                "db_tablespace": "",
                "managed": True,
                "default_permissions": (),
                "constraints": [
                    models.UniqueConstraint(
                        fields=("language_code", "master"),
                        name="app_account_sitecontent_translation_uniq_lang",
                    )
                ],
            },
            bases=(parler.models.TranslatedFieldsModelMixin, models.Model),
        ),
        migrations.RunPython(copy_content_to_fa, noop_reverse),
        migrations.RunSQL(
            sql=[
                "ALTER TABLE app_account_aboutpage DROP COLUMN title",
                "ALTER TABLE app_account_aboutpage DROP COLUMN body",
                "ALTER TABLE app_account_resumepage DROP COLUMN title",
                "ALTER TABLE app_account_resumepage DROP COLUMN body",
                "ALTER TABLE app_account_sitecontent DROP COLUMN key",
                "ALTER TABLE app_account_sitecontent DROP COLUMN value",
            ],
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
