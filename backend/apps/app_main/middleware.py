from django.utils import translation
from django.utils.deprecation import MiddlewareMixin

from .i18n_chrome import DEFAULT_LANG, SESSION_KEY, get_ui_lang, set_ui_lang


class UILanguageMiddleware(MiddlewareMixin):
    """
    Sync custom ui_lang (session/cookie) to Django's active language
    so django-parler returns the correct CMS translations in views.
    """

    def process_request(self, request):
        if SESSION_KEY not in request.session:
            cookie_lang = request.COOKIES.get("ui_lang")
            if cookie_lang:
                set_ui_lang(request, cookie_lang)
            else:
                request.session[SESSION_KEY] = DEFAULT_LANG
        lang = get_ui_lang(request)
        translation.activate(lang)
        request.LANGUAGE_CODE = lang
        return None
