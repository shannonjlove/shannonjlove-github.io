"""
Skill: PDF OCR Detection and Queuing
Origin: Hazel "Determine if a PDF needs to be OCR'd & Automate FineReader"
SJL Stage: analyze (post-hook)

The Hazel technique: grep the raw PDF binary for the word "Font" to detect
whether a text layer already exists. If not, queue for OCRmyPDF on Oracle/sOs.

This skill:
1. Detects whether the PDF has a text layer
2. Queues it for OCRmyPDF if needed
3. Optionally reduces file size via Ghostscript (replaces quartzfilter)
4. Updates ocr_state in the transaction
"""

from __future__ import annotations

import logging
import subprocess
from pathlib import Path
from typing import Any, Dict

from filewarden.core.pipeline import Transaction, skill

log = logging.getLogger("filewarden.skills.pdf_ocr_detect")


def _has_text_layer(path: Path) -> bool:
    """
    Hazel's original technique: grep the raw PDF bytes for 'Font'.
    A native or OCR'd PDF contains font directives; a bitmap scan does not.
    """
    try:
        with open(path, "rb") as f:
            # Read in 64KB chunks; text layer indicators appear in first ~20% of file
            for _ in range(8):
                chunk = f.read(65536)
                if not chunk:
                    break
                if b"Font" in chunk or b"/Text" in chunk:
                    return True
        return False
    except OSError:
        return False


def _has_text_via_pdftotext(path: Path) -> bool:
    """Secondary check: pdftotext (poppler) to extract and count characters."""
    try:
        result = subprocess.run(
            ["pdftotext", str(path), "-"],
            capture_output=True, timeout=30
        )
        return len(result.stdout.strip()) > 50
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def _submit_to_ocr_queue(path: Path, docid: str, config: Dict[str, Any]) -> bool:
    """
    Submit PDF to OCR queue (n8n webhook → Oracle/sOs OCRmyPDF worker).
    Falls back to local ocrmypdf if available.
    """
    import json
    import urllib.request

    n8n_url = config.get("n8n_ocr_webhook")
    if n8n_url:
        payload = json.dumps({
            "docid": docid,
            "path": str(path),
            "tool": "ocrmypdf",
            "priority": "normal",
        }).encode()
        try:
            req = urllib.request.Request(
                n8n_url,
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            urllib.request.urlopen(req, timeout=10)
            return True
        except Exception as e:
            log.warning("OCR queue submission failed: %s", e)

    # Local fallback: run ocrmypdf inline
    try:
        result = subprocess.run(
            [
                "ocrmypdf",
                "--skip-text",          # don't re-OCR pages that already have text
                "--optimize", "1",
                "--output-type", "pdfa",
                str(path), str(path),   # in-place
            ],
            capture_output=True, text=True, timeout=300
        )
        if result.returncode == 0:
            log.info("Local OCR completed for %s", path.name)
            return True
        log.warning("Local OCR failed: %s", result.stderr)
    except FileNotFoundError:
        log.debug("ocrmypdf not installed locally")
    except subprocess.TimeoutExpired:
        log.warning("Local OCR timed out for %s", path.name)

    return False


def _reduce_pdf_size(path: Path, config: Dict[str, Any]) -> None:
    """
    Reduce PDF file size using Ghostscript.
    Replaces the macOS quartzfilter technique from the Hazel thread.
    Only replaces if the result is smaller.
    """
    try:
        import tempfile, os
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp_path = Path(tmp.name)

        result = subprocess.run(
            [
                "gs",
                "-sDEVICE=pdfwrite",
                "-dCompatibilityLevel=1.4",
                "-dPDFSETTINGS=/ebook",  # 150dpi images
                "-dNOPAUSE", "-dQUIET", "-dBATCH",
                f"-sOutputFile={tmp_path}",
                str(path),
            ],
            capture_output=True, timeout=120
        )
        if result.returncode == 0:
            orig_size = path.stat().st_size
            new_size = tmp_path.stat().st_size
            if new_size < orig_size:
                import shutil
                shutil.move(str(tmp_path), str(path))
                log.info(
                    "PDF reduced: %s → %s bytes (%.0f%% reduction)",
                    orig_size, new_size, (1 - new_size / orig_size) * 100
                )
            else:
                os.unlink(tmp_path)
                log.debug("PDF reduction not beneficial, keeping original")
        else:
            if tmp_path.exists():
                os.unlink(tmp_path)
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        log.debug("Ghostscript PDF reduction skipped: %s", e)


@skill(stage="analyze", when="post", name="pdf_ocr_detect")
def detect_and_queue_ocr(tx: Transaction, config: Dict[str, Any]) -> None:
    """
    Check PDF for text layer; queue OCR if missing; optionally reduce size.
    """
    path = tx.original_path
    if path.suffix.lower() != ".pdf":
        return

    # Stabilize check: don't process multi-page scans still being written
    # (The stabilize stage already handled this, but log state)
    has_text = _has_text_layer(path) or _has_text_via_pdftotext(path)

    if has_text:
        tx.ocr_state = "native-text"
        tx.skill_outputs["pdf_ocr"] = {"has_text_layer": True, "action": "none"}
        log.debug("PDF already has text layer: %s", path.name)
    else:
        tx.ocr_state = "queued"
        queued = _submit_to_ocr_queue(path, tx.docid or path.stem, config)
        tx.skill_outputs["pdf_ocr"] = {
            "has_text_layer": False,
            "action": "ocr-queued" if queued else "ocr-queue-failed",
        }
        log.info("PDF needs OCR, queued: %s", path.name)

    # Optionally reduce PDF size after OCR queuing
    if config.get("pdf_reduce_size", False):
        _reduce_pdf_size(path, config)
