# SJL Sovereign Cloud — Master Deployment To-Do
**Owner:** Shannon J. Love · sjlove@shannonjeffreylove.com  
**Repo:** `shannonjlove/shannonjlove-github.io`  
**Branch:** `claude/cloud-files-org-labels-2hgpzz`  
**Last updated:** 2026-06-29  
**TickTick sync:** Pending API access — import this file when token is available

> **Legend:** `[ ]` = pending · `[~]` = in progress · `[x]` = done · `[!]` = blocked

---

## SECTION A — CLAUDE.md REVISIONS
*Blocked until user gives explicit go-ahead. All reference material is in hand.*

- [ ] **A1** Revise Part 1 — replace legacy naming format with six-digit PARA code system
  - Remove: `YYYY-MM-DD_HH-MM_category-subcategory_description_UUID24.ext`
  - Replace with: `PPPPPP_YYYY-MM-DD__DOCID__semantic-title__vMAJOR-MINOR__sha8.ext`
  - Document all 6 field rules (double underscores, no HH-MM, DOCID not UUID4)
- [ ] **A2** Update all filename examples in Parts 1–12 (UUID24 → DOCID, single `_` → double `__`)
- [ ] **A3** Add server architecture section — two-node (Nexus + Oracle sOs), iDrive E2, ports
- [ ] **A4** Add 9-namespace filesystem tree (010000–090000 with QUARANTINE)
- [ ] **A5** Add 18-step FileWarden v2 pipeline (discover → stabilize → … → publish)
- [ ] **A6** Add canonical file bundle structure (`.sjl.json`, `.sha256`, `.sidecars/DOCID/`)
- [ ] **A7** Add integrity acceptance criteria (sha8 match, JSON valid, ≥3 link types, ≥1 mirror)
- [ ] **A8** Define and document C+SS digit allocations for all 9 namespaces
  - Requires: BookStack access (login) OR Shannon provides master registry table
- [ ] **A9** Replace all `pm2` deployment references with Podman Quadlet equivalents
- [ ] **A10** Add QUARANTINE routing rules (090000 branch: 09200 hash mismatch, 09400 mirror fail)

---

## SECTION B — GOOGLE DRIVE PHASE 1 CLEANUP
*All open questions resolved. Ready to execute once CLAUDE.md A-series is done.*

### B1 — Root PARA Bucket Renames (4 renames)
- [ ] `@PROJECTS_gdrive` → `@PROJECTS_gDrive`
- [ ] `@AREAS_gdrive` → `@AREAS_gDrive`
- [ ] `@RESOURCES_gdrive` → `@RESOURCES_gDrive`
- [ ] `@ARCHIVES_gdrive` → `@ARCHIVES_gDrive`

### B2 — Stray Root Folders → Move to PARA (8 moves)
- [ ] `SnAPPTrap` → `@PROJECTS_gDrive`
- [ ] `Google AI Studio` → `@RESOURCES_gDrive`
- [ ] `Collab Notebooks` → `@RESOURCES_gDrive`
- [ ] `Downloads` → `@INBOX_gDrive`
- [ ] `Saved from Chrome` (2026-06-07) → `@INBOX_gDrive`
- [ ] `Saved from Chrome` (2025-12-03) → merge into `@INBOX_gDrive` (deduplicate first)
- [ ] `Spent 2025` → `@ARCHIVES_gDrive`
- [ ] `meta-2026-Jan-05-04-14-56` → investigate → `@INBOX_gDrive`

### B3 — Stray Root Files → Move + Deduplicate (5 files)
- [ ] `NappyBoy Thank You` (Google Doc) → `@PROJECTS_gDrive/NappyBoy-Thank-You_PROJECTS_gDrive/`
- [ ] `NappyBoy Thank You.docx` → TRASH (Google Doc is canonical)
- [ ] `Revelation 9-1-1 Outline...` (Google Doc) → `@PROJECTS_gDrive/Revelation-911_PROJECTS_gDrive/`
- [ ] `Revelation 9-1-1 Outline...06102026.docx` → TRASH (duplicate export)
- [ ] `Austin apartment furniture` (Google Doc) → `@PROJECTS_gDrive/Austin-Apartment_PROJECTS_gDrive/`

