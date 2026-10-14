from django.contrib.auth.models import AnonymousUser
from django.template.loader import render_to_string
from django.test import RequestFactory, SimpleTestCase

from apps.app_account.models import User
from .i18n_chrome import LANG_META


class ChromeTemplateTests(SimpleTestCase):
    def render_page(self, template, lang="fa", authenticated=False, **context):
        request = RequestFactory().get("/")
        request.session = {"ui_lang": lang}
        request.user = User(username="preview") if authenticated else AnonymousUser()
        return render_to_string(template, context, request=request)

    def test_navbar_positions_are_independent_of_language(self):
        for lang, meta in LANG_META.items():
            for authenticated in (False, True):
                with self.subTest(lang=lang, authenticated=authenticated):
                    html = self.render_page("finance/hub.html", lang, authenticated)
                    self.assertIn(f'<html lang="{lang}" dir="{meta["dir"]}">', html)
                    self.assertIn('<div class="site-navbar-inner" dir="rtl">', html)
                    self.assertIn(f'<ul class="site-nav-links" dir="{meta["dir"]}">', html)
                    self.assertIn('<div class="site-navbar-actions" dir="ltr">', html)
                    self.assertLess(html.index('id="themeToggleBtn"'), html.index('class="nav-lang-btn'))
                    last_action = 'class="nav-profile-chip"' if authenticated else 'class="nav-btn nav-btn-accent"'
                    self.assertLess(html.index('class="nav-lang-btn'), html.index(last_action))

    def test_home_uses_fade_carousel(self):
        html = self.render_page("main/home.html", carousel_images=["/one.jpg", "/two.jpg"])
        self.assertIn('class="carousel slide carousel-fade"', html)
        self.assertIn('data-bs-interval="5000"', html)
        self.assertEqual(html.count('class="carousel-item '), 2)

    def test_short_page_footer_follows_content(self):
        html = self.render_page("finance/hub.html")
        self.assertIn('class="site-body', html)
        self.assertLess(html.index("</main>"), html.index('<footer class="app-footer">'))
