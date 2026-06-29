# SJL Sovereign Cloud v7.4
## Persistent Metadata Doctrine — Universal File Governance and Implementation Manual

**Document class:** Canonical architecture and operating manual  
**Owner:** Shannon J. Love  
**Version:** v7.4  
**Date:** 2026-06-29  
**Status:** Implementation baseline — FileWarden v2 skill library complete  
**Security:** No credentials, tokens, passwords, or private keys  
**DOCID:** SJL-CLOUD-FILE-GOVERNANCE  

> **Controlling principle:** No file becomes canonical until it has been identified, analyzed, named, versioned, sidecar-linked, mirrored, registered, and logged.

---

## Change Log

| Version | Date       | Summary |
|---------|------------|---------|
| v7.3    | 2026-06-19 | Target architecture — implementation baseline |
| v7.4    | 2026-06-29 | FileWarden v2 skill library complete (20 skills); iOS Scriptable app; xattr tagging system; sidecar bundle schema expanded; CLAUDE.md expanded; n8n intake documented |

---

## Contents

1. Executive Architecture Decision
2. Universal File Governance Doctrine
3. Canonical Five-Digit PARA Structure
4. Canonical Naming Convention
5. Permanent Identity and Automatic Versioning
6. Persistent Metadata Architecture
7. OCR, Vision, and Semantic Renaming
8. FileWarden v2 Operating Pipeline
9. Hook Scripts and Persistent Linking
10. Diff Scripts and Change Intelligence
11. Mirror, Sidecar, and Cloud Persistence
12. Device and Application Intake
13. BookStack and PaperParrot Publishing
14. Claude Code Implementation Strategy
15. Security, Exclusions, and Failure Handling
16. Integrity Audits and Acceptance Criteria
17. Implementation Sequence
18. Current shannonjlove.cloud Snapshot
19. Canonical Server and Service Hierarchy
20. Filesystem and PARA Tree Map
21. Domain and Route Map
22. Snapshot Verification and Discovery Requirements
23. Claude Code Operating Architecture
24. FileWarden Skill Library
25. Sidecar Bundle Schema
26. iOS Device Intake — Scriptable App
27. Extended Attribute Tagging System

---

## 1. Executive Architecture Decision

SJL Sovereign Cloud v7.4 establishes a mandatory file-governance layer beneath every approved application, device, sync path, and storage destination. The system is centered on **Nexus** (Hostinger x86_64) as the authoritative control and persistence node, with **Oracle/sOs** (ARM64, private Tailscale worker) providing replaceable private compute for OCR, vision, indexing, and batch processing.

**Controlling principle:** No file becomes canonical until it has been identified, analyzed, named, versioned, sidecar-linked, mirrored, registered, and logged.

- FileWarden v2 (Python, watchdog, skill plugin architecture) replaces Hazel as the universal policy-enforcement daemon.
- SJL hook scripts and HookVault replace Hookmark. Hook identity is DOCID-based, never path-based.
- SJL diff scripts and the optional DiffForge viewer replace DeltaWalker. Format-aware diffs are automatic.
- Every byte-level content change creates an immutable new version with a new SHA-256.
- Every canonical file receives persistent metadata in six synchronized layers.
- Every canonical file bundle is mirrored to iDrive E2 object storage and checksum-verified.
- BookStack stores manuals, service state, and summarized change records.
- PaperParrot/Paperless stores archived records and governed document copies.
- iOS files enter governance via the Scriptable Share Sheet app or PaperParrot intake.
- Every xattr-capable filesystem receives governance tags in the macOS-compatible binary plist format.

---

## 2. Universal File Governance Doctrine

1. Detect every governed file creation, upload, synchronization event, move, rename, or content save.
2. Wait until the write is stable before processing (size polling + lock-file detection).
3. Calculate a full SHA-256 digest.
4. Extract native text and embedded metadata (EXIF, PDF metadata, YAML front matter, DOCX properties).
5. Run OCR (OCRmyPDF/Tesseract) and image/media recognition when applicable.
6. Assign or recover a permanent DOCID.
7. Determine the five-digit PARA destination.
8. Compare the new content digest with the current registry version.
9. Preserve the prior version and generate a format-specific diff when content changed.
10. Rename the file canonically.
11. Write embedded metadata, extended attributes, and sidecar JSON bundle.
12. Update the central SQLite registry and persistent HookVault record.
13. Mirror the complete bundle to iDrive E2 cloud storage.
14. Verify the remote checksum (rclone md5sum).
15. Publish the change summary to BookStack and archive the governed record to PaperParrot.

**Authority rule:** A file may exist temporarily outside the canonical environment, but it is not authoritative until it passes through Nexus governance.

---

## 3. Canonical Five-Digit PARA Structure

All governed directories and hierarchies use five digits. Four-digit legacy paths may remain only as temporary compatibility aliases during migration.

| Code  | Category          | Primary Purpose                                                  | Finder Color |
|-------|-------------------|------------------------------------------------------------------|--------------|
| 01000 | INBOX             | Controlled intake, staging, and review                           | Orange       |
| 02000 | PROJECTS          | Active finite projects and deliverables                          | Red          |
| 03000 | AREAS             | Ongoing responsibilities and operations                          | Blue         |
| 04000 | RESOURCES         | Reference material and reusable assets                           | Green        |
| 05000 | ARCHIVES          | Inactive, completed, and retained records                        | Gray         |
| 06000 | PRIVATE MEDIA     | Restricted media and sensitive assets                            | Purple       |
| 07000 | SYSTEM AUTOMATION | Scripts, agents, Quadlets, manifests, and manuals                | Yellow       |
| 08000 | APPLICATION DATA  | Governed application exports and controlled state                | Yellow       |
| 09000 | QUARANTINE        | Failures, conflicts, unsupported files, and review-required items| Red          |

---

## 4. Canonical Naming Convention

```
[PPPPP]_YYYY-MM-DD__DOCID__semantic-title__vMAJOR-MINOR__sha8.ext
```

**Example:**
```
02000_2026-06-19__SJL-CLOUD-0017__persistent-metadata-manual__v7-2__843dc901.pdf
```

| Field         | Rule                                                                 |
|---------------|----------------------------------------------------------------------|
| PPPPP         | Five-digit PARA classification code                                  |
| YYYY-MM-DD    | Authoritative creation or document date (from embedded metadata, OCR, or filesystem) |
| DOCID         | Permanent identity that never changes across renames or moves        |
| semantic-title| Lowercase hyphenated slug from OCR, vision, metadata, or user input  |
| vMAJOR-MINOR  | Automatic immutable content version (hyphen separator, not dot)      |
| sha8          | First eight hex characters of the full SHA-256 digest                |
| ext           | Lowercase normalized extension                                       |

**Naming rules:**
- Separator between name segments: double underscore `__`
- Word separator within semantic title: single hyphen `-`
- No spaces, no special characters except hyphens and underscores
- Extension always lowercase
- sha8 changes whenever content changes; unchanged on metadata-only edits
- Version always matches sha8 at the moment of that version's creation

---

## 5. Permanent Identity and Automatic Versioning

Path and filename are mutable properties. **DOCID is the durable identity.**

- A new file receives a DOCID exactly once. It never changes.
- Moves and renames update the path record in the registry without changing DOCID.
- Any byte-level content change creates a new immutable version, new SHA-256, new sha8.
- Metadata-only changes create metadata events without incrementing the content version.
- The prior canonical version is always preserved before replacement.
- The version chain must remain complete and recoverable.

