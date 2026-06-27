# SJL Sovereign Cloud v7.3
## Persistent Metadata Doctrine — Universal File Governance and Implementation Manual

**Document class:** Canonical architecture and operating manual  
**Owner:** Shannon J. Love  
**Version:** v7.3  
**Date:** 2026-06-19  
**Status:** Target architecture — implementation baseline  
**Security:** No credentials, tokens, passwords, or private keys  
**DOCID:** SJL-CLOUD-FILE-GOVERNANCE  

> **Controlling principle:** No file becomes canonical until it has been identified, analyzed, named, versioned, sidecar-linked, mirrored, registered, and logged.

---

## Mission

Ensure every governed file remains identifiable, versioned, searchable, mirrored, and recoverable across devices and cloud storage.

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

---

## 1. Executive Architecture Decision

SJL Sovereign Cloud v7.3 establishes a mandatory file-governance layer beneath every approved application, device, sync path, and storage destination. The system is centered on Nexus as the authoritative control and persistence node, with Oracle/sOs providing replaceable private compute for OCR, vision, indexing, and batch processing.

- FileWarden replaces Hazel as the universal policy-enforcement daemon.
- SJL hook scripts and HookVault replace Hookmark.
- SJL diff scripts and the optional DiffForge viewer replace DeltaWalker.
- Every byte-level content change creates a new version.
- Every canonical file receives persistent metadata in multiple synchronized layers.
- Every canonical file bundle is mirrored to cloud storage and checksum-verified.
- BookStack stores manuals, service state, and summarized change records.
- PaperParrot/Paperless stores archived records and governed document copies.

---

## 2. Universal File Governance Doctrine

1. Detect every governed file creation, upload, synchronization event, move, rename, or content save.
2. Wait until the write is stable before processing.
3. Calculate a full SHA-256 digest.
4. Extract native text and embedded metadata.
5. Run OCR and image/media recognition when applicable.
6. Assign or recover a permanent DOCID.
7. Determine the five-digit PARA destination.
8. Compare the new content digest with the current registry version.
9. Preserve the prior version and generate a diff when content changed.
10. Rename the file canonically.
11. Write embedded metadata, extended attributes, and sidecar JSON.
12. Update the central registry and persistent hook record.
13. Mirror the complete bundle to cloud storage.
14. Verify the remote checksum.
15. Publish the change summary and manual updates to BookStack and archive the governed record to PaperParrot.

---

## 3. Canonical Five-Digit PARA Structure

All governed directories and hierarchies use five digits. Four-digit legacy paths may remain only as temporary compatibility aliases during migration.

| Code  | Category          | Primary Purpose                                              |
|-------|-------------------|--------------------------------------------------------------|
| 01000 | INBOX             | Controlled intake, staging, and review                       |
| 02000 | PROJECTS          | Active finite projects and deliverables                      |
| 03000 | AREAS             | Ongoing responsibilities and operations                      |
| 04000 | RESOURCES         | Reference material and reusable assets                       |
| 05000 | ARCHIVES          | Inactive, completed, and retained records                    |
| 06000 | PRIVATE MEDIA     | Restricted media and sensitive assets                        |
| 07000 | SYSTEM AUTOMATION | Scripts, agents, Quadlets, manifests, and manuals            |
| 08000 | APPLICATION DATA  | Governed application exports and controlled state            |
| 09000 | QUARANTINE        | Failures, conflicts, unsupported files, and review-required  |

---

## 4. Canonical Naming Convention

```
[PPPPP]_YYYY-MM-DD__DOCID__semantic-title__vMAJOR-MINOR__sha8.ext
```

**Example:**
```
02000_2026-06-19__SJL-CLOUD-0017__persistent-metadata-manual__v7-2__843dc901.pdf
```

| Field         | Rule                                                              |
|---------------|-------------------------------------------------------------------|
| PPPPP         | Five-digit PARA classification                                    |
| YYYY-MM-DD    | Authoritative creation or document date                           |
| DOCID         | Permanent identity that never changes                             |
| semantic-title| OCR-, vision-, metadata-, or user-derived title                   |
| vMAJOR-MINOR  | Automatic immutable content version                               |
| sha8          | First eight characters of the full SHA-256 digest                 |
| ext           | Lowercase normalized extension                                    |

