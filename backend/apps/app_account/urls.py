from django.urls import path

from . import views

app_name = "account"

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile_view, name="profile"),
    path("settings/", views.settings_view, name="settings"),
    path("about/", views.about_view, name="about"),
    path("contact/", views.contact_view, name="contact"),
]
