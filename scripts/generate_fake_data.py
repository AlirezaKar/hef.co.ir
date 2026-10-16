#!/usr/bin/env python
"""
Generate fake data for HEF website models.

This script creates realistic test data for:
- Users (with Iranian names and phone numbers)
- Trading accounts
- Site content (FAQ, About, Contact)
- Page visits
- Login attempts

Usage:
    python scripts/generate_fake_data.py

Requires Django environment. Run from project root:
    cd /path/to/hef.co.ir
    python scripts/generate_fake_data.py
"""

import os
import sys
import random
from datetime import datetime, timedelta

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.app_account.models import TradingAccount, LoginAttempt, PageVisit
from apps.app_main.models import SiteContent, AboutPage, ResumePage

User = get_user_model()

# Iranian names
FIRST_NAMES_MALE = [
    "علی", "محمد", "حسین", "رضا", "مهدی", "امیر", "سعید", "محسن",
    "حسن", "جواد", "مصطفی", "ابوالفضل", "مجتبی", "حمید", "مجید",
]

FIRST_NAMES_FEMALE = [
    "فاطمه", "زهرا", "مریم", "سارا", "نرگس", "لیلا", "نازنین", "شیما",
    "مینا", "سمیه", "زهرا", "معصومه", "حوری", "اعظم", "اکرم",
]

LAST_NAMES = [
    "محمدی", "حسینی", "احمدی", "رضایی", "کریمی", "موسوی", "هاشمی",
    "رحیمی", "مرادی", "صادقی", "کاظمی", "نجفی", "باقری", "عباسی",
    "توکلی", "اکبری", "سلطانی", "فتاحی", "نوری", "امینی",
]

CITIES = [
    "تهران", "اصفهان", "مشهد", "شیراز", "تبریز", "کرج", "اهواز",
    "قم", "کرمانشاه", "ارومیه", "رشت", "زاهدان", "همدان", "کرمان",
]

BROKERS = [
    "Alpari", "Exness", "RoboForex", "FBS", "IC Markets", "XM",
    "Pepperstone", "AvaTrade", "Tickmill", "FTMO", "OctaFX", "Amar Markets",
]

FAQ_ITEMS = [
    ("چطور می‌توانم ثبت‌نام کنم؟", "برای ثبت‌نام روی دکمه «ثبت‌نام» در بالای صفحه کلیک کنید و اطلاعات خواسته شده را وارد نمایید."),
    ("آیا استفاده از سایت رایگان است؟", "بله، مشاهده تاریخچه حساب‌های ترید کاملاً رایگان است."),
    ("چطور حساب ترید خود را اضافه کنم؟", "پس از ورود به حساب کاربری، از منوی پروفایل گزینه «ایجاد حساب ترید» را انتخاب کنید."),
    ("آیا اطلاعات من امن است؟", "بله، تمام اطلاعات با رمزنگاری قوی محافظت می‌شوند و فقط شما به آن‌ها دسترسی دارید."),
    ("چطور رمز عبور خود را تغییر دهم؟", "از صفحه پروفایل، روی «ویرایش اطلاعات» کلیک کنید و رمز عبور جدید را وارد نمایید."),
    ("آیا می‌توانم چند حساب ترید داشته باشم؟", "بله، می‌توانید هر تعداد حساب ترید که می‌خواهید اضافه کنید."),
    ("پشتیبانی چگونه کار می‌کند؟", "می‌توانید از طریق صفحه تماس با ما یا ایمیل support@hef.co.ir با ما در ارتباط باشید."),
    ("آیا اپلیکیشن موبایل دارید؟", "در حال حاضر فقط نسخه وب در دسترس است، اما اپلیکیشن موبایل در دست توسعه است."),
]

CONTACT_ITEMS = [
    ("ایمیل پشتیبانی", "support@hef.co.ir", "✉️"),
    ("تلفن تماس", "۲۱-۱۲۳۴۵۶۷۸", "📞"),
    ("آدرس", "تهران، خیابان ولیعصر، پلاک ۱۲۳", "📍"),
    ("ساعات کاری", "شنبه تا چهارشنبه ۹ صبح تا ۶ عصر", ""),
]

