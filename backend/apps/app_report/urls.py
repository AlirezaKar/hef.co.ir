from django.urls import path

from . import views

app_name = "report"

urlpatterns = [
    path("home/", views.home_view, name="home"),
    path("history/", views.history_index_view, name="index"),
    path(
        "history/accounts/new/",
        views.trading_account_create_view,
        name="trading_account_create",
    ),
    path(
        "history/accounts/<int:pk>/",
        views.history_account_view,
        name="history_account",
    ),
    path("history/file/<str:filename>/", views.history_file_view, name="history_file"),
]