---

## 5. Permanent Identity and Automatic Versioning

- Path and filename are mutable properties. DOCID is the durable identity.
- A new file receives a DOCID once.
- Moves and renames update the path record without changing DOCID.
- Any byte-level content change creates a new immutable version.
- Metadata-only changes create metadata events without necessarily incrementing the content version.
- The prior canonical version is preserved before replacement.
- The version chain must remain complete and recoverable.

| Version | Event                                      |
|---------|--------------------------------------------|
| v1-0    | Initial ingestion                          |
| v1-1    | First content modification                 |
| v1-2    | Second content modification                |
| v2-0    | Intentional major revision or transformation |

---

## 6. Persistent Metadata Architecture

A governed file must remain reconstructable even if it is renamed, moved to another filesystem, downloaded from cloud storage, stripped of extended attributes, or restored after complete server loss.

### Mandatory Base Metadata

- DOCID, canonical filename, and original filename
- PARA code and hierarchy
- Semantic title and title-confidence source
- Current and prior version
- Full SHA-256 and sidecar digest
- MIME type and format
- Creation, document, ingestion, and modification timestamps
- Originating device, application, and intake method
- Current canonical path and historical paths
- OCR and vision state
- Sensitivity, retention, and review status
- Mirror target, object key, and checksum verification
- Hook ID and registry record ID

### Canonical File Bundle

```
file.ext
file.ext.sjl.json
file.ext.sha256
.sidecars/DOCID/ocr.txt
.sidecars/DOCID/vision.json
.sidecars/DOCID/provenance.json
.sidecars/DOCID/links.json
.sidecars/DOCID/mirror-manifest.json
.sidecars/DOCID/diffs/
```

### Metadata Layer Precedence

Reviewed user metadata outranks verified canonical metadata, embedded source metadata, application metadata, OCR, vision inference, filename inference, and filesystem timestamps.

| Layer                            | Purpose                                          | Persistence Rule       |
|----------------------------------|--------------------------------------------------|------------------------|
| Canonical filename               | Human-readable minimum recovery data             | Always present         |
| Embedded metadata                | Portable metadata inside supported formats       | Write when safe        |
| Extended attributes              | Fast local lookup and filesystem indexing        | Reconstructable        |
| Sidecar JSON                     | Complete portable file-level metadata record     | Mandatory              |
| Central registry                 | Current state, paths, versions, links, provenance| Authoritative system index |
| Cloud object metadata/manifests  | Off-device recovery and integrity verification   | Mandatory for mirrors  |

---

## 7. OCR, Vision, and Semantic Renaming

Semantic naming occurs only after text and image intelligence have been collected.

- Use native text extraction before OCR.
- Use OCRmyPDF/Tesseract for scanned PDFs and images.
- Use ExifTool and format-native parsers for embedded metadata.
- Use image recognition for objects, scenes, visible text, and duplicate detection.
- Preserve original camera and source metadata.
- Record confidence, source, review state, and field locks for AI-derived metadata.
- Route low-confidence or conflicting results to 01000 review or 09000 quarantine.

---

## 8. FileWarden v2 Operating Pipeline

FileWarden is the universal transaction coordinator for all approved SJL roots.

```
discover -> stabilize -> identify -> analyze -> version -> diff -> rename
        -> sidecar -> hook -> mirror -> register -> publish
```

### Required Native Actions

```
stabilize_write       calculate_hash        assign_docid
extract_metadata      run_ocr               run_vision
classify_para         snapshot_previous     increment_version
generate_diff         canonical_rename      write_embedded_metadata
write_xattrs          write_sidecar         register_hook
mirror_object         verify_remote_checksum update_registry
update_bookstack      archive_paperparrot   quarantine
```

### Approved Scope

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

- `/proc`, `/sys`, `/dev`, `/run`, and ephemeral `/tmp` content
- Container overlay and image storage
- Live database data directories
- Package caches, `node_modules`, virtual environments, and build caches
- `.git` object stores and application lock files
- Operating-system and service runtime internals

---

## 9. Hook Scripts and Persistent Linking

Hook identity must be DOCID-based, not path-based.

