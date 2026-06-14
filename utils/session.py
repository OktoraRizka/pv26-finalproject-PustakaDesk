"""
PustakaDesk — utils/session.py
Data remember-me disimpan memakai QSettings milik sistem operasi, bukan di
SQLite dan bukan di dalam folder project. Password tidak pernah disimpan.
"""
from __future__ import annotations

from PySide6.QtCore import QSettings


_ORGANIZATION = "PV26"
_APPLICATION = "PustakaDesk"
_SESSION_KEY = "session/remembered_user_id"


def _settings() -> QSettings:
    # NativeFormat: Windows Registry pada Windows, dan lokasi konfigurasi user
    # milik OS pada platform lain. Tidak ikut saat folder project dikirim/di-zip.
    return QSettings(_ORGANIZATION, _APPLICATION)


def save_remembered_user(user_id: int) -> None:
    settings = _settings()
    settings.setValue(_SESSION_KEY, int(user_id))
    settings.sync()


def get_remembered_user_id() -> int | None:
    settings = _settings()
    value = settings.value(_SESSION_KEY, None)
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        clear_remembered_user()
        return None


def clear_remembered_user() -> None:
    settings = _settings()
    settings.remove(_SESSION_KEY)
    settings.sync()
