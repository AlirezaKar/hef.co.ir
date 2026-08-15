# Transfer CMS model ownership to app_main without touching existing tables.

import django.db.models.deletion
import parler.fields
import parler.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("app_account", "0007_parler_cms_translations"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name="AboutPage",
                    fields=[
                        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                        ("updated_at", models.DateTimeField(auto_now=True, verbose_name="زمان به‌روزرسانی")),
                    ],
                    options={
                        "verbose_name": "صفحه درباره ما",
                        "verbose_name_plural": "صفحه درباره ما",
                        "db_table": "app_account_aboutpage",
                    },
                    bases=(parler.models.TranslatableModel,),
                ),
                migrations.CreateModel(
                    name="ResumePage",
                    fields=[
                        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                        ("updated_at", models.DateTimeField(auto_now=True, verbose_name="زمان به‌روزرسانی")),
                    ],
                    options={
                        "verbose_name": "صفحه رزومه",
                        "verbose_name_plural": "صفحه رزومه",
                        "db_table": "app_account_resumepage",
                    },
                    bases=(parler.models.TranslatableModel,),
                ),
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
                        "db_table": "app_account_sitecontent",
                    },
                    bases=(parler.models.TranslatableModel,),
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
                                to="app_main.aboutpage",
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
                                to="app_main.resumepage",
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
                                to="app_main.sitecontent",
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
            ],
            database_operations=[],
        ),
    ]
