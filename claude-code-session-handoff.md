# SJL Sovereign Cloud — Claude Code Session Handoff
**Session ID:** e29562c1-a916-5db1-9e54-5ff08e0baeb2  
**Branch:** `claude/cloud-files-org-labels-2hgpzz`  
**Repo:** `shannonjlove/shannonjlove-github.io`  
**Date:** 2026-06-29  
**Handoff version:** 1.0

---

## CRITICAL RULE — READ FIRST

This session governs the `CLAUDE.md` file in the root of `shannonjlove/shannonjlove-github.io`. `CLAUDE.md` is the **single governing knowledge base** for all SJL file operations. No file is created, renamed, moved, uploaded, or migrated without following the rules in `CLAUDE.md`. All agents must read it in full before taking any action.

---

## 1. System Identity

| Field | Value |
|---|---|
| Owner | Shannon J. Love |
| Email | sjlove@shannonjeffreylove.com |
| Primary domain | shannonjlove.cloud |
| Secondary domain | shannonjeffreylove.com |
| Primary VPS (Nexus) | Hostinger x86_64 · IP: 72.61.74.250 |
| Private worker (sOs) | Oracle Cloud ARM64 via Tailscale (`oracle-sos`) |
| OS | Ubuntu 24.04.x · Linux 6.8.0-124-generic x86_64 |
| Storage | 193 GB total · 97 GB used · 96 GB free (as of 2026-06-19) |
| RAM | 15 GiB total · ~10 GiB available |
| Container standard | Rootless Podman + systemd Quadlets under `sjl` user |
| Object storage | iDrive E2 (S3-compatible) |
| Listening ports | 8766, 8797, 8777 (localhost), 8811 (localhost) |

---

## 2. Domain Map

| Subdomain | Service |
|---|---|
| `bookstack.shannonjlove.cloud` | BookStack (knowledge, manuals, change history) |
| `docs.shannonjlove.cloud` | Paperless-ngx / PaperParrot |
| `n8n.shannonjlove.cloud` | n8n automation |
| `mcp.shannonjlove.cloud` | MCP gateway |
| `github-mcp.shannonjlove.cloud` | GitHub MCP |
| `oracle-mcp.shannonjlove.cloud` | Oracle MCP bridge |
| `hooks.shannonjlove.cloud` | HookVault |
| `hub.shannonjlove.cloud` | SJL Hub cluster UI + Universal Link resolver |
| `diff.shannonjlove.cloud` | DiffForge |
| `photos.shannonjlove.cloud` | PhotoPrism (photo/video DAM) |
| `private.shannonjlove.cloud` | Private media boundary |
| `status.shannonjlove.cloud` | Status / monitoring |
| `filetagger.cloud` | FileTagger product domain |
| `productionbinder.app` | ProductionBinder product domain |

---

## 3. The Six-Digit SJL PARA Code System

**Source document:** `070000_20260628__SJLPARAMETHODOLOGY__sixdigitcodesystemllmhandoff__v10.pdf`

### Structure: `[P][C][SS][NN]`

| Position | Width | Meaning |
|---|---|---|
| P | 1 digit | PARA namespace prefix (always `0` for SJL Sovereign Cloud) |
| C | 1 digit | Root namespace / lifecycle bucket (1–9) |
| SS | 2 digits | Subcategory / functional subdivision (00–99) |
| NN | 2 digits | Local sequence within P+C+SS branch (00–99) |

### Root Namespace Table

| Code | Namespace | Purpose |
|---|---|---|
| `010000` | INBOX | Unprocessed intake and temporary capture |
| `020000` | PROJECTS | Finite outcomes, productions, deliverables, active initiatives |
| `030000` | AREAS | Ongoing responsibilities, operations, maintained domains |
| `040000` | RESOURCES | Reference knowledge, reusable material, research |
| `050000` | ARCHIVES | Inactive, superseded, completed, retained historical material |
| `060000` | PRIVATE MEDIA | Restricted personal or sensitive media isolated by policy |
| `070000` | SYSTEM AUTOMATION | Infrastructure, scripts, agents, governance, technical operations |
| `080000` | APPLICATION DATA | App-owned state, exports, configurations, managed datasets |
| `090000` | QUARANTINE | Untrusted, incomplete, conflicting, failed, or review-required material |

