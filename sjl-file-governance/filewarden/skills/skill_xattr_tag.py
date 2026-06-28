"""
Skill: Extended Attribute Tagging (macOS + Linux)
Origin: eclecticlight.co xattred / xattr tool research — Howard Oakley
SJL Stage: analyze (post, READ) + sidecar (post, WRITE)

Technical basis synthesised from The Eclectic Light Company articles:
  • "How to tag documents with metadata that works in search" (2019-08-19)
  • "How to store and manage metadata in macOS" (2026-05-05)
  • "APFS: Extended attributes revisited" (2024-05-13)
  • "Which extended attributes does macOS Tahoe preserve?" (2025-12-17)
  • "Which extended attributes does iCloud preserve?" (2020-03-18)
  • "Quarantine, MACL and provenance: what are they up to?" (2025-12-05)
  • xattred / Metamer / Sandstrip tool documentation

────────────────────────────────────────────────────────────────────────
XATTR KEY REFERENCE
────────────────────────────────────────────────────────────────────────

Finder Tags (binary plist NSArray of NSString):
  com.apple.metadata:_kMDItemUserTags
  • Each element is either a plain string ("Work") or a color-tagged string
    ("Red\n5") where the digit after \n is the Finder color number:
      0 = None   1 = Gray   2 = Green  3 = Purple
      4 = Blue   5 = Red    6 = Orange 7 = Yellow
  • Flags: PS (preserved on copy/save/sync/backup; stripped on share/AirDrop)
  • iCloud: preserved since ~2019; previously stripped

Spotlight-searchable Metadata (binary plist NSString or NSArray):
  com.apple.metadata:kMDItemKeywords   — array of keyword strings (PS flags)
  com.apple.metadata:kMDItemComment    — single string, Spotlight "Comments" (PS)
  com.apple.metadata:kMDItemHeadline   — single string headline (PS)
  com.apple.metadata:kMDItemDescription— single string description (PS)
  com.apple.metadata:kMDItemCreator    — single string creator (PS)
  com.apple.metadata:kMDItemCopyright  — single string (PS)
  com.apple.metadata:kMDItemWhereFroms — array of source URLs (PS)
  com.apple.metadata:kMDItemStarRating — NSNumber integer 0-5 (PS)

Security / Provenance:
  com.apple.quarantine   — "0083;TIMESTAMP;App;UUID" (PCS flags, Gatekeeper)
  com.apple.macl         — 72 bytes, two UUIDs or binary ACL data (N flag)
  com.apple.provenance   — 11-byte integer, app identifier (Ventura+)

APFS Inline vs Overflow:
  ≤ 3,804 bytes → stored inline with inode metadata (fast access)
  >  3,804 bytes → stored in separate overflow data stream (effectively unlimited)

XATTR Flag Suffixes (append to key name to override defaults):
  #S = XATTR_FLAG_SYNCABLE          — survives iCloud sync
  #C = XATTR_FLAG_CONTENT_DEPENDENT — tied to file content
  #P = XATTR_FLAG_NO_EXPORT         — stripped on share/AirDrop
  #N = XATTR_FLAG_NEVER_PRESERVE    — never copied

SJL Custom Namespace:
  co.sjl.filewarden:docid           — DOCID identity string (#S)
  co.sjl.filewarden:para            — five-digit PARA code (#S)
  co.sjl.filewarden:version         — vMAJOR-MINOR string (#S)
  co.sjl.filewarden:sha8            — 8-char SHA-256 prefix (#S)
  co.sjl.filewarden:semantic_title  — slug (#S)
  co.sjl.filewarden:governed_at     — ISO-8601 timestamp (#S)

Linux Compatibility:
  On Linux, xattrs live in the "user." namespace:
    user.com.apple.metadata:_kMDItemUserTags
  Not readable by macOS Finder but preserved by rsync/cp -a.
  SJL sidecar JSON is the canonical portable metadata carrier.
────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import logging
import plistlib
import struct
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from filewarden.core.pipeline import Transaction, skill

log = logging.getLogger("filewarden.skills.xattr_tag")

# ─── Color Map ────────────────────────────────────────────────────────────────
# Finder color number → (label_name, hex_color)
FINDER_COLORS: Dict[int, Tuple[str, str]] = {
    0: ("None",   "#ffffff"),
    1: ("Gray",   "#b2b2b2"),
    2: ("Green",  "#63e55c"),
    3: ("Purple", "#c77bff"),
    4: ("Blue",   "#6abdff"),
    5: ("Red",    "#ff6b6b"),
    6: ("Orange", "#ff9e51"),
    7: ("Yellow", "#ffe44f"),
}

# PARA five-digit code → Finder color number for visual routing
PARA_COLOR_MAP: Dict[str, int] = {
    "01000": 6,  # INBOX     → Orange  (action needed)
    "02000": 5,  # PROJECTS  → Red     (active work)
    "03000": 4,  # AREAS     → Blue    (ongoing)
    "04000": 2,  # RESOURCES → Green   (reference)
    "05000": 1,  # ARCHIVES  → Gray    (done)
    "06000": 3,  # PRIVATE   → Purple  (personal)
    "07000": 7,  # SYSTEM    → Yellow  (automation)
    "08000": 7,  # APP DATA  → Yellow  (system)
    "09000": 5,  # QUARANTINE→ Red     (error)
}

# SJL xattr namespace (syncable — append #S to survive iCloud)
_SJL_NS = "co.sjl.filewarden:"
_SJL_SYNCABLE_SUFFIX = "#S"

# ─── Low-level xattr helpers ──────────────────────────────────────────────────

def _xattr_module() -> Any:
    """Import xattr, return None if not installed."""
    try:
        import xattr as _x
        return _x
    except ImportError:
        return None


def _get_xattr(path: Path, key: str) -> Optional[bytes]:
    xmod = _xattr_module()
    if xmod:
        try:
            return xmod.getxattr(str(path), key)
        except (OSError, IOError):
            return None
    # Fallback: subprocess
    try:
        import subprocess
        r = subprocess.run(
            ["xattr", "-p", key, str(path)],
            capture_output=True, text=True
        )
        if r.returncode == 0 and r.stdout.strip():
            # xattr -p outputs hex; decode it
            hexstr = r.stdout.strip().replace(" ", "").replace("\n", "")
            return bytes.fromhex(hexstr)
    except (FileNotFoundError, ValueError):
        pass
    return None


def _set_xattr(path: Path, key: str, value: bytes) -> bool:
    xmod = _xattr_module()
    if xmod:
        try:
            xmod.setxattr(str(path), key, value)
            return True
        except (OSError, IOError) as e:
            log.warning("xattr set failed for %s on %s: %s", key, path.name, e)
            return False
    # Fallback: subprocess (macOS only — xattr -w takes hex)
    try:
        import subprocess, binascii
        hexval = binascii.hexlify(value).decode()
        r = subprocess.run(
            ["xattr", "-w", key, hexval, str(path)],
            capture_output=True
        )
        return r.returncode == 0
    except FileNotFoundError:
        return False


def _del_xattr(path: Path, key: str) -> bool:
    xmod = _xattr_module()
    if xmod:
        try:
            xmod.removexattr(str(path), key)
            return True
        except (OSError, IOError):
            return False
    try:
        import subprocess
        r = subprocess.run(
            ["xattr", "-d", key, str(path)],
            capture_output=True
        )
        return r.returncode == 0
    except FileNotFoundError:
        return False


def _list_xattrs(path: Path) -> List[str]:
    xmod = _xattr_module()
    if xmod:
        try:
            return list(xmod.listxattr(str(path)))
        except (OSError, IOError):
            return []
    try:
        import subprocess
        r = subprocess.run(
            ["xattr", "-l", str(path)],
            capture_output=True, text=True
        )
        if r.returncode == 0:
            keys = []
            for line in r.stdout.splitlines():
                if ":" in line and not line.startswith(" "):
                    keys.append(line.split(":")[0].strip())
            return keys
    except FileNotFoundError:
        pass
    return []

# ─── Plist helpers ────────────────────────────────────────────────────────────

def _read_plist_xattr(path: Path, key: str) -> Any:
    """Read an xattr whose value is a binary plist. Returns parsed Python object."""
    raw = _get_xattr(path, key)
    if not raw:
        return None
    try:
        return plistlib.loads(raw)
    except Exception:
        return None


def _write_plist_xattr(path: Path, key: str, value: Any) -> bool:
    """Encode a Python object as a binary plist and write as xattr."""
    try:
        data = plistlib.dumps(value, fmt=plistlib.FMT_BINARY)
        return _set_xattr(path, key, data)
    except Exception as e:
        log.warning("plist encode failed for %s: %s", key, e)
        return False


def _write_string_xattr(path: Path, key: str, value: str) -> bool:
    """Write a plist string xattr."""
    return _write_plist_xattr(path, key, value)


def _write_array_xattr(path: Path, key: str, values: List[str]) -> bool:
    """Write a plist array xattr."""
    return _write_plist_xattr(path, key, values)

# ─── Finder Tag Helpers ───────────────────────────────────────────────────────

def _parse_finder_tags(raw_tags: Optional[List[str]]) -> List[Dict[str, Any]]:
    """
    Parse the raw string list from _kMDItemUserTags into structured dicts.

    Format: each element is either:
      "TagName"         → plain tag, no color
      "TagName\n5"      → tag with Finder color number (0-7)
    """
    if not raw_tags:
        return []
    result = []
    for item in raw_tags:
        if "\n" in item:
            name, color_str = item.rsplit("\n", 1)
            try:
                color = int(color_str)
            except ValueError:
                color = 0
        else:
            name = item
            color = 0
        result.append({"name": name.strip(), "color": color})
    return result


def _build_finder_tag_strings(tags: List[Dict[str, Any]]) -> List[str]:
    """
    Convert structured tag dicts back to Finder tag strings.
    Tags with color=0 are stored as plain strings.
    Tags with color 1-7 are stored as "Name\nN".
    """
    result = []
    for tag in tags:
        name = tag.get("name", "").strip()
        color = int(tag.get("color", 0))
        if not name:
            continue
        if color > 0:
            result.append(f"{name}\n{color}")
        else:
            result.append(name)
    return result


def read_finder_tags(path: Path) -> List[Dict[str, Any]]:
    """Read and parse Finder tags from a file."""
    raw = _read_plist_xattr(path, "com.apple.metadata:_kMDItemUserTags")
    return _parse_finder_tags(raw if isinstance(raw, list) else None)


def write_finder_tags(path: Path, tags: List[Dict[str, Any]]) -> bool:
    """Write structured tag dicts as Finder tags."""
    strings = _build_finder_tag_strings(tags)
    return _write_array_xattr(path, "com.apple.metadata:_kMDItemUserTags", strings)


def merge_tags(existing: List[Dict], additions: List[Dict]) -> List[Dict]:
    """
    Merge addition tags into existing, avoiding duplicates by name (case-insensitive).
    If an addition matches an existing name, the addition wins (updates color).
    """
    by_name: Dict[str, Dict] = {t["name"].lower(): t for t in existing}
    for tag in additions:
        by_name[tag["name"].lower()] = tag
    return list(by_name.values())

# ─── Quarantine Helpers ───────────────────────────────────────────────────────

def read_quarantine(path: Path) -> Optional[str]:
    """Read quarantine xattr as string. Format: FLAGS;TIMESTAMP;APP;UUID"""
    raw = _get_xattr(path, "com.apple.quarantine")
    if raw:
        try:
            return raw.decode("utf-8").strip()
        except UnicodeDecodeError:
            return None
    return None


def strip_quarantine(path: Path) -> bool:
    """
    Remove quarantine xattr (makes Gatekeeper stop blocking the file).
    Equivalent to: xattr -d com.apple.quarantine <file>
    Only strips if the quarantine flag indicates it came from a sandboxed source
    (i.e. not manually added). FileWarden governs provenance separately.
    """
    return _del_xattr(path, "com.apple.quarantine")


def parse_quarantine_string(q: str) -> Dict[str, str]:
    """
    Parse quarantine string "0083;5f123456;Safari;UUID" into fields.
    Fields: flags, timestamp_hex, source_app, uuid
    """
    parts = q.split(";")
    return {
        "flags":         parts[0] if len(parts) > 0 else "",
        "timestamp_hex": parts[1] if len(parts) > 1 else "",
        "source_app":    parts[2] if len(parts) > 2 else "",
        "uuid":          parts[3] if len(parts) > 3 else "",
    }

# ─── SJL Governance Xattrs ────────────────────────────────────────────────────

def _sjl_key(name: str, syncable: bool = True) -> str:
    """Build a SJL namespace xattr key with optional #S syncable suffix."""
    suffix = _SJL_SYNCABLE_SUFFIX if syncable else ""
    return f"{_SJL_NS}{name}{suffix}"


