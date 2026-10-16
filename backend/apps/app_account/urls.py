from django.urls import path

from . import views

app_name = "account"

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile_view, name="profile"),
    path("tickets/", views.tickets_view, name="tickets"),
    path("notifications/", views.notifications_api, name="notifications_api"),
    path(
        "notifications/mark-read/",
        views.mark_notifications_read,
        name="notifications_mark_read",
    ),
]