### Reading a Code — Example: `076000`

```
P  C  S  S  N  N
0  7  6  0  0  0
│  │  └──┘  └──┘
│  │    │     └── Local sequence: 00
│  │    └──────── Subcategory: 60
│  └───────────── Namespace: 07 = SYSTEM AUTOMATION
└──────────────── Prefix: 0 (SJL Sovereign Cloud)
```

Result: System Automation · subcategory 60 · sequence 00.

### Legacy Migration Table

| Legacy (5-digit) | Current (6-digit) | Treatment |
|---|---|---|
| `01000` | `010000` | Zero-pad, preserve alias |
| `02000` | `020000` | Zero-pad, preserve alias |
| `07000` | `070000` | Zero-pad, preserve alias |
| `76000` | `076000` | Map through registry; do not reinterpret |
| `09000` | `090000` | Zero-pad, preserve alias |

### Governance Rules (non-negotiable)
- Every governed filename and folder begins with **exactly six numeric characters**.
- New work uses six digits; five-digit codes remain as migration aliases only.
- No LLM or automation may invent a new code — resolve through the controlled master allocation registry and BookStack.
- Classification changes do **not** change DOCID.
- Uncertain classification → route to `090000` QUARANTINE.
- Bulk renames require: mapping table + rollback plan + provenance log + post-migration validation.

### LLM Pre-Assignment Checklist (7 questions)
1. Which PARA lifecycle bucket owns this artifact?
2. Which registered category applies inside that bucket?
3. Which two-digit subcategory is already allocated?
4. Is NN a parent reservation, existing leaf, or new allocation requiring approval?
5. Does the artifact already have a legacy five-digit alias?
6. What permanent DOCID must be preserved?
7. Is classification authoritative, or should item go to QUARANTINE for review?

---

## 4. Canonical Filename Format

### Current (6-digit, from `v10.pdf` — 28 June 2026 onward)

```
PPPPPP_YYYY-MM-DD__DOCID__semantic-title__vMAJOR-MINOR__sha8.ext
```

| Field | Function | Rule |
|---|---|---|
| `PPPPPP` | Six-digit PARA code | First field, always present |
| `YYYY-MM-DD` | Canonical creation or issue date | ISO 8601, never MM-DD-YY |
| `DOCID` | Permanent artifact identity | Never changes; assigned once |
| `semantic-title` | Human-readable description | OCR-, vision-, or user-derived |
| `vMAJOR-MINOR` | Revision state | Increments on content change |
| `sha8` | First 8 chars of SHA-256 | Content integrity; not a version |
| `ext` | Lowercase extension | Always lowercase |

**Example:**
```
070000_2026-06-28__SJL-PARA-METHODOLOGY__six-digit-code-system-llm-handoff__v1-0__pending.docx
```

**Field separator:** double underscore `__` between PPPPPP/date/DOCID/title/version/sha8.  
**Intra-field separator:** single hyphen `-`.

### Prior Format (v7.3 DOCX, 5-digit era — reference only)

```
PPPPP_YYYY-MM-DD__DOCID__semantic-title__vMAJOR-MINOR__sha8.ext
```
Five-digit codes remain as provenance aliases. Do not silently rewrite them.

### What CLAUDE.md Currently Has (NEEDS REVISION)

```
YYYY-MM-DD_HH-MM_category-subcategory_description_UUID24.ext
```

This is **outdated**. The CLAUDE.md revision must replace it with the six-digit format above. Key differences to reconcile:
- `UUID24` (Python `uuid4().hex[:24]`) → replaced by `DOCID` (assigned once, never from UUID4)
- `HH-MM` time → removed from filename (not in canonical format)
- Single underscores → double underscores as field separators
- Six-digit code at front → missing entirely from CLAUDE.md currently
- `sha8` (SHA-256 first 8 chars) → new field, not in CLAUDE.md
- `vMAJOR-MINOR` version → new field, not in CLAUDE.md

---

## 5. DOCID vs UUID24 — Critical Distinction

