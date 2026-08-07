from django.urls import path

from . import views

app_name = "finance"

urlpatterns = [
    path("finance/", views.finance_hub_view, name="hub"),
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
