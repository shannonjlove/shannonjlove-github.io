"""
Skill: Content-Based Classification (Custom List Matching)
Origin: Hazel "Amazing trick to write one simple rule instead of 100s"
        Hazel "How to set up a perfect filing system"
SJL Stage: analyze (post-hook)

Hazel's "Contents contain match Custom List item" + "Sort into subfolder
with pattern" — one rule replaces hundreds. The token capture also enables
renaming with the matched entity name.

This skill reads the file's text content and matches against a configurable
entity list (vendors, document types, correspondents). Sets PARA, semantic
title, and destination subpath from the matched entity.
"""

from __future__ import annotations

import logging
import re
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from filewarden.core.pipeline import Transaction, skill

log = logging.getLogger("filewarden.skills.content_classify")


def _extract_text(path: Path) -> str:
    """Extract readable text from PDF, DOCX, or plain text file."""
    ext = path.suffix.lower()

    if ext == ".pdf":
        try:
            result = subprocess.run(
                ["pdftotext", str(path), "-"],
                capture_output=True, timeout=30
            )
            return result.stdout.decode("utf-8", errors="replace")
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

    elif ext in {".docx", ".doc"}:
        try:
            import docx as _docx
            doc = _docx.Document(str(path))
            return "\n".join(p.text for p in doc.paragraphs)
        except ImportError:
            pass

    elif ext in {".txt", ".md", ".csv", ".json", ".yaml", ".yml", ".xml"}:
        try:
            return path.read_text(errors="replace")
        except OSError:
            pass

    return ""


def _match_entity(text: str, entity_list: List[Dict]) -> Optional[Dict]:
    """
    Find first entity whose match_patterns appear in text.
    Returns the entity dict with display_name substituted if needed.

    entity_list format:
      [
        {"match_patterns": ["amazon.com", "amazon order"], "display_name": "Amazon", "para": "03000", "subpath": "03100_BUSINESS/invoices"},
        {"match_patterns": ["merrill lynch", "merrilledge"], "display_name": "Merrill Lynch", "para": "03000"},
        ...
      ]
    """
    text_lower = text.lower()
    for entity in entity_list:
        for pattern in entity.get("match_patterns", []):
            if pattern.lower() in text_lower:
                return entity
    return None


@skill(stage="analyze", when="post", name="content_classify")
def classify_by_content(tx: Transaction, config: Dict[str, Any]) -> None:
    """
    Match document content against entity/keyword list and route to
    the appropriate PARA destination with a meaningful semantic title.
    """
    entity_list = config.get("content_classify_entities", [])
    if not entity_list:
        return

    path = tx.original_path
    text = _extract_text(path)
    if not text:
        return

    entity = _match_entity(text, entity_list)
    if not entity:
        return

    display_name = entity.get("display_name", "unknown")
    para = entity.get("para", tx.para or "03000")
    subpath = entity.get("subpath", "")

    # Override PARA and title from entity match
    tx.para = para
    tx.semantic_title = re.sub(r"[^a-z0-9]+", "-", display_name.lower()).strip("-")
    if subpath:
        tx.metadata["dest_subpath"] = subpath

    # Add sequential document number prefix to semantic title
    # (Hazel "perfect filing system" technique: sequential number + date + descriptor)
    seq = _next_sequence_number(config)
    tx.metadata["doc_sequence"] = seq
    tx.metadata["content_entity"] = display_name

    tx.skill_outputs["content_classify"] = {
        "matched_entity": display_name,
        "para": para,
        "sequence": seq,
    }
    log.info("Content classified as '%s' (PARA=%s) for %s", display_name, para, path.name)


def _next_sequence_number(config: Dict[str, Any]) -> str:
    """
    Increment and return the global document sequence counter.
    Stored in a simple counter file for persistence across runs.
    """
    counter_path = Path(config.get(
        "sequence_counter_path",
        "/srv/sjl/07000_SYSTEM-AUTOMATION/07400_MIRROR-REGISTRY/doc-sequence.txt"
    ))
    counter_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        n = int(counter_path.read_text().strip()) + 1
    except (FileNotFoundError, ValueError):
        n = 1
    counter_path.write_text(str(n))
    return f"{n:06d}"
