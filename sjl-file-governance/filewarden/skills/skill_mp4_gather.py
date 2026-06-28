"""
Skill: MP4 Gather from Subfolders
Origin: Hazel "Finding mp4's in subfolders & moving them to master folder"
        Key Hazel insights: use "Continue" rule + nested conditions on subfiles
SJL Stage: analyze (post-hook)

FileWarden's inotify/watchdog already sees deep subfolder events natively.
This skill handles the aggregation pattern: when a subfolder contains MP4s
(even mixed with other files), move the subfolder to 04300_VIDEO/mp4-gather/.
"""

from __future__ import annotations

import logging
import shutil
from pathlib import Path
from typing import Any, Dict

from filewarden.core.pipeline import Transaction, skill

log = logging.getLogger("filewarden.skills.mp4_gather")


def _folder_contains_mp4(folder: Path) -> bool:
    """Recursively check if any file in folder has .mp4 extension."""
    return any(
        f.suffix.lower() == ".mp4"
        for f in folder.rglob("*")
        if f.is_file()
    )


@skill(stage="analyze", when="post", name="mp4_gather")
def gather_mp4_subfolders(tx: Transaction, config: Dict[str, Any]) -> None:
    """
    If a directory contains MP4 files (anywhere in its tree),
    move the entire directory to the MP4 gather destination.
    """
    if not config.get("mp4_gather_enabled", False):
        return

    path = tx.original_path

    # Only act on directories
    if not path.is_dir():
        return

    # Skip if already in the gather destination
    gather_dest = Path(config.get(
        "mp4_gather_dest",
        "/srv/sjl/04000_RESOURCES/04300_VIDEO/mp4-gather"
    ))
    if path.is_relative_to(gather_dest):
        return

    if not _folder_contains_mp4(path):
        return

    gather_dest.mkdir(parents=True, exist_ok=True)
    dest = gather_dest / path.name

    try:
        shutil.move(str(path), str(dest))
        tx.canonical_path = dest
        tx.para = "04000"
        tx.metadata["mp4_gather_dest"] = str(dest)
        tx.skill_outputs["mp4_gather"] = {"moved_to": str(dest)}
        log.info("MP4 subfolder gathered: %s → %s", path.name, dest)
    except Exception as e:
        log.error("MP4 gather failed for %s: %s", path.name, e)