### B4 — Project Folder Renames (40+ renames)
- [ ] `Austin apartment` → `Austin-Apartment_PROJECTS_gDrive`
- [ ] `Revelation 911` → `Revelation-911_PROJECTS_gDrive`
- [ ] `TGMGPYSM` → `Gay-Mans-Guide-Pleasing-Straight-Man_PROJECTS_gDrive`
- [ ] `Asha 2026 bday` → `Asha-2026-Birthday_PROJECTS_gDrive`
- [ ] `SJL Personal Server Cloud Project` → `SJL-Personal-Server_PROJECTS_gDrive`
- [ ] `Built For This_gDrive` → `Built-For-This_PROJECTS_gDrive`
- [ ] `CCC 2025 Welcodm` → `CCC-2025-Welcome_PROJECTS_gDrive` *(typo fixed)*
- [ ] `CCC Writing Room 2025` → `CCC-Writing-Room-2025_PROJECTS_gDrive`
- [ ] `CCC Welcome Team Scripts` → `CCC-Welcome-Team-Scripts_PROJECTS_gDrive`
- [ ] `CCC Reception 06242023` → `CCC-Reception-2023-06-24_PROJECTS_gDrive`
- [ ] `Crockettscience` → `Crockett-Science_PROJECTS_gDrive`
- [ ] `Filetagger` → `Filetagger_PROJECTS_gDrive`
- [ ] `53 anniversary` → `53rd-Anniversary_PROJECTS_gDrive`
- [ ] `Crockett Science B roll clips` → `Crockett-Science-Broll_PROJECTS_gDrive`
- [ ] `DFlat DEvans Music` → `DFlat-DEvans-Music_PROJECTS_gDrive`
- [ ] `Our Time` + `Our Time Adapation Project_Projects_gDrive` → merge → `Our-Time_PROJECTS_gDrive`
- [ ] `Our Time (Promo)` → move inside `Our-Time_PROJECTS_gDrive/Our-Time-Promo/`
- [ ] Create `Our-Time_PROJECTS_gDrive/Our-Time-Pitch-Deck/` subfolder
- [ ] `TagBack Project Folder` → `TagBack_PROJECTS_gDrive`
- [ ] `TV One Lawsuit_PROJECTS_gDRIVE` → `TV-One-Lawsuit_PROJECTS_gDrive`
- [ ] `Fathers Master Plan_Projects_gDrive` → `Fathers-Master-Plan_PROJECTS_gDrive`
- [ ] `Lord Of The Manners` → `Lord-Of-The-Manners_PROJECTS_gDrive`
- [ ] `Enoch Series` → `Enoch-Series_PROJECTS_gDrive`
- [ ] `Nicodemus Movie` → `Nicodemus-Movie_PROJECTS_gDrive`
- [ ] `Covid vaccination spots` → `Covid-Vaccination-Spots_PROJECTS_gDrive`
- [ ] `Content Clutter Stock Media` → `Content-Clutter-Stock-Media_PROJECTS_gDrive`
- [ ] `LoveYou Concert series Promotion Rebranding` → `LoveYou-Concert-Promo-Rebrand_PROJECTS_gDrive`
- [ ] `Mother dear nurse December 2025` → `Mother-Nurse-Dec-2025_PROJECTS_gDrive`
- [ ] `SPENT NBN (Net Worth)` → `SPENT-NBN-Net-Worth_PROJECTS_gDrive`
- [ ] `NET WORTH` → `Net-Worth_PROJECTS_gDrive`
- [ ] `SJL .com` → `SJL-dotCom_PROJECTS_gDrive`
- [ ] `WOMEN'S PROJECT` → `Womens-Project_PROJECTS_gDrive`
- [ ] `UNDERGROUND IN MIDTOWN OPEN MIC PROJECT` → `Underground-Midtown-Open-Mic_PROJECTS_gDrive`
- [ ] `HappyBirthdayAdrienneLove_Projects_gDrive` → `Happy-Birthday-Adrienne-Love_PROJECTS_gDrive`
- [ ] `Butter P's (candied nuts project)` → `Butter-Ps-Candied-Nuts_PROJECTS_gDrive`
- [ ] `For Ariel (ShannonJLove)` → `For-Ariel_PROJECTS_gDrive`
- [ ] `Amadaeus & Ashley` → `Amadaeus-And-Ashley_PROJECTS_gDrive`
- [ ] `Mom & Dad 50th Anniversary Pictures` → `Mom-Dad-50th-Anniversary_PROJECTS_gDrive`
- [ ] `Cinema 4D Projects 2025` → `Cinema-4D-2025_PROJECTS_gDrive`

