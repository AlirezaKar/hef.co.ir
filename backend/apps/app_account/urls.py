from django.urls import path

from . import views

app_name = "account"

urlpatterns = [
    path("", views.home_view, name="home"),
    path("landing/", views.home_view, name="landing"),
    path("set-language/", views.set_language_view, name="set_language"),
    path("adobe-connect/", views.adobe_connect_view, name="adobe_connect"),
    path("resume/", views.resume_view, name="resume"),
    path("login/", views.login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile_view, name="profile"),
    path("about/", views.about_view, name="about"),
    path("faq/", views.faq_view, name="faq"),
    path("contact/", views.contact_view, name="contact"),
    path("uploads/tinymce/", views.tinymce_upload_view, name="tinymce_upload"),
]