| Version | Meaning                                        |
|---------|------------------------------------------------|
| v1-0    | Initial ingestion                              |
| v1-1    | First content modification                     |
| v1-2    | Second content modification                    |
| v2-0    | Intentional major revision or transformation   |

**DOCID format (server-generated):**
```
SJL-CLOUD-NNNN     (sequential, four-digit, e.g. SJL-CLOUD-0017)
```

**DOCID format (iOS Scriptable-generated):**
```
SJL-DEVICE-YYYYMMDD-HHMMSS-XXXX  (timestamp + 4-digit random suffix)
```

On first server-side governance of a device-generated file, the device DOCID is preserved and cross-referenced in the registry. The server does not reassign DOCIDs.

---

## 6. Persistent Metadata Architecture

A governed file must remain reconstructable even if it is renamed, moved to another filesystem, downloaded from cloud storage, stripped of extended attributes, or restored after complete server loss.

| Layer                              | Purpose                                              | Persistence Rule    |
|------------------------------------|------------------------------------------------------|---------------------|
| Canonical filename                 | Human-readable minimum recovery data                 | Always present      |
| Embedded metadata                  | Portable metadata inside supported formats           | Write when safe     |
| Extended attributes (xattrs)       | Fast local lookup, filesystem indexing, Finder tags  | Reconstructable     |
| Sidecar JSON bundle                | Complete portable file-level metadata record         | Mandatory           |
| Central SQLite registry            | Current state, paths, versions, links, provenance    | Authoritative index |
| Cloud object metadata + manifests  | Off-device recovery and integrity verification       | Mandatory for mirrors|

### Mandatory Base Metadata Fields

- DOCID, canonical filename, and original filename
- PARA code and hierarchy
- Semantic title and title-confidence source (`ocr`, `vision`, `embedded`, `filename`, `user`)
- Current version and prior version
- Full SHA-256 and sidecar digest
- MIME type and format
- Creation, document, ingestion, and modification timestamps
- Originating device, application, and intake method
- Current canonical path and historical paths
- OCR state and confidence (`pending`, `not-applicable`, `complete`, `failed`)
- Vision state and confidence
- Sensitivity classification and retention status
- Mirror target, object key, and remote checksum verification state
- Hook ID and registry record ID
- BookStack page URL and PaperParrot document ID

### Canonical File Bundle

```
file.ext
file.ext.sjl.json           ← inline sidecar (always co-located)
file.ext.sha256             ← plain-text full SHA-256 checksum
.sidecars/
  DOCID/
    provenance.json         ← full governance record, immutable per version
    ocr.txt                 ← extracted OCR text (plain UTF-8)
    vision.json             ← vision analysis (objects, scene, text, perceptual hash)
    links.json              ← HookVault link graph (inbound + outbound DOCIDs)
    mirror-manifest.json    ← rclone object key, ETag, remote checksum, verify timestamp
    diffs/
      v1-0_v1-1.diff        ← unified diff or binary delta for each version transition
      v1-1_v1-2.diff
```

---

## 7. OCR, Vision, and Semantic Renaming

Semantic naming occurs only after text and image intelligence have been collected.

1. Use native text extraction before OCR (pdftotext, python-docx, ExifTool).
2. Use OCRmyPDF/Tesseract for scanned PDFs and images when native text is absent.
3. Use ExifTool and format-native parsers for embedded metadata (EXIF GPS, IPTC, XMP, PDF properties, DOCX custom properties).
4. Use image recognition (YOLO/CLIP/Whisper) for objects, scenes, visible text, and duplicate detection.
5. Preserve original camera and source metadata. Never overwrite; append derived fields.
6. Record confidence score, source method, review state, and field locks for AI-derived metadata.
7. Route low-confidence (`< 0.7`) or conflicting results to `01900_REVIEW-REQUIRED` or `09300_METADATA-CONFLICT`.

**Precedence order (highest to lowest):**

> Reviewed user metadata → Verified canonical metadata → Embedded source metadata → Application metadata → OCR → Vision inference → Filename inference → Filesystem timestamps

---

## 8. FileWarden v2 Operating Pipeline

FileWarden is the universal transaction coordinator for all approved SJL roots. It runs as a systemd Quadlet under the `sjl` service user using rootless Podman. The watchdog inotify observer feeds events into a staged transaction pipeline.

```
discover → stabilize → identify → analyze → version → diff
         → rename → sidecar → hook → mirror → register → publish
```

### Pipeline Stages

| Stage      | Required Native Actions                                                         |
|------------|---------------------------------------------------------------------------------|
| stabilize  | stabilize_write, lock-file detection, size-stable polling                       |
| identify   | calculate_hash (SHA-256), assign_docid, registry duplicate check                |
| analyze    | extract_metadata, run_ocr, run_vision, classify_para, read_xattrs               |
| version    | compare_hash, snapshot_previous, increment_version, generate_diff               |
| rename     | canonical_rename, move to PARA destination                                      |
| sidecar    | write_embedded_metadata, write_xattrs, write_sidecar_json, write_sha256_file    |
| hook       | register_hook (HookVault API or local fallback)                                 |
| mirror     | mirror_object (rclone copyto), verify_remote_checksum (rclone md5sum)           |
| register   | update_registry (SQLite UPSERT), record historical_paths                        |
| publish    | update_bookstack (Markdown table), archive_paperparrot (PDF/image types)        |

### Quarantine Actions

Any stage may abort a transaction. Aborted transactions are moved to the quarantine subdirectory matching the failure code. The original file is **never destroyed**.

| Code  | Quarantine Bucket       | Trigger                                           |
|-------|-------------------------|---------------------------------------------------|
| 09100 | MISSING-SIDECAR         | Sidecar not found during audit                    |
| 09200 | HASH-MISMATCH           | File content hash disagrees with registry         |
| 09300 | METADATA-CONFLICT       | DOCID collision, version chain gap, or abort      |
| 09400 | MIRROR-FAILURE          | rclone failed or remote checksum mismatch         |
| 09500 | VERSION-CHAIN-ERROR     | Version sequence broken or prior version missing  |

### Approved Scope (Watch Paths)

```
/srv/sjl/
/data/
/mnt/sjl-sync/
/home/sjl/Downloads/
/home/sjl/Documents/
/home/sjl/Desktop/
/home/sjl/Webtop/
/home/sjl/shared/
```

### Mandatory Exclusions

```
/proc /sys /dev /run  (ephemeral kernel interfaces)
Container overlay and image storage
Live database data directories (PostgreSQL, SQLite WAL files)
Package caches, node_modules, .venv, __pycache__, build output
.git object stores and .gitignore'd paths
Application lock files (.~lock.*, .DS_Store, Thumbs.db)
Operating-system and service runtime internals
/opt/secrets and credential files
```

---

## 9. Hook Scripts and Persistent Linking

Hook identity is DOCID-based. Path-based identifiers are prohibited.

```bash
sjl-hook register <file>                        # create hook, return hook_id
sjl-hook resolve  <docid>                       # return current canonical path
sjl-hook link     <source-docid> <target-docid> # create directional link
sjl-hook backlinks <docid>                      # list all inbound links
sjl-hook moved    <docid> <new-path>            # update path record
sjl-hook validate <docid>                       # confirm file exists at registered path
```

- HookVault is the API and relationship store (`hooks.shannonjlove.cloud`).
- The central registry resolves DOCID → current path.
- Renames and moves update location without changing identity.
- Links and backlinks persist through migrations and cloud restoration.
- The `links.json` sidecar carries the in-flight link graph for portability.

