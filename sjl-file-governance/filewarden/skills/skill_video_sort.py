"""
Skill: Video Sort (Movies / TV Shows / Other Videos)
Origin: Hazel "Sorting Movies, TV Shows, and Other Videos"
SJL Stage: analyze (post-hook)

Routes video files to canonical PARA destinations based on filename patterns.
Uses the same logic as the Hazel thread:
  - Folders matching "Title (Year)" → Movies
  - Files with S##E## pattern → TV Shows
  - Kind=Movie but no pattern match → Other Videos
All land in 04000_RESOURCES/04300_VIDEO/<category>/
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any, Dict, Optional

from filewarden.core.pipeline import Transaction, skill

log = logging.getLogger("filewarden.skills.video_sort")

VIDEO_EXTENSIONS = {".mkv", ".mp4", ".avi", ".mov", ".m4v", ".wmv", ".flv", ".webm", ".mpg", ".mpeg"}

# Movie: "Title (Year)" or "Title.Year." pattern
MOVIE_PATTERN = re.compile(r"^(.+?)\s*[\(\.\-]\s*(\d{4})\s*[\)\.\-]?", re.IGNORECASE)

# TV Show: S##E## (with or without spaces/dots between S and E)
TV_PATTERN = re.compile(r"[Ss](\d{1,2})\s*[Ee](\d{1,2})", re.IGNORECASE)


def _classify_video(path: Path) -> str:
    """Return 'movies', 'tv-shows', 'other-videos', or None (not a video)."""
    if path.suffix.lower() not in VIDEO_EXTENSIONS:
        return None

    # Use full name (stem + suffix) to avoid dots being treated as extension
    full_name = path.name

    if TV_PATTERN.search(full_name):
        return "tv-shows"

    if MOVIE_PATTERN.search(path.stem):
        return "movies"

    return "other-videos"


def _extract_series_info(name: str) -> Optional[Dict[str, str]]:
    """Extract show title, season, episode from TV show filename."""
    m = TV_PATTERN.search(name)
    if not m:
        return None
    season = int(m.group(1))
    episode = int(m.group(2))
    # Title is everything before the S##E## token
    title_raw = name[:m.start()].replace(".", " ").replace("_", " ").strip()
    return {
        "title": title_raw,
        "season": f"{season:02d}",
        "episode": f"{episode:02d}",
        "se_tag": f"S{season:02d}E{episode:02d}",
    }


def _extract_movie_info(name: str) -> Optional[Dict[str, str]]:
    """Extract movie title and year."""
    m = MOVIE_PATTERN.search(name)
    if not m:
        return None
    return {
        "title": m.group(1).strip().replace(".", " "),
        "year": m.group(2),
    }


@skill(stage="analyze", when="post", name="video_sort")
def classify_video(tx: Transaction, config: Dict[str, Any]) -> None:
    """
    Classify video file as movie / TV show / other and set PARA + semantic title.
    """
    path = tx.original_path
    category = _classify_video(path)
    if not category:
        return

    tx.para = "04000"

    if category == "tv-shows":
        info = _extract_series_info(path.stem)
        if info:
            show_slug = re.sub(r"[^a-z0-9]+", "-", info["title"].lower()).strip("-")
            tx.semantic_title = f"{show_slug}-{info['se_tag'].lower()}"
            tx.metadata["tv_show"] = info
            tx.metadata["dest_subpath"] = f"04300_VIDEO/tv-shows/{show_slug}/season-{info['season']}"
        else:
            tx.semantic_title = "tv-show-episode"
            tx.metadata["dest_subpath"] = "04300_VIDEO/tv-shows"

    elif category == "movies":
        info = _extract_movie_info(path.stem)
        if info:
            movie_slug = re.sub(r"[^a-z0-9]+", "-", info["title"].lower()).strip("-")
            tx.semantic_title = f"{movie_slug}-{info['year']}"
            tx.metadata["movie"] = info
            tx.metadata["dest_subpath"] = f"04300_VIDEO/movies"
        else:
            tx.semantic_title = "movie"
            tx.metadata["dest_subpath"] = "04300_VIDEO/movies"

    else:
        tx.semantic_title = "video"
        tx.metadata["dest_subpath"] = "04300_VIDEO/other-videos"

    tx.skill_outputs["video_sort"] = {
        "category": category,
        "semantic_title": tx.semantic_title,
    }
    log.info("Video classified as '%s': %s → %s", category, path.name, tx.semantic_title)
