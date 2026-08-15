"""
Interactive seed command — create relatable dummy rows for chosen models.

Usage:
  python manage.py seed_data
"""

from __future__ import annotations

import random
import string
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.app_account.models import (
    LoginAttempt,
    PageVisit,
    TradingAccount,
    User,
)
from apps.app_main.models import AboutPage, ResumePage, SiteContent

try:
    from tqdm import tqdm
except ImportError:  # pragma: no cover
    tqdm = None


SEED_PASSWORD = "Seed@1234"

FIRST_NAMES = [
    "Ali", "Reza", "Sara", "Neda", "Hossein", "Maryam", "Amir", "Zahra",
    "Mohammad", "Fatemeh", "Parsa", "Helia", "Kian", "Yasaman", "Arman",
    "Shiva", "Nima", "Elham", "Pouya", "Atena",
]
LAST_NAMES = [
    "Ahmadi", "Hosseini", "Karimi", "Mohammadi", "Rezaei", "Moradi",
    "Nouri", "Jafari", "Kazemi", "Ghasemi", "Salehi", "Mousavi",
    "Hashemi", "Rahimi", "Ebrahimi", "Kalaiee", "Shirazi", "Tehrani",
]
BROKERS = [
    "Alpari", "Exness", "IC Markets", "RoboForex", "XM", "FBS",
    "Pepperstone", "AvaTrade", "Tickmill", "FTMO",
]
MAC_SOURCES = ["ip", "hdd", "generated"]

SITE_CONTENT_POOL = {
    SiteContent.Page.ABOUT: [
        ("ماموریت", "ارائه آموزش و ابزارهای مالی شفاف برای کاربران فارسی‌زبان.", "🎯"),
        ("چشم‌انداز", "ساخت یک اکوسیستم قابل اعتماد برای یادگیری و سرمایه‌گذاری.", "🔭"),
        ("ارزش‌ها", "صداقت، پشتیبانی سریع، و محتوای کاربردی.", "💎"),
        ("تیم", "تیمی از مدرسین و متخصصان بازارهای مالی.", "👥"),
        ("سابقه", "سال‌ها تجربه در آموزش و مشاوره سرمایه‌گذاری.", "📚"),
    ],
    SiteContent.Page.FAQ: [
        ("چطور ثبت‌نام کنم؟", "از صفحه ثبت‌نام اطلاعات خود را وارد کنید و حساب بسازید.", "❓"),
        ("رمز عبورم را فراموش کردم", "از صفحه ورود گزینه بازیابی را انتخاب کنید یا با پشتیبانی تماس بگیرید.", "🔑"),
        ("حساب ترید چیست؟", "حسابی که برای پیگیری تاریخچه معاملات به پروفایل شما متصل می‌شود.", "📈"),
        ("آیا خدمات رایگان است؟", "بخشی از محتوا رایگان است؛ برخی سرویس‌ها ممکن است پولی باشند.", "💰"),
        ("چطور با پشتیبانی تماس بگیرم؟", "از صفحه تماس با ما پیام بفرستید یا ایمیل پشتیبانی را استفاده کنید.", "📞"),
        ("زبان سایت را چطور عوض کنم؟", "از منوی بالای صفحه زبان مورد نظر را انتخاب کنید.", "🌐"),
    ],
    SiteContent.Page.CONTACT: [
        ("ایمیل", "support@hef.co.ir", "✉️"),
        ("تلفن", "021-91000000", "📱"),
        ("آدرس", "تهران، خیابان ولیعصر، پلاک ۱۲۳", "📍"),
        ("ساعات پاسخگویی", "شنبه تا چهارشنبه ۹ تا ۱۷", "🕒"),
        ("تلگرام", "@hef_support", "💬"),
    ],
}

PAGE_ROUTES = [
    ("/", "main:home", "صفحه اصلی"),
    ("/about/", "main:about", "درباره ما"),
    ("/faq/", "main:faq", "سؤالات متداول"),
    ("/contact/", "main:contact", "تماس با ما"),
    ("/resume/", "main:resume", "رزومه"),
    ("/login/", "account:login", "ورود"),
    ("/signup/", "account:signup", "ثبت‌نام"),
    ("/profile/", "account:profile", "پروفایل"),
    ("/learn/", "learn:index", "آموزش"),
    ("/download/", "download:index", "مرکز دانلود"),
    ("/finance/", "finance:hub", "سرمایه‌گذاری"),
]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_3) Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) Firefox/123.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) Mobile/15E148",
    "Mozilla/5.0 (Linux; Android 14) Chrome/122.0.6261.64 Mobile",
]

