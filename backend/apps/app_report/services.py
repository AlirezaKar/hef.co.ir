"""Secure history file discovery and serving helpers."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from django.conf import settings

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

ALLOWED_HISTORY_RE = re.compile(
    r"^(Index|Daily|Weekly|Monthly|Yearly)_[A-Za-z0-9._-]+\.htm$"
)
HREF_VALUE_RE = re.compile(
    r"""href=(['"])(?P<file>(?:Index|Daily|Weekly|Monthly|Yearly)_[A-Za-z0-9._-]+\.htm)\1""",
)


def rewrite_index_hrefs(html: str, trading_acc_username: str, file_url_builder) -> str:
    """Rewrite relative history hrefs to Django URLs; open each in a new tab/page."""

    def repl(match: re.Match) -> str:
        quote = match.group(1)
        filename = match.group("file")
        if classify_filename(filename, trading_acc_username) is None:
            return match.group(0)
        url = file_url_builder(filename)
        return f"href={quote}{url}{quote}"

    html = HREF_VALUE_RE.sub(repl, html)

    def add_new_tab_attrs(match: re.Match) -> str:
        tag = match.group(0)
        tag = re.sub(r'\s+target=(["\'])[^"\']*\1', "", tag, flags=re.IGNORECASE)
        tag = re.sub(r'\s+rel=(["\'])[^"\']*\1', "", tag, flags=re.IGNORECASE)
        return tag[:-1] + ' target="_blank" rel="noopener noreferrer">'

    return re.sub(
        r'''<a\b[^>]*\bhref=(["'])/history/file/[^"']+\1[^>]*>''',
        add_new_tab_attrs,
        html,
        flags=re.IGNORECASE,
    )


HOME_ANCHOR_RE = re.compile(
    r"<a\b([^>]*)>(.*?بازگشت به صفحه اصلی.*?)</a>",
    re.IGNORECASE | re.DOTALL,
)


def rewrite_report_home_button(html: str, home_url: str) -> str:
    """Point the history file's native 'بازگشت به صفحه اصلی' control to the site home."""

    def repl(match: re.Match) -> str:
        attrs = match.group(1) or ""
        inner = match.group(2)
        attrs = re.sub(r'\s*href\s*=\s*(["\'])[^"\']*\1', "", attrs, flags=re.IGNORECASE)
        attrs = re.sub(r'\s*target\s*=\s*(["\'])[^"\']*\1', "", attrs, flags=re.IGNORECASE)
        attrs = attrs.rstrip()
        return f'<a{attrs} href="{home_url}" target="_top">{inner}</a>'

    return HOME_ANCHOR_RE.sub(repl, html)


@dataclass
class HistoryFile:
    filename: str
    report_type: str
    path: Path


def history_root() -> Path:
    return Path(settings.HISTORY_ROOT)


def history_acc_dir(trading_acc_username: str) -> Path:
    safe = Path(str(trading_acc_username)).name
    return history_root() / f"History-{safe}"


def ensure_history_dir(trading_acc_username: str) -> Path:
    """
    Ensure data/History/History-{trading_acc_username}/ exists.
    Creates the folder (and parents) when missing.
    """
    folder = history_acc_dir(trading_acc_username)
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def classify_filename(filename: str, trading_acc_username: str) -> Optional[str]:
    for report_type, pattern in (
        ("index", INDEX_RE),
        ("daily", DAILY_RE),
        ("weekly", WEEKLY_RE),
        ("monthly", MONTHLY_RE),
        ("yearly", YEARLY_RE),
    ):
        match = pattern.match(filename)
        if match and match.group("username") == trading_acc_username:
            return report_type
    return None


def safe_resolve_history(trading_acc_username: str, filename: str) -> Optional[Path]:
    """Return a resolved path only if it is a valid history file under the account folder."""
    if not filename or "/" in filename or "\\" in filename or ".." in filename:
        return None
    if not ALLOWED_HISTORY_RE.match(filename):
        return None
    if classify_filename(filename, trading_acc_username) is None:
        return None

    base = history_acc_dir(trading_acc_username).resolve()
    candidate = (base / filename).resolve()
    try:
        candidate.relative_to(base)
    except ValueError:
        return None
    if not candidate.is_file():
        return None
    return candidate


def scan_account_history(trading_acc_username: str) -> List[HistoryFile]:
    folder = history_acc_dir(trading_acc_username)
    if not folder.is_dir():
        return []
    results: List[HistoryFile] = []
    for path in sorted(folder.glob("*.htm")):
        report_type = classify_filename(path.name, trading_acc_username)
        if report_type:
            results.append(
                HistoryFile(filename=path.name, report_type=report_type, path=path)
            )
    return results


def read_history_html(path: Path) -> str:
    raw = path.read_bytes()
    for encoding in ("utf-8", "utf-8-sig", "cp1256", "latin-1"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")
