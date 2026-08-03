import uuid
from pathlib import Path

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST

from .forms import (
    ContactMessageForm,
    LoginForm,
    ProfileForm,
    SignupForm,
)
from .models import AboutPage, LoginAttempt, SiteContent, User
from .utils import apply_network_identity, get_client_ip

AUTH_BACKEND = settings.AUTHENTICATION_BACKENDS[0]


def _record_login_attempt(*, username_tried, user, request, successful):
    LoginAttempt.objects.create(
        user=user if successful else (user if user and user.is_authenticated else None),
        username_tried=username_tried,
        ip_address=get_client_ip(request),
        successful=successful,
    )
    if user and getattr(user, "pk", None):
        User.objects.filter(pk=user.pk).update(
            login_attempt_count=F("login_attempt_count") + 1
        )
    elif not successful:
        matched = User.objects.filter(username__iexact=username_tried).first()
        if matched is None and "@" in username_tried:
            matched = User.objects.filter(email__iexact=username_tried).first()
        if matched:
            User.objects.filter(pk=matched.pk).update(
                login_attempt_count=F("login_attempt_count") + 1
            )
            return matched
    return user


@require_http_methods(["GET"])
def landing_view(request):
    """Public About landing — first page for anonymous visitors."""
    if request.user.is_authenticated:
        return redirect("report:home")
    about = AboutPage.get_solo()
    return render(
        request,
        "account/landing.html",
        {"about": about},
    )


@require_http_methods(["GET", "POST"])
def signup_view(request):
    if request.user.is_authenticated:
        return redirect("report:home")

    form = SignupForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save(commit=False)
        user.email = form.cleaned_data["email"]
        user.phone_number = form.cleaned_data["phone_number"]
        user.save()
        apply_network_identity(user, request, force_mac=True)
        login(request, user, backend=AUTH_BACKEND)
        messages.success(request, "ثبت‌نام با موفقیت انجام شد.")
        return redirect("report:home")
    return render(request, "account/signup.html", {"form": form})


@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.user.is_authenticated:
        return redirect("report:home")

    form = LoginForm(request, data=request.POST or None)
    if request.method == "POST":
        identifier = request.POST.get("username", "").strip()
        if form.is_valid():
            user = form.get_user()
            _record_login_attempt(
                username_tried=identifier,
                user=user,
                request=request,
                successful=True,
            )
            login(request, user, backend=AUTH_BACKEND)
            if form.cleaned_data.get("remember_me"):
                # ~1 year
                request.session.set_expiry(365 * 24 * 60 * 60)
            else:
                # Idle timeout: 30 minutes
                request.session.set_expiry(30 * 60)
            apply_network_identity(user, request, force_mac=not bool(user.mac_address))
            messages.success(request, "ورود موفقیت‌آمیز بود.")
            return redirect(request.GET.get("next") or "report:home")
        matched = User.objects.filter(username__iexact=identifier).first()
        if matched is None and "@" in identifier:
            matched = User.objects.filter(email__iexact=identifier).first()
        _record_login_attempt(
            username_tried=identifier or "unknown",
            user=matched,
            request=request,
            successful=False,
        )
    return render(request, "account/login.html", {"form": form})


@require_POST
@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "با موفقیت خارج شدید.")
    return redirect("account:landing")


@login_required
@require_http_methods(["GET", "POST"])
def profile_view(request):
    user = request.user
    form = ProfileForm(request.POST or None, request.FILES or None, instance=user)
    if request.method == "POST" and form.is_valid():
        profile_user = form.save(commit=False)
        if "picture" in request.FILES:
            try:
                profile_user.save_picture_as_webp(request.FILES["picture"])
            except Exception:
                messages.error(
                    request, "پردازش تصویر ناموفق بود. فایل معتبر ارسال کنید."
                )
                return render(request, "account/profile.html", {"form": form})
        profile_user.save()
        messages.success(request, "پروفایل به‌روزرسانی شد.")
        return redirect("account:profile")
    return render(request, "account/profile.html", {"form": form})


@login_required
def about_view(request):
    about = AboutPage.get_solo()
    items = SiteContent.objects.filter(page=SiteContent.Page.ABOUT, is_active=True)
    return render(
        request,
        "account/about.html",
        {"about": about, "items": items},
    )


@login_required
def faq_view(request):
    items = SiteContent.objects.filter(page=SiteContent.Page.FAQ, is_active=True)
    return render(request, "account/faq.html", {"items": items})


@login_required
@require_http_methods(["GET", "POST"])
def contact_view(request):
    items = SiteContent.objects.filter(page=SiteContent.Page.CONTACT, is_active=True)
    form = ContactMessageForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        messages.success(request, "پیام شما ثبت شد. سپاسگزاریم.")
        return redirect("account:contact")
    return render(request, "account/contact.html", {"form": form, "items": items})


@csrf_exempt
@staff_member_required
@require_POST
def tinymce_upload_view(request):
    """Accept image/file uploads from TinyMCE admin editor."""
    upload = request.FILES.get("file")
    if not upload:
        return JsonResponse({"error": "فایلی ارسال نشده است."}, status=400)

    allowed_ext = {
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".webp",
        ".svg",
        ".pdf",
        ".doc",
        ".docx",
        ".xls",
        ".xlsx",
        ".zip",
    }
    ext = Path(upload.name).suffix.lower()
    if ext not in allowed_ext:
        return JsonResponse({"error": "نوع فایل مجاز نیست."}, status=400)

    max_size = 10 * 1024 * 1024
    if upload.size > max_size:
        return JsonResponse({"error": "حجم فایل بیش از ۱۰ مگابایت است."}, status=400)

    name = f"about_uploads/{uuid.uuid4().hex}{ext}"
    saved = default_storage.save(name, upload)
    url = request.build_absolute_uri(settings.MEDIA_URL + saved.replace("\\", "/"))
    return JsonResponse({"location": url})