ABOUT_BODIES = [
    "<p>هلدینگ آموزشی و مالی <strong>HEF</strong> با تمرکز بر آموزش کاربردی بازارهای مالی فعالیت می‌کند.</p>"
    "<p>ما محتوای آموزشی، ابزارهای پیگیری معاملات و پشتیبانی کاربران را در یک پلتفرم گرد آورده‌ایم.</p>",
    "<p>هدف ما ساده‌سازی مسیر یادگیری و سرمایه‌گذاری برای کاربران فارسی‌زبان است.</p>"
    "<ul><li>آموزش ساخت‌یافته</li><li>پشتیبانی واقعی</li><li>ابزارهای شفاف</li></ul>",
]

RESUME_BODIES = [
    "<h2>سوابق حرفه‌ای</h2>"
    "<p>تدریس بازارهای مالی، طراحی محتوای آموزشی و مشاوره سرمایه‌گذاری.</p>"
    "<h2>مهارت‌ها</h2><ul><li>تحلیل تکنیکال</li><li>مدیریت ریسک</li><li>آموزش آنلاین</li></ul>",
    "<h2>تحصیلات</h2><p>کارشناسی ارشد مدیریت مالی</p>"
    "<h2>پروژه‌ها</h2><p>راه‌اندازی پلتفرم آموزشی HEF و دوره‌های تخصصی معامله‌گری.</p>",
]


def _progress(iterable, desc: str, total: int | None = None):
    if tqdm is None:
        print(f"  -> {desc} ({total or '?'} items)  [install tqdm for a progress bar]")
        return iterable
    return tqdm(iterable, desc=desc, total=total, unit="row", ncols=80)


def _rand_phone() -> str:
    return "09" + "".join(str(random.randint(0, 9)) for _ in range(9))


def _rand_national_id() -> str:
    return "".join(str(random.randint(0, 9)) for _ in range(10))


def _rand_ip() -> str:
    return ".".join(str(random.randint(1, 254)) for _ in range(4))


def _rand_mac() -> str:
    return ":".join(f"{random.randint(0, 255):02X}" for _ in range(6))


def _unique_suffix(n: int = 6) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=n))


