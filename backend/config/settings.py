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
    "apps.app_finance.apps.AppFinanceConfig",
    "apps.app_learn.apps.AppLearnConfig",
    "apps.app_download.apps.AppDownloadConfig",
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
                "apps.app_account.context_processors.chrome_i18n",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# PostgreSQL when POSTGRES_HOST (or DATABASE_URL) is set; otherwise SQLite for local dev.
_postgres_host = os.getenv("POSTGRES_HOST", "").strip()
_database_url = os.getenv("DATABASE_URL", "").strip()

if _database_url.startswith("postgres"):
    # Simple postgres://user:pass@host:port/db parsing without extra deps
    import urllib.parse as _urlparse

    _u = _urlparse.urlparse(_database_url)
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": (_u.path or "/").lstrip("/") or "hef",
            "USER": _u.username or "hef",
            "PASSWORD": _u.password or "",
            "HOST": _u.hostname or "localhost",
            "PORT": str(_u.port or 5432),
        }
    }
elif _postgres_host:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("POSTGRES_DB", "hef").strip() or "hef",
            "USER": os.getenv("POSTGRES_USER", "hef").strip() or "hef",
            "PASSWORD": os.getenv("POSTGRES_PASSWORD", "").strip(),
            "HOST": _postgres_host,
            "PORT": os.getenv("POSTGRES_PORT", "5432").strip() or "5432",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# Sessions: sliding idle expiry for non-remembered logins (set_expiry in login_view)
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_AGE = 30 * 60  # default 30 minutes; overridden per-login when "remember me"

_csrf_origins = [
    o.strip()
    for o in os.getenv("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",")
    if o.strip()
]
CSRF_TRUSTED_ORIGINS = _csrf_origins

SESSION_COOKIE_SECURE = env_bool("DJANGO_SESSION_COOKIE_SECURE", default=False)
CSRF_COOKIE_SECURE = env_bool("DJANGO_CSRF_COOKIE_SECURE", default=False)
SECURE_SSL_REDIRECT = env_bool("DJANGO_SECURE_SSL_REDIRECT", default=False)
# Caddy terminates TLS and proxies HTTP to Gunicorn
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

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
_static_root = os.getenv("DJANGO_STATIC_ROOT", "").strip()
STATIC_ROOT = Path(_static_root) if _static_root else (BASE_DIR / "staticfiles")

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
_media_root = os.getenv("DJANGO_MEDIA_ROOT", "").strip()
MEDIA_ROOT = Path(_media_root) if _media_root else (BASE_DIR / "media")

# Local CDN for download-center files (swap CDN_URL to an external host later).
_cdn_root = os.getenv("DJANGO_CDN_ROOT", "").strip()
CDN_ROOT = Path(_cdn_root) if _cdn_root else (BASE_DIR / "cdn")
CDN_URL = os.getenv("DJANGO_CDN_URL", "/cdn/").strip() or "/cdn/"
if not CDN_URL.endswith("/"):
    CDN_URL = f"{CDN_URL}/"

# Optional override; default is <project>/data/History
_history_root = os.getenv("HISTORY_ROOT", "").strip()
HISTORY_ROOT = Path(_history_root) if _history_root else (PROJECT_ROOT / "data" / "History")

LOGIN_URL = "account:login"
LOGIN_REDIRECT_URL = "account:home"
LOGOUT_REDIRECT_URL = "account:home"

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
        "@font-face{font-family:'Vazirmatn';src:url('/static/fonts/vazirmatn/Vazirmatn-Light.woff2') format('woff2');font-weight:300;font-style:normal;font-display:swap;}"
        "@font-face{font-family:'Vazirmatn';src:url('/static/fonts/vazirmatn/Vazirmatn-Regular.woff2') format('woff2');font-weight:400;font-style:normal;font-display:swap;}"
        "@font-face{font-family:'Vazirmatn';src:url('/static/fonts/vazirmatn/Vazirmatn-Medium.woff2') format('woff2');font-weight:500;font-style:normal;font-display:swap;}"
        "@font-face{font-family:'Vazirmatn';src:url('/static/fonts/vazirmatn/Vazirmatn-SemiBold.woff2') format('woff2');font-weight:600;font-style:normal;font-display:swap;}"
        "@font-face{font-family:'Vazirmatn';src:url('/static/fonts/vazirmatn/Vazirmatn-Bold.woff2') format('woff2');font-weight:700;font-style:normal;font-display:swap;}"
        "body { font-family: Vazirmatn, Tahoma, sans-serif; direction: rtl; "
        "font-size: 16px; line-height: 1.75; color: #000; }"
        "img { max-width: 100%; height: auto; }"
        ".text-start { text-align: left; }"
        ".text-center { text-align: center; }"
        ".text-end { text-align: right; }"
    ),
}
TINYMCE_COMPRESSOR = False