def write_sjl_governance_xattrs(path: Path, tx: Transaction) -> Dict[str, bool]:
    """
    Write all SJL governance fields as custom xattrs.
    All use #S suffix so they survive iCloud Drive sync.
    Returns dict of key → success bool.
    """
    results: Dict[str, bool] = {}

    def _ws(name: str, val: Optional[str]) -> None:
        if val:
            results[name] = _write_string_xattr(path, _sjl_key(name), val)

    _ws("docid",          tx.docid)
    _ws("para",           tx.para)
    _ws("version",        tx.version)
    _ws("sha8",           tx.sha8)
    _ws("semantic_title", tx.semantic_title)
    results["governed_at"] = _write_string_xattr(
        path, _sjl_key("governed_at"),
        datetime.now(timezone.utc).isoformat()
    )
    return results


def read_sjl_governance_xattrs(path: Path) -> Dict[str, str]:
    """Read all SJL governance xattrs from a file."""
    out: Dict[str, str] = {}
    for name in ("docid", "para", "version", "sha8", "semantic_title", "governed_at"):
        raw = _read_plist_xattr(path, _sjl_key(name))
        if raw and isinstance(raw, str):
            out[name] = raw
    return out

# ─── Spotlight Metadata Helpers ───────────────────────────────────────────────