```bash
sjl-hook register <file>
sjl-hook resolve <docid>
sjl-hook link <source-docid> <target-docid>
sjl-hook backlinks <docid>
sjl-hook moved <docid> <new-path>
sjl-hook validate <docid>
```

- HookVault remains the API and relationship store.
- The registry resolves a DOCID to the current path.
- Renames and moves update location without changing identity.
- Links and backlinks persist through migrations and cloud restoration.

---

## 10. Diff Scripts and Change Intelligence

Diff generation is automatic for every changed version. DiffForge remains an optional private viewer.

| File Class                                          | Comparison Method                                              |
|-----------------------------------------------------|----------------------------------------------------------------|
| Text, Markdown, CSV, JSON, YAML, XML, source        | Unified and structured text diff                               |
| DOCX                                                | Paragraph, XML, and custom-property comparison                 |
| PDF                                                 | Page count, extracted text, annotation, metadata, hash         |
| Images                                              | Dimensions, EXIF, perceptual hash, and visual similarity       |
| Audio/video                                         | Duration, streams, fingerprints, and metadata                  |
| Archives                                            | Manifest and directory-tree comparison                         |
| Unknown binary                                      | Hash, size, and metadata delta                                 |

---

## 11. Mirror, Sidecar, and Cloud Persistence

Mirror the canonical file, sidecar, checksum, OCR derivative, vision derivative, diff records, version history, and mirror manifest.

- Use compact cloud object metadata for DOCID, PARA, version, hash, Hook ID, origin device, and sidecar schema.
- Use object tags for status, sensitivity, document type, retention, and mirror verification.
- Do not mark a mirror successful until remote existence and checksum verification both pass.
- Use iDrive E2 as durable object storage, archive, and recovery infrastructure — not as a live database filesystem.

### Cloud Object Structure

```
bucket/PARA/subarea/DOCID/current/
bucket/PARA/subarea/DOCID/versions/
bucket/PARA/subarea/DOCID/metadata/
bucket/PARA/subarea/DOCID/manifests/
```

---

## 12. Device and Application Intake

The server cannot observe every private application sandbox directly. Universal enforcement is achieved through controlled intake boundaries.

| Source               | Governed Intake                                                       |
|----------------------|-----------------------------------------------------------------------|
| iPhone / iPad        | Share Sheet, Files app, WebDAV/SFTP, PaperParrot intake               |
| macOS                | Watched save locations and synchronized folders                        |
| Webtop               | Watched desktop, downloads, documents, and shared directories          |
| Nexus applications   | Export, upload, workflow, and consume directories                      |
| Oracle/sOs workers   | Controlled return queue retaining parent DOCID                         |
| Email                | PaperParrot/Paperless ingestion                                        |
| n8n                  | Governed workflow-output endpoint                                      |
| Browser downloads    | Controlled inbox staging                                               |

**Authority rule:** A file may exist temporarily outside the canonical environment, but it is not authoritative until it passes through Nexus governance.

---

## 13. BookStack and PaperParrot Publishing

### BookStack Responsibilities

- Current architecture and service inventory
- Operations manuals and recovery procedures
- Naming, metadata, versioning, OCR, hook, diff, and mirror standards
- Proxy, MCP, backup, and device-intake maps
- Summarized change ledger
- Integrity and exception reports
- Architecture decision records

### PaperParrot/Paperless Responsibilities

- Archived governed documents
- PDFs, scans, contracts, correspondence, invoices, and retained exports
- OCR-searchable copies
- Document types, tags, correspondents, dates, and retention classifications
- Final manuals and published architecture records

**Publication rule:** Every completed documentation build must publish the current manual to BookStack and archive the governed PDF to PaperParrot. Fine-grained machine events remain in the registry and sidecars; BookStack receives summarized, navigable records.

---

## 14. Claude Code Implementation Strategy

Claude Code is the implementation, migration, testing, and maintenance agent. It is not the permanent filesystem event daemon.

### Discovery-First Rule

```bash
find /srv/sjl /opt /etc/containers ~/.config/containers/systemd -maxdepth 5 -type f
podman ps --all
podman network ls
systemctl --user list-units --all
systemctl --user list-timers --all
find /data -maxdepth 5 -type d
```