class Command(BaseCommand):
    help = "Interactively seed relatable dummy data for selected models (with tqdm)."

    SEEDERS = (
        ("User", "Demo users with Iranian-style names/phones", True),
        ("TradingAccount", "Broker trading accounts linked to users", True),
        ("SiteContent", "FAQ / About / Contact content cards", True),
        ("AboutPage", "Singleton About page (always 1 row)", False),
        ("ResumePage", "Singleton Resume page (always 1 row)", False),
        ("LoginAttempt", "Login success/failure audit rows", True),
        ("PageVisit", "Page visit analytics rows", True),
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--non-interactive",
            action="store_true",
            help="Skip prompts; use --models and --counts",
        )
        parser.add_argument(
            "--models",
            type=str,
            default="",
            help="Comma-separated model names, e.g. User,TradingAccount",
        )
        parser.add_argument(
            "--counts",
            type=str,
            default="",
            help="Comma-separated counts matching --models, e.g. 10,5",
        )

    def handle(self, *args, **options):
        if tqdm is None:
            self.stderr.write(
                self.style.WARNING(
                    "tqdm is not installed. Run: pip install tqdm\n"
                    "Continuing without a progress bar..."
                )
            )

        if options["non_interactive"]:
            plan = self._plan_from_flags(options["models"], options["counts"])
        else:
            plan = self._plan_interactive()

        if not plan:
            self.stdout.write(self.style.WARNING("Nothing to seed. Bye."))
            return

        self.stdout.write("")
        self.stdout.write(self.style.MIGRATE_HEADING("Seed plan"))
        for name, count in plan:
            self.stdout.write(f"  - {name}: {count}")
        self.stdout.write("")

        if not options["non_interactive"]:
            confirm = input("Proceed? [Y/n]: ").strip().lower()
            if confirm in {"n", "no"}:
                self.stdout.write(self.style.WARNING("Cancelled."))
                return

        created = {}
        with transaction.atomic():
            for name, count in plan:
                created[name] = self._run_seeder(name, count)

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Done."))
        for name, n in created.items():
            self.stdout.write(f"  {name}: {n} created/updated")
        if created.get("User"):
            self.stdout.write(
                self.style.NOTICE(f"\nSeeded user password: {SEED_PASSWORD}")
            )

    # ── planning ──────────────────────────────────────────────

    def _plan_interactive(self) -> list[tuple[str, int]]:
        self.stdout.write("")
        self.stdout.write(self.style.MIGRATE_HEADING("HEF seed data"))
        self.stdout.write("Choose models to seed:\n")
        for i, (name, desc, multi) in enumerate(self.SEEDERS, start=1):
            kind = "N rows" if multi else "singleton"
            self.stdout.write(f"  [{i}] {name:<16} ({kind})  — {desc}")
        self.stdout.write("  [A] All")
        self.stdout.write("  [0] Cancel")
        self.stdout.write("")

        raw = input("Enter numbers (e.g. 1,2,6) or A: ").strip()
        if not raw or raw == "0":
            return []

        selected_names: list[str] = []
        if raw.lower() in {"a", "all"}:
            selected_names = [name for name, *_ in self.SEEDERS]
        else:
            by_index = {str(i): name for i, (name, *_rest) in enumerate(self.SEEDERS, start=1)}
            for part in raw.replace(" ", "").split(","):
                if part not in by_index:
                    self.stderr.write(self.style.ERROR(f"Unknown option: {part}"))
                    return []
                selected_names.append(by_index[part])

        # Stable dependency order
        order = [name for name, *_ in self.SEEDERS]
        selected_names = [n for n in order if n in selected_names]

        plan: list[tuple[str, int]] = []
        self.stdout.write("")
        for name in selected_names:
            meta = next(m for m in self.SEEDERS if m[0] == name)
            multi = meta[2]
            if not multi:
                self.stdout.write(f"{name} is a singleton — will create/update 1 row.")
                plan.append((name, 1))
                continue
            default = self._default_count(name)
            while True:
                raw_count = input(f"How many {name} rows? [{default}]: ").strip()
                if not raw_count:
                    count = default
                    break
                if raw_count.isdigit() and int(raw_count) >= 0:
                    count = int(raw_count)
                    break
                self.stderr.write("Enter a non-negative integer.")
            if count > 0:
                plan.append((name, count))
        return plan

    def _plan_from_flags(self, models_csv: str, counts_csv: str) -> list[tuple[str, int]]:
        if not models_csv.strip():
            self.stderr.write(self.style.ERROR("--models is required with --non-interactive"))
            return []
        names = [p.strip() for p in models_csv.split(",") if p.strip()]
        valid = {m[0] for m in self.SEEDERS}
        for name in names:
            if name not in valid:
                self.stderr.write(self.style.ERROR(f"Unknown model: {name}. Valid: {', '.join(sorted(valid))}"))
                return []
        counts_list = [p.strip() for p in counts_csv.split(",")] if counts_csv.strip() else []
        if counts_list and len(counts_list) != len(names):
            self.stderr.write(self.style.ERROR("--counts length must match --models"))
            return []

        plan: list[tuple[str, int]] = []
        order = [m[0] for m in self.SEEDERS]
        for name in order:
            if name not in names:
                continue
            idx = names.index(name)
            multi = next(m[2] for m in self.SEEDERS if m[0] == name)
            if not multi:
                plan.append((name, 1))
                continue
            if counts_list:
                if not counts_list[idx].isdigit():
                    self.stderr.write(self.style.ERROR(f"Bad count for {name}"))
                    return []
                count = int(counts_list[idx])
            else:
                count = self._default_count(name)
            if count > 0:
                plan.append((name, count))
        return plan

    @staticmethod
    def _default_count(name: str) -> int:
        return {
            "User": 10,
            "TradingAccount": 5,
            "SiteContent": 8,
            "LoginAttempt": 20,
            "PageVisit": 30,
        }.get(name, 5)

    # ── seeders ───────────────────────────────────────────────

    def _run_seeder(self, name: str, count: int) -> int:
        fn = {
            "User": self._seed_users,
            "TradingAccount": self._seed_trading_accounts,
            "SiteContent": self._seed_site_content,
            "AboutPage": self._seed_about_page,
            "ResumePage": self._seed_resume_page,
            "LoginAttempt": self._seed_login_attempts,
            "PageVisit": self._seed_page_visits,
        }[name]
        return fn(count)

    def _seed_users(self, count: int) -> int:
        created = 0
        for i in _progress(range(count), "User", total=count):
            first = random.choice(FIRST_NAMES)
            last = random.choice(LAST_NAMES)
            suffix = _unique_suffix(5)
            username = f"{first.lower()}.{last.lower()}.{suffix}"[:150]
            email = f"{first.lower()}.{last.lower()}.{suffix}@example.com"
            user = User(
                username=username,
                email=email,
                first_name=first,
                last_name=last,
                phone_number=_rand_phone(),
                national_id=_rand_national_id(),
                ip_address=_rand_ip(),
                mac_address=_rand_mac(),
                mac_source=random.choice(MAC_SOURCES),
                click_count=random.randint(0, 80),
                login_attempt_count=random.randint(0, 25),
                is_active=True,
                is_staff=False,
                is_superuser=False,
            )
            user.set_password(SEED_PASSWORD)
            user.save()
            created += 1
        return created

    def _seed_trading_accounts(self, count: int) -> int:
        users = list(User.objects.filter(is_superuser=False).order_by("-id")[:50])
        created = 0
        for i in _progress(range(count), "TradingAccount", total=count):
            acc = TradingAccount.objects.create(
                trading_acc_username=f"TA-{timezone.now().strftime('%y%m%d')}-{_unique_suffix(6).upper()}",
                broker=random.choice(BROKERS),
            )
            if users:
                linked = random.sample(users, k=min(len(users), random.randint(1, 3)))
                acc.users.set(linked)
            created += 1
        return created

    def _seed_site_content(self, count: int) -> int:
        # Build a shuffled pool of relatable cards, then take `count`
        pool: list[tuple[str, str, str, str]] = []
        for page, items in SITE_CONTENT_POOL.items():
            for key, value, icon in items:
                pool.append((page, key, value, icon))
        random.shuffle(pool)

        created = 0
        # If more requested than pool, cycle with numbered variants
        for i in _progress(range(count), "SiteContent", total=count):
            page, key, value, icon = pool[i % len(pool)]
            if i >= len(pool):
                key = f"{key} ({i + 1})"
            item = SiteContent()
            item.set_current_language("fa")
            item.page = page
            item.key = key[:100]
            item.value = value
            item.icon = icon
            item.order = i
            item.is_active = True
            item.save()
            created += 1
        return created

    def _seed_about_page(self, count: int) -> int:
        for _ in _progress(range(1), "AboutPage", total=1):
            page = AboutPage.get_solo()
            page.set_current_language("fa")
            page.title = "درباره HEF"
            page.body = random.choice(ABOUT_BODIES)
            page.save()
        return 1

    def _seed_resume_page(self, count: int) -> int:
        for _ in _progress(range(1), "ResumePage", total=1):
            page = ResumePage.get_solo()
            page.set_current_language("fa")
            page.title = "رزومه"
            page.body = random.choice(RESUME_BODIES)
            page.save()
        return 1

    def _seed_login_attempts(self, count: int) -> int:
        users = list(User.objects.all()[:40])
        usernames = [u.username for u in users] or ["guest", "trader01", "demo_user"]
        created = 0
        now = timezone.now()
        for i in _progress(range(count), "LoginAttempt", total=count):
            successful = random.random() < 0.65
            username = random.choice(usernames)
            user = next((u for u in users if u.username == username), None) if successful else None
            if not successful and random.random() < 0.3:
                username = username + "_wrong"
                user = None
            LoginAttempt.objects.create(
                user=user,
                username_tried=username[:150],
                ip_address=_rand_ip(),
                successful=successful,
                created_at=now - timedelta(minutes=random.randint(1, 60 * 24 * 14)),
            )
            created += 1
        return created

    def _seed_page_visits(self, count: int) -> int:
        users = list(User.objects.filter(is_active=True)[:40])
        created = 0
        now = timezone.now()
        for i in _progress(range(count), "PageVisit", total=count):
            path, url_name, label = random.choice(PAGE_ROUTES)
            authenticated = bool(users) and random.random() < 0.55
            user = random.choice(users) if authenticated else None
            PageVisit.objects.create(
                user=user,
                visitor_label=user.username if user else "anonymous",
                ip_address=_rand_ip(),
                mac_address=_rand_mac() if random.random() < 0.7 else "",
                path=path,
                url_name=url_name,
                page_label=label,
                user_agent=random.choice(USER_AGENTS),
                created_at=now - timedelta(minutes=random.randint(1, 60 * 24 * 30)),
            )
            created += 1
        return created
