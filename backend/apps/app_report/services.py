"""Secure report file discovery and serving helpers."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from django.conf import settings
from django.db.models import F
from django.utils import timezone

INDEX_RE = re.compile(r"^Index_(?P<username>.+)\.htm$")
DAILY_RE = re.compile(
    r"^Daily_(?P<username>.+)_(?P<start>\d{4}-\d{2}-\d{2})_to_(?P<end>\d{4}-\d{2}-\d{2})\.htm$"
)
WEEKLY_RE = re.compile(
    r"^Weekly_(?P<username>.+)_Week(?P<week>\d+)_(?P<start>\d{4}-\d{2}-\d{2})_to_(?P<end>\d{4}-\d{2}-\d{2})\.htm$"
)
MONTHLY_RE = re.compile(
    r"^Monthly_(?P<username>.+)_(?P<start>\d{4}-\d{2}-\d{2})_to_(?P<end>\d{4}-\d{2}-\d{2})\.htm$"
)
YEARLY_RE = re.compile(
    r"^Yearly_(?P<username>.+)_(?P<start>\d{4}-\d{2}-\d{2})_to_(?P<end>\d{4}-\d{2}-\d{2})\.htm$"
)

ALLOWED_REPORT_RE = re.compile(
    r"^(Index|Daily|Weekly|Monthly|Yearly)_[A-Za-z0-9._-]+\.htm$"
)
HREF_VALUE_RE = re.compile(
    r"""href=(['"])(?P<file>(?:Index|Daily|Weekly|Monthly|Yearly)_[A-Za-z0-9._-]+\.htm)\1""",
)


def rewrite_index_hrefs(html: str, username: str, file_url_builder) -> str:
    """Rewrite relative report hrefs to Django URLs; open each in a new tab/page."""

    def repl(match: re.Match) -> str:
        quote = match.group(1)
        filename = match.group("file")
        if classify_filename(filename, username) is None:
            return match.group(0)
        url = file_url_builder(filename)
        return f"href={quote}{url}{quote}"

    html = HREF_VALUE_RE.sub(repl, html)

    def add_new_tab_attrs(match: re.Match) -> str:
        tag = match.group(0)
        # Drop any existing target/rel so we can set a clean new-tab behavior
        tag = re.sub(r'\s+target=(["\'])[^"\']*\1', "", tag, flags=re.IGNORECASE)
        tag = re.sub(r'\s+rel=(["\'])[^"\']*\1', "", tag, flags=re.IGNORECASE)
        return tag[:-1] + ' target="_blank" rel="noopener noreferrer">'

    return re.sub(
        r'''<a\b[^>]*\bhref=(["'])/reports/file/[^"']+\1[^>]*>''',
        add_new_tab_attrs,
        html,
        flags=re.IGNORECASE,
    )


@dataclass
class ReportFile:
    filename: str
    report_type: str
    path: Path


def reports_root() -> Path:
    return Path(settings.REPORTS_ROOT)


def user_report_dir(username: str) -> Path:
    safe = Path(username).name
    return reports_root() / safe


def classify_filename(filename: str, username: str) -> Optional[str]:
    for report_type, pattern in (
        ("index", INDEX_RE),
        ("daily", DAILY_RE),
        ("weekly", WEEKLY_RE),
        ("monthly", MONTHLY_RE),
        ("yearly", YEARLY_RE),
    ):
        match = pattern.match(filename)
        if match and match.group("username") == username:
            return report_type
    return None


def safe_resolve_report(username: str, filename: str) -> Optional[Path]:
    """Return a resolved path only if it is a valid report under the user folder."""
    if not filename or "/" in filename or "\\" in filename or ".." in filename:
        return None
    if not ALLOWED_REPORT_RE.match(filename):
        return None
    if classify_filename(filename, username) is None:
        return None

    base = user_report_dir(username).resolve()
    candidate = (base / filename).resolve()
    try:
        candidate.relative_to(base)
    except ValueError:
        return None
    if not candidate.is_file():
        return None
    return candidate


def scan_user_reports(username: str) -> List[ReportFile]:
    folder = user_report_dir(username)
    if not folder.is_dir():
        return []
    results: List[ReportFile] = []
    for path in sorted(folder.glob("*.htm")):
        report_type = classify_filename(path.name, username)
        if report_type:
            results.append(
                ReportFile(filename=path.name, report_type=report_type, path=path)
            )
    return results


def folder_fingerprint(username: str) -> str:
    files = scan_user_reports(username)
    payload = []
    for item in files:
        try:
            mtime = item.path.stat().st_mtime_ns
        except OSError:
            mtime = 0
        payload.append(f"{item.filename}:{mtime}")
    return hashlib.sha256("|".join(payload).encode("utf-8")).hexdigest()


def maybe_rescan(user) -> int:
    """
    Rescan if interval elapsed. Bumps scan_version only when folder content changes.
    """
    from apps.app_account.models import UserScanSetting

    setting, _ = UserScanSetting.objects.get_or_create(user=user)
    now = timezone.now()
    due = (
        setting.last_scan_at is None
        or (now - setting.last_scan_at).total_seconds() >= setting.interval_seconds
    )
    if not due:
        return setting.scan_version

    fingerprint = folder_fingerprint(user.username)
    update_fields = {"last_scan_at": now, "last_fingerprint": fingerprint}
    if fingerprint != (setting.last_fingerprint or ""):
        UserScanSetting.objects.filter(pk=setting.pk).update(
            **update_fields,
            scan_version=F("scan_version") + 1,
        )
    else:
        UserScanSetting.objects.filter(pk=setting.pk).update(**update_fields)

    setting.refresh_from_db()
    return setting.scan_version


def read_report_html(path: Path) -> str:
    raw = path.read_bytes()
    for encoding in ("utf-8", "utf-8-sig", "cp1256", "latin-1"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")