ABOUT_TEXT = """
<h2>درباره HEF</h2>
<p>
    HEF یک پلتفرم جامع برای مدیریت و مشاهده تاریخچه حساب‌های ترید است.
    ما با ارائه ابزارهای ساده و کاربردی، به تریدرها کمک می‌کنیم تا عملکرد
    معاملات خود را بهتر تحلیل کنند.
</p>
<h3>مأموریت ما</h3>
<p>
    ارائه بهترین تجربه کاربری برای تریدرهای ایرانی با تمرکز بر سادگی،
    امنیت و سرعت.
</p>
<h3>چشم‌انداز</h3>
<p>
    تبدیل شدن به مرجع اصلی تریدرهای ایرانی برای مدیریت و تحلیل تاریخچه معاملات.
</p>
"""

RESUME_TEXT = """
<h2>تیم HEF</h2>
<p>
    تیم ما متشکل از متخصصان با تجربه در حوزه‌های برنامه‌نویسی، طراحی UX/UI،
    و بازارهای مالی است.
</p>
<h3>تخصص‌ها</h3>
<ul>
    <li>توسعه وب با Django و Python</li>
    <li>طراحی رابط کاربری مدرن و کاربرپسند</li>
    <li>تحلیل بازارهای مالی و فارکس</li>
    <li>امنیت سایبری و حفاظت از داده‌ها</li>
</ul>
"""


def generate_phone_number():
    """Generate a random Iranian mobile number."""
    prefix = random.choice(["0912", "0913", "0914", "0915", "0916", "0917", "0918", "0919", "0990", "0991"])
    suffix = "".join([str(random.randint(0, 9)) for _ in range(7)])
    return prefix + suffix


def generate_national_id():
    """Generate a random Iranian national ID (10 digits)."""
    return "".join([str(random.randint(0, 9)) for _ in range(10)])


def generate_username(first_name, last_name):
    """Generate a username from Persian name."""
    # Simple transliteration for username
    username_map = {
        "علی": "ali", "محمد": "mohammad", "حسین": "hossein", "رضا": "reza",
        "مهدی": "mehdi", "امیر": "amir", "سعید": "saeed", "محسن": "mohsen",
        "فاطمه": "fateme", "زهرا": "zahra", "مریم": "maryam", "سارا": "sara",
        "نرگس": "narges", "لیلا": "leila",
    }
    first_en = username_map.get(first_name, first_name[:3])
    last_en = last_name[:4]
    suffix = str(random.randint(100, 999))
    return f"{first_en}_{last_en}_{suffix}"


def create_users(count=10):
    """Create fake users."""
    print(f"Creating {count} users...")
    users = []
    
    for i in range(count):
        is_male = random.random() > 0.5
        first_name = random.choice(FIRST_NAMES_MALE if is_male else FIRST_NAMES_FEMALE)
        last_name = random.choice(LAST_NAMES)
        username = generate_username(first_name, last_name)
        
        # Ensure unique username
        while User.objects.filter(username=username).exists():
            username = generate_username(first_name, last_name)
        
        user = User.objects.create_user(
            username=username,
            email=f"{username}@example.com",
            password="TestPass123!",
            first_name=first_name,
            last_name=last_name,
            phone_number=generate_phone_number(),
            national_id=generate_national_id(),
        )
        users.append(user)
        print(f"  ✓ Created user: {username}")
    
    return users


def create_trading_accounts(users, count=15):
    """Create fake trading accounts."""
    print(f"Creating {count} trading accounts...")
    accounts = []
    
    for i in range(count):
        broker = random.choice(BROKERS)
        account_number = f"ACC{random.randint(100000, 999999)}"
        
        account = TradingAccount.objects.create(
            trading_acc_username=account_number,
            broker=broker,
        )
        
        # Assign to 1-3 random users
        num_users = random.randint(1, min(3, len(users)))
        assigned_users = random.sample(users, num_users)
        account.users.set(assigned_users)
        
        accounts.append(account)
        print(f"  ✓ Created account: {account_number} ({broker})")
    
    return accounts


