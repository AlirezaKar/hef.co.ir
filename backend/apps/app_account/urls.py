from django.urls import path

from . import views

app_name = "account"

urlpatterns = [
    path("", views.landing_view, name="landing"),
    path("login/", views.login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile_view, name="profile"),
    path("about/", views.about_view, name="about"),
    path("faq/", views.faq_view, name="faq"),
    path("contact/", views.contact_view, name="contact"),
    path("uploads/tinymce/", views.tinymce_upload_view, name="tinymce_upload"),
]
