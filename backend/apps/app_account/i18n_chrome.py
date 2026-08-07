"""Chrome-only UI language helpers (navbar / footer / common buttons)."""

from __future__ import annotations

ALLOWED_LANGS = ("fa", "en", "fr", "ar")
DEFAULT_LANG = "fa"
SESSION_KEY = "ui_lang"

LANG_META = {
    "fa": {"dir": "rtl", "label": "فارسی", "html_lang": "fa", "code": "IR"},
    "en": {"dir": "ltr", "label": "English", "html_lang": "en", "code": "GB"},
    "fr": {"dir": "ltr", "label": "Français", "html_lang": "fr", "code": "FR"},
    "ar": {"dir": "rtl", "label": "العربية", "html_lang": "ar", "code": "SA"},
}

STRINGS = {
    "fa": {
        "nav_home": "صفحه اصلی",
        "nav_learn": "آموزش",
        "nav_download": "مرکز دانلود",
        "nav_adobe": "ادوب کانکت",
        "nav_finance": "سرمایه‌گذاری",
        "nav_faq": "سؤالات متداول",
        "nav_resume": "رزومه",
        "nav_about": "درباره ما",
        "nav_contact": "تماس با ما",
        "nav_login": "ورود",
        "nav_signup": "ثبت‌نام",
        "nav_logout": "خروج",
        "nav_profile": "پروفایل",
        "nav_lang": "زبان",
        "nav_theme": "حالت تاریک/روشن",
        "footer_rights": "کلیه حقوق محفوظ است.",
        "coming_soon": "به‌زودی",
        "coming_soon_body": "این بخش به‌زودی در دسترس قرار می‌گیرد.",
        "finance_title": "سرمایه‌گذاری",
        "finance_body": "از اینجا به بخش تاریخچه حساب‌های ترید دسترسی دارید.",
        "finance_history_cta": "ورود به تاریخچه",
        "home_login": "ورود",
        "home_signup": "ثبت‌نام",
        "resume_empty": "هنوز محتوایی از پنل مدیریت ثبت نشده است.",
    },
    "en": {
        "nav_home": "Main Page",
        "nav_learn": "Learn",
        "nav_download": "Download Center",
        "nav_adobe": "Adobe Connect",
        "nav_finance": "Finance",
        "nav_faq": "FAQ",
        "nav_resume": "Resume",
        "nav_about": "About",
        "nav_contact": "Contact",
        "nav_login": "Login",
        "nav_signup": "Sign up",
        "nav_logout": "Logout",
        "nav_profile": "Profile",
        "nav_lang": "Language",
        "nav_theme": "Dark/Light mode",
        "footer_rights": "All rights reserved.",
        "coming_soon": "Coming soon",
        "coming_soon_body": "This section will be available soon.",
        "finance_title": "Finance",
        "finance_body": "Access your trading account history from here.",
        "finance_history_cta": "Open History",
        "home_login": "Login",
        "home_signup": "Sign up",
        "resume_empty": "No content has been published yet.",
    },
    "fr": {
        "nav_home": "Accueil",
        "nav_learn": "Apprendre",
        "nav_download": "Centre de téléchargement",
        "nav_adobe": "Adobe Connect",
        "nav_finance": "Finance",
        "nav_faq": "FAQ",
        "nav_resume": "CV",
        "nav_about": "À propos",
        "nav_contact": "Contact",
        "nav_login": "Connexion",
        "nav_signup": "Inscription",
        "nav_logout": "Déconnexion",
        "nav_profile": "Profil",
        "nav_lang": "Langue",
        "nav_theme": "Mode sombre/clair",
        "footer_rights": "Tous droits réservés.",
        "coming_soon": "Bientôt disponible",
        "coming_soon_body": "Cette section sera bientôt disponible.",
        "finance_title": "Finance",
        "finance_body": "Accédez à l’historique de vos comptes de trading ici.",
        "finance_history_cta": "Ouvrir l’historique",
        "home_login": "Connexion",
        "home_signup": "Inscription",
        "resume_empty": "Aucun contenu n’a encore été publié.",
    },
    "ar": {
        "nav_home": "الصفحة الرئيسية",
        "nav_learn": "التعلم",
        "nav_download": "مركز التحميل",
        "nav_adobe": "أدوب كونكت",
        "nav_finance": "الاستثمار",
        "nav_faq": "الأسئلة الشائعة",
        "nav_resume": "السيرة الذاتية",
        "nav_about": "من نحن",
        "nav_contact": "اتصل بنا",
        "nav_login": "تسجيل الدخول",
        "nav_signup": "إنشاء حساب",
        "nav_logout": "خروج",
        "nav_profile": "الملف الشخصي",
        "nav_lang": "اللغة",
        "nav_theme": "الوضع الداكن/الفاتح",
        "footer_rights": "جميع الحقوق محفوظة.",
        "coming_soon": "قريبًا",
        "coming_soon_body": "سيكون هذا القسم متاحًا قريبًا.",
        "finance_title": "الاستثمار",
        "finance_body": "يمكنك الوصول إلى سجل حسابات التداول من هنا.",
        "finance_history_cta": "فتح السجل",
        "home_login": "تسجيل الدخول",
        "home_signup": "إنشاء حساب",
        "resume_empty": "لم يُنشر أي محتوى بعد.",
    },
}


def normalize_lang(code: str | None) -> str:
    code = (code or "").strip().lower()
    if code in ALLOWED_LANGS:
        return code
    return DEFAULT_LANG


def get_ui_lang(request) -> str:
    return normalize_lang(request.session.get(SESSION_KEY, DEFAULT_LANG))


def set_ui_lang(request, code: str) -> str:
    lang = normalize_lang(code)
    request.session[SESSION_KEY] = lang
    return lang


def ui_context(request) -> dict:
    lang = get_ui_lang(request)
    meta = LANG_META[lang]
    return {
        "ui_lang": lang,
        "ui_dir": meta["dir"],
        "ui_html_lang": meta["html_lang"],
        "ui_lang_label": meta["label"],
        "ui_lang_code": meta["code"],
        "ui_t": STRINGS[lang],
        "ui_langs": [
            {
                "code": c,
                "label": LANG_META[c]["label"],
                "region": LANG_META[c]["code"],
            }
            for c in ALLOWED_LANGS
        ],
    }
