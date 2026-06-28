"""
Skill: New Files Only / Stabilize Timing
Origin: Hazel "Processing New Files Only"
        Hazel "Giving a Folder Some Time"
        Hazel "Tip, working with big file databases" (smart folder + tag batching)
SJL Stage: stabilize (pre-hook)

Provides three Hazel best-practice patterns as configurable guards:

1. NEW FILES ONLY — process a file only if it's newer than the last scan
   ("Date Added is after Date Last Matched")

2. STABILIZE TIMING — don't process files written in the last N minutes
   ("Date Added is Today" AND "Date Added is not in last N hours")
   Prevents partial writes from entering governance.

3. BATCH WINDOW — process files only during configured time windows
   (avoids constant CPU load on large databases — the "smart folder + tag" trick)
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict

from filewarden.core.pipeline import Transaction, skill

log = logging.getLogger("filewarden.skills.new_files_only")

_SCAN_TIMES_PATH_KEY = "new_files_only_scan_cache"


def _load_scan_times(config: Dict[str, Any]) -> Dict[str, str]:
    path = Path(config.get(_SCAN_TIMES_PATH_KEY,
        "/srv/sjl/07000_SYSTEM-AUTOMATION/07400_MIRROR-REGISTRY/scan-times.json"
    ))
    try:
        return json.loads(path.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _save_scan_times(config: Dict[str, Any], data: Dict[str, str]) -> None:
    path = Path(config.get(_SCAN_TIMES_PATH_KEY,
        "/srv/sjl/07000_SYSTEM-AUTOMATION/07400_MIRROR-REGISTRY/scan-times.json"
    ))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def _is_within_batch_window(config: Dict[str, Any]) -> bool:
    """
    Check if current time is within any configured batch window.
    batch_windows: list of {"start": "HH:MM", "end": "HH:MM"}
    """
    windows = config.get("batch_windows", [])
    if not windows:
        return True  # no windows = always process

    now = datetime.now(timezone.utc).time()
    for w in windows:
        try:
            start_h, start_m = map(int, w["start"].split(":"))
            end_h, end_m = map(int, w["end"].split(":"))
            from datetime import time as dtime
            if dtime(start_h, start_m) <= now <= dtime(end_h, end_m):
                return True
        except (KeyError, ValueError):
            continue
    return False


@skill(stage="stabilize", when="pre", name="new_files_only")
def gate_new_files(tx: Transaction, config: Dict[str, Any]) -> None:
    """
    Enforce new-files-only and timing gating before stabilization.
    """
    path = tx.original_path
    file_key = str(path.resolve())
    now = datetime.now(timezone.utc)

    # ── Batch window check ──────────────────────────────────────────
    if not _is_within_batch_window(config):
        tx.abort_with("new_files_only: outside batch processing window")
        return

    # ── Stabilize timing gate ───────────────────────────────────────
    # "Date Added is not in the last N minutes"
    min_age_minutes = config.get("new_files_min_age_minutes", 0)
    if min_age_minutes > 0:
        try:
            mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
            age = now - mtime
            if age < timedelta(minutes=min_age_minutes):
                tx.abort_with(
                    f"new_files_only: file written {age.seconds // 60}m ago, "
                    f"minimum is {min_age_minutes}m"
                )
                return
        except OSError:
            pass

    # ── New-files-only check ────────────────────────────────────────
    # "Date Added is after Date Last Matched"
    if config.get("new_files_only_enabled", False):
        scan_times = _load_scan_times(config)
        last_seen = scan_times.get(file_key)

        if last_seen:
            try:
                last_dt = datetime.fromisoformat(last_seen)
                mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
                if mtime <= last_dt:
                    tx.abort_with(
                        "new_files_only: file not modified since last scan"
                    )
                    return
            except (ValueError, OSError):
                pass

        # Record this scan time
        scan_times[file_key] = now.isoformat()
        _save_scan_times(config, scan_times)

    tx.skill_outputs["new_files_only"] = {"passed": True}