| Property | DOCID | UUID24 (old) |
|---|---|---|
| Source | Assigned by governance system (e.g. `SJL-CLOUD-0017`) | Python `uuid4().hex[:24]` |
| Changes? | Never | Never |
| Purpose | Permanent artifact identity | Permanent artifact identity |
| Format | Registry-assigned slug or sequential ID | 24-char hex |
| Stored in | Sidecar JSON, registry, embedded metadata | Filename, Raindrop |
| **Status** | **Canonical going forward** | **Legacy — superseded** |

---

## 6. The v7.3 File Governance Doctrine (DOCX Key Points)

**Source document:** `07000_20260619__SJLCLOUDFILEGOVERNANCE__persistentmetadataclaudecodemanualwithserversnapshot__v73__40d15da9.docx`

### FileWarden v2 Pipeline (18 steps)
```
discover → stabilize → identify → analyze → version → diff → rename →
sidecar → hook → mirror → register → publish
```

Required native actions:
`stabilize_write` · `calculate_hash` · `assign_docid` · `extract_metadata` · `run_ocr` · `run_vision` · `classify_para` · `snapshot_previous` · `increment_version` · `generate_diff` · `canonical_rename` · `write_embedded_metadata` · `write_xattrs` · `write_sidecar` · `register_hook` · `mirror_object` · `verify_remote_checksum` · `update_registry` · `update_bookstack` · `archive_paperparrot` · `quarantine`

### FileWarden Approved Scope (watched paths)
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

### Canonical File Bundle (per file)
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

### Canonical Filesystem Tree (`/srv/sjl/`)
```
/srv/sjl/
├── 01000_INBOX/
│   ├── 01100_DEVICE-INTAKE/
│   ├── 01200_EMAIL-INTAKE/
│   ├── 01300_PAPERLESS-CONSUME/
│   ├── 01400_N8N-OUTPUT/
│   └── 01900_REVIEW-REQUIRED/
├── 02000_PROJECTS/
│   ├── 02100_FILETAGGER/
│   ├── 02200_PRODUCTIONBINDER/
│   ├── 02300_CREATIVE-PROJECTS/
│   └── 02400_CLOUD-ARCHITECTURE/
├── 03000_AREAS/
│   ├── 03100_BUSINESS/
│   ├── 03200_LEGAL/
│   ├── 03300_CLOUD-OPERATIONS/
│   └── 03400_MEDIA-OPERATIONS/
├── 04000_RESOURCES/
│   ├── 04100_DOCUMENTS/
│   ├── 04200_IMAGES/
│   ├── 04300_VIDEO/
│   ├── 04400_AUDIO/
│   └── 04500_RESEARCH/
├── 05000_ARCHIVES/
│   ├── 05100_COMPLETED-PROJECTS/
│   ├── 05200_RETIRED-SYSTEMS/
│   └── 05300_HISTORICAL-MANUALS/
├── 06000_PRIVATE-MEDIA/
│   ├── 06100_STASH/
│   └── 06200_RESTRICTED-DOCUMENTS/
├── 07000_SYSTEM-AUTOMATION/
│   ├── 07100_FILEWARDEN/
│   ├── 07200_HOOK-SCRIPTS/
│   ├── 07300_DIFF-SCRIPTS/
│   ├── 07400_MIRROR-REGISTRY/
│   ├── 07500_BOOKSTACK-AUTOMATION/
│   ├── 07600_OCR-VISION/
│   ├── 07700_DEVICE-INTAKE/
│   ├── 07800_MIGRATION/
│   └── 07900_AGENT-CONTEXT/          ← CLAUDE.md lives here
├── 08000_APPLICATION-DATA/
│   ├── 08100_BOOKSTACK-EXPORTS/
│   ├── 08200_PAPERLESS-EXPORTS/
│   ├── 08300_N8N-EXPORTS/
│   └── 08400_MCP-REGISTRY/
└── 09000_QUARANTINE/
    ├── 09100_MISSING-SIDECAR/
    ├── 09200_HASH-MISMATCH/
    ├── 09300_METADATA-CONFLICT/
    ├── 09400_MIRROR-FAILURE/
    └── 09500_VERSION-CHAIN-ERROR/
```

