"""
Skill: PDF Size Reduction
Origin: Hazel "Determine if a PDF needs to be OCR'd" — Quartz filter technique
SJL Stage: analyze (post-hook) — runs after OCR detection

Linux/server replacement for macOS quartzfilter using Ghostscript.
Only replaces the file if the compressed version is actually smaller
(same size check as the original Hazel bash script).

Quality profiles (maps to Ghostscript -dPDFSETTINGS):
  screen  → 72 dpi, maximum compression (for web preview)
  ebook   → 150 dpi, moderate compression (default)
  printer → 300 dpi, minimal compression (for print archival)
  prepress→ 300 dpi, high quality, color preservation
"""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict

from filewarden.core.pipeline import Transaction, skill

log = logging.getLogger("filewarden.skills.pdf_size_reduce")

QUALITY_PROFILES = {
    "screen": "/screen",
    "ebook": "/ebook",
    "printer": "/printer",
    "prepress": "/prepress",
}


def _reduce_with_ghostscript(
    src: Path,
    quality: str = "ebook",
    compat: str = "1.4",
) -> Path:
    """
    Run Ghostscript to reduce PDF size. Returns temp file path.
    Caller is responsible for checking size and replacing if beneficial.
    """
    gs_setting = QUALITY_PROFILES.get(quality, "/ebook")
    tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
    tmp.close()
    tmp_path = Path(tmp.name)

    result = subprocess.run(
        [
            "gs",
            "-sDEVICE=pdfwrite",
            f"-dCompatibilityLevel={compat}",
            f"-dPDFSETTINGS={gs_setting}",
            "-dNOPAUSE", "-dQUIET", "-dBATCH",
            f"-sOutputFile={tmp_path}",
            str(src),
        ],
        capture_output=True, timeout=180
    )
    if result.returncode != 0:
        if tmp_path.exists():
            os.unlink(tmp_path)
        raise RuntimeError(f"Ghostscript failed: {result.stderr.decode()[:300]}")

    return tmp_path


@skill(stage="analyze", when="post", name="pdf_size_reduce")
def reduce_pdf_size(tx: Transaction, config: Dict[str, Any]) -> None:
    """
    Reduce PDF file size using Ghostscript if the result is smaller.
    """
    if not config.get("pdf_reduce_size", False):
        return

    path = tx.original_path
    if path.suffix.lower() != ".pdf":
        return

    quality = config.get("pdf_reduce_quality", "ebook")
    compat = config.get("pdf_reduce_compat", "1.4")

    try:
        orig_size = path.stat().st_size
        tmp_path = _reduce_with_ghostscript(path, quality, compat)
        new_size = tmp_path.stat().st_size

        if new_size < orig_size:
            reduction_pct = (1 - new_size / orig_size) * 100
            shutil.move(str(tmp_path), str(path))
            tx.metadata["pdf_original_size"] = orig_size
            tx.metadata["pdf_reduced_size"] = new_size
            tx.skill_outputs["pdf_size_reduce"] = {
                "original_bytes": orig_size,
                "reduced_bytes": new_size,
                "reduction_pct": round(reduction_pct, 1),
            }
            log.info(
                "PDF reduced: %s → %s bytes (%.1f%%): %s",
                orig_size, new_size, reduction_pct, path.name
            )
        else:
            os.unlink(tmp_path)
            tx.skill_outputs["pdf_size_reduce"] = {
                "action": "not-beneficial",
                "original_bytes": orig_size,
                "gs_output_bytes": new_size,
            }
            log.debug("PDF reduction not beneficial for %s", path.name)

    except FileNotFoundError:
        log.debug("Ghostscript (gs) not installed; pdf_size_reduce skipped")
    except subprocess.TimeoutExpired:
        log.warning("Ghostscript timed out for %s", path.name)
    except Exception as e:
        log.error("PDF size reduction failed for %s: %s", path.name, e)