def write_spotlight_keywords(path: Path, keywords: List[str]) -> bool:
    """
    Write keywords to com.apple.metadata:kMDItemKeywords.
    These are indexed by Spotlight and searchable as "Keywords".
    """
    return _write_array_xattr(path, "com.apple.metadata:kMDItemKeywords", keywords)


def write_spotlight_comment(path: Path, comment: str) -> bool:
    """
    Write to com.apple.metadata:kMDItemComment.
    Searchable in Spotlight as "Comment". Max ~3,804 bytes for inline storage.
    """
    return _write_string_xattr(path, "com.apple.metadata:kMDItemComment", comment)


def read_spotlight_keywords(path: Path) -> List[str]:
    raw = _read_plist_xattr(path, "com.apple.metadata:kMDItemKeywords")
    return raw if isinstance(raw, list) else []


def read_spotlight_comment(path: Path) -> Optional[str]:
    raw = _read_plist_xattr(path, "com.apple.metadata:kMDItemComment")
    return raw if isinstance(raw, str) else None


def full_xattr_inventory(path: Path) -> Dict[str, Any]:
    """
    Enumerate ALL xattrs on a file and categorize them.
    Returns a dict of key → {raw_bytes, category, size}.
    """
    keys = _list_xattrs(path)
    result: Dict[str, Any] = {}
    for key in keys:
        raw = _get_xattr(path, key)
        if raw is None:
            continue
        # Try to parse as plist
        parsed = None
        try:
            parsed = plistlib.loads(raw)
        except Exception:
            pass

        category = "unknown"
        if key.startswith("com.apple.metadata:"):
            category = "spotlight-metadata"
        elif key.startswith("com.apple."):
            category = "apple-system"
        elif key.startswith(_SJL_NS):
            category = "sjl-governance"
        elif key.startswith("user."):
            category = "linux-user"

        result[key] = {
            "size":     len(raw),
            "category": category,
            "parsed":   parsed,
            "raw_hex":  raw.hex() if len(raw) <= 256 else f"<{len(raw)} bytes>",
        }
    return result