### B5 — Archive Completed Projects (16 folders → @ARCHIVES_gDrive)
- [ ] `Love Family Portrait`
- [ ] `90s Girl Group Project`
- [ ] `Girls Cruise Files`
- [ ] `SJL Recordings`
- [ ] `SJL Songwriting Projects 2020`
- [ ] `SWV_IF_ONLY_YOU_KNEW`
- [ ] `AshaRuRu & SJL 2021 Writing Sessions`
- [ ] `Making Love Deck 2022`
- [ ] `Amadaeus & Ashley` *(after rename)*
- [ ] `For Ariel (ShannonJLove)` *(after rename)*
- [ ] `HappyBirthdayAdrienneLove_Projects_gDrive` *(after rename)*
- [ ] `CCC Reception 06242023` *(after rename)*
- [ ] `Mom & Dad 50th Anniversary Pictures` *(after rename)*
- [ ] `NET WORTH` *(after rename)*
- [ ] `UNDERGROUND IN MIDTOWN OPEN MIC PROJECT` *(after rename)*
- [ ] `WOMEN'S PROJECT` *(after rename)*

### B6 — @ARCHIVES_gDrive Fix
- [ ] `SJL_Produced_Content_RESOURCES_iDrive` → rename to `SJL-Produced-Content_ARCHIVES_gDrive`

### B7 — Raindrop.io gDrive Entries
- [ ] Create Raindrop entries for all 5 gDrive PARA folders → FOLDERS collection
- [ ] Create Project Hub entries for all active projects → @PROJECTS collection (pinned)

---

## SECTION C — DROPBOX PERSONAL CLEANUP
*Audit required first — need file listing with sizes before recommending modifications.*

- [ ] **C1** Export file listing from Dropbox personal web UI (CSV with sizes)
- [ ] **C2** Analyze listing — identify stray files, non-PARA folders, duplicates
- [ ] **C3** Create 5 PARA folders: `@INBOX_dropbox`, `@PROJECTS_dropbox`, `@AREAS_dropbox`, `@RESOURCES_dropbox`, `@ARCHIVES_dropbox`
- [ ] **C4** Move all existing folders into correct PARA bucket
- [ ] **C5** Apply SJL rename to all files (requires DOCID assignment from master registry)
- [ ] **C6** Trash duplicate exports (.docx when .gdoc exists, etc.)
- [ ] **C7** Create Raindrop entries for all 5 Dropbox folders → FOLDERS collection
- [ ] **C8** Wire HookVault to monitor Dropbox @INBOX and fire on new arrivals

---

## SECTION D — DROPBOX-BIZ CLEANUP (2nd Account)
*Audit required first — separate from personal account; label is `dropbox-biz`.*

- [ ] **D1** Export file listing from Dropbox-biz web UI (CSV with sizes)
- [ ] **D2** Cross-account deduplication check (files that exist in both accounts)
- [ ] **D3** Designate canonical copy for each cross-account duplicate; tag other `cross-cloud-mirror`
- [ ] **D4** Create 5 PARA folders: `@INBOX_dropbox-biz`, `@PROJECTS_dropbox-biz`, etc.
- [ ] **D5** Move all existing content into correct PARA bucket
- [ ] **D6** Apply SJL rename to all files
- [ ] **D7** Create Raindrop entries for all 5 Dropbox-biz folders → FOLDERS collection
- [ ] **D8** Wire HookVault to monitor Dropbox-biz @INBOX

---

## SECTION E — pCLOUD CLEANUP
*Audit required first — need file listing with sizes.*

- [ ] **E1** Export file listing from pCloud web UI or pCloud Drive desktop (CSV with sizes)
- [ ] **E2** Analyze listing — identify stray files, non-PARA folders, duplicates
- [ ] **E3** Create 5 PARA folders: `@INBOX_pcloud`, `@PROJECTS_pcloud`, `@AREAS_pcloud`, `@RESOURCES_pcloud`, `@ARCHIVES_pcloud`
- [ ] **E4** Move all existing content into correct PARA bucket
- [ ] **E5** Apply SJL rename to all files
- [ ] **E6** Create Raindrop entries for all 5 pCloud folders → FOLDERS collection
- [ ] **E7** Wire HookVault to monitor pCloud @INBOX