Locate the newest FileWarden, HookVault, DiffForge, deployment, Quadlet, BookStack, and agent-context files. Compare deployed VPS files with uploaded source files before editing. Create verified backups and Git commits before migrations. Work through staged branches, tests, and rollback checkpoints. Never rename or mutate the entire corpus in an unreviewed pass. Never expose secrets in documentation or logs. Never use Docker; use rootless Podman and systemd Quadlets under the dedicated `sjl` user.

### Repository Structure

```
/srv/sjl/07000_SYSTEM-AUTOMATION/
  07100_filewarden/
  07200_hook-scripts/
  07300_diff-scripts/
  07400_mirror-registry/
  07500_bookstack-automation/
  07600_ocr-vision/
  07700_device-intake/
  07800_migration/
  07900_agent-context/
```

---

## 15. Security, Exclusions, and Failure Handling

- Secrets remain in `/opt/secrets`, root-only environment files, or the password manager.
- Published manuals store secret locations and variable names, never secret values.
- MCP and automation actions are allowlisted and scoped.
- Mattermost, if used, calls authenticated n8n workflows rather than direct privileged infrastructure APIs.
- No failed transaction may destroy or overwrite the original.
- Partially completed transactions must roll back or enter quarantine with a complete event record.
- Sensitive and private media routes to the dedicated 06000 namespace and private service boundary.

---

## 16. Integrity Audits and Acceptance Criteria

- ☐ Canonical file exists.
- ☐ Filename hash matches file content.
- ☐ Sidecar exists and validates against schema.
- ☐ Sidecar digest matches the registry.
- ☐ Embedded DOCID matches the sidecar.
- ☐ Extended-attribute DOCID matches the sidecar where xattrs are supported.
- ☐ Registry version matches the filename version.
- ☐ Cloud object and associated metadata exist.
- ☐ Remote checksum matches the local digest.
- ☐ Mirror manifest is current.
- ☐ Version chain is complete and unbroken.
- ☐ Hook ID resolves to the current canonical path.
- ☐ BookStack and PaperParrot publication status is recorded.

### Quarantine Routing

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

| Phase | Name                    | Scope                                                                                               |
|-------|-------------------------|-----------------------------------------------------------------------------------------------------|
| 0     | Discovery               | Inventory files, applications, devices, sync paths, service files, Quadlets, and current automation |
| 1     | Backup                  | Snapshot source, databases, registries, BookStack pages, and service definitions; verify cloud copies |
| 2     | Registry first          | Build the identity, path, version, event, mirror, metadata, and device schema                       |
| 3     | FileWarden v2           | Implement idempotent transaction processing, rollback, and content-aware state                       |
| 4     | OCR and vision          | Deploy controlled workers and confidence-aware semantic naming                                      |
| 5     | Hook and diff           | Convert HookVault to DOCID identity and trigger automatic diffs                                     |
| 6     | Sidecar and mirror      | Create mandatory sidecars, cloud metadata, manifests, and checksum verification                     |
| 7     | Device intake           | Implement iOS, macOS, Webtop, Paperless, n8n, and Oracle return paths                              |
| 8     | BookStack and PaperParrot | Publish manuals, architecture, change summaries, and governed PDF archives                        |
| 9     | Historical migration    | Dry-run and migrate Inbox, active projects, areas, resources, archives, and private media           |
| 10    | Enforcement             | Enable daily audits, sidecar repair, mirror verification, and quarantine routing                    |

---

## Final Doctrine

- Five-digit PARA applies to every governed directory and hierarchy.
- The canonical filename applies to every governed file.
- DOCID is identity; path is location.
- Every content change creates a version.
- Every version receives a hash and diff record.
- Every compatible document receives OCR.
- Every compatible image or media asset receives technical and semantic analysis.
- Every file receives a sidecar.
- Every canonical object is mirrored and checksum-verified.
- BookStack maintains manuals, current state, and summarized changes.
- PaperParrot archives governed records and searchable document copies.
- Nexus owns authoritative state; Oracle/sOs provides replaceable compute.
- No migration is complete until rollback and restoration have been tested.

---

## 18. Current shannonjlove.cloud Snapshot

