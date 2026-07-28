"""
Django settings for HEF History Portal.

Sensitive values are loaded from backend/.env — never commit real secrets.
"""

import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BASE_DIR.parent

load_dotenv(BASE_DIR / ".env")


def env_required(name: str) -> str:
    value = os.getenv(name)
    if value is None or not str(value).strip():
        raise ImproperlyConfigured(
            f"Missing required environment variable: {name}. "
            f"Copy backend/.env.sample to backend/.env and set a value."
        )
    return value.strip()


def env_bool(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None or not str(raw).strip():
        return default
    return str(raw).strip().lower() in ("1", "true", "yes", "on")


SECRET_KEY = env_required("DJANGO_SECRET_KEY")
DEBUG = env_bool("DJANGO_DEBUG", default=False)

ALLOWED_HOSTS = [
    h.strip()
    for h in os.getenv("DJANGO_ALLOWED_HOSTS", "").split(",")
    if h.strip()
]
if not ALLOWED_HOSTS:
    raise ImproperlyConfigured(
        "DJANGO_ALLOWED_HOSTS is empty. Set it in backend/.env "
        "(e.g. localhost,127.0.0.1)."
    )

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "tinymce",
    "apps.app_account.apps.AppAccountConfig",
    "apps.app_report.apps.AppReportConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "apps.app_account.middleware.ClickTrackingMiddleware",
    "config.middleware.FriendlyErrorMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.template.context_processors.media",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 8},
    },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

AUTH_USER_MODEL = "app_account.User"

AUTHENTICATION_BACKENDS = [
    "apps.app_account.backends.UsernameOrEmailBackend",
    "django.contrib.auth.backends.ModelBackend",
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Tehran"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# Serve project static files reliably (works even when DEBUG is False)
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}
WHITENOISE_USE_FINDERS = DEBUG
WHITENOISE_AUTOREFRESH = DEBUG

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Optional override; default is <project>/data/History
_history_root = os.getenv("HISTORY_ROOT", "").strip()
HISTORY_ROOT = Path(_history_root) if _history_root else (PROJECT_ROOT / "data" / "History")

LOGIN_URL = "account:login"
LOGIN_REDIRECT_URL = "report:home"
LOGOUT_REDIRECT_URL = "account:landing"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Allow same-origin iframes (used to embed the Index dashboard)
X_FRAME_OPTIONS = "SAMEORIGIN"

# Profile picture constraints
PROFILE_PICTURE_MAX_SIZE = 5 * 1024 * 1024  # 5 MB

# Friendly CSRF error page (no technical details)
CSRF_FAILURE_VIEW = "config.error_views.csrf_failure"

# TinyMCE (admin About page editor) — full formatting / style controls
TINYMCE_DEFAULT_CONFIG = {
    "theme": "silver",
    "height": 620,
    "menubar": "file edit view insert format tools table help",
    "plugins": (
        "advlist autolink lists link image charmap preview anchor "
        "searchreplace visualblocks code fullscreen insertdatetime media "
        "table help wordcount directionality emoticons accordion"
    ),
    "toolbar_mode": "wrap",
    "toolbar": (
        "undo redo | blocks styles fontfamily fontsize lineheight | "
        "bold italic underline strikethrough | forecolor backcolor | "
        "alignleft aligncenter alignright alignjustify | "
        "bullist numlist outdent indent | "
        "link image media table emoticons charmap | "
        "ltr rtl | removeformat | visualblocks code fullscreen preview | help"
    ),
    "font_family_formats": (
        "Vazirmatn=Vazirmatn,Tahoma,sans-serif;"
        "Tahoma=Tahoma,Arial,sans-serif;"
        "Arial=arial,helvetica,sans-serif;"
        "Courier New=courier new,courier,monospace;"
        "Times New Roman=times new roman,times,serif;"
        "Georgia=georgia,palatino,serif"
    ),
    "font_size_formats": "10px 12px 14px 16px 18px 20px 24px 28px 32px 36px 48px",
    "line_height_formats": "1 1.2 1.4 1.5 1.6 1.8 2 2.5 3",
    "style_formats": [
        {
            "title": "متن",
            "items": [
                {"title": "پاراگراف", "format": "p"},
                {"title": "عنوان ۱", "format": "h1"},
                {"title": "عنوان ۲", "format": "h2"},
                {"title": "عنوان ۳", "format": "h3"},
                {"title": "نقل‌قول", "format": "blockquote"},
            ],
        },
        {
            "title": "سبک‌ها",
            "items": [
                {
                    "title": "متن برجسته",
                    "inline": "span",
                    "styles": {"font-weight": "700", "color": "#0f172a"},
                },
                {
                    "title": "متن کم‌رنگ",
                    "inline": "span",
                    "styles": {"color": "#475569"},
                },
                {
                    "title": "پس‌زمینه روشن",
                    "block": "div",
                    "styles": {
                        "background": "#eff6ff",
                        "padding": "12px 14px",
                        "border-radius": "10px",
                    },
                },
            ],
        },
    ],
    "style_formats_merge": True,
    "formats": {
        "alignleft": {"selector": "p,h1,h2,h3,h4,h5,h6,td,th,div,ul,ol,li,table", "classes": "text-start"},
        "aligncenter": {"selector": "p,h1,h2,h3,h4,h5,h6,td,th,div,ul,ol,li,table", "classes": "text-center"},
        "alignright": {"selector": "p,h1,h2,h3,h4,h5,h6,td,th,div,ul,ol,li,table", "classes": "text-end"},
    },
    "color_map": [
        "000000", "مشکی",
        "111827", "زغال",
        "374151", "خاکستری تیره",
        "6B7280", "خاکستری",
        "FFFFFF", "سفید",
        "DC2626", "قرمز",
        "EA580C", "نارنجی",
        "CA8A04", "زرد",
        "16A34A", "سبز",
        "2563EB", "آبی",
        "7C3AED", "بنفش",
        "0F172A", "سرمه‌ای",
    ],
    "directionality": "rtl",
    "branding": False,
    "promotion": False,
    "browser_spellcheck": True,
    "relative_urls": False,
    "remove_script_host": False,
    "convert_urls": True,
    "images_upload_url": "/uploads/tinymce/",
    "automatic_uploads": True,
    "file_picker_types": "image media file",
    "image_caption": True,
    "image_advtab": True,
    "table_toolbar": (
        "tableprops tablerowprops tablecellprops | "
        "tableinsertrowbefore tableinsertrowafter tabledeleterow | "
        "tableinsertcolbefore tableinsertcolafter tabledeletecol"
    ),
    # Keep inline style attributes so admin formatting survives save
    "valid_children": "+body[style]",
    "extended_valid_elements": (
        "span[*],div[*],p[*],h1[*],h2[*],h3[*],h4[*],h5[*],h6[*],"
        "a[*],img[*],table[*],thead[*],tbody[*],tr[*],td[*],th[*],"
        "ul[*],ol[*],li[*],blockquote[*],pre[*],code[*],hr,br"
    ),
    "content_style": (
        "@import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;600;700&display=swap');"
        "body { font-family: Vazirmatn, Tahoma, sans-serif; direction: rtl; "
        "font-size: 16px; line-height: 1.75; color: #000; }"
        "img { max-width: 100%; height: auto; }"
        ".text-start { text-align: left; }"
        ".text-center { text-align: center; }"
        ".text-end { text-align: right; }"
    ),
}
TINYMCE_COMPRESSOR = False
