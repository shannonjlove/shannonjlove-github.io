"""
Skill: Audio Format Conversion (DTS → AC3 / normalize)
Origin: Hazel "Convert DTS to AC3 Script" — mkvdts2ac3 workflow
SJL Stage: analyze (post-hook)

Detects audio streams needing conversion (DTS, FLAC in video containers)
and converts using ffmpeg with stream-copy for video. Standalone audio
files (WAV, AIFF, FLAC) are converted to AAC/MP3 per config.
"""

from __future__ import annotations

import logging
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

from filewarden.core.pipeline import Transaction, skill

log = logging.getLogger("filewarden.skills.audio_convert")

# Video containers that may contain DTS audio
VIDEO_CONTAINERS = {".mkv", ".avi", ".ts", ".m2ts"}
# Standalone audio extensions
AUDIO_EXTENSIONS = {".wav", ".aiff", ".aif", ".flac", ".dts", ".wma"}


def _detect_audio_codec(path: Path) -> Optional[str]:
    """Detect audio codec using ffprobe."""
    try:
        result = subprocess.run(
            [
                "ffprobe", "-v", "quiet",
                "-select_streams", "a:0",
                "-show_entries", "stream=codec_name",
                "-of", "csv=p=0",
                str(path),
            ],
            capture_output=True, text=True, timeout=15
        )
        return result.stdout.strip().lower() or None
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None


def _convert_audio_stream(src: Path, target_codec: str, config: Dict[str, Any]) -> Optional[Path]:
    """
    Convert audio in video container (copy video, re-encode audio).
    Returns output path or None on failure.
    """
    output = src.with_name(src.stem + f"_{target_codec}" + src.suffix)
    bitrate = config.get("audio_convert_bitrate", "640k") if target_codec == "ac3" else config.get("audio_convert_bitrate", "256k")

    cmd = [
        "ffmpeg", "-i", str(src),
        "-c:v", "copy",
        "-c:a", target_codec,
        "-b:a", bitrate,
        str(output),
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
        if result.returncode == 0:
            return output
        log.warning("ffmpeg audio conversion failed: %s", result.stderr[:300])
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        log.warning("Audio conversion error: %s", e)

    return None


@skill(stage="analyze", when="post", name="audio_convert")
def convert_audio(tx: Transaction, config: Dict[str, Any]) -> None:
    """
    Detect and convert DTS or other unsupported audio codecs.
    """
    if not config.get("audio_convert_enabled", False):
        return

    path = tx.original_path
    ext = path.suffix.lower()
    trigger_codecs = set(config.get("audio_convert_trigger_codecs", ["dts"]))
    target_codec = config.get("audio_convert_target_codec", "ac3")

    codec = _detect_audio_codec(path)
    if not codec or codec not in trigger_codecs:
        return

    log.info("Audio codec %s detected in %s, converting to %s", codec, path.name, target_codec)

    output_path = _convert_audio_stream(path, target_codec, config)
    if not output_path:
        tx.skill_outputs["audio_convert"] = {"error": "conversion failed"}
        return

    # Archive original and switch transaction to converted file
    if config.get("audio_convert_archive_original", True):
        import shutil
        archive_dir = Path(config.get("sjl_root", "/srv/sjl")) / "05000_ARCHIVES" / "05200_RETIRED-SYSTEMS" / "audio-originals"
        archive_dir.mkdir(parents=True, exist_ok=True)
        shutil.move(str(path), str(archive_dir / path.name))

    # Re-target transaction to converted file
    tx.original_path = output_path
    tx.skill_outputs["audio_convert"] = {
        "source_codec": codec,
        "target_codec": target_codec,
        "output": str(output_path),
    }
    log.info("Audio converted: %s → %s (%s)", codec, target_codec, output_path.name)