---

## 10. Diff Scripts and Change Intelligence

Diff generation is automatic for every changed version.

| File Class                                      | Comparison Method                                              |
|-------------------------------------------------|----------------------------------------------------------------|
| Text, Markdown, CSV, JSON, YAML, XML, source    | Unified text diff (`difflib.unified_diff`)                     |
| DOCX                                            | Paragraph-level, XML, and custom-property comparison           |
| PDF                                             | Page count, extracted text, annotation, metadata, hash delta   |
| Images                                          | Dimensions, EXIF delta, perceptual hash (imagehash)            |
| Audio / video                                   | Duration, stream metadata, fingerprints                        |
| Archives                                        | Manifest and directory-tree comparison                         |
| Unknown binary                                  | Hash, size, and metadata delta                                 |

Diff files are stored in `.sidecars/DOCID/diffs/` named `vPREV_vCURR.diff`. DiffForge (`diff.shannonjlove.cloud`) is the optional private viewer.

---

## 11. Mirror, Sidecar, and Cloud Persistence

Mirror the canonical file, sidecar, checksum, OCR derivative, vision derivative, diff records, version history, and mirror manifest as a single atomic bundle per governed version.

**iDrive E2 object path structure:**
```
bucket/
  PPPPP/
    subarea/
      DOCID/
        current/
          canonical-filename.ext
          canonical-filename.ext.sjl.json
          canonical-filename.ext.sha256
        versions/
          v1-0/
          v1-1/
        metadata/
          provenance.json
          vision.json
          ocr.txt
          links.json
        manifests/
          mirror-manifest.json
```

**Cloud object metadata tags (per object):**

```
docid, para, version, sha256_full, hook_id, origin_device, sidecar_schema,
status (verified|pending), sensitivity, document_type, retention, mirror_verified_at
```

**Verification rules:**
- Do not mark a mirror successful until remote existence AND checksum verification both pass.
- Use rclone `copyto` with `--checksum` flag; verify with `rclone md5sum`.
- Record remote ETag and verify timestamp in `mirror-manifest.json`.
- Use iDrive E2 as durable object storage — not as a live database filesystem.

---

## 12. Device and Application Intake

The server cannot observe every private application sandbox directly. Governance enforcement is achieved through controlled intake boundaries.

| Source              | Governed Intake                                                    |
|---------------------|--------------------------------------------------------------------|
| iPhone / iPad       | Scriptable Share Sheet app → `01100_DEVICE-INTAKE/` → FileWarden  |
| iPhone / iPad       | PaperParrot / Paperless intake webhook                             |
| iPhone / iPad       | WebDAV/SFTP direct to intake folder                                |
| macOS               | Watched save locations and synchronized folders                    |
| Webtop              | Watched desktop, downloads, documents, and shared directories      |
| Nexus applications  | Export, upload, workflow, and consume directories                  |
| Oracle/sOs workers  | Controlled return queue, retaining parent DOCID                    |
| Email               | PaperParrot/Paperless ingestion pipeline                           |
| n8n workflows       | Governed workflow-output endpoint (`01400_N8N-OUTPUT/`)            |
| Browser downloads   | Controlled inbox staging (`01100_DEVICE-INTAKE/`)                  |

**n8n webhook intake pattern:**
```
iOS Scriptable → POST /webhook/filewarden-intake
  payload: { docid, filename, para, sha256, base64_content, metadata }
n8n workflow:
  1. Validate payload and DOCID
  2. Write file to /srv/sjl/01000_INBOX/01100_DEVICE-INTAKE/
  3. FileWarden watchdog detects and governs
  4. n8n receives completion webhook from FileWarden
  5. n8n sends notification (Mattermost or push)
```

---

## 13. BookStack and PaperParrot Publishing

### BookStack Responsibilities

- Current architecture and service inventory
- Operations manuals and recovery procedures
- Naming, metadata, versioning, OCR, hook, diff, and mirror standards
- Proxy, MCP, backup, and device-intake maps
- Summarized change ledger (not machine event log — that lives in the registry)
- Integrity and exception reports
- Architecture decision records

### PaperParrot / Paperless Responsibilities

- Archived governed documents (PDFs, scans, contracts, correspondence, invoices)
- OCR-searchable copies with full-text indexing
- Document types, tags, correspondents, dates, and retention classifications
- Final manuals and published architecture records in PDF form

**Publication rule:** Every completed documentation build must publish the current manual to BookStack and archive the governed PDF to PaperParrot. Fine-grained machine events remain in the registry and sidecars.

**Publication transaction:**
```
change completed
  → generate canonical Markdown/TXT source
  → export DOCX/PDF
  → calculate SHA-256
  → canonical rename
  → write sidecar
  → POST to BookStack API (shelf + page)
  → POST to PaperParrot API (document + tags)
  → store BookStack URL + PaperParrot document ID in registry and sidecar
  → record publication event in change ledger
```

---

## 14. Claude Code Implementation Strategy

Claude Code is the implementation, migration, testing, and maintenance agent. It is **not** the permanent filesystem event daemon, scheduler, registry, or backup authority.

**Discovery-first rule.** Before modifying any server component, run:
```bash
hostnamectl && uname -a && df -h / && free -h && ss -tulpn
tailscale status
podman ps --all --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
podman images && podman network ls
systemctl --user list-units --type=service --all
systemctl --user list-timers --all
find /srv/sjl /data /opt ~/.config/containers/systemd -maxdepth 6 -print
find /srv/sjl /opt -type f \( -iname 'CLAUDE.md' -o -iname 'filewarden*.py' \
  -o -iname 'hookvault*.py' -o -iname '*.container' -o -iname '*.network' \)
git -C /srv/sjl/07000_SYSTEM-AUTOMATION status --short --branch
rclone listremotes
```

**Canonical repository structure:**
```
/srv/sjl/07000_SYSTEM-AUTOMATION/
  07100_FILEWARDEN/
    src/              ← filewarden Python package
    config/           ← filewarden.yaml (reference config)
    migrations/       ← schema migrations
    tests/            ← pytest suite
    quadlet/          ← systemd Quadlet service definition
  07200_HOOK-SCRIPTS/
  07300_DIFF-SCRIPTS/
  07400_MIRROR-REGISTRY/
  07500_BOOKSTACK-AUTOMATION/
  07600_OCR-VISION/
  07700_DEVICE-INTAKE/
  07800_MIGRATION/
  07900_AGENT-CONTEXT/   ← Claude Code context files (see §23.2)
```

---

## 15. Security, Exclusions, and Failure Handling

- Secrets remain in `/opt/secrets`, root-only environment files, or the password manager.
- Published manuals store secret **locations and variable names**, never secret values.
- MCP and automation actions are allowlisted and scoped.
- Mattermost calls authenticated n8n workflows — never direct privileged infrastructure APIs.
- No failed transaction may destroy or overwrite the original.
- Partially completed transactions must roll back or enter quarantine with a complete event record.
- Sensitive and private media routes to the dedicated `06000` namespace and private service boundary.
- The `sjl` service user runs all Podman containers and FileWarden under rootless Podman + systemd Quadlets. Never Docker. Never root.
- Every xattr write that carries governance data uses the `#S` (SYNCABLE) suffix so custom attributes survive iCloud Drive sync.

---

## 16. Integrity Audits and Acceptance Criteria

For every governed file, confirm:

- [ ] Canonical file exists at registered path
- [ ] Filename hash (sha8) matches file content
- [ ] Sidecar JSON exists and validates against schema
- [ ] Sidecar digest matches the registry record
- [ ] Embedded DOCID matches sidecar DOCID (where format supports it)
- [ ] xattr DOCID matches sidecar DOCID (where filesystem supports xattrs)
- [ ] Registry version matches filename version
- [ ] Cloud object and associated metadata exist on iDrive E2
- [ ] Remote checksum matches local SHA-256 digest
- [ ] Mirror manifest is current and verification timestamp ≤ 24 hours old
- [ ] Version chain is complete and unbroken (no gaps in v1-0 → v1-N sequence)
- [ ] Hook ID resolves to current canonical path
- [ ] BookStack publication URL is recorded in sidecar
- [ ] PaperParrot document ID is recorded in sidecar (applicable types only)

**Quarantine routing on failure:**
```
09000_QUARANTINE/
  09100_MISSING-SIDECAR/
  09200_HASH-MISMATCH/
  09300_METADATA-CONFLICT/
  09400_MIRROR-FAILURE/
  09500_VERSION-CHAIN-ERROR/
```

---

## 17. Implementation Sequence

| Phase | Name                | Scope                                                                                     |
|-------|---------------------|-------------------------------------------------------------------------------------------|
| 0     | Discovery           | Inventory files, applications, devices, sync paths, service files, Quadlets, current automation |
| 1     | Backup              | Snapshot source, databases, registries, BookStack pages, and service definitions; verify cloud copies |
| 2     | Registry first      | Build the identity, path, version, event, mirror, metadata, and device schema              |
| 3     | FileWarden v2       | Deploy idempotent transaction processing, rollback, and content-aware state (COMPLETE)     |
| 4     | OCR and vision      | Deploy controlled workers and confidence-aware semantic naming                             |
| 5     | Hook and diff       | Convert HookVault to DOCID identity; trigger automatic format-specific diffs               |
| 6     | Sidecar and mirror  | Create mandatory sidecar bundles, cloud metadata, manifests, and checksum verification     |
| 7     | Device intake       | Deploy iOS Scriptable, macOS watched paths, Webtop, Paperless, n8n, Oracle return paths (COMPLETE for iOS) |
| 8     | BookStack/PaperParrot | Publish manuals, architecture, change summaries, and governed PDF archives              |
| 9     | Historical migration | Dry-run and migrate Inbox, active projects, areas, resources, archives, and private media |
| 10    | Enforcement         | Enable daily audits, sidecar repair, mirror verification, and quarantine routing           |

---

## 18. Current shannonjlove.cloud Snapshot

*(Verified 2026-06-19; revalidate before any migration per §22)*

| Field                  | Current Value                                           | Evidence              |
|------------------------|---------------------------------------------------------|-----------------------|
| Primary domain         | shannonjlove.cloud                                      | Documented            |
| Primary VPS hostname   | shannonjlove (Nexus)                                    | Kernel telemetry      |
| Primary VPS role       | Public edge, control plane, authoritative state node    | Architecture          |
| OS / kernel            | Ubuntu 24.04.x; Linux 6.8.0-124-generic x86_64         | Kernel verified       |
| Public IPv4            | 72.61.74.250                                            | Documented            |
| Root filesystem        | 193 GB total; 97 GB used; 96 GB available (51%)        | Runtime snapshot      |
| Memory                 | 15 GiB total; ~10 GiB available                        | Runtime snapshot      |
| Swap                   | 0 B configured                                          | Runtime snapshot      |
| Listening ports        | 8766, 8797, 8777 (lo), 8811 (lo)                       | Runtime snapshot      |
| Reverse proxy          | Nginx Proxy Manager                                     | Architecture          |
| Container standard     | Rootless Podman + systemd Quadlets under `sjl` user     | Doctrine              |
| Private worker         | Oracle Cloud ARM64 / oracle-sos via Tailscale           | Architecture          |
| Object storage         | iDrive E2 S3-compatible                                 | Persistence layer     |
| Knowledge layer        | BookStack + Paperless/PaperParrot                       | Architecture          |

---

## 19. Canonical Server and Service Hierarchy

```
shannonjlove.cloud
|
+-- 00000_SJL-SOVEREIGN-CLOUD
|   |
|   +-- NEXUS_HOSTINGER_X86_64  [VERIFIED HOST]
|   |   |
|   |   +-- 01000_PUBLIC-EDGE
|   |   |   +-- Nginx Proxy Manager                      [DOCUMENTED]
|   |   |   +-- TLS / Let's Encrypt                      [DOCUMENTED]
|   |   |   +-- Public IPv4: 72.61.74.250                [VERIFIED]
|   |   |   +-- Ports: 80 / 443                          [DOCUMENTED]
|   |   |
|   |   +-- 02000_KNOWLEDGE-AND-DOCUMENTS
|   |   |   +-- BookStack                                [DOCUMENTED]
|   |   |   +-- Paperless-ngx / PaperParrot              [DOCUMENTED]
|   |   |   +-- OCR consume and metadata pipeline        [DOCUMENTED]
|   |   |
|   |   +-- 03000_AUTOMATION-AND-CONTROL
|   |   |   +-- n8n                                      [DOCUMENTED]
|   |   |   +-- MCP Gateway                              [DOCUMENTED]
|   |   |   +-- Hostinger MCP                            [DOCUMENTED]
|   |   |   +-- GitHub MCP                               [DOCUMENTED]
|   |   |   +-- Pipedream MCP                            [DOCUMENTED]
|   |   |   +-- TickTick MCP                             [DOCUMENTED]
|   |   |   +-- Unified Cloud MCP                        [VERIFIED CONNECTOR]
|   |   |
|   |   +-- 04000_FILE-GOVERNANCE
|   |   |   +-- FileWarden v2                            [IMPLEMENTED]
|   |   |   +-- HookVault + SJL hook scripts             [TARGET]
|   |   |   +-- DiffForge + automatic diff scripts       [TARGET]
|   |   |   +-- Central DOCID / version registry (SQLite)[IMPLEMENTED]
|   |   |   +-- Sidecar generation                       [IMPLEMENTED]
|   |   |   +-- Mirror verification                      [IMPLEMENTED]
|   |   |   +-- BookStack publishing                     [IMPLEMENTED]
|   |   |   +-- PaperParrot archival                     [IMPLEMENTED]
|   |   |
|   |   +-- 05000_DATA-AND-STATE
|   |   |   +-- Application databases                    [DOCUMENTED]
|   |   |   +-- Redis / queues                           [DOCUMENTED]
|   |   |   +-- Local governed file roots                [DOCUMENTED]
|   |   |   +-- Version history                          [IMPLEMENTED]
|   |   |   +-- Sidecars / manifests                     [IMPLEMENTED]
|   |   |
|   |   +-- 06000_PRIVATE-SERVICES
|   |   |   +-- Stash / private media                    [DOCUMENTED]
|   |   |   +-- Private admin interfaces                 [DOCUMENTED]
|   |   |
|   |   +-- 07000_OPERATIONS
|   |       +-- Cockpit                                  [DOCUMENTED]
|   |       +-- Portainer (non-canonical UI only)        [DOCUMENTED]
|   |       +-- Uptime / health monitoring               [DOCUMENTED]
|   |       +-- Backup coordinator                       [DOCUMENTED]
|   |       +-- Audit and integrity timers               [TARGET]
|   |
|   +-- SOS_ORACLE_ARM64  [DOCUMENTED PRIVATE WORKER]
|   |   |
|   |   +-- 01000_PRIVATE-COMPUTE
|   |   |   +-- OCR workers (OCRmyPDF / Tesseract)       [TARGET]
|   |   |   +-- Vision workers (YOLO / CLIP)             [TARGET]
|   |   |   +-- Whisper transcription                    [DOCUMENTED]
|   |   |   +-- Media processing                         [DOCUMENTED]
|   |   |
|   |   +-- 02000_PRIVATE-WORKSPACE
|   |       +-- Webtop desktop                           [DOCUMENTED]
|   |
|   +-- 09000_STORAGE-AND-RECOVERY
|       +-- iDrive E2
|       |   +-- PARA object buckets                      [DOCUMENTED]
|       |   +-- Config snapshots                         [DOCUMENTED]
|       |   +-- Database dumps                           [DOCUMENTED]
|       |   +-- File bundles + sidecars                  [IMPLEMENTED]
|       |   +-- Version history + diffs                  [TARGET]
|       |   +-- Checksum manifests                       [IMPLEMENTED]
|       |
|       +-- Git repositories (shannonjlove-github.io)
|           +-- Quadlets                                 [TARGET CANONICAL]
|           +-- Scripts                                  [TARGET CANONICAL]
|           +-- Schemas                                  [TARGET CANONICAL]
|           +-- Manuals source                           [IMPLEMENTED]
```

