from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods, require_POST

from .forms import LoginForm, ProfileForm, SignupForm
from .models import LoginAttempt, User
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


@require_http_methods(["GET", "POST"])
def signup_view(request):
    if request.user.is_authenticated:
        return redirect("main:home")

    form = SignupForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save(commit=False)
        user.email = form.cleaned_data["email"]
        user.phone_number = form.cleaned_data["phone_number"]
        user.save()
        apply_network_identity(user, request, force_mac=True)
        login(request, user, backend=AUTH_BACKEND)
        messages.success(request, "ثبت‌نام با موفقیت انجام شد.")
        return redirect("main:home")
    return render(request, "account/signup.html", {"form": form})


@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.user.is_authenticated:
        return redirect("main:home")

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
                request.session.set_expiry(365 * 24 * 60 * 60)
            else:
                request.session.set_expiry(30 * 60)
            apply_network_identity(user, request, force_mac=not bool(user.mac_address))
            messages.success(request, "ورود موفقیت‌آمیز بود.")
            return redirect(request.GET.get("next") or "main:home")
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
    return redirect("main:home")


@login_required
@require_http_methods(["GET", "POST"])
def profile_view(request):
    user = request.user

    if request.method == "POST" and request.POST.get("clear_picture") == "1":
        if user.picture:
            user.picture.delete(save=False)
            user.picture = None
            user.save(update_fields=["picture"])
        messages.success(request, "تصویر پروفایل حذف شد.")
        return redirect("account:profile")

    form = ProfileForm(request.POST or None, request.FILES or None, instance=user)
    if request.method == "POST" and form.is_valid():
        profile_user = form.save(commit=False)
        if "picture" in request.FILES:
            uploaded = request.FILES["picture"]
            max_size = getattr(settings, "PROFILE_PICTURE_MAX_SIZE", 5 * 1024 * 1024)
            if getattr(uploaded, "size", 0) > max_size:
                messages.error(request, "حجم تصویر نباید بیشتر از ۵ مگابایت باشد.")
                return render(request, "account/profile.html", {"form": form})
            try:
                profile_user.save_picture_as_webp(uploaded)
            except Exception:
                messages.error(
                    request, "پردازش تصویر ناموفق بود. فایل معتبر ارسال کنید."
                )
                return render(request, "account/profile.html", {"form": form})
        profile_user.save()
        messages.success(request, "پروفایل به‌روزرسانی شد.")
        return redirect("account:profile")
    return render(request, "account/profile.html", {"form": form})
