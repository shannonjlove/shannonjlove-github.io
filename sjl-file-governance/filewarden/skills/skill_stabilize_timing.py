"""
Skill: Write-Stable Guard (extended)
Origin: Hazel discussion on AutoImporter / scanner multi-page detection
        "Date Modified is not in the last N minutes" technique
SJL Stage: stabilize (pre-hook)

Extended write-stability detection. Supplements the core stabilize stage with:
  - Minimum file size threshold (won't process partial downloads)
  - Application-lock file detection (e.g. .~lock.file, .DS_Store race)
  - Size-stable polling for very large files (rclone syncs, video imports)
"""

from __future__ import annotations

import logging
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, Optional

from filewarden.core.pipeline import Transaction, skill

log = logging.getLogger("filewarden.skills.stabilize_timing")

# Files that indicate an application is still writing
LOCK_SUFFIXES = {
    ".part", ".partial", ".crdownload", ".download", ".tmp",
    ".~lock", ".lock", "_lock",
}
LOCK_PREFIXES = {".~lock.", "~$"}


def _is_locked(path: Path) -> bool:
    """Check if file has an active write-lock indicator."""
    name = path.name.lower()
    for suffix in LOCK_SUFFIXES:
        if name.endswith(suffix):
            return True
    for prefix in LOCK_PREFIXES:
        if name.startswith(prefix):
            return True
    # Check for companion lock file
    for suffix in LOCK_SUFFIXES:
        if (path.parent / (path.name + suffix)).exists():
            return True
    return False


def _is_size_stable(path: Path, wait_seconds: int = 5, checks: int = 3) -> bool:
    """
    Poll file size multiple times. Stable = same size across all checks.
    For large files being rclone-synced or scanner-assembled.
    """
    sizes = []
    for _ in range(checks):
        try:
            sizes.append(path.stat().st_size)
        except OSError:
            return False
        time.sleep(wait_seconds)
    return len(set(sizes)) == 1


def _min_size_met(path: Path, min_bytes: int) -> bool:
    try:
        return path.stat().st_size >= min_bytes
    except OSError:
        return False


@skill(stage="stabilize", when="pre", name="stabilize_timing")
def extended_stabilize_check(tx: Transaction, config: Dict[str, Any]) -> None:
    """
    Extended stabilization checks before the core stabilize stage runs.
    """
    path = tx.original_path

    # Lock file / partial download detection
    if _is_locked(path):
        tx.abort_with(
            f"stabilize_timing: file has active write lock indicator: {path.name}"
        )
        return

    # Minimum file size (won't process empty or near-empty temp files)
    min_bytes = config.get("stabilize_min_bytes", 0)
    if min_bytes > 0 and not _min_size_met(path, min_bytes):
        tx.abort_with(
            f"stabilize_timing: file too small ({path.stat().st_size} < {min_bytes} bytes)"
        )
        return

    # For large files, do extended size polling before handing off to core stabilize
    large_file_threshold = config.get("stabilize_large_file_bytes", 100 * 1024 * 1024)  # 100MB
    try:
        if path.stat().st_size >= large_file_threshold:
            if not _is_size_stable(
                path,
                wait_seconds=config.get("stabilize_large_poll_seconds", 10),
                checks=config.get("stabilize_large_poll_checks", 3),
            ):
                tx.abort_with(
                    "stabilize_timing: large file is still growing, will retry"
                )
                return
    except OSError:
        pass

    tx.skill_outputs["stabilize_timing"] = {"passed": True}
