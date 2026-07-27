"""Helpers for client IP and MAC address resolution."""

from __future__ import annotations

import hashlib
import random
import re
import subprocess
from typing import Optional, Tuple

from django.http import HttpRequest


def get_client_ip(request: HttpRequest) -> Optional[str]:
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def _normalize_mac(mac: str) -> Optional[str]:
    if not mac:
        return None
    cleaned = re.sub(r"[^0-9A-Fa-f]", "", mac)
    if len(cleaned) != 12:
        return None
    parts = [cleaned[i : i + 2] for i in range(0, 12, 2)]
    return ":".join(parts).upper()


def _mac_from_ip(ip: Optional[str]) -> Optional[str]:
    if not ip or ip in ("127.0.0.1", "::1"):
        return None
    try:
        from getmac import get_mac_address

        mac = get_mac_address(ip=ip)
        return _normalize_mac(mac or "")
    except Exception:
        pass
    try:
        output = subprocess.check_output(
            ["arp", "-a", ip],
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=3,
        )
        match = re.search(
            r"([0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}",
            output,
        )
        if match:
            return _normalize_mac(match.group(0))
    except Exception:
        pass
    return None


def _mac_from_hdd() -> Optional[str]:
    """Derive a stable MAC-format id from local disk serial (Windows/Linux)."""
    serial = None
    try:
        output = subprocess.check_output(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                "(Get-CimInstance Win32_DiskDrive | Select-Object -First 1 -ExpandProperty SerialNumber)",
            ],
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=5,
        ).strip()
        if output:
            serial = output
    except Exception:
        pass

    if not serial:
        try:
            output = subprocess.check_output(
                ["wmic", "diskdrive", "get", "SerialNumber"],
                stderr=subprocess.DEVNULL,
                text=True,
                timeout=5,
            )
            lines = [
                line.strip()
                for line in output.splitlines()
                if line.strip() and "SerialNumber" not in line
            ]
            if lines:
                serial = lines[0]
        except Exception:
            pass

    if not serial:
        try:
            with open("/sys/class/dmi/id/product_uuid", encoding="utf-8") as fh:
                serial = fh.read().strip()
        except Exception:
            pass

    if not serial:
        return None

    digest = hashlib.sha256(serial.encode("utf-8", errors="ignore")).hexdigest()[:12]
    # Locally administered, unicast bit pattern
    first_byte = (int(digest[0:2], 16) | 0x02) & 0xFE
    mac = f"{first_byte:02X}{digest[2:]}"
    return _normalize_mac(mac)


def _generate_mac() -> str:
    data = [random.randint(0x00, 0xFF) for _ in range(6)]
    data[0] = (data[0] | 0x02) & 0xFE
    return ":".join(f"{b:02X}" for b in data)


def resolve_mac_address(request: HttpRequest) -> Tuple[str, str]:
    """
    Resolve MAC with fallback chain: IP ARP -> HDD serial -> generated.
    Returns (mac_address, mac_source) where source is ip|hdd|generated.
    """
    ip = get_client_ip(request)
    mac = _mac_from_ip(ip)
    if mac:
        return mac, "ip"

    mac = _mac_from_hdd()
    if mac:
        return mac, "hdd"

    return _generate_mac(), "generated"


def apply_network_identity(user, request: HttpRequest, *, force_mac: bool = False) -> None:
    """Update user IP and MAC fields from the current request."""
    ip = get_client_ip(request)
    changed = []
    if ip and user.ip_address != ip:
        user.ip_address = ip
        changed.append("ip_address")

    if force_mac or not user.mac_address:
        mac, source = resolve_mac_address(request)
        user.mac_address = mac
        user.mac_source = source
        changed.extend(["mac_address", "mac_source"])

    if changed:
        user.save(update_fields=changed)
