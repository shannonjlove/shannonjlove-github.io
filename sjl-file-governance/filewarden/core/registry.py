"""
FileWarden v2 — Central Registry (SQLite)
SJL Sovereign Cloud | 07100_FILEWARDEN | 07400_MIRROR-REGISTRY

Stores DOCID → canonical path, version, hash, and mirror state.
SQLite for local authoritative state; rclone mirrors to iDrive E2.
"""

from __future__ import annotations

import json
import logging
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

log = logging.getLogger("filewarden.registry")

_SCHEMA = """
CREATE TABLE IF NOT EXISTS files (
    docid               TEXT PRIMARY KEY,
    canonical_filename  TEXT,
    canonical_path      TEXT,
    version             TEXT,
    prior_version       TEXT,
    sha256_full         TEXT,
    sha256_8            TEXT,
    para                TEXT,
    semantic_title      TEXT,
    mime_type           TEXT,
    file_size           INTEGER,
    date_ingested       TEXT,
    date_modified       TEXT,
    mirror_verified     INTEGER DEFAULT 0,
    mirror_state        TEXT DEFAULT 'pending',
    hook_id             TEXT,
    ocr_state           TEXT DEFAULT 'pending',
    vision_state        TEXT DEFAULT 'pending',
    origin_device       TEXT,
    historical_paths    TEXT  -- JSON array
);

CREATE TABLE IF NOT EXISTS events (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    docid       TEXT,
    event_type  TEXT,
    version     TEXT,
    sha256      TEXT,
    timestamp   TEXT,
    details     TEXT  -- JSON
);

CREATE INDEX IF NOT EXISTS idx_files_sha256 ON files(sha256_full);
CREATE INDEX IF NOT EXISTS idx_files_path ON files(canonical_path);
CREATE INDEX IF NOT EXISTS idx_events_docid ON events(docid);
"""


def _db_path(config: Dict[str, Any]) -> Path:
    path = Path(config.get(
        "registry_db",
        "/srv/sjl/07000_SYSTEM-AUTOMATION/07400_MIRROR-REGISTRY/filewarden.db"
    ))
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def load(config: Dict[str, Any]) -> sqlite3.Connection:
    """Open (and initialize) the registry database."""
    conn = sqlite3.connect(str(_db_path(config)), timeout=30)
    conn.row_factory = sqlite3.Row
    conn.executescript(_SCHEMA)
    conn.commit()
    return conn


def find_by_path(conn: sqlite3.Connection, path: str) -> Optional[Dict]:
    row = conn.execute(
        "SELECT * FROM files WHERE canonical_path = ?", (path,)
    ).fetchone()
    return dict(row) if row else None


def find_by_hash(conn: sqlite3.Connection, sha256: str) -> Optional[Dict]:
    row = conn.execute(
        "SELECT * FROM files WHERE sha256_full = ?", (sha256,)
    ).fetchone()
    return dict(row) if row else None


def find_by_docid(conn: sqlite3.Connection, docid: str) -> Optional[Dict]:
    row = conn.execute(
        "SELECT * FROM files WHERE docid = ?", (docid,)
    ).fetchone()
    return dict(row) if row else None


def upsert(conn: sqlite3.Connection, record: Dict[str, Any], config: Dict[str, Any]) -> None:
    """Insert or update a file record. Appends old path to historical_paths."""
    existing = find_by_docid(conn, record["docid"])
    historical = []
    if existing:
        historical = json.loads(existing.get("historical_paths") or "[]")
        old_path = existing.get("canonical_path")
        if old_path and old_path != record.get("canonical_path"):
            historical.append(old_path)

    record["historical_paths"] = json.dumps(historical)

    conn.execute("""
        INSERT INTO files (
            docid, canonical_filename, canonical_path, version, prior_version,
            sha256_full, sha256_8, para, semantic_title, mime_type, file_size,
            date_ingested, date_modified, mirror_verified, mirror_state,
            hook_id, ocr_state, vision_state, origin_device, historical_paths
        ) VALUES (
            :docid, :canonical_filename, :canonical_path, :version, :prior_version,
            :sha256_full, :sha256_8, :para, :semantic_title, :mime_type, :file_size,
            :date_ingested, :date_modified, :mirror_verified, :mirror_state,
            :hook_id, :ocr_state, :vision_state, :origin_device, :historical_paths
        )
        ON CONFLICT(docid) DO UPDATE SET
            canonical_filename = excluded.canonical_filename,
            canonical_path     = excluded.canonical_path,
            version            = excluded.version,
            prior_version      = excluded.prior_version,
            sha256_full        = excluded.sha256_full,
            sha256_8           = excluded.sha256_8,
            para               = excluded.para,
            semantic_title     = excluded.semantic_title,
            mime_type          = excluded.mime_type,
            file_size          = excluded.file_size,
            date_modified      = excluded.date_modified,
            mirror_verified    = excluded.mirror_verified,
            mirror_state       = excluded.mirror_state,
            hook_id            = excluded.hook_id,
            ocr_state          = excluded.ocr_state,
            vision_state       = excluded.vision_state,
            historical_paths   = excluded.historical_paths
    """, record)
    conn.commit()

    # Log event
    import json as _json
    from datetime import datetime, timezone
    conn.execute("""
        INSERT INTO events (docid, event_type, version, sha256, timestamp, details)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        record["docid"],
        "upsert",
        record.get("version"),
        record.get("sha256_full"),
        datetime.now(timezone.utc).isoformat(),
        _json.dumps({"canonical_path": record.get("canonical_path")}),
    ))
    conn.commit()


def audit_all(conn: sqlite3.Connection) -> List[Dict]:
    """Return all records with integrity issues."""
    issues = []
    rows = conn.execute("SELECT * FROM files").fetchall()
    for row in rows:
        r = dict(row)
        path = Path(r.get("canonical_path", ""))
        if not path.exists():
            r["_issue"] = "FILE_MISSING"
            issues.append(r)
            continue
        # Verify hash
        import hashlib
        h = hashlib.sha256()
        try:
            with open(path, "rb") as f:
                for chunk in iter(lambda: f.read(65536), b""):
                    h.update(chunk)
            if h.hexdigest() != r.get("sha256_full"):
                r["_issue"] = "HASH_MISMATCH"
                issues.append(r)
        except OSError:
            r["_issue"] = "UNREADABLE"
            issues.append(r)
    return issues
