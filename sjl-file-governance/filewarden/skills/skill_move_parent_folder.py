"""
Skill: Move Parent/Containing Folder
Origin: Hazel "Moving Containing Folder of A File"
        Hazel's AppleScript: hazelSwitchFile → parent container
SJL Stage: analyze (post-hook)

When a file matches a condition, this skill re-targets the transaction
to the file's parent folder — equivalent to Hazel's hazelSwitchFile return
and the AppleScript container of theFile technique.

Use case: a music file arrives in a subfolder → move the entire album folder
to the Music library. Or: a PAR2 arrives in a download folder → process
the entire download folder when it's complete.
"""

from __future__ import annotations

import logging
import shutil
from pathlib import Path
from typing import Any, Callable, Dict, Optional

from filewarden.core.pipeline import Transaction, skill

log = logging.getLogger("filewarden.skills.move_parent_folder")


def _should_switch_to_parent(tx: Transaction, config: Dict[str, Any]) -> bool:
    """
    Determine if this file should trigger parent-folder processing.
    Configurable via match_extensions or match_kinds.
    """
    path = tx.original_path
    trigger_extensions = set(
        e.lower() for e in config.get("parent_folder_trigger_extensions", [])
    )
    if trigger_extensions and path.suffix.lower() not in trigger_extensions:
        return False

    # Only trigger when inside a subfolder (depth > 0)
    sjl_root = Path(config.get("sjl_root", "/srv/sjl"))
    try:
        depth = len(path.relative_to(sjl_root).parts) - 1
        return depth > 0
    except ValueError:
        return path.parent != path.parent.parent  # any nesting


@skill(stage="analyze", when="post", name="move_parent_folder")
def switch_to_parent(tx: Transaction, config: Dict[str, Any]) -> None:
    """
    Re-target transaction to the parent folder and move it to
    the configured destination.

    Config keys:
      parent_folder_trigger_extensions: list[str] — file extensions that trigger
      parent_folder_dest: str — destination root path
      parent_folder_move_para: str — PARA code for destination
    """
    if not config.get("parent_folder_enabled", False):
        return

    if not _should_switch_to_parent(tx, config):
        return

    parent = tx.original_path.parent
    dest_root = Path(config.get(
        "parent_folder_dest",
        "/srv/sjl/04000_RESOURCES/04400_AUDIO"
    ))
    dest_root.mkdir(parents=True, exist_ok=True)
    dest = dest_root / parent.name

    try:
        shutil.move(str(parent), str(dest))
        # Re-target the transaction to the moved folder
        tx.original_path = dest
        tx.para = config.get("parent_folder_move_para", "04000")
        tx.semantic_title = parent.name.lower().replace(" ", "-").replace("_", "-")[:60]
        tx.metadata["parent_folder_moved"] = str(dest)
        tx.skill_outputs["move_parent_folder"] = {
            "original_parent": str(parent),
            "moved_to": str(dest),
        }
        log.info("Parent folder moved: %s → %s", parent.name, dest)
    except Exception as e:
        log.error("Parent folder move failed for %s: %s", parent.name, e)