### Object Storage Layout (iDrive E2)
```
bucket/PARA/subarea/DOCID/current/
bucket/PARA/subarea/DOCID/versions/
bucket/PARA/subarea/DOCID/metadata/
bucket/PARA/subarea/DOCID/manifests/
```

### Version Numbering
- `v1-0` = initial ingestion
- `v1-1` = first content modification
- `v2-0` = intentional major revision
- Content edits → increment version
- Metadata-only changes → metadata event only (version may not increment)
- Prior version preserved before replacement; version chain must be complete

### Persistent Metadata Layers
| Layer | Purpose |
|---|---|
| Canonical filename | Human-readable minimum recovery data — always present |
| Embedded metadata | Portable inside supported formats — write when safe |
| Extended attributes (xattrs) | Fast local lookup — reconstructable |
| Sidecar JSON | Complete portable file-level record — mandatory |
| Central registry | Current state, paths, versions, links, provenance — authoritative |
| Cloud object metadata | Off-device recovery and integrity verification — mandatory for mirrors |

### Integrity Acceptance Criteria (16 checks)
- [ ] Canonical file exists
- [ ] Filename hash matches file content
- [ ] Sidecar exists and validates against schema
- [ ] Sidecar digest matches registry
- [ ] Embedded DOCID matches sidecar
- [ ] Extended-attribute DOCID matches sidecar (where xattrs supported)
- [ ] Registry version matches filename version
- [ ] Cloud object and associated metadata exist
- [ ] Remote checksum matches local digest
- [ ] Mirror manifest is current
- [ ] Version chain is complete and unbroken
- [ ] Hook ID resolves to current canonical path
- [ ] BookStack publication status recorded
- [ ] PaperParrot archival status recorded

---

## 7. PARA Structure — Cloud vs Server

### Cloud Services (8 clouds — PARA applied to folder names)

| Cloud | Tag | Inbox | Projects | Areas | Resources | Archives |
|---|---|---|---|---|---|---|
| Google Drive | `gdrive` | `@INBOX_gDrive` | `@PROJECTS_gDrive` | `@AREAS_gDrive` | `@RESOURCES_gDrive` | `@ARCHIVES_gDrive` |
| MediaFire | `mediafire` | `@INBOX_mediafire` | `@PROJECTS_mediafire` | `@AREAS_mediafire` | `@RESOURCES_mediafire` | `@ARCHIVES_mediafire` |
| pCloud | `pcloud` | `@INBOX_pcloud` | `@PROJECTS_pcloud` | `@AREAS_pcloud` | `@RESOURCES_pcloud` | `@ARCHIVES_pcloud` |
| Dropbox (personal) | `dropbox` | `@INBOX_dropbox` | `@PROJECTS_dropbox` | `@AREAS_dropbox` | `@RESOURCES_dropbox` | `@ARCHIVES_dropbox` |
| Dropbox (business) | `dropbox-biz` | `@INBOX_dropbox-biz` | `@PROJECTS_dropbox-biz` | `@AREAS_dropbox-biz` | `@RESOURCES_dropbox-biz` | `@ARCHIVES_dropbox-biz` |
| MEGA | `mega` | `@INBOX_mega` | `@PROJECTS_mega` | `@AREAS_mega` | `@RESOURCES_mega` | `@ARCHIVES_mega` |
| iCloud | `icloud` | `@INBOX_icloud` | `@PROJECTS_icloud` | `@AREAS_icloud` | `@RESOURCES_icloud` | `@ARCHIVES_icloud` |
| shannonjlove.cloud | `sjlcloud` | `@INBOX` | `@PROJECTS` | `@AREAS` | `@RESOURCES` | `@ARCHIVES` |

### Server (`/srv/sjl/`) — 9 namespaces (includes Private Media, System Automation, App Data, Quarantine)

See canonical filesystem tree in Section 6 above.

---

## 8. Tool Stack

