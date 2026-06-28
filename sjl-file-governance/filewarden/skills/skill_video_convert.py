"""
Skill: Video Format Conversion
Origin: Hazel "Script to convert a video file" (HandBrakeCLI)
        Hazel "Convert DTS to AC3 Script" (mkvdts2ac3 / ffmpeg)
SJL Stage: analyze (post-hook) — queues conversion job
         + stabilize (pre-hook) — prevents re-triggering in-progress conversions

Converts video files to target format via HandBrakeCLI or ffmpeg.
Guards against re-triggering by checking for a .converting sentinel file.
After conversion, routes original to 05000_ARCHIVES or trash per config.
"""

from __future__ import annotations

import logging
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List

from filewarden.core.pipeline import Transaction, skill

log = logging.getLogger("filewarden.skills.video_convert")

# Extensions that trigger conversion
CONVERT_TRIGGER_EXTENSIONS = {".mkv", ".avi", ".wmv", ".flv", ".mpg", ".mpeg", ".m4v"}
# Extensions that indicate already-converted output
SKIP_IF_ALREADY = {".mp4"}


def _sentinel_path(path: Path) -> Path:
    return path.parent / (path.stem + ".converting")


@skill(stage="stabilize", when="pre", name="video_convert_guard")
def guard_in_progress_conversion(tx: Transaction, config: Dict[str, Any]) -> None:
    """
    Hazel's 4th rule: "Check whether conversion is already in progress."
    If a .converting sentinel exists, abort to prevent double processing.
    """
    if not config.get("video_convert_enabled", False):
        return
    sentinel = _sentinel_path(tx.original_path)
    if sentinel.exists():
        tx.abort_with(
            f"video_convert: conversion already in progress ({sentinel.name})"
        )


@skill(stage="analyze", when="post", name="video_convert")
def queue_video_conversion(tx: Transaction, config: Dict[str, Any]) -> None:
    """
    Detect video files needing conversion and submit to HandBrakeCLI or ffmpeg.
    Creates a sentinel file to prevent re-triggering.
    """
    if not config.get("video_convert_enabled", False):
        return

    path = tx.original_path
    ext = path.suffix.lower()

    if ext not in CONVERT_TRIGGER_EXTENSIONS:
        return
    if ext in SKIP_IF_ALREADY:
        return

    convert_to = config.get("video_convert_target_ext", "mp4")
    output_path = path.with_suffix(f".{convert_to}")
    sentinel = _sentinel_path(path)

    # Create sentinel to prevent double-trigger
    sentinel.touch()

    try:
        converter = config.get("video_converter", "handbrake")

        if converter == "handbrake":
            _convert_handbrake(path, output_path, config)
        elif converter == "ffmpeg":
            _convert_ffmpeg(path, output_path, config)
        else:
            log.warning("Unknown converter: %s", converter)
            return

        # Conversion complete: archive original
        if config.get("video_convert_archive_original", True):
            from datetime import datetime, timezone
            archive_dir = Path(config.get("sjl_root", "/srv/sjl")) / "05000_ARCHIVES" / "05200_RETIRED-SYSTEMS" / "video-originals"
            archive_dir.mkdir(parents=True, exist_ok=True)
            import shutil
            shutil.move(str(path), str(archive_dir / path.name))
            log.info("Original archived: %s", path.name)

        tx.skill_outputs["video_convert"] = {
            "converted_to": str(output_path),
            "converter": converter,
        }
        log.info("Video converted: %s → %s", path.name, output_path.name)

    except Exception as e:
        log.error("Video conversion failed for %s: %s", path.name, e)
        tx.skill_outputs["video_convert"] = {"error": str(e)}
    finally:
        if sentinel.exists():
            sentinel.unlink()


def _convert_handbrake(src: Path, dst: Path, config: Dict[str, Any]) -> None:
    """Convert using HandBrakeCLI."""
    preset = config.get("handbrake_preset", "Fast 1080p30")
    cmd = [
        "HandBrakeCLI",
        "-i", str(src),
        "-o", str(dst),
        "--preset", preset,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
    if result.returncode != 0:
        raise RuntimeError(f"HandBrakeCLI error: {result.stderr[:500]}")


def _convert_ffmpeg(src: Path, dst: Path, config: Dict[str, Any]) -> None:
    """
    Convert using ffmpeg. Also handles DTS→AC3 audio conversion
    (equivalent to mkvdts2ac3 from the Hazel thread).
    """
    video_codec = config.get("ffmpeg_video_codec", "libx264")
    audio_codec = config.get("ffmpeg_audio_codec", "aac")
    crf = config.get("ffmpeg_crf", "23")

    # For DTS→AC3 specifically: keep video stream, convert audio only
    if config.get("video_convert_audio_only", False):
        audio_codec = "ac3"
        cmd = [
            "ffmpeg", "-i", str(src),
            "-c:v", "copy",          # copy video untouched
            "-c:a", audio_codec,
            "-b:a", "640k",
            str(dst),
        ]
    else:
        cmd = [
            "ffmpeg", "-i", str(src),
            "-c:v", video_codec,
            "-crf", str(crf),
            "-c:a", audio_codec,
            "-movflags", "+faststart",
            str(dst),
        ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg error: {result.stderr[:500]}")