---

## 20. Filesystem and PARA Tree Map

```
/srv/sjl/
|
+-- 01000_INBOX/
|   +-- 01100_DEVICE-INTAKE/       ← iOS Scriptable, browser downloads
|   +-- 01200_EMAIL-INTAKE/
|   +-- 01300_PAPERLESS-CONSUME/
|   +-- 01400_N8N-OUTPUT/
|   +-- 01900_REVIEW-REQUIRED/
|
+-- 02000_PROJECTS/
|   +-- 02100_FILETAGGER/
|   +-- 02200_PRODUCTIONBINDER/
|   +-- 02300_CREATIVE-PROJECTS/
|   +-- 02400_CLOUD-ARCHITECTURE/
|
+-- 03000_AREAS/
|   +-- 03100_BUSINESS/
|   +-- 03200_LEGAL/
|   +-- 03300_CLOUD-OPERATIONS/
|   +-- 03400_MEDIA-OPERATIONS/
|
+-- 04000_RESOURCES/
|   +-- 04100_DOCUMENTS/
|   +-- 04200_IMAGES/
|   +-- 04300_VIDEO/
|   +-- 04400_AUDIO/
|   +-- 04500_RESEARCH/
|
+-- 05000_ARCHIVES/
|   +-- 05100_COMPLETED-PROJECTS/
|   +-- 05200_RETIRED-SYSTEMS/
|   +-- 05300_HISTORICAL-MANUALS/
|
+-- 06000_PRIVATE-MEDIA/
|   +-- 06100_STASH/
|   +-- 06200_RESTRICTED-DOCUMENTS/
|   +-- 06300_UNSORTED/
|
+-- 07000_SYSTEM-AUTOMATION/
|   +-- 07100_FILEWARDEN/
|   |   +-- src/                   ← filewarden Python package
|   |   +-- config/                ← filewarden.yaml (reference config)
|   |   +-- migrations/
|   |   +-- tests/
|   |   +-- quadlet/               ← systemd .container / .network files
|   |
|   +-- 07200_HOOK-SCRIPTS/
|   +-- 07300_DIFF-SCRIPTS/
|   +-- 07400_MIRROR-REGISTRY/
|   +-- 07500_BOOKSTACK-AUTOMATION/
|   +-- 07600_OCR-VISION/
|   +-- 07700_DEVICE-INTAKE/
|   |   +-- scriptable/            ← SJL-File-Governance.js (iOS Scriptable)
|   |
|   +-- 07800_MIGRATION/
|   +-- 07900_AGENT-CONTEXT/       ← Claude Code context files
|
+-- 08000_APPLICATION-DATA/
|   +-- 08100_BOOKSTACK-EXPORTS/
|   +-- 08200_PAPERLESS-EXPORTS/
|   +-- 08300_N8N-EXPORTS/
|   +-- 08400_MCP-REGISTRY/
|   +-- filewarden/                ← SQLite registry, counter, cache files
|
+-- 09000_QUARANTINE/
    +-- 09100_MISSING-SIDECAR/
    +-- 09200_HASH-MISMATCH/
    +-- 09300_METADATA-CONFLICT/
    +-- 09400_MIRROR-FAILURE/
    +-- 09500_VERSION-CHAIN-ERROR/
```

---

## 21. Domain and Route Map

```
shannonjlove.cloud
|
+-- bookstack.shannonjlove.cloud      → BookStack
+-- docs.shannonjlove.cloud           → Paperless / PaperParrot
+-- n8n.shannonjlove.cloud            → n8n
+-- mcp.shannonjlove.cloud            → MCP gateway
+-- github-mcp.shannonjlove.cloud     → GitHub MCP
+-- oracle-mcp.shannonjlove.cloud     → Oracle MCP bridge (prefer private upstream)
+-- hooks.shannonjlove.cloud          → HookVault
+-- diff.shannonjlove.cloud           → DiffForge
+-- private.shannonjlove.cloud        → Private media boundary
+-- status.shannonjlove.cloud         → Status / monitoring
+-- filetagger.cloud                  → FileTagger product domain
+-- productionbinder.app              → ProductionBinder product domain
```

---

## 22. Snapshot Verification and Discovery Requirements

Before Claude Code or any migration agent modifies the server, it must regenerate the live snapshot and reconcile it against this manual. The current connected status tool does not provide a complete filesystem or Podman inventory. Run the mandatory discovery commands from §14 before any Class B, C, or D change.

---

## 23. Claude Code Operating Architecture

### 23.1 Role Separation

| Component            | Canonical Responsibility                                          | NOT Permitted to Replace               |
|----------------------|-------------------------------------------------------------------|----------------------------------------|
| Claude Code          | Inspect, plan, write, test, migrate, document, submit changes     | File event daemon, scheduler, registry, backup authority |
| FileWarden           | Continuous file detection and governance transactions             | Architecture planner, coding agent     |
| n8n                  | Workflow orchestration, approvals, notifications, retries         | Arbitrary shell administrator          |
| systemd Quadlets     | Durable service lifecycle and restart behavior                    | Source control, deployment planning    |
| Git                  | Executable source of truth and change history                     | Live application database              |
| BookStack            | Human-readable manuals, current state, decisions, change summaries| Machine event database                 |
| PaperParrot          | Governed document archive and OCR-searchable records              | Source-code repository                 |

### 23.2 Claude Code Canonical Context Files

```
/srv/sjl/07000_SYSTEM-AUTOMATION/07900_AGENT-CONTEXT/
|
+-- CLAUDE.md             ← behavioral constitution (behavioral rules, prohibited actions)
+-- ARCHITECTURE.md       ← two-node infrastructure, service map, data flows
+-- FILE-GOVERNANCE.md    ← canonical naming, PARA, DOCID, versioning rules
+-- NAMING-STANDARD.md    ← field-by-field naming specification table
+-- METADATA-SCHEMA.md    ← sidecar JSON schema, xattr keys, registry schema
+-- SECURITY.md           ← secret locations (names only), exclusion lists, MCP scope
+-- DEPLOYMENT.md         ← Quadlet files, rclone config, Nginx routes
+-- TESTS.md              ← test contract, acceptance criteria, failure scenarios
+-- CURRENT-STATE.md      ← last verified live snapshot (regenerated before migrations)
+-- SERVICE-REGISTRY.md   ← DOCID → service/URL map for all managed services
+-- CHANGE-POLICY.md      ← Class A/B/C/D classification table and approval gates
+-- BOOKSTACK-PUBLISHING.md ← shelf IDs, page templates, change ledger format
+-- PAPERPARROT-ARCHIVAL.md ← intake API, document types, tag taxonomy, retention
```

