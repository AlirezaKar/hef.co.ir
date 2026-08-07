from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path, re_path
from django.views.static import serve

urlpatterns = [
    path("admin/", admin.site.urls),
    path("tinymce/", include("tinymce.urls")),
    path("", include("apps.app_account.urls")),
    path("learn/", include("apps.app_learn.urls")),
    path("download/", include("apps.app_download.urls")),
    path("", include("apps.app_finance.urls")),
]

handler400 = "config.error_views.bad_request"
handler403 = "config.error_views.permission_denied"
handler404 = "config.error_views.not_found"
handler500 = "config.error_views.server_error"

# Media must be served even when DEBUG=False — django.conf.urls.static.static()
# is a no-op outside DEBUG, which left carousel /media/ URLs as 404s.
urlpatterns += [
    re_path(
        r"^media/(?P<path>.*)$",
        serve,
        {"document_root": settings.MEDIA_ROOT},
    ),
]
if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