Verified runtime telemetry retrieved from the connected VPS status service on 2026-06-19.

| Field                   | Current Value                                                    | Evidence                |
|-------------------------|------------------------------------------------------------------|-------------------------|
| Primary domain          | shannonjlove.cloud                                               | Documented              |
| Primary VPS hostname    | shannonjlove                                                     | Verified kernel         |
| OS / kernel             | Ubuntu 24.04.x; Linux 6.8.0-124-generic x86_64                  | Kernel verified         |
| Public IPv4             | 72.61.74.250                                                     | Documented              |
| Root filesystem         | 193 GB total; 97 GB used; 96 GB available; 51% used              | Verified snapshot       |
| Memory                  | 15 GiB total; 4.7 GiB used; ~10 GiB available                   | Verified snapshot       |
| Swap                    | 0 B configured                                                   | Verified snapshot       |
| Verified listening ports| 8766, 8797, 8777 (localhost), 8811 (localhost)                   | Verified snapshot       |
| Container standard      | Rootless Podman with systemd Quadlets under dedicated service user| Documented doctrine    |
| Object storage          | iDrive E2 S3-compatible storage                                  | Documented              |
| Knowledge layer         | BookStack + Paperless/PaperParrot                                | Documented              |

---

## 19. Canonical Server and Service Hierarchy

```
shannonjlove.cloud
|
+-- 00000_SJL-SOVEREIGN-CLOUD
|   |
|   +-- NEXUS_HOSTINGER_X86_64  [VERIFIED HOST]
|   |   +-- 01000_PUBLIC-EDGE
|   |   |   +-- Nginx Proxy Manager              [DOCUMENTED]
|   |   |   +-- TLS / Let's Encrypt              [DOCUMENTED]
|   |   |   +-- Public DNS: 72.61.74.250         [DOCUMENTED]
|   |   |   +-- Public ports: 80 / 443           [DOCUMENTED]
|   |   |
|   |   +-- 02000_KNOWLEDGE-AND-DOCUMENTS
|   |   |   +-- BookStack                        [DOCUMENTED]
|   |   |   +-- Paperless-ngx / PaperParrot      [DOCUMENTED]
|   |   |   +-- OCR consume and metadata pipeline [DOCUMENTED]
|   |   |
|   |   +-- 03000_AUTOMATION-AND-CONTROL
|   |   |   +-- n8n                              [DOCUMENTED]
|   |   |   +-- MCP Gateway                      [DOCUMENTED]
|   |   |   +-- Hostinger MCP                    [DOCUMENTED]
|   |   |   +-- GitHub MCP                       [DOCUMENTED]
|   |   |   +-- Pipedream MCP                    [DOCUMENTED]
|   |   |   +-- TickTick MCP                     [DOCUMENTED]
|   |   |   +-- Unified Cloud MCP                [VERIFIED CONNECTOR]
|   |   |
|   |   +-- 04000_FILE-GOVERNANCE
|   |   |   +-- FileWarden v2                    [TARGET]
|   |   |   +-- HookVault + SJL hook scripts     [TARGET]
|   |   |   +-- DiffForge + diff scripts         [TARGET]
|   |   |   +-- Central DOCID / version registry  [TARGET]
|   |   |   +-- Sidecar generation               [TARGET]
|   |   |   +-- Mirror verification              [TARGET]
|   |   |   +-- BookStack publishing             [TARGET]
|   |   |   +-- PaperParrot archival             [TARGET]
|   |   |
|   |   +-- 05000_DATA-AND-STATE
|   |   |   +-- Application databases            [DOCUMENTED]
|   |   |   +-- Redis / queues                   [DOCUMENTED]
|   |   |   +-- Local governed file roots        [DOCUMENTED]
|   |   |   +-- Version history                  [TARGET]
|   |   |   +-- Sidecars / manifests             [TARGET]
|   |   |
|   |   +-- 06000_PRIVATE-SERVICES
|   |   |   +-- Stash / private media            [DOCUMENTED]
|   |   |   +-- Private admin interfaces         [DOCUMENTED]
|   |   |
|   |   +-- 07000_OPERATIONS
|   |       +-- Cockpit                          [DOCUMENTED]
|   |       +-- Portainer                        [DOCUMENTED, NON-CANONICAL UI]
|   |       +-- Uptime / health monitoring       [DOCUMENTED]
|   |       +-- Backup coordinator               [DOCUMENTED]
|   |       +-- Audit and integrity timers       [TARGET]
|   |
|   +-- SOS_ORACLE_ARM64  [DOCUMENTED PRIVATE WORKER]
|   |   +-- 01000_PRIVATE-COMPUTE
|   |   |   +-- OCR workers                      [TARGET]
|   |   |   +-- Vision workers                   [TARGET]
|   |   |   +-- Whisper / YOLO / CLIP            [DOCUMENTED]
|   |   |   +-- Media processing                 [DOCUMENTED]
|   |   |
|   |   +-- 02000_PRIVATE-WORKSPACE
|   |   |   +-- Webtop desktop                   [DOCUMENTED]
|   |   |   +-- Dev and admin tools              [DOCUMENTED]
|   |   |
|   |   +-- 03000_WORKER-ORCHESTRATION
|   |       +-- n8n workers                      [DOCUMENTED]
|   |       +-- Oracle MCP bridge                [DOCUMENTED]
|   |       +-- Controlled return queue          [TARGET]
|   |
|   +-- 08000_EXTERNAL-INTEGRATIONS
|   |   +-- GitHub                               [DOCUMENTED]
|   |   +-- Pipedream                            [DOCUMENTED]
|   |   +-- TickTick                             [DOCUMENTED]
|   |   +-- Google Cloud APIs                    [VERIFIED CONFIG PATH]
|   |   +-- Hostinger API                        [VERIFIED CONNECTOR PATH]
|   |   +-- Oracle Cloud API                     [CONFIGURATION REQUIRES REPAIR]
|   |
|   +-- 09000_STORAGE-AND-RECOVERY
|       +-- iDrive E2
|       |   +-- PARA object buckets              [DOCUMENTED]
|       |   +-- Config snapshots                 [DOCUMENTED]
|       |   +-- Database dumps                   [DOCUMENTED]
|       |   +-- File bundles + sidecars          [TARGET]
|       |   +-- Version history + diffs          [TARGET]
|       |   +-- Checksum manifests               [TARGET]
|       |
|       +-- Git repositories
|           +-- Quadlets                         [TARGET CANONICAL]
|           +-- Scripts                          [TARGET CANONICAL]
|           +-- Schemas                          [TARGET CANONICAL]
|           +-- Manuals source                   [TARGET CANONICAL]
```

