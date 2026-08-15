# Public CMS models (moved from app_account). Tables keep legacy names.
from django.db import models
from parler.models import TranslatableModel, TranslatedFields


class SiteContent(TranslatableModel):
    class Page(models.TextChoices):
        ABOUT = "about", "درباره ما"
        CONTACT = "contact", "تماس با ما"
        FAQ = "faq", "سؤالات متداول"

    page = models.CharField("صفحه", max_length=20, choices=Page.choices)
    icon = models.CharField("آیکون (اختیاری)", max_length=50, blank=True)
    order = models.PositiveIntegerField("ترتیب", default=0)
    is_active = models.BooleanField("فعال", default=True)
    translations = TranslatedFields(
        key=models.CharField("کلید", max_length=100),
        value=models.TextField("مقدار"),
        meta={"db_table": "app_account_sitecontent_translation"},
    )

    class Meta:
        verbose_name = "محتوای سایت"
        verbose_name_plural = "محتوای سایت"
        ordering = ["page", "order", "id"]
        db_table = "app_account_sitecontent"

    def __str__(self):
        return f"{self.get_page_display()}: {self.safe_translation_getter('key', any_language=True) or self.pk}"


class AboutPage(TranslatableModel):
    """Singleton rich About content edited with TinyMCE (landing + /about/)."""

    translations = TranslatedFields(
        title=models.CharField("عنوان", max_length=200, default="درباره ما"),
        body=models.TextField("محتوا", blank=True, help_text="محتوای HTML با TinyMCE"),
        meta={"db_table": "app_account_aboutpage_translation"},
    )
    updated_at = models.DateTimeField("زمان به‌روزرسانی", auto_now=True)

    class Meta:
        verbose_name = "صفحه درباره ما"
        verbose_name_plural = "صفحه درباره ما"
        db_table = "app_account_aboutpage"

    def __str__(self):
        return self.safe_translation_getter("title", any_language=True) or "About"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class ResumePage(TranslatableModel):
    """Singleton Resume / CV content edited with TinyMCE."""

    translations = TranslatedFields(
        title=models.CharField("عنوان", max_length=200, default="رزومه"),
        body=models.TextField("محتوا", blank=True, help_text="محتوای HTML با TinyMCE"),
        meta={"db_table": "app_account_resumepage_translation"},
    )
    updated_at = models.DateTimeField("زمان به‌روزرسانی", auto_now=True)

    class Meta:
        verbose_name = "صفحه رزومه"
        verbose_name_plural = "صفحه رزومه"
        db_table = "app_account_resumepage"

    def __str__(self):
        return self.safe_translation_getter("title", any_language=True) or "Resume"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
