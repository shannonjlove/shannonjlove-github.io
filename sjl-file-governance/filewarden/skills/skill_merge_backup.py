"""
Skill: Merge-to Backup (Non-Destructive Mirror)
Origin: Hazel "Merge to" to copy a folder structure without deleting destination
SJL Stage: mirror (post-hook)

Hazel had no "Merge to" — it took two rules to avoid overwriting destination.
This skill mirrors the canonical file to a secondary backup destination
(external drive or secondary cloud path) only if the destination doesn't
already have the same content (SHA-256 match), never deleting destination files.
"""

from __future__ import annotations

import logging
import shutil
from pathlib import Path
from typing import Any, Dict

from filewarden.core.pipeline import Transaction, skill

log = logging.getLogger("filewarden.skills.merge_backup")


@skill(stage="mirror", when="post", name="merge_backup")
def merge_to_backup(tx: Transaction, config: Dict[str, Any]) -> None:
    """
    Non-destructive copy of canonical file to secondary backup destinations.

    Config keys:
      merge_backup_destinations: list[str] — list of local/mounted paths
      merge_backup_preserve_structure: bool — recreate PARA subfolder structure
    """
    destinations = config.get("merge_backup_destinations", [])
    if not destinations or not tx.canonical_path:
        return

    preserve_structure = config.get("merge_backup_preserve_structure", True)

    for dest_root in destinations:
        dest_root_path = Path(dest_root)
        if not dest_root_path.exists():
            log.warning("Backup destination not available: %s", dest_root)
            tx.skill_outputs.setdefault("merge_backup", {}).update(
                {dest_root: "destination-unavailable"}
            )
            continue

        # Build destination path mirroring PARA structure
        if preserve_structure and tx.para:
            dest_dir = dest_root_path / tx.para
        else:
            dest_dir = dest_root_path

        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_file = dest_dir / tx.canonical_name

        # Never overwrite if destination has the same SHA-256
        if dest_file.exists():
            import hashlib
            h = hashlib.sha256()
            try:
                with open(dest_file, "rb") as f:
                    for chunk in iter(lambda: f.read(65536), b""):
                        h.update(chunk)
                if h.hexdigest() == tx.sha256:
                    log.debug("Backup already current at %s", dest_file)
                    tx.skill_outputs.setdefault("merge_backup", {})[dest_root] = "already-current"
                    continue
            except OSError:
                pass

        # Copy canonical file and companions (sidecar, checksum)
        try:
            shutil.copy2(str(tx.canonical_path), str(dest_file))
            # Copy sidecar
            if tx.sidecar_path and tx.sidecar_path.exists():
                shutil.copy2(str(tx.sidecar_path), str(dest_dir / tx.sidecar_path.name))
            # Copy checksum
            checksum_src = tx.canonical_path.parent / (tx.canonical_name + ".sha256")
            if checksum_src.exists():
                shutil.copy2(str(checksum_src), str(dest_dir / checksum_src.name))

            log.info("Merged backup: %s → %s", tx.canonical_name, dest_dir)
            tx.skill_outputs.setdefault("merge_backup", {})[dest_root] = "copied"
        except Exception as e:
            log.error("Merge backup failed for %s: %s", dest_root, e)
            tx.skill_outputs.setdefault("merge_backup", {})[dest_root] = f"error: {e}"