---

## 20. Filesystem and PARA Tree Map

```
/srv/sjl/
|
+-- 01000_INBOX/
|   +-- 01100_DEVICE-INTAKE/
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
|
+-- 07000_SYSTEM-AUTOMATION/
|   +-- 07100_FILEWARDEN/
|   |   +-- src/
|   |   +-- config/
|   |   +-- migrations/
|   |   +-- tests/
|   |   +-- quadlet/
|   |
|   +-- 07200_HOOK-SCRIPTS/
|   +-- 07300_DIFF-SCRIPTS/
|   +-- 07400_MIRROR-REGISTRY/
|   +-- 07500_BOOKSTACK-AUTOMATION/
|   +-- 07600_OCR-VISION/
|   +-- 07700_DEVICE-INTAKE/
|   +-- 07800_MIGRATION/
|   +-- 07900_AGENT-CONTEXT/
|
+-- 08000_APPLICATION-DATA/
|   +-- 08100_BOOKSTACK-EXPORTS/
|   +-- 08200_PAPERLESS-EXPORTS/
|   +-- 08300_N8N-EXPORTS/
|   +-- 08400_MCP-REGISTRY/
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
+-- bookstack.shannonjlove.cloud      -> BookStack
+-- docs.shannonjlove.cloud           -> Paperless / PaperParrot
+-- n8n.shannonjlove.cloud            -> n8n
+-- mcp.shannonjlove.cloud            -> MCP gateway
+-- github-mcp.shannonjlove.cloud     -> GitHub MCP
+-- oracle-mcp.shannonjlove.cloud     -> Oracle MCP bridge (prefer private upstream)
+-- hooks.shannonjlove.cloud          -> HookVault
+-- diff.shannonjlove.cloud           -> DiffForge
+-- private.shannonjlove.cloud        -> Private media boundary
+-- status.shannonjlove.cloud         -> Status / monitoring
+-- filetagger.cloud                  -> FileTagger product domain
+-- productionbinder.app              -> ProductionBinder product domain
```

