from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from django.conf import settings
from django.core.files.storage import FileSystemStorage


@lru_cache(maxsize=1)
def get_cdn_storage() -> FileSystemStorage:
    root = Path(settings.CDN_ROOT)
    root.mkdir(parents=True, exist_ok=True)
    return FileSystemStorage(location=str(root), base_url=settings.CDN_URL)