---

## SECTION F — REMAINING CLOUDS (Phases 2, 5, 6)
*Blocked until gDrive + Dropbox + pCloud are complete.*

### F1 — MediaFire (Phase 2)
- [ ] Audit existing structure
- [ ] Create 5 PARA folders
- [ ] Apply SJL rename (note: MediaFire compresses images — write XMP sidecar before upload)
- [ ] Create Raindrop entries for all 5 folders

### F2 — MEGA (Phase 5)
- [ ] Audit existing structure
- [ ] Create 5 PARA folders
- [ ] Apply SJL rename + hook all files
- [ ] Create Raindrop entries for all 5 folders

### F3 — iCloud Drive (Phase 6)
- [ ] Audit (manual or via Apple Shortcuts on iPhone)
- [ ] Create 5 PARA folders
- [ ] Apply SJL rename + hook all files
- [ ] Consider using iCloud Shortcuts to trigger HookVault webhooks on file events
- [ ] Create Raindrop entries for all 5 folders

---

## SECTION G — SERVER INFRASTRUCTURE (Nexus · hub.shannonjlove.cloud)
*Server: Hostinger x86_64 · Ubuntu 24.04 · 72.61.74.250 · 16 GB RAM · 193 GB disk*
*All containers: rootless Podman + systemd Quadlets under `sjl` user. NO Docker.*

- [ ] **G1** Verify Podman is installed and rootless for `sjl` user
  ```bash
  podman --version && podman info --format '{{.Host.Security.Rootless}}'
  ```
- [ ] **G2** Verify `/opt/secrets` exists and is root-only (`chmod 700`)
- [ ] **G3** Confirm listening ports are free: 8001 (TagBot), 2342 (PhotoPrism), 8000 (Paperless), 3000 (SJL Hub), 11434 (Ollama)
- [ ] **G4** Confirm nginx is installed and has wildcard SSL for `*.shannonjlove.cloud`
- [ ] **G5** Confirm iDrive E2 credentials are in `/opt/secrets` — bucket name + access key + secret key

---

## SECTION H — OLLAMA DEPLOYMENT
*Self-hosted LLM — replaces ALL Claude/Anthropic/OpenAI API calls in n8n. Zero token cost.*

- [ ] **H1** Install Ollama on Nexus
  ```bash
  curl -fsSL https://ollama.com/install.sh | sh
  ```
- [ ] **H2** Pull required models
  ```bash
  ollama pull phi3:mini          # TagBot synthesis (fast, 3 GB RAM)
  ollama pull mistral:7b         # n8n workflows (richer, 6 GB RAM)
  ollama pull nomic-embed-text   # SJL Hub semantic search (274 MB)
  ```
- [ ] **H3** Create Quadlet to keep Ollama running as `sjl` user service
- [ ] **H4** Test: `curl http://localhost:11434/api/tags` → confirm models listed
- [ ] **H5** In n8n: swap all Anthropic/OpenAI nodes → Ollama node (base URL: `http://localhost:11434`)
- [ ] **H6** Pull `llava:7b` only after GPU is added (too slow on CPU for production)

---

## SECTION I — PHOTOPRISM DEPLOYMENT
*Primary photo/video DAM. Domain: `photos.shannonjlove.cloud`. Port: 2342.*

- [ ] **I1** Create `/data/photoprism/{originals,storage,db}` directories under `sjl` user
- [ ] **I2** Create MariaDB Podman container (Quadlet) — `photoprism-db.container`
- [ ] **I3** Create PhotoPrism Podman container (Quadlet) — `photoprism.container`
  - Mount: `/data/inbox` → `/photoprism/import` (@INBOX_sjlcloud maps here)
  - Mount: `/data/photoprism/originals` → `/photoprism/originals`
  - Set: `PHOTOPRISM_DISABLE_EXIFTOOL=false` (keep ExifTool enabled)
- [ ] **I4** Add nginx vhost: `photos.shannonjlove.cloud` → port 2342
- [ ] **I5** First run: trigger PhotoPrism index scan via web UI
- [ ] **I6** Install PhotoSync on iPhone — configure to upload to `photos.shannonjlove.cloud`
- [ ] **I7** (Optional) Purchase PhotoPrism Plus ($25/yr) for GPS world map + vector search
- [ ] **I8** Test ExifTool integration: upload one photo → confirm all EXIF fields readable in UI

