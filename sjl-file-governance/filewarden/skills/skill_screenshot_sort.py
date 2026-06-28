"""
Skill: Screenshot Sort by Device
Origin: Hazel "Sorting Screenshots" — classify by image dimensions to identify source device
SJL Stage: analyze (post-hook)

Identifies the source device from screenshot dimensions and routes to:
  04000_RESOURCES/04200_IMAGES/<device>/
Sets PARA code, semantic title prefix, and device tag.
"""

from __future__ import annotations

import logging
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from filewarden.core.pipeline import Transaction, skill

log = logging.getLogger("filewarden.skills.screenshot_sort")

# Device dimension signatures (width x height, both orientations)
DEVICE_SIGNATURES: Dict[Tuple[int, int], str] = {
    (390, 844): "iphone-14",
    (393, 852): "iphone-15",
    (430, 932): "iphone-14-plus",
    (428, 926): "iphone-13-pro-max",
    (375, 667): "iphone-se-2020",
    (414, 896): "iphone-11",
    (820, 1180): "ipad-air",
    (1024, 1366): "ipad-pro-13",
    (834, 1194): "ipad-pro-11",
    (768, 1024): "ipad-mini",
    (2560, 1600): "macbook-pro-13",
    (3024, 1964): "macbook-pro-14",
    (3456, 2234): "macbook-pro-16",
    (2880, 1800): "macbook-pro-15",
    (1920, 1080): "display-1080p",
    (2560, 1440): "display-1440p",
    (3840, 2160): "display-4k",
    (1280, 800): "webtop-1280",
    (1920, 1200): "webtop-1920",
}

SCREENSHOT_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp"}


def _get_dimensions(path: Path) -> Optional[Tuple[int, int]]:
    try:
        result = subprocess.run(
            ["identify", "-format", "%wx%h", str(path)],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            parts = result.stdout.strip().split("x")
            if len(parts) == 2:
                return (int(parts[0]), int(parts[1]))
    except (FileNotFoundError, ValueError):
        pass
    try:
        from PIL import Image
        with Image.open(path) as img:
            return img.size
    except ImportError:
        pass
    return None


def _identify_device(dims: Tuple[int, int]) -> str:
    w, h = dims
    device = DEVICE_SIGNATURES.get((w, h)) or DEVICE_SIGNATURES.get((h, w))
    if device:
        return device
    return "desktop-unknown" if w > h else "mobile-unknown"


@skill(stage="analyze", when="post", name="screenshot_sort")
def classify_screenshot(tx: Transaction, config: Dict[str, Any]) -> None:
    path = tx.original_path
    if path.suffix.lower() not in SCREENSHOT_EXTENSIONS:
        return

    name_lower = path.stem.lower()
    is_screenshot = (
        name_lower.startswith("screenshot")
        or name_lower.startswith("screen shot")
        or "screenshot" in name_lower
    )
    if not is_screenshot and not config.get("screenshot_sort_all_images", False):
        return

    dims = _get_dimensions(path)
    if not dims:
        return

    device = _identify_device(dims)
    tx.metadata["source_device"] = device
    tx.metadata["image_dimensions"] = f"{dims[0]}x{dims[1]}"
    tx.para = "04000"
    tx.semantic_title = f"screenshot-{device}"

    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    tx.metadata["dest_subpath"] = f"04200_IMAGES/{now.year}/{now.strftime('%m')}/{device}"

    tx.skill_outputs["screenshot_sort"] = {
        "device": device,
        "dimensions": f"{dims[0]}x{dims[1]}",
        "para": "04000",
    }
    log.info("Screenshot from %s (%dx%d): %s", device, dims[0], dims[1], path.name)
