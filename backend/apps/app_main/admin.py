from django.contrib import admin
from parler.admin import TranslatableAdmin
from tinymce.widgets import AdminTinyMCE

from .models import AboutPage, ResumePage, SiteContent


@admin.register(SiteContent)
class SiteContentAdmin(TranslatableAdmin):
    list_display = ("page", "key", "order", "is_active", "icon")
    list_filter = ("page", "is_active")
    search_fields = ("translations__key", "translations__value")
    list_editable = ("order", "is_active")


@admin.register(AboutPage)
class AboutPageAdmin(TranslatableAdmin):
    list_display = ("title", "updated_at")
    readonly_fields = ("updated_at",)
    fields = ("title", "body", "updated_at")

    def has_add_permission(self, request):
        return not AboutPage.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == "body":
            kwargs["widget"] = AdminTinyMCE(
                attrs={"cols": 100, "rows": 36, "style": "width:100%; min-height:620px;"},
            )
        return super().formfield_for_dbfield(db_field, request, **kwargs)


@admin.register(ResumePage)
class ResumePageAdmin(TranslatableAdmin):
    list_display = ("title", "updated_at")
    readonly_fields = ("updated_at",)
    fields = ("title", "body", "updated_at")

    def has_add_permission(self, request):
        return not ResumePage.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == "body":
            kwargs["widget"] = AdminTinyMCE(
                attrs={"cols": 100, "rows": 36, "style": "width:100%; min-height:620px;"},
            )
        return super().formfield_for_dbfield(db_field, request, **kwargs)
