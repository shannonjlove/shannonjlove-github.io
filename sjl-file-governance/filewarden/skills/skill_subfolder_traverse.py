"""
Skill: Subfolder Traverse
Origin: Hazel "How to get Hazel to go into subfolders"
SJL Stage: analyze (pre-hook)

FileWarden watches filesystem events natively via inotify/watchdog, so
subfolder traversal is automatic. This skill handles the edge cases:
- Depth limiting (Hazel's "Subfolder Depth" condition)
- Per-depth rule gating
- Folder-vs-file rule separation
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict

from filewarden.core.pipeline import Transaction, skill

log = logging.getLogger("filewarden.skills.subfolder_traverse")


@skill(stage="analyze", when="pre", name="subfolder_traverse")
def check_subfolder_depth(tx: Transaction, config: Dict[str, Any]) -> None:
    """
    Gate processing on subfolder depth rules from config.

    Config keys:
      subfolder_max_depth: int  — skip files deeper than this (default: unlimited)
      subfolder_min_depth: int  — skip files shallower than this (default: 0)
      subfolder_skip_folders: bool — skip Kind=Folder items (default: False)
      subfolder_skip_files: bool   — skip Kind=File items (default: False)
    """
    sjl_root = Path(config.get("sjl_root", "/srv/sjl"))
    max_depth = config.get("subfolder_max_depth", None)
    min_depth = config.get("subfolder_min_depth", 0)
    skip_folders = config.get("subfolder_skip_folders", False)
    skip_files = config.get("subfolder_skip_files", False)

    path = tx.original_path

    # Kind check
    if path.is_dir() and skip_folders:
        tx.abort_with("subfolder_traverse: skipping directory (skip_folders=true)")
        return
    if path.is_file() and skip_files:
        tx.abort_with("subfolder_traverse: skipping file (skip_files=true)")
        return

    # Depth calculation relative to SJL root
    try:
        relative = path.relative_to(sjl_root)
        depth = len(relative.parts) - 1  # 0 = directly in sjl_root
    except ValueError:
        depth = 0  # outside sjl_root, treat as depth 0

    if max_depth is not None and depth > max_depth:
        tx.abort_with(
            f"subfolder_traverse: depth {depth} exceeds max_depth {max_depth}"
        )
        return

    if depth < min_depth:
        tx.abort_with(
            f"subfolder_traverse: depth {depth} below min_depth {min_depth}"
        )
        return

    tx.metadata["subfolder_depth"] = depth
    tx.skill_outputs["subfolder_traverse"] = {"depth": depth}
    log.debug("subfolder depth=%d for %s", depth, path.name)