# ─── Pipeline Skills ──────────────────────────────────────────────────────────

@skill(stage="analyze", when="post", name="xattr_tag_read")
def read_xattr_tags(tx: Transaction, config: Dict[str, Any]) -> None:
    """
    READ pass: extract existing xattrs to inform routing decisions.
    Runs after other analyze skills; can override PARA/semantic_title.
    """
    if not config.get("xattr_tag_enabled", True):
        return

    path = tx.original_path
    if not path.is_file():
        return

    # ── Read Finder Tags ───────────────────────────────────────────────────────
    finder_tags = read_finder_tags(path)
    if finder_tags:
        tx.metadata["finder_tags"] = finder_tags
        tag_names = [t["name"] for t in finder_tags]
        log.info("Finder tags on %s: %s", path.name, tag_names)

        # Merge into skill output for downstream skills
        tx.skill_outputs["xattr_tag_read"] = {"finder_tags": finder_tags}

    # ── Read Existing SJL Governance Xattrs (re-ingestion detection) ──────────
    existing_gov = read_sjl_governance_xattrs(path)
    if existing_gov.get("docid"):
        # File was already governed — recover DOCID if not already set
        if not tx.docid:
            tx.docid = existing_gov["docid"]
            log.info("Recovered DOCID from xattr: %s", tx.docid)
        if not tx.para and existing_gov.get("para"):
            tx.para = existing_gov["para"]
        tx.metadata["existing_gov_xattrs"] = existing_gov

    # ── Read Spotlight Keywords → seed metadata ────────────────────────────────
    existing_kw = read_spotlight_keywords(path)
    if existing_kw:
        tx.metadata["existing_keywords"] = existing_kw

    # ── Quarantine Check ───────────────────────────────────────────────────────
    q = read_quarantine(path)
    if q:
        qdata = parse_quarantine_string(q)
        tx.metadata["quarantine"] = qdata
        log.debug("Quarantine on %s: source=%s", path.name, qdata.get("source_app"))

        # Auto-strip quarantine if configured (FileWarden takes custody)
        if config.get("xattr_strip_quarantine_on_govern", False):
            if strip_quarantine(path):
                log.info("Stripped quarantine xattr from %s", path.name)
                tx.skill_outputs.setdefault("xattr_tag_read", {})["quarantine_stripped"] = True


