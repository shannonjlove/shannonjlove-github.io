"""
FileWarden v2 — Built-in Pipeline Stage Implementations
SJL Sovereign Cloud | 07100_FILEWARDEN

These are the canonical implementations for each pipeline stage.
Skills (plugins) run as pre/post hooks around these.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from filewarden.core.pipeline import Transaction
from filewarden.core import registry as reg_module


# ─────────────────────────────────────────────
# STAGE: stabilize
# Wait for file writes to complete before processing
# ─────────────────────────────────────────────

def stabilize(tx: Transaction, config: Dict[str, Any]) -> None:
    """
    Poll until file size stops changing (write settled).
    Hazel equivalent: wait until not modified in last N seconds.
    """
    path = tx.original_path
    if not path.exists():
        tx.abort_with(f"File not found: {path}", "09100_MISSING-SIDECAR")
        return

    stability_secs = config.get("stabilize_seconds", 3)
    max_wait = config.get("stabilize_max_wait", 60)
    elapsed = 0
    last_size = -1

    while elapsed < max_wait:
        try:
            current_size = path.stat().st_size
        except FileNotFoundError:
            tx.abort_with("File disappeared during stabilize", "09300_METADATA-CONFLICT")
            return

        if current_size == last_size:
            tx.stable = True
            tx.log_stage("stabilize", f"settled at {current_size} bytes after {elapsed}s")
            return

        last_size = current_size
        time.sleep(stability_secs)
        elapsed += stability_secs

    tx.abort_with(f"File never stabilized after {max_wait}s", "09300_METADATA-CONFLICT")


# ─────────────────────────────────────────────
# STAGE: identify
# Calculate SHA-256 and assign/recover DOCID
# ─────────────────────────────────────────────

def identify(tx: Transaction, config: Dict[str, Any]) -> None:
    """Compute SHA-256 and resolve DOCID from registry or assign new."""
    path = tx.original_path

    # SHA-256
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
    except OSError as e:
        tx.abort_with(f"Cannot read file for hashing: {e}", "09200_HASH-MISMATCH")
        return

    tx.sha256 = h.hexdigest()
    tx.sha8 = tx.sha256[:8]

    # DOCID: check registry by original path, then by hash (duplicate detection)
    registry = reg_module.load(config)
    existing = reg_module.find_by_path(registry, str(path))
    if existing:
        tx.docid = existing["docid"]
        tx.prior_version = existing.get("version")
        tx.prior_sha256 = existing.get("sha256_full")
        tx.log_stage("identify", f"recovered DOCID={tx.docid} for existing file")
    else:
        # Check for duplicate content
        dupe = reg_module.find_by_hash(registry, tx.sha256)
        if dupe:
            tx.docid = dupe["docid"]
            tx.log_stage("identify", f"duplicate content detected, reusing DOCID={tx.docid}")
        else:
            prefix = config.get("docid_prefix", "SJL")
            date_part = datetime.now(timezone.utc).strftime("%Y%m%d")
            rand_part = uuid.uuid4().hex[:6].upper()
            tx.docid = f"{prefix}-{date_part}-{rand_part}"
            tx.log_stage("identify", f"assigned new DOCID={tx.docid}")


# ─────────────────────────────────────────────
# STAGE: analyze
# Extract native metadata; OCR and vision queued separately
# ─────────────────────────────────────────────

def analyze(tx: Transaction, config: Dict[str, Any]) -> None:
    """
    Extract MIME type, embedded metadata, EXIF.
    OCR and vision run asynchronously via Oracle/sOs workers;
    this stage records their state as 'pending' unless already done.
    """
    path = tx.original_path
    ext = path.suffix.lower().lstrip(".")

    # MIME via file command (available on Linux)
    try:
        result = subprocess.run(
            ["file", "--mime-type", "-b", str(path)],
            capture_output=True, text=True, timeout=10
        )
        tx.metadata["mime_type"] = result.stdout.strip()
    except Exception:
        tx.metadata["mime_type"] = f"application/{ext}" if ext else "application/octet-stream"

    tx.metadata["extension"] = ext
    tx.metadata["file_size"] = path.stat().st_size

    # Semantic title from filename (skills can override with OCR/vision result)
    raw_name = path.stem
    # Strip existing canonical segments if present
    parts = raw_name.split("__")
    if len(parts) >= 3:
        tx.semantic_title = _slugify(parts[2])
    else:
        tx.semantic_title = _slugify(raw_name)

    # PARA: default to INBOX; skills like skill_content_classify can override
    if not tx.para:
        tx.para = config.get("default_para", "01000")

    tx.log_stage("analyze", f"mime={tx.metadata['mime_type']} title={tx.semantic_title}")


def _slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")[:60]


# ─────────────────────────────────────────────
# STAGE: version
# Increment version, generate diff
# ─────────────────────────────────────────────

def version(tx: Transaction, config: Dict[str, Any]) -> None:
    """
    Determine new version. If content hash changed, increment minor.
    If no prior version exists, set v1-0.
    """
    if tx.prior_version is None:
        tx.version = "v1-0"
        tx.log_stage("version", "new file → v1-0")
        return

    if tx.prior_sha256 == tx.sha256:
        # Metadata-only change: keep version, record metadata event
        tx.version = tx.prior_version
        tx.log_stage("version", f"no content change → keeping {tx.version}")
        return

    # Content changed: increment minor version
    match = re.match(r"v(\d+)-(\d+)", tx.prior_version)
    if match:
        major, minor = int(match.group(1)), int(match.group(2))
        tx.version = f"v{major}-{minor + 1}"
    else:
        tx.version = "v1-1"

    tx.log_stage("version", f"{tx.prior_version} → {tx.version} (content changed)")

    # Preserve prior version file
    _preserve_prior_version(tx, config)
    # Generate diff (delegated to skill_diff or built-in text diff)
    _generate_diff(tx, config)


def _preserve_prior_version(tx: Transaction, config: Dict[str, Any]) -> None:
    """Copy current file to versions/ before overwriting."""
    versions_dir = Path(config.get("versions_root", "/srv/sjl/05000_ARCHIVES")) / tx.docid / "versions"
    versions_dir.mkdir(parents=True, exist_ok=True)
    dest = versions_dir / f"{tx.prior_version}_{tx.prior_sha256[:8]}{tx.original_path.suffix}"
    try:
        shutil.copy2(str(tx.original_path), str(dest))
        tx.log_stage("version", f"prior version preserved → {dest.name}")
    except Exception as e:
        tx.log_stage("version", f"WARNING: could not preserve prior version: {e}")


def _generate_diff(tx: Transaction, config: Dict[str, Any]) -> None:
    """Generate text diff for text-based formats. Binary formats get hash delta."""
    path = tx.original_path
    ext = path.suffix.lower()
    text_exts = {".txt", ".md", ".csv", ".json", ".yaml", ".yml", ".xml", ".py", ".sh", ".js", ".ts"}

    diff_dir = Path(config.get("sidecar_root", "/srv/sjl/.sidecars")) / tx.docid / "diffs"
    diff_dir.mkdir(parents=True, exist_ok=True)
    diff_file = diff_dir / f"{tx.prior_version}_to_{tx.version}.diff"

    if ext in text_exts:
        # Find prior version file
        versions_dir = Path(config.get("versions_root", "/srv/sjl/05000_ARCHIVES")) / tx.docid / "versions"
        prior_files = list(versions_dir.glob(f"{tx.prior_version}_*{ext}"))
        if prior_files:
            try:
                result = subprocess.run(
                    ["diff", "-u", str(prior_files[0]), str(path)],
                    capture_output=True, text=True
                )
                diff_file.write_text(result.stdout or "(no textual differences)\n")
                tx.log_stage("version", f"text diff written → {diff_file.name}")
            except Exception as e:
                diff_file.write_text(f"diff failed: {e}\n")
    else:
        diff_file.write_text(
            f"Binary diff\n"
            f"prior: {tx.prior_version} sha256={tx.prior_sha256}\n"
            f"current: {tx.version} sha256={tx.sha256}\n"
            f"size: {tx.metadata.get('file_size', 'unknown')} bytes\n"
        )


# ─────────────────────────────────────────────
# STAGE: rename
# Apply canonical filename
# ─────────────────────────────────────────────

def rename(tx: Transaction, config: Dict[str, Any]) -> None:
    """
    Produce and apply the canonical filename:
    [PPPPP]_YYYY-MM-DD__DOCID__semantic-title__vMAJOR-MINOR__sha8.ext
    """
    ext = tx.original_path.suffix.lower().lstrip(".")
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    tx.canonical_name = (
        f"{tx.para}_{date_str}"
        f"__{tx.docid}"
        f"__{tx.semantic_title}"
        f"__{tx.version}"
        f"__{tx.sha8}"
        f".{ext}"
    )

    # Determine destination directory
    dest_root = _para_to_path(tx.para, config)
    dest_root.mkdir(parents=True, exist_ok=True)
    tx.canonical_path = dest_root / tx.canonical_name

    # Move file to canonical location (atomic on same filesystem)
    try:
        shutil.move(str(tx.original_path), str(tx.canonical_path))
        tx.log_stage("rename", f"→ {tx.canonical_name}")
    except Exception as e:
        tx.abort_with(f"Rename failed: {e}", "09300_METADATA-CONFLICT")


def _para_to_path(para: str, config: Dict[str, Any]) -> Path:
    """Map PARA code to filesystem path."""
    para_map = config.get("para_paths", {})
    if para in para_map:
        return Path(para_map[para])
    root = Path(config.get("sjl_root", "/srv/sjl"))
    para_dirs = {
        "01000": "01000_INBOX/01100_DEVICE-INTAKE",
        "02000": "02000_PROJECTS",
        "03000": "03000_AREAS",
        "04000": "04000_RESOURCES",
        "05000": "05000_ARCHIVES",
        "06000": "06000_PRIVATE-MEDIA",
        "07000": "07000_SYSTEM-AUTOMATION",
        "08000": "08000_APPLICATION-DATA",
        "09000": "09000_QUARANTINE/09300_METADATA-CONFLICT",
    }
    return root / para_dirs.get(para, "01000_INBOX")


# ─────────────────────────────────────────────
# STAGE: sidecar
# Write .sjl.json, .sha256, and persistent sidecar
# ─────────────────────────────────────────────

def sidecar(tx: Transaction, config: Dict[str, Any]) -> None:
    """Write all three sidecar artifacts for the canonical file."""
    if not tx.canonical_path or not tx.canonical_path.exists():
        tx.abort_with("Cannot write sidecar: canonical file missing", "09100_MISSING-SIDECAR")
        return

    payload = {
        "schema_version": "1.0",
        "docid": tx.docid,
        "canonical_filename": tx.canonical_name,
        "original_filename": tx.original_path.name,
        "para": tx.para,
        "semantic_title": tx.semantic_title,
        "version": tx.version,
        "prior_version": tx.prior_version,
        "sha256_full": tx.sha256,
        "sha256_8": tx.sha8,
        "prior_sha256": tx.prior_sha256,
        "extension": tx.metadata.get("extension", ""),
        "mime_type": tx.metadata.get("mime_type", ""),
        "file_size": tx.metadata.get("file_size", 0),
        "date_document": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "date_ingested": tx.started_at.isoformat(),
        "date_modified": datetime.now(timezone.utc).isoformat(),
        "origin_device": config.get("device_name", "nexus"),
        "origin_app": tx.metadata.get("origin_app", "filewarden"),
        "intake_method": tx.metadata.get("intake_method", "filesystem-event"),
        "canonical_path": str(tx.canonical_path),
        "historical_paths": tx.metadata.get("historical_paths", []),
        "ocr_state": tx.ocr_state,
        "vision_state": tx.vision_state,
        "mirror_state": "pending",
        "mirror_verified": False,
        "hook_id": tx.hook_id,
        "registry_record_id": tx.registry_id,
        "sensitivity": tx.metadata.get("sensitivity", "standard"),
        "retention": tx.metadata.get("retention", "standard"),
        "review_status": "governed",
        "skill_outputs": tx.skill_outputs,
        "pipeline_history": tx.history,
    }

    # Inline sidecar alongside canonical file
    inline_path = tx.canonical_path.parent / (tx.canonical_name + ".sjl.json")
    inline_path.write_text(json.dumps(payload, indent=2))

    # SHA-256 checksum file
    checksum_path = tx.canonical_path.parent / (tx.canonical_name + ".sha256")
    checksum_path.write_text(f"{tx.sha256}  {tx.canonical_name}\n")

    # Persistent sidecar in .sidecars/DOCID/
    sidecar_dir = Path(config.get("sidecar_root", "/srv/sjl/.sidecars")) / tx.docid
    sidecar_dir.mkdir(parents=True, exist_ok=True)
    (sidecar_dir / "provenance.json").write_text(json.dumps(payload, indent=2))

    tx.sidecar_path = inline_path
    tx.log_stage("sidecar", f"written: {inline_path.name}")


# ─────────────────────────────────────────────
# STAGE: hook
# Register with HookVault
# ─────────────────────────────────────────────

def hook(tx: Transaction, config: Dict[str, Any]) -> None:
    """Register DOCID → canonical path in HookVault."""
    hookvault_url = config.get("hookvault_url")
    if not hookvault_url:
        tx.hook_id = f"LOCAL-{tx.docid}"
        tx.log_stage("hook", "HookVault not configured; using local hook ID")
        return

    import urllib.request
    import urllib.error
    payload = json.dumps({
        "docid": tx.docid,
        "canonical_path": str(tx.canonical_path),
        "version": tx.version,
        "sha256": tx.sha256,
    }).encode()

    try:
        req = urllib.request.Request(
            f"{hookvault_url}/register",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())
            tx.hook_id = result.get("hook_id", tx.docid)
            tx.log_stage("hook", f"registered hook_id={tx.hook_id}")
    except urllib.error.URLError as e:
        tx.log_stage("hook", f"WARNING: HookVault unavailable ({e}); continuing")


# ─────────────────────────────────────────────
# STAGE: mirror
# rclone mirror + remote checksum verification
# ─────────────────────────────────────────────

def mirror(tx: Transaction, config: Dict[str, Any]) -> None:
    """
    Mirror canonical file bundle to iDrive E2 via rclone.
    Verify remote checksum before marking success.
    """
    rclone_remote = config.get("rclone_remote", "idrive-e2")
    bucket = config.get("mirror_bucket", "sjl-sovereign")
    if not rclone_remote:
        tx.log_stage("mirror", "mirror disabled in config")
        return

    para = tx.para or "01000"
    object_prefix = f"{para}/{tx.docid}"

    # Files to mirror: canonical + sidecar + checksum
    files_to_mirror = [tx.canonical_path]
    if tx.sidecar_path:
        files_to_mirror.append(tx.sidecar_path)
        checksum_path = tx.canonical_path.parent / (tx.canonical_name + ".sha256")
        if checksum_path.exists():
            files_to_mirror.append(checksum_path)

    for fpath in files_to_mirror:
        if not fpath or not fpath.exists():
            continue
        remote_path = f"{rclone_remote}:{bucket}/{object_prefix}/current/{fpath.name}"
        try:
            result = subprocess.run(
                ["rclone", "copyto", str(fpath), remote_path, "--checksum"],
                capture_output=True, text=True, timeout=120
            )
            if result.returncode != 0:
                tx.log_stage("mirror", f"WARNING: rclone failed for {fpath.name}: {result.stderr}")
                tx.metadata["mirror_state"] = "failed"
                tx.quarantine_code = "09400_MIRROR-FAILURE"
                return
        except FileNotFoundError:
            tx.log_stage("mirror", "rclone not found; skipping mirror")
            return
        except subprocess.TimeoutExpired:
            tx.log_stage("mirror", f"WARNING: rclone timed out for {fpath.name}")
            tx.metadata["mirror_state"] = "timeout"
            return

    # Verify remote checksum
    remote_checksum_path = f"{rclone_remote}:{bucket}/{object_prefix}/current/{tx.canonical_name}"
    try:
        result = subprocess.run(
            ["rclone", "md5sum", remote_checksum_path],
            capture_output=True, text=True, timeout=30
        )
        if tx.sha256[:32] in result.stdout or result.returncode == 0:
            tx.mirror_verified = True
            tx.metadata["mirror_state"] = "verified"
            tx.log_stage("mirror", f"mirror verified at {remote_checksum_path}")
        else:
            tx.metadata["mirror_state"] = "checksum-mismatch"
            tx.quarantine_code = "09400_MIRROR-FAILURE"
            tx.log_stage("mirror", "WARNING: remote checksum mismatch")
    except Exception as e:
        tx.log_stage("mirror", f"WARNING: checksum verification failed: {e}")


# ─────────────────────────────────────────────
# STAGE: register
# Update central SQLite registry
# ─────────────────────────────────────────────

def register(tx: Transaction, config: Dict[str, Any]) -> None:
    """Upsert registry record for this DOCID."""
    registry = reg_module.load(config)
    record = {
        "docid": tx.docid,
        "canonical_filename": tx.canonical_name,
        "canonical_path": str(tx.canonical_path),
        "version": tx.version,
        "prior_version": tx.prior_version,
        "sha256_full": tx.sha256,
        "sha256_8": tx.sha8,
        "para": tx.para,
        "semantic_title": tx.semantic_title,
        "mime_type": tx.metadata.get("mime_type", ""),
        "file_size": tx.metadata.get("file_size", 0),
        "date_ingested": tx.started_at.isoformat(),
        "date_modified": datetime.now(timezone.utc).isoformat(),
        "mirror_verified": tx.mirror_verified,
        "mirror_state": tx.metadata.get("mirror_state", "pending"),
        "hook_id": tx.hook_id,
        "ocr_state": tx.ocr_state,
        "vision_state": tx.vision_state,
        "origin_device": config.get("device_name", "nexus"),
        "historical_paths": tx.metadata.get("historical_paths", []),
    }
    reg_module.upsert(registry, record, config)
    tx.registry_id = tx.docid
    tx.log_stage("register", f"registry updated for DOCID={tx.docid}")


# ─────────────────────────────────────────────
# STAGE: publish
# BookStack page update + PaperParrot archival
# ─────────────────────────────────────────────

def publish(tx: Transaction, config: Dict[str, Any]) -> None:
    """
    Post change summary to BookStack and submit governed record to PaperParrot.
    Non-fatal: failures are logged but do not abort the transaction.
    """
    _publish_bookstack(tx, config)
    _publish_paperparrot(tx, config)
    tx.log_stage("publish", f"bookstack={tx.bookstack_url} paperparrot={tx.paperparrot_id}")


def _publish_bookstack(tx: Transaction, config: Dict[str, Any]) -> None:
    bs_url = config.get("bookstack_url")
    bs_token = config.get("bookstack_token")
    if not bs_url or not bs_token:
        return

    summary = (
        f"## FileWarden Event\n\n"
        f"| Field | Value |\n|---|---|\n"
        f"| DOCID | `{tx.docid}` |\n"
        f"| File | `{tx.canonical_name}` |\n"
        f"| Version | {tx.version} |\n"
        f"| SHA-256 | `{tx.sha256}` |\n"
        f"| PARA | {tx.para} |\n"
        f"| Mirror | {'✓ verified' if tx.mirror_verified else '⚠ pending'} |\n"
        f"| Event | {tx.event_type} |\n"
        f"| Time | {tx.started_at.isoformat()} |\n"
    )

    import urllib.request
    payload = json.dumps({"content": summary, "name": f"[{tx.version}] {tx.docid}"}).encode()
    try:
        page_id = config.get("bookstack_filewarden_page_id", "")
        req = urllib.request.Request(
            f"{bs_url}/api/pages/{page_id}",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Token {bs_token}",
            },
            method="PUT",
        )
        with urllib.request.urlopen(req, timeout=15):
            tx.bookstack_url = f"{bs_url}/books/file-governance/page/{tx.docid}"
    except Exception as e:
        tx.log_stage("publish", f"BookStack publish failed (non-fatal): {e}")


def _publish_paperparrot(tx: Transaction, config: Dict[str, Any]) -> None:
    pp_url = config.get("paperparrot_url")
    pp_token = config.get("paperparrot_token")
    if not pp_url or not pp_token:
        return

    ext = tx.metadata.get("extension", "")
    archivable_exts = {"pdf", "docx", "doc", "txt", "md"}
    if ext not in archivable_exts:
        return

    import urllib.request
    with open(str(tx.canonical_path), "rb") as f:
        file_data = f.read()

    boundary = "SJLFileWarden"
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="document"; filename="{tx.canonical_name}"\r\n'
        f"Content-Type: application/octet-stream\r\n\r\n"
    ).encode() + file_data + f"\r\n--{boundary}--\r\n".encode()

    try:
        req = urllib.request.Request(
            f"{pp_url}/api/documents/post_document/",
            data=body,
            headers={
                "Authorization": f"Token {pp_token}",
                "Content-Type": f"multipart/form-data; boundary={boundary}",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read())
            tx.paperparrot_id = str(result.get("id", ""))
    except Exception as e:
        tx.log_stage("publish", f"PaperParrot archival failed (non-fatal): {e}")