The root `CLAUDE.md` is the behavioral constitution. Detailed technical rules live in adjacent context files so the agent receives precise, task-specific instructions without relying on a monolithic prompt.

### 23.3 Required CLAUDE.md Directives

```markdown
# SJL Sovereign Cloud Agent Constitution

- Use rootless Podman under the dedicated `sjl` service user.
- Use systemd Quadlets for durable services.
- Never use Docker, docker-compose, or `sudo podman`.
- Treat DOCID as permanent identity; never use path as identity.
- Apply the five-digit PARA hierarchy to all governed directories.
- Apply the canonical filename:
    [PPPPP]_YYYY-MM-DD__DOCID__semantic-title__vMAJOR-MINOR__sha8.ext
- Never overwrite changed canonical content without:
    1. Calculating SHA-256
    2. Preserving the prior version
    3. Incrementing the version
    4. Creating a format-appropriate diff
    5. Updating embedded metadata, xattrs, and sidecar
    6. Updating the registry and Hook ID
    7. Mirroring and checksum-verifying the bundle
    8. Publishing change to BookStack; archiving governed record to PaperParrot
- Never expose or echo secrets.
- Never modify excluded OS, database, cache, container, package, or temporary paths.
- Never perform a bulk rename or migration without dry run, backup, manifest, and rollback plan.
- Do not mark work complete until tests, service health, remote checksums, and
  documentation publication are verified.
- Reference the skill library in sjl-file-governance/filewarden/skills/ for all
  FileWarden pipeline extensions.
```

### 23.4 Claude Code Execution Lifecycle

1. Read `CLAUDE.md` and all relevant task-specific context files.
2. Run discovery in read-only mode; capture a timestamped current-state snapshot.
3. Locate the newest deployed source, Quadlets, schemas, scripts, databases, and manuals.
4. Compare deployed VPS files against Git and uploaded reference artifacts.
5. Create a written implementation plan with risks, affected services, backup requirements, and rollback commands.
6. Create or verify backups before modifying proxy, auth, database, registry, or file-governance components.
7. Create a Git branch using the canonical naming convention.
8. Implement the smallest safe change set.
9. Run unit, integration, migration, and failure tests.
10. Deploy to a staging or limited-scope path first.
11. Validate systemd status, container health, logs, network routes, file transactions, mirror checksums, and restoration.
12. Commit the final source and generated manifests.
13. Publish updated manuals and change summaries to BookStack.
14. Archive the approved PDF/TXT/manual bundle to PaperParrot.
15. Close the change only after evidence links and rollback references are recorded.

### 23.5 Change Classification and Approval Gates

| Class | Examples                                          | Claude Code Action                             | Approval               |
|-------|---------------------------------------------------|------------------------------------------------|------------------------|
| A     | Inventory, status, diffs, documentation review    | Execute and report                             | None required          |
| B     | Quadlet, NPM route, non-secret config             | Backup, patch, test, deploy                    | Record change          |
| C     | Database schema, registry migration, volume move  | Dry run, dump, migration test, restore test    | Explicit approval      |
| D     | Bulk rename, delete, firewall, credential replace | Generate plan only until approved              | Explicit + rollback gate |

### 23.6 Claude Code Implementation Workstreams

- **FileWarden v2:** Content-aware state, transaction journal, rollback, DOCID assignment, versioning, metadata writes, quarantine, and publishing hooks. *(Skill library complete — see §24)*
- **Metadata registry:** Files, versions, paths, metadata events, mirrors, OCR, vision, hooks, devices, applications, and integrity checks.
- **Hook scripts:** DOCID-based registration, resolution, movement, linking, backlinks, and validation.
- **Diff scripts:** Automatic format-specific comparison and persistent diff reports.
- **OCR and vision:** Queue-driven workers, confidence records, semantic title proposals, and review routing.
- **Cloud persistence:** Sidecar bundles, object metadata, tags, checksum verification, and restore workflows.
- **Device intake:** iOS Scriptable, macOS watched paths, Webtop, Paperless, email, n8n, Oracle return queues.
- **BookStack publishing:** Architecture, manuals, current state, service pages, change ledger, and exceptions.
- **PaperParrot archival:** Final PDF, TXT, manifests, document types, tags, OCR, and retention classification.

### 23.7 Branch, Commit, and Artifact Naming

```
Branch:             claude/07000-YYYY-MM-DD-short-change-slug
Commit:             [07000][DOCID][vMAJOR-MINOR] imperative change summary
Generated artifact: [PPPPP]_YYYY-MM-DD__DOCID__semantic-title__vMAJOR-MINOR__sha8.ext
Migration manifest: 07000_YYYY-MM-DD__MIGRATION-DOCID__scope-manifest__vX-Y__sha8.json
Rollback script:    07000_YYYY-MM-DD__ROLLBACK-DOCID__scope-rollback__vX-Y__sha8.sh
```

### 23.8 Testing Contract

- **Unit tests:** Naming, version increments, hashes, sidecar validation, DOCID stability, path changes, metadata precedence.
- **Integration tests:** FileWarden, registry, HookVault, DiffForge, OCR/vision, rclone, BookStack API, Paperless API.
- **Failure tests:** Interrupted writes, concurrent saves, cloud outage, BookStack outage, PaperParrot outage, corrupt sidecar, duplicate content, low disk, database unavailability.
- **Restore tests:** Prove a file can be reconstructed from canonical object, sidecar, checksum, cloud manifest, and version chain.
- **Reboot tests:** Prove all Quadlet services return automatically under the `sjl` user.
- No completion claim without machine-readable test evidence and human-readable BookStack summary.

### 23.9 Final Claude Code Rule

> Claude Code may design and execute controlled changes, but **no change becomes canonical** until FileWarden/registry state, Git history, backup evidence, service health, cloud checksum verification, BookStack publication, and PaperParrot archival all agree.

---

## 24. FileWarden Skill Library

FileWarden v2 uses a `@skill(stage, when, name)` decorator to register Python functions as pipeline hooks. All 20 production skills are in `sjl-file-governance/filewarden/skills/`.

### 24.1 Skill Registration

```python
from filewarden.core.pipeline import skill, Transaction

@skill(stage="analyze", when="post", name="my_skill")
def my_skill(tx: Transaction, config: dict) -> None:
    ...
```

Skills register at module import time. `skills/__init__.py` imports all skill modules; `load_skills(pipeline)` wires them into the pipeline engine.

### 24.2 Skill Library Index