@skill(stage="sidecar", when="post", name="xattr_tag_write")
def write_xattr_tags(tx: Transaction, config: Dict[str, Any]) -> None:
    """
    WRITE pass: persist SJL governance xattrs + Finder tags + Spotlight keywords.
    Runs after the sidecar JSON is written.
    """
    if not config.get("xattr_tag_enabled", True):
        return

    # Use canonical path if rename has already occurred, else original
    path = tx.canonical_path or tx.original_path
    if not path or not path.is_file():
        return

    results: Dict[str, Any] = {}

    # ── 1. SJL Governance Custom Xattrs (#S syncable) ─────────────────────────
    gov_results = write_sjl_governance_xattrs(path, tx)
    results["sjl_governance"] = gov_results
    log.debug("Wrote SJL xattrs to %s: %s", path.name, gov_results)

    # ── 2. Finder Tags ─────────────────────────────────────────────────────────
    existing_tags = read_finder_tags(path)

    sjl_tags: List[Dict[str, Any]] = []

    # PARA code → color tag
    if tx.para:
        color_num = PARA_COLOR_MAP.get(tx.para[:5], 0)
        color_name = FINDER_COLORS.get(color_num, ("None", ""))[0]
        para_label = config.get("para_tag_labels", {}).get(
            tx.para[:5], tx.para[:5]
        )
        sjl_tags.append({"name": f"SJL-{para_label}", "color": color_num})
        if color_num and config.get("xattr_write_color_tag", True):
            sjl_tags.append({"name": color_name, "color": color_num})

    # DOCID as a plain tag (no color)
    if tx.docid and config.get("xattr_tag_docid", True):
        sjl_tags.append({"name": tx.docid, "color": 0})

    # User-configured extra tags
    extra_tags = config.get("xattr_extra_tags", [])
    for t in extra_tags:
        if isinstance(t, str):
            sjl_tags.append({"name": t, "color": 0})
        elif isinstance(t, dict):
            sjl_tags.append(t)

    # Merge: existing user tags preserved; SJL governance tags upserted
    merged = merge_tags(existing_tags, sjl_tags)

    if write_finder_tags(path, merged):
        results["finder_tags_written"] = [t["name"] for t in merged]
        log.info("Finder tags written to %s: %s", path.name,
                 results["finder_tags_written"])

    # ── 3. Spotlight Keywords (kMDItemKeywords) ────────────────────────────────
    kw_base: List[str] = list(tx.metadata.get("existing_keywords", []))
    kw_additions: List[str] = []

    if tx.para:
        kw_additions.append(tx.para[:5])
    if tx.docid:
        kw_additions.append(tx.docid)
    if tx.semantic_title:
        kw_additions.append(tx.semantic_title)
    if tx.version:
        kw_additions.append(f"v{tx.version}")

    # YAML-extracted tags from earlier in pipeline
    yaml_tags: List[str] = tx.metadata.get("yaml_tags", [])
    kw_additions.extend(yaml_tags)

    # Deduplicate while preserving order
    seen: set[str] = set()
    all_kw: List[str] = []
    for kw in kw_base + kw_additions:
        kw_lower = kw.lower()
        if kw_lower not in seen:
            seen.add(kw_lower)
            all_kw.append(kw)

    if all_kw and write_spotlight_keywords(path, all_kw):
        results["spotlight_keywords"] = all_kw

    # ── 4. Spotlight Comment (kMDItemComment) ─────────────────────────────────
    if config.get("xattr_write_spotlight_comment", True) and tx.docid:
        comment = (
            f"DOCID:{tx.docid} | PARA:{tx.para or '?'} | "
            f"v{tx.version or '?'} | {tx.sha8 or '?'}"
        )
        if write_spotlight_comment(path, comment):
            results["spotlight_comment"] = comment

    tx.skill_outputs["xattr_tag_write"] = results


# ─── Utility: Inventory All Xattrs (for diagnostics / sidecar enrichment) ────

@skill(stage="analyze", when="pre", name="xattr_inventory")
def inventory_xattrs(tx: Transaction, config: Dict[str, Any]) -> None:
    """
    Optional diagnostic: enumerate all xattrs at the start of analyze.
    Disabled by default (xattr_inventory_enabled: false).
    Useful for debugging unknown files or during re-ingestion.
    """
    if not config.get("xattr_inventory_enabled", False):
        return

    path = tx.original_path
    if not path.is_file():
        return

    inventory = full_xattr_inventory(path)
    if inventory:
        tx.metadata["xattr_inventory"] = inventory
        log.info(
            "xattr inventory for %s: %d attributes (%s)",
            path.name, len(inventory),
            ", ".join(inventory.keys())
        )
        tx.skill_outputs["xattr_inventory"] = {
            "count": len(inventory),
            "keys":  list(inventory.keys()),
        }
