"""
Skill: YAML Front Matter Tag Extraction
Origin: Hazel "Use Hazel to Add Tags to Files" (bash script reading line 5)
SJL Stage: analyze (post-hook)

Reads YAML front matter from text/Markdown files.
Extracts Tags:, Category:, Title:, Date: fields.
Writes them as:
  - Extended attributes (macOS xattrs compatible; Linux via python-xattr)
  - SJL metadata fields (semantic title, PARA override, date override)
  - ExifTool keywords (for searchability)

YAML front matter format:
  ---
  Title: My Document Title
  Date: 2026-06-28
  Category: Writing
  Tags: Hazel, Automation, SJL
  ---
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from filewarden.core.pipeline import Transaction, skill

log = logging.getLogger("filewarden.skills.yaml_tag_extract")

TEXT_EXTENSIONS = {".txt", ".md", ".markdown", ".rst", ".tex", ".org"}
YAML_FRONT_MATTER = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)
YAML_FIELD = re.compile(r"^(\w+):\s*(.+)$", re.MULTILINE)


def _parse_front_matter(content: str) -> Optional[Dict[str, str]]:
    """Extract YAML front matter fields from text content."""
    m = YAML_FRONT_MATTER.match(content)
    if not m:
        return None
    yaml_block = m.group(1)
    fields = {}
    for fm in YAML_FIELD.finditer(yaml_block):
        fields[fm.group(1).lower()] = fm.group(2).strip()
    return fields if fields else None


def _parse_tags(tags_value: str) -> List[str]:
    """Split 'Tag1, Tag2, Tag3' into ['Tag1', 'Tag2', 'Tag3']."""
    return [t.strip() for t in tags_value.split(",") if t.strip()]


def _write_xattrs(path: Path, tags: List[str]) -> None:
    """Write tags as extended attributes (com.apple.metadata:_kMDItemUserTags style)."""
    try:
        import xattr  # type: ignore
        import plistlib
        existing = xattr.getxattr(str(path), "com.apple.metadata:_kMDItemUserTags")
        existing_tags = plistlib.loads(existing)
    except (ImportError, OSError, Exception):
        existing_tags = []

    merged = list(set(existing_tags + tags))
    try:
        import xattr, plistlib
        xattr.setxattr(str(path), "com.apple.metadata:_kMDItemUserTags",
                       plistlib.dumps(merged, fmt=plistlib.FMT_BINARY))
    except (ImportError, OSError):
        # Fallback: write to .tags sidecar
        tag_file = path.parent / (path.name + ".tags")
        tag_file.write_text("\n".join(merged))


def _write_exiftool_keywords(path: Path, keywords: List[str]) -> None:
    """Write keywords using ExifTool for searchability."""
    import subprocess
    try:
        kw_args = [f"-keywords+={kw}" for kw in keywords]
        subprocess.run(
            ["exiftool", "-overwrite_original_in_place", "-P"] + kw_args + [str(path)],
            capture_output=True, timeout=15
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass


def _infer_para_from_category(category: str) -> Optional[str]:
    """Map common YAML Category values to PARA codes."""
    cat_lower = category.lower()
    mapping = {
        "projects": "02000",
        "project": "02000",
        "areas": "03000",
        "area": "03000",
        "business": "03000",
        "legal": "03000",
        "resources": "04000",
        "resource": "04000",
        "reference": "04000",
        "writing": "04000",
        "research": "04000",
        "archives": "05000",
        "archive": "05000",
        "completed": "05000",
        "private": "06000",
    }
    for key, code in mapping.items():
        if key in cat_lower:
            return code
    return None


@skill(stage="analyze", when="post", name="yaml_tag_extract")
def extract_yaml_tags(tx: Transaction, config: Dict[str, Any]) -> None:
    """
    Parse YAML front matter from text/Markdown files.
    Apply tags, override title, date, and PARA classification.
    """
    path = tx.original_path
    if path.suffix.lower() not in TEXT_EXTENSIONS:
        return

    try:
        content = path.read_text(errors="replace")
    except OSError:
        return

    fields = _parse_front_matter(content)
    if not fields:
        return

    tags = _parse_tags(fields.get("tags", ""))
    title = fields.get("title", "")
    category = fields.get("category", "")
    date_val = fields.get("date", "")

    # Override semantic title from YAML Title field
    if title:
        slug = re.sub(r"[^a-z0-9]+", title.lower().replace(" ", "-"), "")
        slug = re.sub(r"[^a-z0-9\-]+", "-", title.lower()).strip("-")[:60]
        tx.semantic_title = slug or tx.semantic_title

    # Override PARA from Category field
    if category:
        para = _infer_para_from_category(category)
        if para:
            tx.para = para

    # Override date from YAML Date field (format: YYYY-MM-DD)
    if date_val and re.match(r"\d{4}-\d{2}-\d{2}", date_val):
        tx.metadata["date_document_override"] = date_val

    # Write tags to extended attributes and ExifTool
    if tags:
        _write_xattrs(path, tags)
        if config.get("yaml_tag_write_exiftool", False):
            _write_exiftool_keywords(path, tags)

    tx.metadata["yaml_front_matter"] = fields
    tx.metadata["yaml_tags"] = tags

    tx.skill_outputs["yaml_tag_extract"] = {
        "title": title,
        "category": category,
        "tags": tags,
        "date": date_val,
        "para_set": tx.para,
    }
    log.info("YAML front matter extracted: title=%r tags=%r para=%s", title, tags, tx.para)
