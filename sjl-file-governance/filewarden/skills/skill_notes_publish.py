"""
Skill: PaperParrot / Notes Publishing
Origin: Hazel "Use Hazel to add a file to a new Apple Notes note"
        (Hazel AppleScript: make new note at folder "Notes" with properties)
SJL Stage: publish (post-hook)

In the SJL architecture, Apple Notes is replaced by BookStack (manuals,
navigable records) and PaperParrot/Paperless (governed document archive).
This skill routes files to PaperParrot with enriched metadata, mirroring
what the Hazel AppleScript was doing for Notes — but with full governance.

For files that explicitly need BookStack page creation (not just change
summaries), this skill creates a dedicated page with file preview content.
"""

from __future__ import annotations

import json
import logging
import urllib.request
from pathlib import Path
from typing import Any, Dict

from filewarden.core.pipeline import Transaction, skill

log = logging.getLogger("filewarden.skills.notes_publish")

PUBLISHABLE_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt", ".md", ".png", ".jpg", ".jpeg"}


@skill(stage="publish", when="post", name="notes_publish")
def publish_to_knowledge_base(tx: Transaction, config: Dict[str, Any]) -> None:
    """
    Create a BookStack page for the governed file with metadata preview.
    Equivalent to the Hazel → Apple Notes AppleScript, but in BookStack.
    """
    if not config.get("notes_publish_enabled", False):
        return

    path = tx.canonical_path
    if not path or not path.exists():
        return

    ext = path.suffix.lower().lstrip(".")
    if ext not in PUBLISHABLE_EXTENSIONS:
        return

    bs_url = config.get("bookstack_url")
    bs_token = config.get("bookstack_token")
    book_id = config.get("bookstack_intake_book_id")

    if not all([bs_url, bs_token, book_id]):
        return

    # Build page content (equivalent to the Notes HTML body)
    content = _build_page_content(tx, config)
    page_name = f"[{tx.version}] {tx.semantic_title or tx.canonical_name}"

    payload = json.dumps({
        "book_id": book_id,
        "name": page_name[:100],
        "markdown": content,
        "tags": [
            {"name": "DOCID", "value": tx.docid or ""},
            {"name": "PARA", "value": tx.para or ""},
            {"name": "Version", "value": tx.version or ""},
        ],
    }).encode()

    try:
        req = urllib.request.Request(
            f"{bs_url}/api/pages",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Token {bs_token}",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            result = json.loads(resp.read())
            page_id = result.get("id")
            tx.skill_outputs["notes_publish"] = {
                "bookstack_page_id": page_id,
                "bookstack_url": f"{bs_url}/books/{book_id}/page/{page_id}",
            }
            log.info("BookStack page created: %s (id=%s)", page_name, page_id)
    except Exception as e:
        log.warning("BookStack page creation failed (non-fatal): %s", e)


def _build_page_content(tx: Transaction, config: Dict[str, Any]) -> str:
    """Build Markdown content for the BookStack page."""
    path = tx.canonical_path
    location = tx.metadata.get("gps_location", {})
    yaml_fm = tx.metadata.get("yaml_front_matter", {})
    entity = tx.metadata.get("content_entity", "")

    sections = [
        f"# {tx.semantic_title or tx.canonical_name}",
        "",
        "## Governance Record",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| DOCID | `{tx.docid}` |",
        f"| Canonical Filename | `{tx.canonical_name}` |",
        f"| PARA | {tx.para} |",
        f"| Version | {tx.version} |",
        f"| SHA-256 | `{tx.sha256}` |",
        f"| MIME | {tx.metadata.get('mime_type', '')} |",
        f"| Size | {tx.metadata.get('file_size', 0):,} bytes |",
        f"| Mirror | {'✓ verified' if tx.mirror_verified else '⚠ pending'} |",
        f"| Ingested | {tx.started_at.isoformat()} |",
    ]

    if entity:
        sections.append(f"| Classified As | {entity} |")

    if location:
        sections.append(f"| Location | {location.get('full_address', '')[:80]} |")

    if yaml_fm:
        sections += ["", "## Document Metadata", ""]
        for k, v in yaml_fm.items():
            sections.append(f"- **{k.title()}**: {v}")

    sections += [
        "",
        "## Sidecar",
        "",
        f"Sidecar: `{path}.sjl.json`",
        f"Checksum: `{path}.sha256`",
        f"Registry ID: `{tx.docid}`",
        "",
        "_Governed by SJL FileWarden v2_",
    ]

    return "\n".join(sections)