def create_site_content():
    """Create FAQ and Contact content."""
    print("Creating site content...")
    
    # Clear existing content
    SiteContent.objects.all().delete()
    
    # Create FAQ items
    for question, answer in FAQ_ITEMS:
        SiteContent.objects.create(
            page=SiteContent.Page.FAQ,
            key=question,
            value=answer,
            order=random.randint(1, 100),
            is_active=True,
        )
    print(f"  ✓ Created {len(FAQ_ITEMS)} FAQ items")
    
    # Create Contact items
    for title, value, icon in CONTACT_ITEMS:
        SiteContent.objects.create(
            page=SiteContent.Page.CONTACT,
            key=title,
            value=value,
            icon=icon,
            order=random.randint(1, 100),
            is_active=True,
        )
    print(f"  ✓ Created {len(CONTACT_ITEMS)} Contact items")


def create_about_page():
    """Create or update About page."""
    print("Creating About page...")
    about = AboutPage.get_solo()
    about.title = "درباره HEF"
    about.body = ABOUT_TEXT
    about.save()
    print("  ✓ About page updated")


def create_resume_page():
    """Create or update Resume page."""
    print("Creating Resume page...")
    resume = ResumePage.get_solo()
    resume.title = "تیم ما"
    resume.body = RESUME_TEXT
    resume.save()
    print("  ✓ Resume page updated")


def create_page_visits(users, count=50):
    """Create fake page visits."""
    print(f"Creating {count} page visits...")
    
    pages = [
        ("/", "main:home", "صفحه اصلی"),
        ("/faq/", "main:faq", "سؤالات متداول"),
        ("/contact/", "main:contact", "تماس با ما"),
        ("/about/", "main:about", "درباره ما"),
        ("/resume/", "main:resume", "رزومه"),
        ("/learn/", "learn:index", "آموزش"),
        ("/download/", "download:index", "مرکز دانلود"),
        ("/finance/", "finance:hub", "سرمایه‌گذاری"),
    ]
    
    now = timezone.now()
    
    for i in range(count):
        # Random date within last 30 days
        days_ago = random.randint(0, 30)
        hours_ago = random.randint(0, 23)
        visit_date = now - timedelta(days=days_ago, hours=hours_ago)
        
        path, url_name, page_label = random.choice(pages)
        
        # 70% authenticated, 30% anonymous
        if random.random() < 0.7 and users:
            user = random.choice(users)
            visitor_label = user.username
        else:
            user = None
            visitor_label = "anonymous"
        
        PageVisit.objects.create(
            user=user,
            visitor_label=visitor_label,
            ip_address=f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",
            path=path,
            url_name=url_name,
            page_label=page_label,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            created_at=visit_date,
        )
    
    print(f"  ✓ Created {count} page visits")


def create_login_attempts(users, count=30):
    """Create fake login attempts."""
    print(f"Creating {count} login attempts...")
    
    now = timezone.now()
    
    for i in range(count):
        # Random date within last 7 days
        hours_ago = random.randint(1, 168)
        attempt_date = now - timedelta(hours=hours_ago)
        
        user = random.choice(users) if users and random.random() < 0.8 else None
        successful = random.random() < 0.7  # 70% success rate
        
        LoginAttempt.objects.create(
            user=user,
            username_tried=user.username if user else f"user{random.randint(1000, 9999)}",
            ip_address=f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",
            successful=successful,
            created_at=attempt_date,
        )
    
    print(f"  ✓ Created {count} login attempts")


def main():
    """Main function to generate all fake data."""
    print("=" * 60)
    print("HEF Fake Data Generator")
    print("=" * 60)
    print()
    
    # Check if we should clear existing data
    clear = input("Clear existing data before generating? (y/n): ").strip().lower()
    if clear == 'y':
        print("\nClearing existing data...")
        PageVisit.objects.all().delete()
        LoginAttempt.objects.all().delete()
        TradingAccount.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        print("✓ Existing data cleared\n")
    
    # Generate data
    users = create_users(count=10)
    print()
    
    accounts = create_trading_accounts(users, count=15)
    print()
    
    create_site_content()
    print()
    
    create_about_page()
    print()
    
    create_resume_page()
    print()
    
    create_page_visits(users, count=50)
    print()
    
    create_login_attempts(users, count=30)
    print()
    
    print("=" * 60)
    print("✓ Fake data generation complete!")
    print("=" * 60)
    print()
    print("Test credentials:")
    print("  Username: any generated username")
    print("  Password: TestPass123!")
    print()


if __name__ == "__main__":
    main()
