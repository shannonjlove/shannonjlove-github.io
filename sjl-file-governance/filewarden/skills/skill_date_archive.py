"""
Skill: Date-Based Archiving
Origin: Hazel "Sorting files into monthly & yearly archives"
        Hazel "Processing New Files Only"
        Hazel "Giving a Folder Some Time"
        Hazel "Tip, working with big file databases"
SJL Stage: analyze (pre-hook) — gating conditions
         + rename (post-hook) — destination path override

Implements the Hazel best-practice patterns:
  1. "Date Last Matched is not Today" — process each file at most once per day
  2. "Date Added is after Date Last Matched" — new files only
  3. Time-delay gating — don't process files written in the last N minutes
  4. Monthly → Yearly archiving for old files in INBOX/Downloads
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, Optional

from filewarden.core.pipeline import Transaction, skill

log = logging.getLogger("filewarden.skills.date_archive")

# Per-file "last processed" cache (in-memory; persisted to JSON on disk)
_last_matched: Dict[str, str] = {}
_cache_path: Optional[Path] = None


def _load_cache(config: Dict[str, Any]) -> None:
    global _last_matched, _cache_path
    _cache_path = Path(config.get(
        "date_archive_cache",
        "/srv/sjl/07000_SYSTEM-AUTOMATION/07400_MIRROR-REGISTRY/date-archive-cache.json"
    ))
    try:
        _last_matched = json.loads(_cache_path.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        _last_matched = {}


def _save_cache() -> None:
    if _cache_path:
        _cache_path.parent.mkdir(parents=True, exist_ok=True)
        _cache_path.write_text(json.dumps(_last_matched, indent=2))


def _is_new_today(path: Path) -> bool:
    """File added/modified today."""
    try:
        mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
        return mtime.date() == datetime.now(timezone.utc).date()
    except OSError:
        return False


def _is_stable_for(path: Path, min_age_minutes: int) -> bool:
    """File has not been modified in the last N minutes (write-settled)."""
    try:
        mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
        age = datetime.now(timezone.utc) - mtime
        return age >= timedelta(minutes=min_age_minutes)
    except OSError:
        return False


def _not_processed_today(file_key: str) -> bool:
    """True if this file has not been processed today (Hazel: Date Last Matched is not Today)."""
    last = _last_matched.get(file_key)
    if not last:
        return True
    today = datetime.now(timezone.utc).date().isoformat()
    return last != today


def _archive_dest_for_age(path: Path, config: Dict[str, Any]) -> Optional[str]:
    """
    Hazel monthly/yearly archive logic:
    - File older than weekly_age_days → monthly subfolder (YYYY-MM)
    - File older than monthly_age_days → yearly subfolder (YYYY)
    """
    weekly_days = config.get("archive_weekly_days", 7)
    monthly_days = config.get("archive_monthly_days", 42)  # ~6 weeks

    try:
        mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
        age_days = (datetime.now(timezone.utc) - mtime).days
    except OSError:
        return None

    sjl_root = config.get("sjl_root", "/srv/sjl")
    if age_days >= monthly_days:
        year = mtime.strftime("%Y")
        return f"{sjl_root}/05000_ARCHIVES/05100_COMPLETED-PROJECTS/{year}"
    elif age_days >= weekly_days:
        month = mtime.strftime("%Y-%m")
        return f"{sjl_root}/05000_ARCHIVES/05100_COMPLETED-PROJECTS/{month}"
    return None


@skill(stage="analyze", when="pre", name="date_archive_gate")
def gate_by_date_rules(tx: Transaction, config: Dict[str, Any]) -> None:
    """
    Gate processing based on date conditions. Abort if file doesn't meet
    the temporal requirements (prevents redundant processing).
    """
    if not config.get("date_archive_enabled", False):
        return

    _load_cache(config)

    path = tx.original_path
    file_key = str(path)

    # "Processing New Files Only" — Date Added is after Date Last Matched
    new_only = config.get("date_archive_new_files_only", False)
    if new_only and not _not_processed_today(file_key):
        tx.abort_with("date_archive: already processed today (Date Last Matched is Today)")
        return

    # Time-delay gating — "Date Added is not in last N minutes"
    min_age = config.get("date_archive_min_age_minutes", 0)
    if min_age > 0 and not _is_stable_for(path, min_age):
        tx.abort_with(
            f"date_archive: file modified within last {min_age} minutes, skipping"
        )
        return

    # Record processing date
    _last_matched[file_key] = datetime.now(timezone.utc).date().isoformat()
    _save_cache()


@skill(stage="rename", when="post", name="date_archive_route")
def route_to_date_archive(tx: Transaction, config: Dict[str, Any]) -> None:
    """
    After canonical rename, check if the file's age warrants moving it
    to the monthly or yearly archive subfolder.
    """
    if not config.get("date_archive_auto_route", False):
        return

    # Only act on INBOX files
    if not tx.para or not tx.para.startswith("01"):
        return

    path = tx.canonical_path or tx.original_path
    archive_dest = _archive_dest_for_age(path, config)
    if not archive_dest:
        return

    dest_dir = Path(archive_dest)
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_file = dest_dir / path.name

    import shutil
    try:
        shutil.move(str(path), str(dest_file))
        tx.canonical_path = dest_file
        tx.para = "05000"
        tx.metadata["archive_route"] = str(dest_dir)
        tx.skill_outputs["date_archive"] = {"routed_to": str(dest_dir)}
        log.info("Archived old file: %s → %s", path.name, dest_dir)
    except Exception as e:
        log.error("Date archive routing failed: %s", e)