---

## SECTION J — PAPERLESS-NGX + PAPERLESS-GPT DEPLOYMENT
*Document DAM. Domain: `docs.shannonjlove.cloud`. Port: 8000.*

- [ ] **J1** Create `/data/paperless/{data,media,export,pgdata}` and `/data/inbox/documents/`
- [ ] **J2** Deploy Paperless-ngx stack (Podman Quadlets): paperless-ngx + Redis + Postgres + Tika + Gotenberg
- [ ] **J3** Deploy paperless-gpt companion container (Ollama integration)
  - Set: `LLM_PROVIDER=ollama`, `OLLAMA_HOST=http://host.docker.internal:11434`
  - Set: `LLM_MODEL=mistral:7b`, `AUTO_TAG_ENABLED=true`, `AUTO_TITLE_ENABLED=true`
- [ ] **J4** Add nginx vhost: `docs.shannonjlove.cloud` → port 8000
- [ ] **J5** Configure consume folder: `/data/inbox/documents/` → Paperless polls every 60s
- [ ] **J6** Install Paper Parrot on iPhone — configure server URL: `https://docs.shannonjlove.cloud`
- [ ] **J7** Test: drop a PDF into `/data/inbox/documents/` → confirm OCR + AI title appear in UI

---

## SECTION K — TAGBOT DEPLOYMENT
*ML auto-tagging service. Port: 8001 (localhost only). Called by FileWarden.*

- [ ] **K1** Create Python 3.11 venv: `/home/sjl/services/tagbot/`
- [ ] **K2** Install model packages (run once — downloads ~2.6 GB to HuggingFace cache):
  ```bash
  pip install transformers torch Pillow    # CLIP, BLIP
  pip install ultralytics                  # YOLOv8
  pip install faster-whisper               # audio/video transcription
  pip install scenedetect[opencv]          # video scene detection
  pip install marker-pdf                   # PDF → Markdown
  pip install pytesseract pdf2image        # scanned PDF OCR
  pip install mutagen                      # audio metadata
  pip install keybert sentence-transformers # keyword extraction
  pip install rawpy                        # RAW camera files
  pip install fastapi uvicorn              # API server
  pip install pyexiftool                   # EXIF read/write
  ```
- [ ] **K3** Write `tagbot.py` FastAPI service with ROUTERS dict (image/video/audio/pdf/document handlers)
- [ ] **K4** Implement CLIP + BLIP handlers (images — most common)
- [ ] **K5** Implement YOLOv8n handler
- [ ] **K6** Implement faster-whisper handler (video + audio)
- [ ] **K7** Implement Marker + KeyBERT handler (PDFs)
- [ ] **K8** Implement SQLite result cache (`/data/tagbot/cache.db` — hash → result)
- [ ] **K9** Create Quadlet: `tagbot.container` — port 8001, localhost only
- [ ] **K10** Test: `POST http://localhost:8001/tag` with a JPG → confirm JSON response with tags
- [ ] **K11** (Optional) Add DeepFace handler — opt-in per folder for personal photos only
- [ ] **K12** (GPU upgrade path) Pull `llava:7b` in Ollama → replace CLIP+BLIP with unified vision model

---

## SECTION L — FILEWARDEN DEPLOYMENT
*Watchdog automation. Monitors @INBOX. Calls TagBot → renames → HookVault → mirrors.*

- [ ] **L1** Write `filewarden.py` with 18-step pipeline
  1. discover, 2. stabilize, 3. identify, 4. analyze (TagBot), 5. version,
  6. diff, 7. rename, 8. sidecar, 9. hook, 10. mirror, 11. register, 12. publish
- [ ] **L2** Write `config.yaml` — inbox routing, categories, rename patterns, QUARANTINE rules
- [ ] **L3** Write `hookvault.py` — fires 20-field JSON payload to Raindrop + SJL Hub
- [ ] **L4** Implement QUARANTINE routing:
  - Unknown type → `090000` (QUARANTINE)
  - Hash mismatch → `09200`
  - Mirror failure → `09400`
- [ ] **L5** Create Quadlet: `filewarden.container` — mounts `/data/inbox` + `/data/photoprism/originals`
- [ ] **L6** Test: drop a JPG into `/data/inbox` → confirm file appears renamed in `@PROJECTS` with sidecar
- [ ] **L7** Test: drop a duplicate → confirm original preserved, duplicate flagged in QUARANTINE

