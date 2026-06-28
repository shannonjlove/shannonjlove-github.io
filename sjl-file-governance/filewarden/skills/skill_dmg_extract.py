"""
Skill: Disk Image (DMG) Extraction
Origin: Hazel "Get contents of disk images" (Ruby script: hdiutil + cp)
SJL Stage: analyze (post-hook)

Mounts a macOS .dmg, extracts non-alias contents to a destination directory,
then cleanly ejects the disk image and optionally archives the DMG.
Linux-compatible fallback: 7-zip extraction for HFS+ images.
"""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List

from filewarden.core.pipeline import Transaction, skill

log = logging.getLogger("filewarden.skills.dmg_extract")


def _mount_dmg_macos(dmg_path: Path) -> str:
    """Mount DMG via hdiutil. Returns mount point path."""
    result = subprocess.run(
        ["hdiutil", "attach", "-nobrowse", "-noverify", str(dmg_path)],
        input=b"y\n",  # auto-agree to license
        capture_output=True, timeout=60
    )
    if result.returncode != 0:
        raise RuntimeError(f"hdiutil attach failed: {result.stderr.decode()}")

    # Last line of output is the mount point
    lines = result.stdout.decode().strip().split("\n")
    mount_point = lines[-1].split("\t")[-1].strip()
    return mount_point


def _eject_dmg_macos(mount_point: str) -> None:
    """Eject using hdiutil eject (cleaner than detach --force)."""
    subprocess.run(["hdiutil", "eject", mount_point], capture_output=True, timeout=30)


def _extract_dmg_linux(dmg_path: Path, dest_dir: Path) -> None:
    """Linux fallback: extract DMG using 7-zip (p7zip-full)."""
    result = subprocess.run(
        ["7z", "x", str(dmg_path), f"-o{dest_dir}", "-y"],
        capture_output=True, text=True, timeout=120
    )
    if result.returncode != 0:
        raise RuntimeError(f"7z extraction failed: {result.stderr}")


def _is_alias(path: Path) -> bool:
    """
    Detect macOS aliases (symlinks or Finder aliases).
    The original Ruby script used GetFileInfo -a; we use os.path.islink.
    """
    return os.path.islink(str(path))


def _count_non_aliases(items: List[Path]) -> int:
    return sum(1 for p in items if not _is_alias(p))


@skill(stage="analyze", when="post", name="dmg_extract")
def extract_disk_image(tx: Transaction, config: Dict[str, Any]) -> None:
    """
    Extract contents of a .dmg file to the configured destination.
    Creates a subfolder if the DMG contains multiple files.
    """
    if not config.get("dmg_extract_enabled", False):
        return

    path = tx.original_path
    if path.suffix.lower() != ".dmg":
        return

    dest_root = Path(config.get(
        "dmg_extract_dest",
        "/srv/sjl/01000_INBOX/01100_DEVICE-INTAKE/dmg-extracts"
    ))
    dest_root.mkdir(parents=True, exist_ok=True)

    import platform
    is_macos = platform.system() == "Darwin"

    try:
        if is_macos:
            _extract_macos(path, dest_root, config)
        else:
            _extract_linux(path, dest_root, config)

        tx.para = "01000"
        tx.skill_outputs["dmg_extract"] = {"extracted_to": str(dest_root)}
        log.info("DMG extracted: %s → %s", path.name, dest_root)

    except Exception as e:
        log.error("DMG extraction failed for %s: %s", path.name, e)
        tx.skill_outputs["dmg_extract"] = {"error": str(e)}


def _extract_macos(dmg_path: Path, dest_root: Path, config: Dict[str, Any]) -> None:
    mount_point = _mount_dmg_macos(dmg_path)
    mount_path = Path(mount_point)

    try:
        items = [p for p in mount_path.iterdir()]
        non_aliases = [p for p in items if not _is_alias(p)]

        # Create subfolder if multiple files (updated Ruby script logic)
        if _count_non_aliases(non_aliases) > 1:
            dest_dir = dest_root / dmg_path.stem
            dest_dir.mkdir(parents=True, exist_ok=True)
        else:
            dest_dir = dest_root

        for item in non_aliases:
            dest = dest_dir / item.name
            if not dest.exists():
                shutil.copytree(str(item), str(dest)) if item.is_dir() else shutil.copy2(str(item), str(dest))

    finally:
        _eject_dmg_macos(mount_point)

    # Archive or trash original DMG
    if config.get("dmg_extract_archive_original", False):
        archive_dir = Path(config.get("sjl_root", "/srv/sjl")) / "05000_ARCHIVES" / "05200_RETIRED-SYSTEMS" / "dmg-originals"
        archive_dir.mkdir(parents=True, exist_ok=True)
        shutil.move(str(dmg_path), str(archive_dir / dmg_path.name))


def _extract_linux(dmg_path: Path, dest_root: Path, config: Dict[str, Any]) -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        _extract_dmg_linux(dmg_path, Path(tmpdir))
        items = list(Path(tmpdir).iterdir())
        if len(items) > 1:
            dest_dir = dest_root / dmg_path.stem
            dest_dir.mkdir(parents=True, exist_ok=True)
        else:
            dest_dir = dest_root

        for item in items:
            dest = dest_dir / item.name
            shutil.copytree(str(item), str(dest)) if item.is_dir() else shutil.copy2(str(item), str(dest))