---

## 22. Snapshot Verification and Discovery Requirements

Before Claude Code or any migration agent modifies the server, it must regenerate the live snapshot and reconcile it against this manual.

```bash
hostnamectl
uname -a
df -h /
free -h
ss -tulpn
tailscale status
podman ps --all --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
podman network ls
systemctl --user list-units --type=service --all
systemctl --user list-timers --all
find /srv/sjl /data /opt ~/.config/containers/systemd -maxdepth 5 -print
```

---

## 23. Claude Code Operating Architecture

Claude Code is incorporated as the implementation, refactoring, migration, testing, documentation, and controlled operations agent for the SJL Sovereign Cloud. It is not the permanent filesystem watcher and does not replace FileWarden, systemd, n8n, the registry, or the backup system.

### 23.1 Role Separation

| Component      | Canonical Responsibility                                            | Not Permitted to Replace         |
|----------------|---------------------------------------------------------------------|----------------------------------|
| Claude Code    | Inspect, plan, write, test, migrate, document, submit changes       | File event daemon, scheduler, registry, backup authority |
| FileWarden     | Continuous file detection and governance transactions               | Architecture planner or coding agent |
| n8n            | Workflow orchestration, approvals, notifications, retries           | Arbitrary shell administrator    |
| systemd Quadlets | Durable service lifecycle and restart behavior                   | Source control or deployment planning |
| Git            | Executable source of truth and change history                       | Live application database        |
| BookStack      | Human-readable manuals, current state, decisions, change summaries  | Machine event database           |
| PaperParrot    | Governed document archive and OCR-searchable records                | Source-code repository           |

### 23.2 Claude Code Canonical Repository Context

```
/srv/sjl/07000_SYSTEM-AUTOMATION/07900_AGENT-CONTEXT/
|
+-- CLAUDE.md
+-- ARCHITECTURE.md
+-- FILE-GOVERNANCE.md
+-- NAMING-STANDARD.md
+-- METADATA-SCHEMA.md
+-- SECURITY.md
+-- DEPLOYMENT.md
+-- TESTS.md
+-- CURRENT-STATE.md
+-- SERVICE-REGISTRY.md
+-- CHANGE-POLICY.md
+-- BOOKSTACK-PUBLISHING.md
+-- PAPERPARROT-ARCHIVAL.md
```

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
  1. calculating SHA-256;
  2. preserving the prior version;
  3. incrementing the version;
  4. creating a diff;
  5. updating embedded metadata, xattrs, and sidecar;
  6. updating the registry and Hook ID;
  7. mirroring and checksum-verifying the bundle;
  8. publishing the change to BookStack and archiving to PaperParrot.