---

## SECTION M — SJL HUB BUILD + DEPLOYMENT
*Cluster management UI + Universal Link resolver. Domain: `hub.shannonjlove.cloud`.*
*Full build spec: see `sjl-hub-lovable-build-handoff.md` in this repo.*

### M1 — Sprint 1: Lovable Build (target: 3–5 days)
- [ ] Paste Lovable prompt from `sjl-hub-lovable-build-handoff.md` Section 11
- [ ] Generate app (Screens 1–5 + `/open` resolver)
- [ ] Iterate on layout until all 5 screens are correct
- [ ] Export to GitHub repo `shannonjlove/sjl-hub`
- [ ] Cancel Lovable subscription

### M2 — Sprint 1: Post-Export Wiring
- [ ] Install `better-sqlite3` + create SQLite schema (DOCID primary key, upsert)
- [ ] Wire `POST /api/hook` → upsert into SQLite
- [ ] Wire Raindrop.io REST API reads (collections + bookmarks)
- [ ] Replace mock data with real API calls
- [ ] Build Containerfile (rootless Podman compatible)
- [ ] Create Quadlet: `sjl-hub.container` — port 3000
- [ ] Add nginx vhost: `hub.shannonjlove.cloud` → port 3000
- [ ] Wire HookVault to `POST https://hub.shannonjlove.cloud/api/hook`

### M3 — Sprint 1: Verification
- [ ] `GET /open?id=[real-DOCID]` → 302 to correct cloud URL
- [ ] `POST /api/hook` → file appears in Dashboard feed
- [ ] Same DOCID twice → one DB row (upsert works)
- [ ] All 40 folder tiles render on Dashboard
- [ ] All 6 copy buttons work on File Detail

### M4 — Sprint 2: Power Features (post-Lovable, direct code)
- [ ] React Flow cluster graph (Screen 6) — nodes + edges + filter panel
- [ ] Inbox Queue (Screen 7) — trigger rename/route from UI
- [ ] PARA Navigator cross-cloud tree (Screen 8)
- [ ] Changes Log (Screen 9)
- [ ] Settings (Screen 10) — API key management

---

## SECTION N — RAINDROP.IO SETUP
*Universal link hub. All files and folders must have Raindrop entries.*

- [ ] **N1** Create all 9 Raindrop collections: @PROJECTS, @AREAS, @RESOURCES, @ARCHIVES, @INBOX, CHANGES, FOLDERS, PAIRS, SEARCH-LINKS
- [ ] **N2** Create all 40 mandatory folder entries (5 PARA × 8 clouds) → FOLDERS collection
- [ ] **N3** Create Project Hub entries for all active gDrive projects → @PROJECTS (pinned)
- [ ] **N4** Configure Raindrop API token → store in `/opt/secrets/raindrop_token`
- [ ] **N5** Test HookVault → Raindrop: process one file end-to-end → confirm bookmark appears

---

## SECTION O — iDRIVE E2 OBJECT STORAGE SETUP
*S3-compatible. All mirrors land here. Bucket layout: `bucket/PARA/subarea/DOCID/`.*

- [ ] **O1** Confirm iDrive E2 bucket exists and credentials are in `/opt/secrets`
- [ ] **O2** Create bucket folder structure (PARA prefixes: `projects/`, `areas/`, `resources/`, `archives/`)
- [ ] **O3** Install `rclone` or `boto3` on Nexus for S3 operations
- [ ] **O4** Configure FileWarden mirror step (Step 10) to push to iDrive E2
- [ ] **O5** Test: process one file → confirm it appears in `bucket/projects/[subarea]/[DOCID]/current/`
- [ ] **O6** Implement post-upload integrity verification (sha8 matches remote file sha256)

---

## SECTION P — DEVONTHINK SERVER ACCESS (Mac-hosted)
*Mac-only. MCP server with ~60 commands. Web server for WebTop browser access.*

- [ ] **P1** Confirm a Mac is available to run DEVONthink Server continuously
- [ ] **P2** Enable DEVONthink Server web server (Settings → AI → MCP)
- [ ] **P3** Set up nginx tunnel on Nexus: `devonthink.shannonjlove.cloud` → Mac:8080 via VPN
- [ ] **P4** Connect DEVONthink MCP server to Claude Code sessions (MCP tool config)
- [ ] **P5** Wire Hazel/Hookmark → HookVault for bidirectional DEVONthink ↔ Raindrop linking