| Tool | Location | Status | Purpose |
|---|---|---|---|
| `filewarden.py` | `07100_FILEWARDEN/` | TARGET | Watchdog: auto-rename + auto-hook (18-step pipeline) |
| `hookvault.py` | `07200_HOOK-SCRIPTS/` | TARGET | Webhook manager → Raindrop + SJL Hub |
| `tagbot.py` | `shannonjlove.cloud:8001` | TARGET | FastAPI media recognition (CLIP+BLIP+YOLO+Whisper+KeyBERT) |
| `diffforge.py` | `07300_DIFF-SCRIPTS/` | TARGET | Automatic diff generation per file type |
| Raindrop.io | Cloud | ACTIVE | Universal link browser / HookVault navigation hub |
| SJL Hub | `hub.shannonjlove.cloud` | TARGET | React app: cluster UI + Universal Link resolver (`/open?id=DOCID`) |
| n8n | `n8n.shannonjlove.cloud` | DOCUMENTED | Automation platform; Anthropic/OpenAI nodes → Ollama |
| Ollama | `shannonjlove.cloud:11434` | DOCUMENTED | Self-hosted LLM: phi3:mini (TagBot), mistral:7b (n8n), nomic-embed-text |
| PhotoPrism | `photos.shannonjlove.cloud` | DOCUMENTED | Photo/video DAM — Docker + MariaDB — ExifTool built-in |
| ExifTool | CLI on server | DOCUMENTED | EXIF/XMP/IPTC write-back; SJL XMP namespace |
| Nominatim | `shannonjlove.cloud:8088` | DOCUMENTED | Self-hosted OSM reverse geocoding |
| Paperless-ngx | `docs.shannonjlove.cloud` | DOCUMENTED | Document DAM — OCR + AI tagging |
| paperless-gpt | Sidecar container | DOCUMENTED | Ollama-powered vision OCR for difficult scans |
| Paper Parrot | iOS app — paperparrot.me | INSTALL | Mobile companion to Paperless-ngx |
| PhotoSync | iOS app (owned) | INSTALL | Mobile photo upload to PhotoPrism |
| DEVONthink Server | Mac-hosted (lifetime license) | DOCUMENTED | Knowledge management + MCP server (4.3, ~60 commands) |
| BookStack | `bookstack.shannonjlove.cloud` | ACTIVE (auth required) | Human-readable methodology, change history, rationale |
| iDrive E2 | S3-compatible cloud | DOCUMENTED | Object storage: PARA buckets + sidecars + version history |

---

## 9. HookVault Webhook Payload (20+ fields)

```json
{
  "title":              "PPPPPP_YYYY-MM-DD__DOCID__semantic-title__vMAJOR-MINOR__sha8.ext",
  "link":               "https://[clean-cloud-native-url]",
  "universal_link":     "https://hub.shannonjlove.cloud/open?id=[DOCID]",
  "markdown_link":      "[title](clean-url)",
  "deep_link":          "https://[url]#[anchor-if-applicable]",
  "search_link":        "hook://search?q=[DOCID]",
  "excerpt":            "Cloud: [cloud] | PARA: [bucket] | Project: [name] | Cat: [cat-subcat]",
  "collection":         "[PARA bucket name]",
  "tags":               ["sjl", "[cloud]", "[category]", "[subcategory]", "[para-bucket]", "[project-slug]"],
  "hub_link":           "[Raindrop URL of project hub]",
  "related_links":      ["[sibling file URLs in same project cluster]"],
  "parent_folder_link": "[Raindrop URL of parent PARA folder entry]",
  "source_url":         "[original webpage URL if this is a saved PDF]",
  "uuid24":             "[legacy field — now DOCID]",
  "cloud":              "[gdrive|mediafire|pcloud|dropbox|dropbox-biz|mega|icloud|sjlcloud]",
  "para_bucket":        "[projects|areas|resources|archives|inbox]",
  "is_hub":             false,
  "is_folder":          false,
  "canonical":          true,
  "created":            "YYYY-MM-DDTHH:MM:SSZ",
  "processed_by":       "filewarden|hookvault|manual"
}
```

---

## 10. TagBot Service (FastAPI, port 8001)

**POST** `http://localhost:8001/tag`