| Skill Module              | Stage(s)               | Origin / Function                                          |
|---------------------------|------------------------|------------------------------------------------------------|
| `skill_stabilize_timing`  | stabilize/pre          | Write-lock detection, large-file size polling              |
| `skill_new_files_only`    | stabilize/pre          | Scan-cache gate + batch window scheduler                   |
| `skill_subfolder_traverse`| analyze/pre            | Depth-gated watchdog recursion control                     |
| `skill_xattr_tag`         | analyze/pre + analyze/post + sidecar/post | Full xattr inventory, Finder tag read/write, SJL governance xattrs |
| `skill_screenshot_sort`   | analyze/post           | Device detection from image dimensions (18 device signatures) |
| `skill_pdf_ocr_detect`    | analyze/post           | "Font" grep OCR detection + queue submission               |
| `skill_pdf_size_reduce`   | analyze/post           | Ghostscript PDF compression (ebook/screen/printer/prepress)|
| `skill_content_classify`  | analyze/post           | Entity list matching + sequential numbering                |
| `skill_image_gps_tag`     | analyze/post           | ExifTool GPS + Nominatim/Google reverse geocoding          |
| `skill_video_sort`        | analyze/post           | S##E## + Title(Year) regex TV/movie classification         |
| `skill_video_convert`     | stabilize/pre + analyze/post | HandBrakeCLI/ffmpeg + sentinel re-trigger guard       |
| `skill_audio_convert`     | analyze/post           | ffprobe DTS/FLAC detection + ffmpeg AC3 re-encode          |
| `skill_date_archive`      | analyze/pre + rename/post | mtime-based monthly/yearly routing with batch windows   |
| `skill_dmg_extract`       | analyze/post           | hdiutil attach/eject + 7-zip Linux fallback                |
| `skill_move_parent_folder`| analyze/post           | `hazelSwitchFile` equivalent (`tx.original_path` re-target)|
| `skill_mp4_gather`        | analyze/post           | Directory-level MP4 bundle routing                         |
| `skill_merge_backup`      | mirror/post            | SHA-256 content-dedup copy to secondary backup stores      |
| `skill_notes_publish`     | publish/post           | BookStack governance record page per governed file         |
| `skill_yaml_tag_extract`  | analyze/post           | YAML front matter → PARA inference + xattr write           |
| `skill_tag_from_yaml`     | —                      | Alias: `extract_yaml_tags as tag_from_yaml`                |

### 24.3 Configuration Keys

All skill behavior is controlled by `filewarden.yaml`. Config key naming follows the pattern `<skill_name>_<setting>`. The reference config at `sjl-file-governance/filewarden/config/filewarden.yaml` documents every supported key with inline comments.

### 24.4 Adding a New Skill

1. Create `sjl-file-governance/filewarden/skills/skill_<name>.py`
2. Import `Transaction, skill` from `filewarden.core.pipeline`
3. Decorate with `@skill(stage="<stage>", when="pre|post", name="<name>")`
4. Add import to `skills/__init__.py`
5. Add config keys to `filewarden.yaml` with defaults
6. Add pytest cases to `filewarden/tests/test_pipeline.py`
7. Commit with message: `[07000][SJL-CLOUD-NNNN][v1-0] add skill_<name>: <purpose>`

---

## 25. Sidecar Bundle Schema

### 25.1 Inline Sidecar (`file.ext.sjl.json`)

```json
{
  "schema_version": "2.0",
  "docid": "SJL-CLOUD-0017",
  "canonical_filename": "02000_2026-06-19__SJL-CLOUD-0017__manual__v7-3__843dc901.pdf",
  "original_filename": "manual-draft.pdf",
  "para": "02000",
  "semantic_title": "persistent-metadata-manual",
  "title_confidence": 0.95,
  "title_source": "embedded",
  "version": "7-3",
  "prior_version": "7-2",
  "sha256_full": "843dc901a4b2c3d4e5f6...",
  "sha8": "843dc901",
  "mime_type": "application/pdf",
  "extension": "pdf",
  "size_bytes": 354201,
  "date_document": "2026-06-19",
  "date_created": "2026-06-19T14:23:00Z",
  "date_ingested": "2026-06-19T14:25:33Z",
  "date_modified": "2026-06-19T14:23:00Z",
  "origin_device": "nexus",
  "origin_application": "filewarden-v2",
  "intake_method": "watchdog",
  "canonical_path": "/srv/sjl/02000_PROJECTS/02400_CLOUD-ARCHITECTURE/02000_2026-06-19__SJL-CLOUD-0017__manual__v7-3__843dc901.pdf",
  "historical_paths": [
    "/srv/sjl/01000_INBOX/01100_DEVICE-INTAKE/manual-draft.pdf"
  ],
  "ocr_state": "complete",
  "ocr_confidence": 0.98,
  "vision_state": "not-applicable",
  "sensitivity": "standard",
  "retention": "indefinite",
  "review_status": "approved",
  "mirror_target": "sjl-e2",
  "mirror_object_key": "02000/02400/SJL-CLOUD-0017/current/...",
  "mirror_verified_at": "2026-06-19T14:30:00Z",
  "hook_id": "HOOK-0017",
  "registry_id": "SJL-CLOUD-0017",
  "bookstack_url": "https://bookstack.shannonjlove.cloud/books/...",
  "paperparrot_id": "PP-0042",
  "skill_outputs": {
    "pdf_size_reduce": { "original_bytes": 420000, "reduced_bytes": 354201, "reduction_pct": 15.7 },
    "xattr_tag_write": { "finder_tags_written": ["SJL-PROJECTS", "Red", "SJL-CLOUD-0017"] }
  },
  "governed_at": "2026-06-19T14:25:33Z",
  "sidecar_sha256": "a1b2c3d4..."
}
```

### 25.2 Provenance Record (`.sidecars/DOCID/provenance.json`)

Contains the full inline sidecar payload plus:
- `event_type`: `created | modified | moved | deleted`
- `pipeline_history`: list of `{ stage, started_at, completed_at, result }`
- `version_chain`: list of `{ version, sha256, date, diff_file }`

### 25.3 Mirror Manifest (`.sidecars/DOCID/mirror-manifest.json`)

```json
{
  "docid": "SJL-CLOUD-0017",
  "mirror_target": "sjl-e2",
  "bucket": "sjl-sovereign",
  "object_key": "02000/02400/SJL-CLOUD-0017/current/canonical-filename.pdf",
  "remote_etag": "\"d41d8cd98f00b204e9800998ecf8427e\"",
  "remote_sha256": "843dc901a4b2c3d4...",
  "local_sha256": "843dc901a4b2c3d4...",
  "checksums_match": true,
  "verified_at": "2026-06-19T14:30:00Z",
  "rclone_remote": "sjl-e2",
  "mirror_files": [
    "canonical-filename.pdf",
    "canonical-filename.pdf.sjl.json",
    "canonical-filename.pdf.sha256"
  ]
}
```

### 25.4 OCR Text (`.sidecars/DOCID/ocr.txt`)

Plain UTF-8 extracted text. First line: `# DOCID: <docid> | confidence: <float> | source: <tesseract|native>`.

### 25.5 Vision Record (`.sidecars/DOCID/vision.json`)

```json
{
  "docid": "SJL-CLOUD-0017",
  "model": "clip-vit-base-patch32",
  "run_at": "2026-06-19T15:00:00Z",
  "confidence": 0.87,
  "objects": ["document", "text", "table"],
  "scene": "document",
  "perceptual_hash": "aabbccdd11223344",
  "duplicate_candidates": [],
  "semantic_title_proposal": "persistent-metadata-manual",
  "review_required": false
}
```

### 25.6 Links Record (`.sidecars/DOCID/links.json`)

```json
{
  "docid": "SJL-CLOUD-0017",
  "updated_at": "2026-06-19T14:25:33Z",
  "outbound": [
    { "target_docid": "SJL-CLOUD-0015", "relationship": "references" }
  ],
  "inbound": [
    { "source_docid": "SJL-CLOUD-0020", "relationship": "referenced-by" }
  ]
}
```

