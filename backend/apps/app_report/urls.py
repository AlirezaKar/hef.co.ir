from django.urls import path

from . import views

app_name = "report"

urlpatterns = [
    path("", views.home_view, name="home"),
    path("reports/", views.reports_index_view, name="index"),
    path("reports/file/<str:filename>/", views.report_file_view, name="report_file"),
    path("reports/raw/<str:filename>/", views.report_raw_view, name="report_raw"),
    path("reports/scan-version/", views.scan_version_view, name="scan_version"),
]