```json
{
  "file_path": "/data/inbox/IMG_4821.jpg",
  "file_type": "image",
  "hints": {"project": "Our-Time", "cloud": "gdrive"}
}
```

Response includes: `suggested_description`, `caption`, `tags[]`, `category`, `subcategory`, `category_confidence`, `objects_detected`, `transcript`, `keywords`, `processing_time_ms`, `models_used`.

**Model stack (CPU-only):**
- Images: CLIP ViT-B/32 + BLIP-base + YOLOv8n + DeepFace (opt-in)
- Video: PySceneDetect + CLIP + YOLOv8n per frame + faster-whisper small
- Audio: mutagen + faster-whisper small
- PDF (digital): Marker + KeyBERT
- PDF (scanned): Tesseract 5 + KeyBERT
- Synthesis: Ollama phi3:mini
- RAM budget: ~4.2 GB models + ~3.0 GB Ollama + system = 16 GB server recommended

---

## 11. Google Drive Phase 1 Cleanup Queue

**All open questions resolved:**
- `Our Time` → `Our-Time_PROJECTS_gDrive` (parent); Promo + Pitch Deck as subfolders ✓
- Dropbox account 2 → `dropbox-biz` ✓
- `TGMGPYSM` → `Gay-Mans-Guide-Pleasing-Straight-Man_PROJECTS_gDrive` ✓ *(The Gay Man's Guide to Pleasing Your Straight Man by Shannon J. Love & Rachael Figueroa)*

**PARA root renames needed:**
- `@PROJECTS_gdrive` → `@PROJECTS_gDrive`
- `@AREAS_gdrive` → `@AREAS_gDrive`
- `@RESOURCES_gdrive` → `@RESOURCES_gDrive`
- `@ARCHIVES_gdrive` → `@ARCHIVES_gDrive`

**40+ project folder renames and 16 archive moves** — full list in CLAUDE.md Part 6.

---

## 12. Current CLAUDE.md State

**Location:** `/home/user/shannonjlove-github.io/CLAUDE.md`  
**Parts:** 12 (Parts 1–12 complete)  
**Last commit:** `7e8cc86` — Resolve TGMGPYSM  
**Branch:** `claude/cloud-files-org-labels-2hgpzz`

### What CLAUDE.md Has (correct)
- Parts 3–12: HookVault, PARA, SJL Hub, TagBot, PhotoPrism, ExifTool, GPS, Paperless-ngx, DEVONthink, Paper Parrot (resolved)
- Google Drive audit queue (Part 6) — all open questions resolved
- Tool stack (Part 8) — complete
- Project identity (Part 9) — complete

### What CLAUDE.md Needs (PENDING REVISION — awaiting user go-ahead)

1. **Part 1 — Naming Convention** — entire master format must be replaced:
   - Old: `YYYY-MM-DD_HH-MM_category-subcategory_description_UUID24.ext`
   - New: `PPPPPP_YYYY-MM-DD__DOCID__semantic-title__vMAJOR-MINOR__sha8.ext`
   - Add: six-digit code table (9 namespaces, SS/NN allocation rules)
   - Add: DOCID vs UUID24 distinction
   - Add: SHA8 field (first 8 chars of SHA-256)
   - Add: version numbering (vMAJOR-MINOR)
   - Add: double-underscore field separators
   - Remove: HH-MM time from filename
   - Remove: UUID24 as primary identity mechanism

2. **Part 2 — File Processing Workflow** — update to match 18-step FileWarden v2 pipeline

3. **New Part (or Part 1 addition) — Server Architecture** — add:
   - Nexus (Hostinger) + Oracle sOs two-node architecture
   - `/srv/sjl/` canonical filesystem tree (9 namespaces)
   - iDrive E2 object storage layout
   - Canonical file bundle structure (file + sidecar + sha256 + ocr + vision + diffs)
   - 16-point integrity acceptance criteria

4. **Update Part 7 — Migration Plan** — Phase 7 is S3; update to iDrive E2

5. **Update throughout** — all filename examples must gain the six-digit prefix

---

## 13. Unresolved Issues

| Issue | Status | Action needed |
|---|---|---|
| CLAUDE.md Part 1 revision | PENDING | Awaiting user go-ahead + old naming convention manual review complete |
| BookStack access | Requires auth | `bookstack.shannonjlove.cloud` — login needed to retrieve master allocation registry |
| Master allocation registry | Not yet built | C and SS digit allocations for each namespace need to be defined and registered |
| Google Drive Phase 1 execution | Not started | Awaiting CLAUDE.md revision completion |
| TagBot build | Not started | Implement FastAPI service with ML handlers |
| PhotoPrism deployment | Not started | Docker deploy at photos.shannonjlove.cloud |
| Paperless-ngx deployment | Not started | Docker deploy at docs.shannonjlove.cloud |
| Ollama deployment | Not started | Install + pull models on shannonjlove.cloud |
| SJL Hub Sprint 1 | Not started | Lovable build → export → self-host |
| DEVONthink Server setup | Not started | Mac mini + nginx tunnel + MCP enable |

---

## 14. Files Modified This Session

| File | Action | Commit |
|---|---|---|
| `CLAUDE.md` | Part 10 (SJL Hub) added | `0d1202f` |
| `CLAUDE.md` | Part 11 (TagBot) added | `a3b1bb5`, `2e22dcb` |
| `CLAUDE.md` | EXIF/GPS/PhotoPrism added to Part 11 | `49ebef6` |
| `CLAUDE.md` | PhotoPrism swap from Immich, RAM budget | `744a8a5` |
| `CLAUDE.md` | Part 12 (Document Intelligence) added | `e07f1ba` |
| `CLAUDE.md` | Paper Parrot resolved (paperparrot.me) | `1e955c3` |
| `CLAUDE.md` | TGMGPYSM resolved | `7e8cc86` |

---

## 15. Key Decisions Made This Session

1. **PhotoPrism over Immich** — more granular metadata (EXIF+XMP+IPTC+YAML sidecars), ExifTool built-in
2. **NeoFinder ruled out** — macOS/iOS only; replaced by PhotoPrism + ExifTool
3. **Ollama replaces all Claude/OpenAI API calls** in n8n — zero token cost
4. **SJL Hub on Lovable** over Wiki.js — purpose-built for HookVault data model; export to GitHub after build, cancel Lovable
5. **Paper Parrot** = iOS companion to Paperless-ngx (not standalone) — mirrors PhotoSync/PhotoPrism relationship
6. **Paperless-ngx + paperless-gpt** = primary document DAM (Docker, WebTop-native)
7. **DEVONthink Server** = knowledge layer only (Mac mini required); MCP server 4.3 enables Claude Code queries
8. **iDrive E2** = object storage for mirrors (S3-compatible)
9. **Rootless Podman + systemd Quadlets** = container standard (never Docker)
10. **Six-digit PARA code** supersedes five-digit; `[P][C][SS][NN]` at front of every filename
11. **DOCID** supersedes UUID24 as permanent file identity

---

## 16. Next Actions (in order)

1. **Receive user go-ahead** → revise CLAUDE.md Part 1 (naming convention) with six-digit system
2. **Update all filename examples** in CLAUDE.md (Parts 1–12) to use `PPPPPP_` prefix
3. **Add server architecture** (Nexus + Oracle + iDrive E2) to CLAUDE.md
4. **Define C and SS allocations** for each of the 9 namespaces in master registry
5. **Execute Google Drive Phase 1** using Pipedream Google Drive MCP tools
6. **Deploy Ollama** on shannonjlove.cloud; pull phi3:mini, mistral:7b, nomic-embed-text
7. **Deploy PhotoPrism** (Docker + MariaDB) at photos.shannonjlove.cloud
8. **Deploy Paperless-ngx + paperless-gpt** at docs.shannonjlove.cloud
9. **Build TagBot** FastAPI service on shannonjlove.cloud:8001
10. **Build SJL Hub Sprint 1** in Lovable; export to `shannonjlove/sjl-hub`

---

## 17. Methodology in One Sentence (from v10.pdf)

> Classify visibly, identify permanently, version explicitly, verify cryptographically, register authoritatively, document the rationale, and preserve every prior state.
