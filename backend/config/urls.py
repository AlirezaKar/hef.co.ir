from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("tinymce/", include("tinymce.urls")),
    path("", include("apps.app_account.urls")),
    path("", include("apps.app_report.urls")),
]

# Custom error handlers (used when DEBUG=False; middleware covers DEBUG=True)
handler400 = "config.error_views.bad_request"
handler403 = "config.error_views.permission_denied"
handler404 = "config.error_views.not_found"
handler500 = "config.error_views.server_error"

# Development helpers for media/static (WhiteNoise also serves static)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += staticfiles_urlpatterns()