- Never expose or echo secrets.
- Never modify excluded OS, database, cache, container, package, or temporary paths.
- Never perform a bulk rename or migration without a dry run, backup, manifest, and rollback plan.
- Do not mark work complete until tests, service health, remote checksums, and documentation publication are verified.
```

### 23.4 Claude Code Execution Lifecycle

1. Read CLAUDE.md and all relevant task-specific context files.
2. Run discovery in read-only mode and capture a timestamped current-state snapshot.
3. Locate the newest deployed source, Quadlets, schemas, scripts, databases, and manuals.
4. Compare deployed VPS files against Git and uploaded reference artifacts.
5. Create a written implementation plan with risks, affected services, backup requirements, and rollback commands.
6. Create or verify backups before modifying proxy, authentication, database, registry, or file-governance components.
7. Create a Git branch using the canonical naming convention.
8. Implement the smallest safe change set.
9. Run unit, integration, migration, and failure tests.
10. Deploy to a staging or limited-scope path first.
11. Validate systemd status, container health, logs, network routes, file transactions, mirror checksums, and restoration.
12. Commit the final source and generated manifests.
13. Publish updated manuals and change summaries to BookStack.
14. Archive the approved PDF/TXT/manual bundle to PaperParrot.
15. Close the change only after evidence links and rollback references are recorded.

### 23.5 Mandatory Discovery Commands

```bash
hostnamectl && uname -a && df -h / && free -h && ss -tulpn
tailscale status
podman ps --all --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
podman images && podman network ls
systemctl --user list-units --type=service --all
systemctl --user list-timers --all
find /srv/sjl /data /opt ~/.config/containers/systemd -maxdepth 6 -print
find /srv/sjl /opt -type f \( -iname 'CLAUDE.md' -o -iname 'filewarden*.py' -o -iname 'hookvault*.py' -o -iname 'diffforge*.py' -o -iname '*.container' -o -iname '*.network' -o -iname '*.volume' \)
git -C /srv/sjl/07000_SYSTEM-AUTOMATION status --short --branch
rclone listremotes
```

### 23.6 Change Classification and Approval Gates

| Class | Examples                                    | Claude Code Action                              | Approval                         |
|-------|---------------------------------------------|-------------------------------------------------|----------------------------------|
| A     | Inventory, status, diffs, doc review        | Execute and report                              | No additional approval           |
| B     | Quadlet, NPM route, non-secret config       | Backup, patch, test, deploy                     | Record change                    |
| C     | Database schema, registry migration, volume  | Dry run, dump, migration test, restore test     | Explicit approval                |
| D     | Bulk rename, delete, firewall, credential   | Generate plan only until approved               | Explicit approval + rollback gate |

### 23.7 Branch, Commit, and Artifact Naming

```
Branch:    claude/07000-YYYY-MM-DD-short-change-slug
Commit:    [07000][DOCID][vMAJOR-MINOR] imperative change summary
Artifact:  [PPPPP]_YYYY-MM-DD__DOCID__semantic-title__vMAJOR-MINOR__sha8.ext
Migration: 07000_YYYY-MM-DD__MIGRATION-DOCID__scope-manifest__vX-Y__sha8.json
Rollback:  07000_YYYY-MM-DD__ROLLBACK-DOCID__scope-rollback__vX-Y__sha8.sh
```

### 23.8 Testing Contract

- Unit tests for naming, version increments, hashes, sidecar validation, DOCID stability, path changes, and metadata precedence.
- Integration tests for FileWarden, registry, HookVault, DiffForge, OCR/vision, rclone, BookStack API, and Paperless API.
- Failure tests for interrupted writes, concurrent saves, cloud outage, BookStack outage, PaperParrot outage, corrupt sidecar, duplicate content, low disk, and database unavailability.
- Restore tests proving a file can be reconstructed from canonical object, sidecar, checksum, cloud manifest, and version chain.
- Reboot tests proving all Quadlet services return automatically under the `sjl` user.
- No completion claim without machine-readable test evidence and human-readable BookStack summary.

### 23.9 Claude Code Publication Transaction

```
change completed
  -> generate canonical Markdown/TXT source
  -> generate DOCX/PDF manual
  -> calculate SHA-256 and rename artifacts
  -> publish current manual/change page to BookStack
  -> ingest PDF/TXT/manifest into PaperParrot
  -> apply document type, PARA tags, version, DOCID, and retention metadata
  -> verify BookStack URL and PaperParrot document ID
  -> store both references in the change ledger and sidecar
```

### 23.10 Claude Code Acceptance Criteria

- The agent used the newest deployed VPS source rather than assuming uploaded files were current.
- Every modified file followed the naming convention or was explicitly exempted.
- Every content change created a version, diff, sidecar update, and registry event.
- Every stateful operation had a verified pre-change backup.
- Every deployed service passed health and restart checks.
- Every cloud mirror passed remote checksum verification.
- Every manual and architecture change was published to BookStack.
- Every final governed PDF/TXT record was archived to PaperParrot.
- The final BookStack entry contains implementation evidence, test results, Git commit, artifact hashes, and rollback instructions.

### 23.11 Final Claude Code Rule

Claude Code may design and execute controlled changes, but no change becomes canonical until FileWarden/registry state, Git history, backup evidence, service health, cloud checksum verification, BookStack publication, and PaperParrot archival all agree.
