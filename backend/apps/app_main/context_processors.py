from django.utils import translation

from .i18n_chrome import DEFAULT_LANG, SESSION_KEY, get_ui_lang, set_ui_lang, ui_context


def chrome_i18n(request):
    """Expose ui_lang / ui_dir / ui_t for navbar, footer, and common UI."""
    if SESSION_KEY not in request.session:
        cookie_lang = request.COOKIES.get("ui_lang")
        if cookie_lang:
            set_ui_lang(request, cookie_lang)
        else:
            request.session[SESSION_KEY] = DEFAULT_LANG
    lang = get_ui_lang(request)
    translation.activate(lang)
    request.LANGUAGE_CODE = lang
    return ui_context(request)