---

## 26. iOS Device Intake — Scriptable App

### 26.1 Architecture

```
iOS Share Sheet
  → Scriptable: SJL-File-Governance.js
    → Generate DOCID (SJL-DEVICE-YYYYMMDD-HHMMSS-XXXX)
    → SHA-256 (pure-JS, public domain Chris Veness algorithm)
    → PARA classification menu (9 codes)
    → Version picker (auto-minor, major, metadata-only)
    → Write canonical file to iCloud Drive/SJL/01000_INBOX/01100_DEVICE-INTAKE/
    → Write inline .sjl.json sidecar
    → Write .sha256 checksum file
    → Write .sidecars/DOCID/provenance.json
    → Update sjl-registry.json
    → POST to n8n webhook (optional)
  → iCloud Drive syncs to Nexus
  → FileWarden watchdog detects and governs
```

### 26.2 Config Block (top of SJL-File-Governance.js)

```javascript
const CONFIG = {
  iCloudInboxFolder:  "SJL/01000_INBOX/01100_DEVICE-INTAKE",
  registryPath:       "SJL/08000_APPLICATION-DATA/sjl-registry.json",
  sidecarBase:        "SJL/.sidecars",
  n8nWebhookURL:      "",          // set to n8n webhook URL to enable
  docidPrefix:        "SJL-DEVICE",
  defaultPARA:        "01000",
};
```

### 26.3 Installation

1. Install Scriptable from the App Store.
2. Open Scriptable → `+` → paste the full source of `scriptable/SJL-File-Governance.js`.
3. Name the script `SJL File Governance`.
4. Enable **Show in Share Sheet** in script settings.
5. Share any file from any app → tap `SJL File Governance`.

### 26.4 n8n Webhook Payload

```json
{
  "event":     "intake",
  "docid":     "SJL-DEVICE-20260629-143022-4827",
  "filename":  "01000_2026-06-29__SJL-DEVICE-20260629-143022-4827__invoice__v1-0__a1b2c3d4.pdf",
  "para":      "03000",
  "sha256":    "a1b2c3d4...",
  "size":      45231,
  "device":    "iPhone",
  "timestamp": "2026-06-29T14:30:22Z",
  "metadata":  { "original_filename": "invoice.pdf" }
}
```

---

## 27. Extended Attribute Tagging System

### 27.1 Key Reference

| xattr Key                                     | Format                    | Flags | iCloud |
|-----------------------------------------------|---------------------------|-------|--------|
| `com.apple.metadata:_kMDItemUserTags`         | Binary plist `NSArray`    | PS    | Preserved |
| `com.apple.metadata:kMDItemKeywords`          | Binary plist `NSArray`    | PS    | Preserved |
| `com.apple.metadata:kMDItemComment`           | Binary plist `NSString`   | PS    | Preserved |
| `com.apple.metadata:kMDItemHeadline`          | Binary plist `NSString`   | PS    | Preserved |
| `com.apple.metadata:kMDItemWhereFroms`        | Binary plist `NSArray`    | PS    | Preserved |
| `com.apple.quarantine`                        | ASCII string              | PCS   | Preserved |
| `com.apple.provenance`                        | 11-byte integer           | —     | Varies |
| `co.sjl.filewarden:docid#S`                  | Binary plist `NSString`   | S     | Syncs |
| `co.sjl.filewarden:para#S`                   | Binary plist `NSString`   | S     | Syncs |
| `co.sjl.filewarden:version#S`                | Binary plist `NSString`   | S     | Syncs |
| `co.sjl.filewarden:sha8#S`                   | Binary plist `NSString`   | S     | Syncs |
| `co.sjl.filewarden:semantic_title#S`         | Binary plist `NSString`   | S     | Syncs |
| `co.sjl.filewarden:governed_at#S`            | Binary plist `NSString`   | S     | Syncs |

### 27.2 Finder Tag Color Encoding

Finder tags in `_kMDItemUserTags` are stored as an array of strings:
- Plain tag: `"Work"` (no color)
- Color tag: `"Red\n5"` (name + newline + color number)

| Color Number | Color Name | Hex     | PARA Zone       |
|:------------:|------------|---------|-----------------|
| 0            | None       | —       | —               |
| 1            | Gray       | #b2b2b2 | 05000 ARCHIVES  |
| 2            | Green      | #63e55c | 04000 RESOURCES |
| 3            | Purple     | #c77bff | 06000 PRIVATE   |
| 4            | Blue       | #6abdff | 03000 AREAS     |
| 5            | Red        | #ff6b6b | 02000 PROJECTS  |
| 6            | Orange     | #ff9e51 | 01000 INBOX     |
| 7            | Yellow     | #ffe44f | 07000/08000 SYS |

### 27.3 XATTR Preservation Flags

| Suffix | Flag                       | Operation Behavior                                    |
|--------|----------------------------|-------------------------------------------------------|
| `#S`   | SYNCABLE                   | Survives iCloud Drive sync (required for SJL xattrs)  |
| `#C`   | CONTENT_DEPENDENT          | Invalidated when file content changes                 |
| `#P`   | NO_EXPORT                  | Stripped on Share/AirDrop                             |
| `#N`   | NEVER_PRESERVE             | Never copied to any destination                       |

### 27.4 APFS Storage Limits

- ≤ 3,804 bytes → stored inline with inode (fast access, no overhead)
- > 3,804 bytes → stored in separate overflow data stream (effectively unlimited, no hard cap)
- Total sync budget: ~32 KiB across all xattrs for iCloud sync operations

### 27.5 Pipeline Integration

The `skill_xattr_tag` skill provides three hooks:

1. `xattr_inventory` (analyze/pre) — enumerate all existing xattrs into `tx.metadata`
2. `xattr_tag_read` (analyze/post) — read Finder tags, recover DOCID on re-ingestion, detect quarantine
3. `xattr_tag_write` (sidecar/post) — write SJL governance xattrs, Finder color tags per PARA zone, Spotlight keywords + comment

---

## Appendix A — Final Doctrine Checklist

1. Five-digit PARA applies to every governed directory and hierarchy.
2. The canonical filename applies to every governed file.
3. DOCID is identity; path is location.
4. Every content change creates a version.
5. Every version receives a hash and diff record.
6. Every compatible document receives OCR.
7. Every compatible image or media asset receives technical and semantic analysis.
8. Every file receives a sidecar.
9. Every canonical object is mirrored and checksum-verified.
10. BookStack maintains manuals, current state, and summarized changes.
11. PaperParrot archives governed records and searchable document copies.
12. Nexus owns authoritative state; Oracle/sOs provides replaceable compute.
13. No migration is complete until rollback and restoration have been tested.
14. No change becomes canonical until FileWarden, registry, Git, backup, cloud checksum, BookStack, and PaperParrot all agree.

---

## Appendix B — Sidecar JSON Schema (Condensed)

```json
{
  "$schema": "https://sjl.cloud/schemas/sidecar-v2.json",
  "required": [
    "schema_version", "docid", "canonical_filename", "para",
    "version", "sha256_full", "sha8", "mime_type",
    "date_ingested", "canonical_path", "governed_at"
  ]
}
```

Full JSON Schema available at `sjl-file-governance/filewarden/schemas/sidecar-v2.json`.

---

*Publication rule: Always export and publish this document to BookStack and archive the governed PDF to PaperParrot after every version update. The sidecar for this document must be updated at the same time.*