---

## SECTION Q — TICKTICK INTEGRATION
*Sync this to-do list to TickTick once API access is established.*

- [ ] **Q1** Obtain TickTick API token (OAuth or personal access token from TickTick developer settings)
- [ ] **Q2** Add TickTick MCP server to Claude Code session config OR use TickTick's REST API directly
- [ ] **Q3** Import this file — create one TickTick task per checklist item above
- [ ] **Q4** Map sections A–P to TickTick projects/lists (e.g. "CLAUDE.md", "gDrive Cleanup", "Server Deploy")
- [ ] **Q5** Set priorities: Section A (urgent) · Sections B–E (high) · Sections G–P (medium) · Section F (low)
- [ ] **Q6** Maintain sync — when a Claude Code session completes tasks, update TickTick

---

## SECTION R — FUTURE / POST-MIGRATION
*Do not start until all clouds are clean and all services are deployed.*

- [ ] **R1** S3 Migration — move canonical files from all 8 clouds to S3/iDrive E2
  - All PARA folders must be clean and SJL-named before migration
  - S3 key prefix mirrors PARA: `projects/` · `areas/` · `resources/` · `archives/`
  - SJL canonical names carry over unchanged (no rename at migration)
- [ ] **R2** GPU upgrade — add RTX 3060 12GB or better to Nexus
  - Unlocks: LLaVA:7b (5s/image vs 120s), Whisper medium real-time, BLIP-2 practical
- [ ] **R3** Nominatim deployment — street-level GPS reverse geocoding (opt-in)
  - `docker pull mediagis/nominatim:4.4` → note: use Podman, not Docker
  - Import Texas OSM data (~10 GB) for Austin-area files
- [ ] **R4** BookStack — export CLAUDE.md → BookStack as structured documentation
- [ ] **R5** DiffForge deployment — `diff.shannonjlove.cloud`

---

## DEPENDENCY ORDER (What Blocks What)

```
A (CLAUDE.md revision)
  └─ blocks B (gDrive cleanup — files must conform to new naming)
       └─ blocks N (Raindrop setup — needs clean filenames)

G (Server infrastructure check)
  └─ blocks H (Ollama)
       └─ blocks K (TagBot — uses Ollama for synthesis)
            └─ blocks L (FileWarden — calls TagBot)
  └─ blocks I (PhotoPrism)
  └─ blocks J (Paperless-ngx)
  └─ blocks M (SJL Hub)

M (SJL Hub deployed)
  └─ blocks L's hook step (FileWarden → SJL Hub endpoint live)

O (iDrive E2 setup)
  └─ blocks L's mirror step (FileWarden mirror target)

Q1 (TickTick API token)
  └─ blocks Q2–Q6 (all TickTick sync steps)

All of B, C, D, E, F (all clouds clean)
  └─ blocks R1 (S3 migration)
```

---

## QUICK COUNTS

| Section | Items | Status |
|---|---|---|
| A — CLAUDE.md Revisions | 10 | Blocked (needs go-ahead) |
| B — Google Drive Phase 1 | 50+ | Ready to execute |
| C — Dropbox Personal | 8 | Audit first |
| D — Dropbox-Biz | 8 | Audit first |
| E — pCloud | 7 | Audit first |
| F — MediaFire/MEGA/iCloud | 12 | After B–E done |
| G — Server Infrastructure | 5 | Check first |
| H — Ollama | 6 | After G |
| I — PhotoPrism | 8 | After G |
| J — Paperless-ngx | 7 | After G + H |
| K — TagBot | 12 | After G + H |
| L — FileWarden | 7 | After K |
| M — SJL Hub | 18 | Start anytime (Lovable sprint) |
| N — Raindrop.io | 5 | After B |
| O — iDrive E2 | 6 | After G |
| P — DEVONthink | 5 | Requires Mac |
| Q — TickTick | 6 | Needs API token |
| R — Future | 5 | Last |
| **TOTAL** | **185+** | |

---

*To import into TickTick: provide API token in next session → Claude Code will create tasks programmatically.*  
*Governing doc: `CLAUDE.md` in `shannonjlove/shannonjlove-github.io`*
