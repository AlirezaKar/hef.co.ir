import uuid
from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.templatetags.static import static
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from .forms import ContactMessageForm
from .i18n_chrome import set_ui_lang
from .models import AboutPage, CarouselImage, ResumePage, SiteContent

# Expose carousel interval from settings for the template
_CAROUSEL_INTERVAL = getattr(settings, "CAROUSEL_INTERVAL", 4000)

CAROUSEL_STATIC_FALLBACK = (
    "img/landing/hero.jpg",
    "img/landing/accent.jpg",
)


def _carousel_image_urls():
    """List image URLs from CarouselImage model; fall back to static."""
    urls = []
    for img in CarouselImage.objects.filter(is_active=True):
        if img.image:
            urls.append(img.image.url)
    if not urls:
        urls = [static(name) for name in CAROUSEL_STATIC_FALLBACK]
    return urls


@require_http_methods(["GET"])
def home_view(request):
    """Public Main page — carousel + about content."""
    about = AboutPage.get_solo()
    return render(
        request,
        "main/home.html",
        {
            "about": about,
            "carousel_images": _carousel_image_urls(),
            "carousel_interval": _CAROUSEL_INTERVAL,
        },
    )


landing_view = home_view


@require_GET
def set_language_view(request):
    lang = set_ui_lang(request, request.GET.get("lang", ""))
    next_url = request.GET.get("next") or request.META.get("HTTP_REFERER") or "/"
    if not next_url.startswith("/") or next_url.startswith("//"):
        next_url = "/"
    response = redirect(next_url)
    response.set_cookie("ui_lang", lang, max_age=365 * 24 * 60 * 60, samesite="Lax")
    return response


@require_http_methods(["GET"])
def adobe_connect_view(request):
    return render(request, "main/adobe_connect.html")


@require_http_methods(["GET"])
def adobe_soon_view(request):
    """Stub page shown when purchase/pricing is not yet available."""
    return render(request, "main/stub.html", {"stub_key": "adobe_pricing"})


@require_http_methods(["GET"])
def resume_view(request):
    resume = ResumePage.get_solo()
    return render(request, "main/resume.html", {"resume": resume})


def about_view(request):
    about = AboutPage.get_solo()
    items = SiteContent.objects.filter(
        page=SiteContent.Page.ABOUT, is_active=True
    ).active_translations()
    return render(
        request,
        "main/about.html",
        {"about": about, "items": items},
    )


def faq_view(request):
    items = SiteContent.objects.filter(
        page=SiteContent.Page.FAQ, is_active=True
    ).active_translations()
    return render(request, "main/faq.html", {"items": items})


@require_http_methods(["GET", "POST"])
def contact_view(request):
    items = SiteContent.objects.filter(
        page=SiteContent.Page.CONTACT, is_active=True
    ).active_translations()
    form = ContactMessageForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        if request.user.is_authenticated:
            from apps.app_account.models import Notification, Ticket

            ticket = Ticket.objects.create(
                user=request.user,
                subject=form.cleaned_data["name"],
                message=form.cleaned_data["message"] or "(بدون پیام)",
            )
            Notification.objects.create(
                user=request.user,
                ticket=ticket,
                message=f"تیکت «{ticket.subject}» با موفقیت ثبت شد.",
            )
        messages.success(request, "پیام شما ثبت شد. سپاسگزاریم.")
        return redirect("main:contact")
    return render(request, "main/contact.html", {"form": form, "items": items})


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
