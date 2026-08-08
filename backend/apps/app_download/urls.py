from django.urls import path

from . import views

app_name = "download"

urlpatterns = [
    path("", views.index_view, name="index"),
    path("manage/", views.manage_view, name="manage"),
    path("manage/upload/", views.upload_view, name="upload"),
    path("manage/<int:pk>/update/", views.update_view, name="update"),
    path("manage/<int:pk>/delete/", views.delete_view, name="delete"),
    path("file/<int:pk>/", views.download_file_view, name="file"),
    path("report/", views.report_view, name="report"),
]
