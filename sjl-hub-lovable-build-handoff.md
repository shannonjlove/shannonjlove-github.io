# SJL Hub — Lovable Build & Configuration Handoff
**Project:** SJL Hub — Bidirectional Link Cluster Management UI  
**Domain:** `hub.shannonjlove.cloud`  
**Repo (post-export):** `shannonjlove/sjl-hub`  
**Date:** 2026-06-29  
**Version:** 1.0  
**Governing doc:** `CLAUDE.md` in `shannonjlove/shannonjlove-github.io`

---

## WHAT THIS DOCUMENT IS

This is the complete build and configuration handoff for generating SJL Hub using Lovable,
exporting it to GitHub, and deploying it to `hub.shannonjlove.cloud`. It covers:

- Why the app exists and what problem it solves
- The complete bidirectional linking system it must visualize
- Every screen spec for Sprint 1 (Lovable) and Sprint 2 (direct code)
- The full data model and API contracts
- The React Flow cluster graph specification
- The Universal Link resolver spec
- Deployment using Podman + systemd Quadlets (NOT Docker — see server constraints)
- The Lovable prompt, ready to paste
- Post-export integration steps

---

## 1. WHAT SJL HUB IS AND WHY IT EXISTS

### The Problem

Shannon manages files across **8 cloud services** organized into a **5-bucket PARA structure**
(Projects, Areas, Resources, Archives, Inbox). Every processed file gets 6 link types,
a permanent identity (DOCID / UUID24), and bidirectional connections to related files and
project hubs. This relational fabric lives in Raindrop.io as a webhook sink — but Raindrop
is a bookmark manager, not a relationship visualizer.

Raindrop cannot:
- Show which files are connected to which projects
- Render a visual cluster graph of bidirectional relationships
- Manage the @INBOX processing queue
- Serve as a Universal Link resolver (`/open?id=DOCID`)
- Display a cross-cloud PARA overview (40 folder tiles: 5 × 8 clouds)

**SJL Hub fills that gap.** It is the visual intelligence layer on top of HookVault + Raindrop.

### The Solution

A purpose-built React app generated in Lovable, exported to GitHub (`shannonjlove/sjl-hub`),
and self-hosted at `hub.shannonjlove.cloud`.

**Key principle — IP ownership:** Lovable generates standard React + TypeScript + Tailwind CSS +
shadcn/ui code. Export to GitHub immediately when the Sprint 1 core is stable. Deploy anywhere.
Cancel the Lovable subscription — the code is yours permanently. The Lovable subscription is
the scaffold, not the foundation.

### What the App Also Does

The domain `hub.shannonjlove.cloud` serves double duty:
1. **Cluster management UI** — visual dashboard for files, projects, and relationships
2. **Universal Link resolver** — `GET /open?id=[DOCID]` → 302 redirect to native cloud URL

Any file processed through HookVault gets a permanent Universal Link in the form:
```
https://hub.shannonjlove.cloud/open?id=[DOCID]
```
This link works from any app, any device, any context — because DOCID never changes,
even if the file is renamed, moved, or migrated to a different cloud.

---

## 2. THE BIDIRECTIONAL LINKING SYSTEM (What the App Must Render)

This is the core data model. Every screen in SJL Hub exists to visualize and navigate
these relationships. A future developer or Lovable agent must understand this before
writing a single line of code.

### The Six Link Types (Every File Has All Six)

| # | Type | Format | Purpose |
|---|---|---|---|
| 1 | **Native** | Cloud-native permanent share URL | Direct access to the file |
| 2 | **Clean** | Native URL stripped of `?utm_*`, `&ref=`, `&fbclid=` etc. | Shareable without tracking |
| 3 | **Universal** | `https://hub.shannonjlove.cloud/open?id=[DOCID]` | Works in any app, any context |
| 4 | **Markdown** | `[filename](clean-url)` | For embedding in docs, notes, Notion |
| 5 | **Deep** | `url#page=N` (PDF) or `url#t=Ns` (video) | Links inside the file, not just to it |
| 6 | **Search** | `hook://search?q=[DOCID]` | Finds file even if URL is dead |

### The Six Bidirectional Rules (What Creates Edges in the Graph)

**Rule 1 — File ↔ Project Hub**
- Every file in a project has a `hub_link` → the project's hub Raindrop entry
- The hub entry simultaneously lists this file in its `related_links` array
- Graph: file node → hub node (bidirectional edge)

**Rule 2 — File ↔ Sibling Files**
- All files in the same project share each other in `related_links`
- Maintained as a cluster — hub is source of truth for the sibling list
- Graph: file node → file node (for every sibling pair)

**Rule 3 — Webpage ↔ PDF**
- When a webpage is saved as PDF: PDF entry has `source_url` = original webpage
- Webpage Raindrop entry has `pdf_link` = PDF's cloud URL
- Both tagged `hook-linked-pair`
- Graph: document node → webpage node (bidirectional edge, distinct edge color)

**Rule 4 — File ↔ Folder**
- Every file's entry has `parent_folder_link` → its PARA folder's Raindrop entry
- Every PARA folder entry includes a count + list of files inside
- Graph: file node → folder node

**Rule 5 — Change ↔ Source File**
- Every CHANGES entry links back to the file that was changed
- The source file's entry is updated with `last_change_link`
- Graph: change node → file node (audit edge, dimmed by default)

**Rule 6 — Cross-Cloud Duplicates**
- If the same logical file exists on 2 clouds:
  - One designated `canonical` (highest fidelity)
  - Both entries link to each other with tag `cross-cloud-mirror`
- Graph: two file nodes connected by a mirror edge (dashed line)

### The Project Hub

Every active project has exactly **one hub entry** in Raindrop. The hub is the cluster anchor.

```
Hub entry fields:
  Title:      [Project-Name] HUB — [PARA_cloud]
  Link:       Raindrop self-link or cloud folder URL
  Excerpt:    Active project | [cloud] | Created: YYYY-MM-DD | Files: N
  Tags:       hub, project, [cloud], [project-slug], sjl
  Collection: @PROJECTS
  Note:       [list of all file Raindrop URLs in this project]
  Pinned:     YES (active projects are pinned)
```

Hub lifecycle:
- **Created:** when the project PARA folder is first set up in any cloud
- **Updated:** each time a file is added (file count incremented, link appended to Note)
- **Unpinned + moved:** when project is archived → hub moves to @ARCHIVES collection

### Permanent Identity

**DOCID** (current standard) — e.g. `SJL-CLOUD-0017` — is the permanent artifact identity.
Assigned once. Never changes. Registered in BookStack master allocation registry.

**UUID24** (legacy, still in CLAUDE.md pending revision) — `uuid4().hex[:24]` 24-char hex string.
The app must handle both formats during the transition period. Treat DOCID as authoritative
when both are present; fall back to UUID24 for older files.

**In either case:** The permanent identity is the primary key in the SJL Hub database.
Upsert on every incoming HookVault payload — never create duplicates.

---

## 3. TECH STACK

```
Frontend:    React 18 + TypeScript + Tailwind CSS + shadcn/ui
Routing:     React Router v6
Graph:       React Flow (cluster visualization — Sprint 2)
Search:      Fuse.js (client-side fuzzy search, Sprint 1) or Algolia (optional, later)
Data:        Raindrop.io REST API + HookVault internal REST API
Database:    SQLite (via better-sqlite3) for Hub's own payload store
Backend:     Express.js or Fastify (lightweight API server, Sprint 1)
Hosting:     hub.shannonjlove.cloud — nginx reverse proxy
Container:   Podman rootless + systemd Quadlet under sjl user (NOT Docker)
Repo:        shannonjlove/sjl-hub (export from Lovable immediately after Sprint 1)
Domain:      hub.shannonjlove.cloud
```

---

## 4. SPRINT 1 — LOVABLE BUILD SCOPE (Screens 1–5 + API)

Build these five screens and the Universal Link resolver in Lovable.
Use mock data for the initial build — wire real APIs after export.

---

### Screen 1 — DASHBOARD

**Route:** `/`

**Purpose:** Command center. At a glance: how many files processed, which clouds are
connected, what just happened, and what's sitting in @INBOX unprocessed.

**Components:**

```
┌─────────────────────────────────────────────────────────┐
│  SJL HUB                              [dark mode toggle] │
├─────────────────────────────────────────────────────────┤
│  QUICK STATS                                             │
│  [ Total Files: 847 ]  [ Active Projects: 23 ]          │
│  [ Inbox Unprocessed: 12 ]  [ Last Sync: 2m ago ]       │
├─────────────────────────────────────────────────────────┤
│  PARA OVERVIEW — 40 FOLDER TILES (5 × 8 clouds)         │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ...            │
│  │ PROJECTS │ │ PROJECTS │ │ PROJECTS │                  │
│  │  gDrive  │ │  pCloud  │ │  MEGA    │                  │
│  │  47 files│ │  12 files│ │  8 files │                  │
│  └──────────┘ └──────────┘ └──────────┘                  │
│  [ AREAS gDrive ] [ AREAS pCloud ] ...                   │
│  [ RESOURCES ... ] [ ARCHIVES ... ] [ INBOX ... ]        │
├─────────────────────────────────────────────────────────┤
│  RECENT ACTIVITY — last 20 HookVault events              │
│  2m  📄 Our-Time screenplay → RENAMED + HOOKED           │
│  14m 🗂 Built-For-This hub UPDATED (12 files now)        │
│  1h  📥 3 files arrived in @INBOX_gdrive                 │
├─────────────────────────────────────────────────────────┤
│  CLOUD HEALTH                                            │
│  ✓ gDrive  ✓ pCloud  ✓ Dropbox  ✗ MediaFire (error)    │
└─────────────────────────────────────────────────────────┘
```

**Data sources:**
- 40 folder tile counts: HookVault `/api/folders` endpoint or Raindrop FOLDERS collection
- Recent activity: HookVault `/api/events?limit=20`
- Cloud health: HookVault `/api/health/clouds`
- Quick stats: HookVault `/api/stats`

---

### Screen 2 — PROJECT HUB VIEW

**Route:** `/projects`

**Purpose:** All active project hubs at a glance. Pinned projects at top. Click any card
to drill into Project Detail.

**Components:**

```
┌─────────────────────────────────────────────────────────┐
│  ACTIVE PROJECTS (23)          [Search projects...]      │
│  [filter: cloud ▼] [filter: PARA ▼]                     │
├─────────────────────────────────────────────────────────┤
│  PINNED                                                  │
│  ┌─────────────────┐ ┌─────────────────┐               │
│  │ 📌 Our-Time      │ │ 📌 Built-For-This│               │
│  │ gDrive · 12 files│ │ gDrive · 8 files │               │
│  │ Last: 2m ago    │ │ Last: 1h ago    │               │
│  │ ●●●●○ cluster   │ │ ●●●○○ cluster   │               │
│  └─────────────────┘ └─────────────────┘               │
├─────────────────────────────────────────────────────────┤
│  ALL PROJECTS                                            │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐   │
│  │ Revelation-911│ │ TagBack      │ │ SJL-dotCom   │   │
│  │ gDrive · 5   │ │ gDrive · 31  │ │ gDrive · 7   │   │
│  └──────────────┘ └──────────────┘ └──────────────┘   │
└─────────────────────────────────────────────────────────┘
```

**Card fields:**
- Project name (from hub entry title)
- Cloud badge (gdrive, pcloud, mega, etc.)
- File count
- Last activity timestamp
- Cluster preview: dots representing files (up to 8 visible; "+N more")
- Pin status

**Data source:** Raindrop.io REST API — `@PROJECTS` collection, filtered by tag `hub`

---

### Screen 3 — PROJECT DETAIL

**Route:** `/projects/:projectSlug`

**Purpose:** Everything about one project. All files, all link types, all subfolders,
all related projects. This is the "file cluster" view for a single hub.

**Layout:**

```
┌─────────────────────────────────────────────────────────┐
│  ← Back to Projects                                      │
│  Our-Time_PROJECTS_gDrive              [Pin] [Archive]   │
│  Active · gDrive · 12 files · Created 2026-05-01        │
├─────────────────────────────────────────────────────────┤
│  SUBFOLDERS                                              │
│  📁 Our-Time-Promo/   📁 Our-Time-Pitch-Deck/           │
├─────────────────────────────────────────────────────────┤
│  FILES (12)                          [Sort ▼] [Filter ▼] │
│  ┌──────────────────────────────────────────────────┐   │
│  │ 2026-06-29_creative-film_our-time-screenplay_... │   │
│  │ gDrive · document-pdf · v1-0                    │   │
│  │                                                  │   │
│  │ 🔗 Native    [copy] https://drive.google.com/...│   │
│  │ 🧹 Clean     [copy] https://drive.google.com/...│   │
│  │ 🌐 Universal [copy] https://hub.sjl.../open?id= │   │
│  │ 📝 Markdown  [copy] [filename](url)             │   │
│  │ 🎯 Deep      [copy] https://...#page=1          │   │
│  │ 🔍 Search    [copy] hook://search?q=DOCID       │   │
│  │                                                  │   │
│  │ Siblings: [promo-cut.mov] [pitch-deck.pdf]      │   │
│  └──────────────────────────────────────────────────┘   │
│  [ + 11 more files... ]                                  │
├─────────────────────────────────────────────────────────┤
│  RELATED PROJECTS                                        │
│  Built-For-This_PROJECTS_gDrive                         │
├─────────────────────────────────────────────────────────┤
│  HUB RAINDROP ENTRY                                      │
│  Raindrop link: [open in Raindrop]                      │
└─────────────────────────────────────────────────────────┘
```

**Data source:**
- Hub metadata: Raindrop.io — the project's hub bookmark entry
- File list: HookVault `/api/files?project=[slug]`
- All 6 link types: stored in HookVault database per file

---

### Screen 4 — FILE DETAIL

**Route:** `/files/:docid`

**Purpose:** Everything about one file. All 6 links, one-click copy each. Full metadata.
All bidirectional connections — project hub + every sibling + folder.

**Layout:**

```
┌─────────────────────────────────────────────────────────┐
│  ← Our-Time_PROJECTS_gDrive                              │
│  2026-06-29_creative-film_our-time-screenplay_SJL-0017  │
├─────────────────────────────────────────────────────────┤
│  METADATA                                                │
│  Cloud: gDrive   PARA: Projects   Category: creative-film│
│  DOCID: SJL-CLOUD-0017   Version: v1-0                  │
│  Processed: 2026-06-29 14:30 UTC   By: filewarden        │
│  SHA8: 40d15da9                                          │
├─────────────────────────────────────────────────────────┤
│  ALL 6 LINKS                                             │
│  ┌─────────┬──────────────────────────────────┬──────┐  │
│  │ Native  │ https://drive.google.com/file/d/ │ Copy │  │
│  │ Clean   │ https://drive.google.com/file/d/ │ Copy │  │
│  │Universal│ https://hub.shannonjlove.cloud/  │ Copy │  │
│  │Markdown │ [filename](clean-url)            │ Copy │  │
│  │ Deep    │ https://...#page=1               │ Copy │  │
│  │ Search  │ hook://search?q=SJL-CLOUD-0017   │ Copy │  │
│  └─────────┴──────────────────────────────────┴──────┘  │
├─────────────────────────────────────────────────────────┤
│  BIDIRECTIONAL CONNECTIONS                               │
│  Project Hub → Our-Time_PROJECTS_gDrive [open]          │
│  Siblings:                                               │
│    • 2026-06-15_media-video_our-time-promo-cut_...mov   │
│    • 2026-05-01_document-pdf_our-time-pitch-deck_...pdf │
│  Parent Folder → @PROJECTS_gDrive [open]                 │
│  Last Change → CHANGES/2026-06-29_rename [open]          │
├─────────────────────────────────────────────────────────┤
│  PROCESSING HISTORY                                      │
│  2026-06-29 14:30  Renamed to SJL convention             │
│  2026-06-29 14:31  Hooked → Raindrop + SJL Hub          │
│  2026-06-29 14:32  Routed to @PROJECTS_gDrive            │
│  2026-06-29 14:33  Mirrored → iDrive E2                  │
└─────────────────────────────────────────────────────────┘
```

**Data source:**
- All metadata + links: HookVault `/api/files/:docid`
- Bidirectional connections: assembled from `hub_link`, `related_links`, `parent_folder_link`

---

### Screen 5 — UNIVERSAL LINK RESOLVER

**Route:** `GET /open?id=[DOCID]`  
**This is an API endpoint, not a UI screen.** It must be implemented as a server-side route.

**Behavior:**

```
Request:  GET /open?id=SJL-CLOUD-0017
          (or legacy: GET /open?id=a1b2c3d4e5f6a1b2c3d4e5f6)

Step 1:   Look up DOCID in HookVault SQLite database → get native_link
Step 2a:  If native_link exists → 302 redirect to native_link
Step 2b:  If native_link is null or 404 → show FALLBACK UI (see below)

FALLBACK UI (URL dead or file missing):
  Title: "Link requires update"
  Shows: last known filename, last known cloud, last known location
  Shows: search link → hook://search?q=DOCID
  Shows: Raindrop search link → https://raindrop.io/search/[DOCID]
  Action: [Open in Raindrop] [Copy Search Link]
```

**Implementation notes:**
- This MUST be server-side (not a client-side React route) — it needs to return HTTP 302
- Implement as an Express/Fastify middleware route before the React SPA is served
- DOCID and UUID24 both accepted — query handles both column lookups

---

## 5. SPRINT 2 — DIRECT CODE BUILD SCOPE (Screens 6–10)

These screens are built directly in code after Lovable export. Do NOT attempt in Lovable —
they require npm packages (React Flow, etc.) that are better wired post-export.

---

### Screen 6 — CLUSTER GRAPH

**Route:** `/graph`  
**Library:** `reactflow` (npm)

**Purpose:** Visual relationship map. Every file and project hub is a node. Every
bidirectional link is an edge. Click any node to navigate to its detail view.

**Node types:**

| Node Type | Visual | Size | Color |
|---|---|---|---|
| Project Hub | `◆` diamond | Large (60px) | Gold `#F59E0B` |
| File — gDrive | `●` circle | Medium (36px) | Blue `#3B82F6` |
| File — pCloud | `●` circle | Medium (36px) | Green `#10B981` |
| File — Dropbox | `●` circle | Medium (36px) | Purple `#8B5CF6` |
| File — MEGA | `●` circle | Medium (36px) | Red `#EF4444` |
| File — MediaFire | `●` circle | Medium (36px) | Orange `#F97316` |
| File — iCloud | `●` circle | Medium (36px) | Sky `#06B6D4` |
| File — sjlcloud | `●` circle | Medium (36px) | Slate `#64748B` |
| PARA Folder | `□` square | Small (28px) | Gray `#6B7280` |
| Webpage | `⬡` hexagon | Medium (36px) | Indigo `#6366F1` |

**Edge types:**

| Edge Type | Style | Label |
|---|---|---|
| File ↔ Hub (Rule 1) | Solid, thick | "in project" |
| File ↔ Sibling (Rule 2) | Solid, thin | "sibling" |
| Webpage ↔ PDF (Rule 3) | Dashed, colored | "archived from" |
| File ↔ Folder (Rule 4) | Dotted, thin | "in folder" |
| Change ↔ File (Rule 5) | Dimmed, dashed | "changed" |
| Cross-cloud mirror (Rule 6) | Dashed, double | "mirror" |

**Controls:**
- Filter panel: by cloud, by PARA bucket, by project, by link type
- Search box: highlight matching nodes, dim others
- Click node: flyout panel with name + all 6 links + [Go to Detail]
- Zoom + pan: React Flow built-in
- Layout: dagre or elk auto-layout (npm: `@dagrejs/dagre`)

**Data source:** HookVault `/api/graph` — returns nodes + edges JSON optimized for React Flow

```json
{
  "nodes": [
    {
      "id": "SJL-CLOUD-0017",
      "type": "file",
      "data": { "label": "our-time-screenplay", "cloud": "gdrive", "para": "projects" },
      "position": { "x": 0, "y": 0 }
    }
  ],
  "edges": [
    {
      "id": "SJL-0017--hub--Our-Time",
      "source": "SJL-CLOUD-0017",
      "target": "hub--Our-Time",
      "type": "file-hub",
      "animated": false
    }
  ]
}
```

---

### Screen 7 — INBOX QUEUE

**Route:** `/inbox`

**Purpose:** Every file sitting in any `@INBOX_[cloud]` folder, waiting to be processed.
Trigger rename, categorize, and route actions directly from this UI.

**Components:**
- Table: filename, cloud, arrived timestamp, size, detected type
- Row actions: [Rename] [Categorize] [Route to PARA] [Trash]
- Batch actions: [Rename All] [Route All] [Select All]
- Status badges: Pending / Processing / Hooked / Error

---

### Screen 8 — PARA NAVIGATOR

**Route:** `/navigator`

**Purpose:** Single tree view of all 8 clouds × 5 PARA buckets. Expand any folder to
see its files. Cross-cloud search by DOCID, filename, category, or project slug.

**Tree structure:**
```
▾ Google Drive
  ▾ @PROJECTS_gDrive (47 files)
    ▸ Our-Time_PROJECTS_gDrive (12)
    ▸ Built-For-This_PROJECTS_gDrive (8)
  ▸ @AREAS_gDrive (23 files)
  ▸ @RESOURCES_gDrive (91 files)
  ▸ @ARCHIVES_gDrive (134 files)
  ▸ @INBOX_gDrive (3 files)
▸ pCloud (...)
▸ Dropbox (...)
```

---

### Screen 9 — CHANGES LOG

**Route:** `/changes`

**Purpose:** Full audit trail. Every rename, move, version bump, migration, and
cloud-to-cloud transfer, filterable.

**Columns:** Timestamp · DOCID · Event type · Before · After · Cloud · Processed by

**Filters:** Date range, event type (rename/move/version/migrate), cloud, project

**Data source:** HookVault `/api/changes` + Raindrop CHANGES collection

---

### Screen 10 — SETTINGS

**Route:** `/settings`

**Sections:**
- Cloud Connections: API key/OAuth status per cloud (gDrive, pCloud, Dropbox, MEGA, MediaFire, iCloud)
- Raindrop.io: API key input + connection test
- HookVault: webhook endpoint URL + HOOKVAULT_SECRET (masked)
- SJL Hub Database: SQLite path, row count, last backup timestamp
- Sync: manual sync trigger, auto-sync interval

---

## 6. DATA MODEL — SJL HUB SQLITE DATABASE

Every incoming HookVault webhook payload is stored here. DOCID (or UUID24) is primary key.

```sql
CREATE TABLE files (
  docid           TEXT PRIMARY KEY,   -- e.g. SJL-CLOUD-0017 (or UUID24 for legacy)
  uuid24          TEXT,               -- legacy field; null for new files
  title           TEXT NOT NULL,
  native_link     TEXT,
  clean_link      TEXT,
  universal_link  TEXT,
  markdown_link   TEXT,
  deep_link       TEXT,
  search_link     TEXT,
  cloud           TEXT,               -- gdrive | pcloud | dropbox | mega | etc.
  para_bucket     TEXT,               -- projects | areas | resources | archives | inbox
  category        TEXT,               -- from SJL taxonomy
  subcategory     TEXT,
  project_slug    TEXT,
  hub_link        TEXT,               -- Raindrop URL of project hub
  related_links   TEXT,               -- JSON array of sibling file URLs
  parent_folder_link TEXT,
  source_url      TEXT,               -- if this is a PDF archived from a webpage
  is_hub          INTEGER DEFAULT 0,
  is_folder       INTEGER DEFAULT 0,
  is_duplicate_of TEXT,
  canonical       INTEGER DEFAULT 1,
  sha8            TEXT,               -- first 8 chars of SHA-256 content hash
  version         TEXT,               -- e.g. "v1-0"
  created         TEXT,               -- ISO 8601
  processed_by    TEXT,               -- filewarden | hookvault | manual
  last_updated    TEXT                -- ISO 8601, set on every upsert
);

CREATE TABLE events (
  id              INTEGER PRIMARY KEY AUTOINCREMENT,
  docid           TEXT,
  event_type      TEXT,               -- rename | route | hook | mirror | version | migrate
  detail          TEXT,               -- JSON blob with before/after
  cloud           TEXT,
  timestamp       TEXT
);

CREATE TABLE graph_edges (
  id              INTEGER PRIMARY KEY AUTOINCREMENT,
  source_docid    TEXT,
  target_docid    TEXT,
  edge_type       TEXT,               -- file-hub | sibling | webpage-pdf | file-folder | change | mirror
  created         TEXT,
  FOREIGN KEY(source_docid) REFERENCES files(docid) ON DELETE CASCADE,
  FOREIGN KEY(target_docid) REFERENCES files(docid) ON DELETE CASCADE
);
```

**Upsert rule:** On every incoming `POST /api/hook` payload:
1. Look up `docid` (or `uuid24` for legacy) in `files` table
2. If found: UPDATE in place; do NOT create new row
3. If not found: INSERT new row
4. Always update `graph_edges` to reflect current bidirectional state

---

## 7. HOOKVAULT API CONTRACT

### Incoming Webhook (HookVault → SJL Hub)

```
POST https://hub.shannonjlove.cloud/api/hook
Authorization: Bearer [HOOKVAULT_SECRET]
Content-Type: application/json
```

**Full payload:**
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
  "hub_link":           "[Raindrop URL of project hub, if applicable]",
  "related_links":      ["[sibling file Raindrop URLs]"],
  "parent_folder_link": "[Raindrop URL of parent PARA folder entry]",
  "source_url":         "[original webpage URL, if this is a saved PDF]",
  "uuid24":             "[24-char hex — legacy identity field]",
  "docid":              "[SJL-CLOUD-XXXX — current identity field]",
  "cloud":              "[gdrive | mediafire | pcloud | dropbox | dropbox-biz | mega | icloud | sjlcloud]",
  "para_bucket":        "[projects | areas | resources | archives | inbox]",
  "is_hub":             false,
  "is_folder":          false,
  "is_duplicate_of":    null,
  "canonical":          true,
  "sha8":               "[first 8 chars of SHA-256 of file content]",
  "version":            "v1-0",
  "created":            "YYYY-MM-DDTHH:MM:SSZ",
  "processed_by":       "filewarden | hookvault | manual"
}
```

### SJL Hub Internal API (consumed by React frontend)

```
GET  /api/stats                     → { total_files, active_projects, inbox_count }
GET  /api/files                     → paginated file list
GET  /api/files/:docid              → single file with all metadata
GET  /api/files?project=[slug]      → all files in a project
GET  /api/projects                  → all project hub entries
GET  /api/graph                     → nodes + edges for React Flow
GET  /api/folders                   → all 40 PARA folder entries (5 × 8 clouds)
GET  /api/events?limit=N            → recent HookVault events
GET  /api/changes                   → audit log
GET  /api/health/clouds             → cloud connection status per service
GET  /open?id=[DOCID]              → 302 redirect (Universal Link resolver)
POST /api/hook                      → receive HookVault webhook; upsert + fire graph update
```

### Raindrop.io REST API (read-only from Hub)

```
Base URL: https://api.raindrop.io/rest/v1
Auth:     Authorization: Bearer [RAINDROP_TEST_TOKEN]

GET /collections                          → all Raindrop collections (PARA buckets + FOLDERS)
GET /raindrops/:collectionId              → all bookmarks in a collection
GET /raindrop/:id                         → single bookmark
GET /raindrops/:collectionId?search=[q]   → search within collection
```

---

## 8. RAINDROP.IO COLLECTION STRUCTURE (What Hub Reads From)

```
RAINDROP.IO
|
+-- @PROJECTS        Active project hubs (pinned) + individual project files
|     tagged: hub (hubs), [project-slug] (all files per project)
|
+-- @AREAS           Ongoing area files and area folder entries
|
+-- @RESOURCES       Reference files, templates, assets, tools
|
+-- @ARCHIVES        Completed project hubs + historical files
|
+-- @INBOX           Unprocessed items awaiting routing
|
+-- CHANGES          Audit trail: every rename, move, version, migration
|
+-- FOLDERS          All 40 PARA folder entries (5 × 8 clouds)
|
+-- PAIRS            Bidirectionally linked pairs (webpage ↔ PDF, etc.)
|
+-- SEARCH-LINKS     hook://search entries for quick cross-cloud searches
```

Hub reads from Raindrop primarily for:
- Project hub metadata (Screen 2 cards — Raindrop @PROJECTS, tag `hub`)
- Folder tile counts (Screen 1 Dashboard — Raindrop FOLDERS collection)
- Audit trail (Screen 9 Changes Log — Raindrop CHANGES collection)

HookVault's SQLite database is the primary source for file-level detail and graph data.
Raindrop is the secondary source for human-managed metadata (project names, pin status, etc.).

---

## 9. DEPLOYMENT — PODMAN + SYSTEMD QUADLET

**Critical server constraint:** This server uses **rootless Podman + systemd Quadlets** under
the `sjl` user. Never Docker. Never root containers. Never `docker-compose`.

The CLAUDE.md Part 10 mentions `pm2` — that was written before the v7.3 governance doc
was incorporated. The authoritative standard is Podman Quadlets.

### Container Build

```dockerfile
# Containerfile (NOT Dockerfile)
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine AS runtime
WORKDIR /app
COPY --from=build /app/dist ./dist
COPY --from=build /app/server ./server
COPY package*.json ./
RUN npm ci --omit=dev
EXPOSE 3000
CMD ["node", "server/index.js"]
```

### Systemd Quadlet (under sjl user)

```ini
# /home/sjl/.config/containers/systemd/sjl-hub.container
[Unit]
Description=SJL Hub — Cluster Management UI
After=network-online.target

[Container]
Image=localhost/sjl-hub:latest
PublishPort=127.0.0.1:3000:3000
Volume=/home/sjl/data/sjl-hub:/app/data:Z
Environment=DATABASE_PATH=/app/data/hub.db
Environment=HOOKVAULT_SECRET_FILE=/run/secrets/hookvault_secret
Environment=RAINDROP_TOKEN_FILE=/run/secrets/raindrop_token
Secret=hookvault_secret,type=mount
Secret=raindrop_token,type=mount

[Service]
Restart=always

[Install]
WantedBy=default.target
```

```bash
# Enable and start
systemctl --user daemon-reload
systemctl --user enable --now sjl-hub
systemctl --user status sjl-hub
```

### nginx Reverse Proxy

```nginx
server {
    listen 443 ssl;
    server_name hub.shannonjlove.cloud;

    ssl_certificate     /etc/letsencrypt/live/hub.shannonjlove.cloud/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/hub.shannonjlove.cloud/privkey.pem;

    location / {
        proxy_pass         http://127.0.0.1:3000;
        proxy_set_header   Host $host;
        proxy_set_header   X-Real-IP $remote_addr;
        proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto $scheme;
    }
}
```

### Secrets Handling

Secrets are stored in `/opt/secrets` (root-only) or in Podman's secret store.
Never in environment variable files checked into git.
Never echoed in chat or documentation.

```bash
# Store secrets in Podman secret store
printf '%s' 'HOOKVAULT_SECRET_VALUE' | podman secret create hookvault_secret -
printf '%s' 'RAINDROP_TOKEN_VALUE'   | podman secret create raindrop_token -
```

---

## 10. SPRINT 1 — STEP-BY-STEP BUILD PLAN

### Phase A — Lovable Build (target: 3–5 days)

- [ ] Paste the Lovable Prompt (Section 11 below) into Lovable
- [ ] Review generated screens; iterate on layout and component details
- [ ] Confirm all 5 screens are present and router links work
- [ ] Confirm `/open?id=` resolver route is implemented server-side
- [ ] Verify mock data renders correctly across all screens
- [ ] Export to GitHub repo `shannonjlove/sjl-hub`
- [ ] Cancel Lovable subscription (code is exported and owned)

### Phase B — Post-Export Wiring (week 1 after export)

- [ ] Clone `shannonjlove/sjl-hub` locally
- [ ] Install `better-sqlite3` + create SQLite schema (Section 6 above)
- [ ] Wire `POST /api/hook` endpoint to upsert into SQLite
- [ ] Wire Raindrop.io REST API (read collections + bookmarks)
- [ ] Replace mock data with real API calls on all 5 screens
- [ ] Build the Express/Fastify server with all routes from Section 7
- [ ] Build Containerfile for rootless Podman
- [ ] Create systemd Quadlet file (Section 9 above)
- [ ] Deploy to `hub.shannonjlove.cloud` via Quadlet + nginx

### Phase C — HookVault Integration (week 2)

- [ ] Update HookVault to POST to `https://hub.shannonjlove.cloud/api/hook` on every file event
- [ ] Test Universal Link resolution with 5 real DOCID files
- [ ] Confirm upsert is idempotent (process same file twice → one DB row)
- [ ] Confirm bidirectional edges are written to `graph_edges` table correctly
- [ ] Verify 302 redirect works from `/open?id=SJL-CLOUD-0017`
- [ ] Verify fallback UI appears when DOCID not in database

---

## 11. SPRINT 2 — STEP-BY-STEP BUILD PLAN

### Phase D — React Flow Cluster Graph (week 3)

- [ ] `npm install reactflow @dagrejs/dagre`
- [ ] Build `/api/graph` endpoint → returns nodes + edges JSON
- [ ] Implement Screen 6 (Cluster Graph) with node types and edge types from Section 5
- [ ] Wire filter panel (by cloud, PARA, project)
- [ ] Wire node click → flyout panel with file detail
- [ ] Auto-layout with dagre

### Phase E — Inbox Queue (week 3)

- [ ] Build `/api/inbox` endpoint → returns unprocessed @INBOX files
- [ ] Implement Screen 7 (Inbox Queue)
- [ ] Wire [Rename] action → calls HookVault rename endpoint
- [ ] Wire [Route to PARA] action → calls HookVault route endpoint

### Phase F — PARA Navigator + Changes Log (week 4)

- [ ] Implement Screen 8 (PARA Navigator) — collapsible cloud tree
- [ ] Implement Screen 9 (Changes Log) from `events` table + Raindrop CHANGES
- [ ] Implement Screen 10 (Settings) — API key management

---

## 12. THE LOVABLE PROMPT (Ready to Paste)

Use this prompt verbatim when starting the Lovable build. Add or remove details
based on what Lovable asks for in follow-up prompts.

---

```
Build a file cluster management dashboard called "SJL Hub" for a personal cloud
file organization system. This is the visual intelligence layer that sits on top
of a webhook system called HookVault and a bookmark sync layer in Raindrop.io.

TECH STACK (non-negotiable):
- React 18 + TypeScript
- Tailwind CSS + shadcn/ui components
- React Router v6 (client-side routing)
- Dark mode by default (light mode optional toggle)
- Mobile-responsive layout

THE SYSTEM THIS APP MANAGES:
- 8 cloud services: Google Drive, MediaFire, pCloud, Dropbox (personal),
  Dropbox-biz (second account), MEGA, iCloud, and a personal server (sjlcloud)
- 5 PARA folders per cloud (Projects, Areas, Resources, Archives, Inbox)
  = 40 total folder tiles
- Every file has a DOCID permanent identity (e.g. SJL-CLOUD-0017) and 6 link types:
  Native, Clean, Universal, Markdown, Deep, Search
- Files belong to project clusters with bidirectional links to a project hub
  and to sibling files in the same project
- Universal Link resolver: GET /open?id=[DOCID] → 302 redirect to native cloud URL

BUILD THESE 5 SCREENS:

Screen 1 — DASHBOARD (route: /)
- Quick stats row: total files, active projects, inbox count, last sync time
- 40 folder tiles in a grid (5 PARA buckets × 8 clouds), each showing file count
  and a cloud badge (color-coded per cloud)
- Recent activity feed: last 20 events (rename, route, hook) with timestamps
- Cloud health row: green/red status indicator per cloud service

Screen 2 — PROJECT HUB VIEW (route: /projects)
- Card grid of all active project hubs
- Pinned projects appear first in a "Pinned" section
- Each card: project name, cloud badge, file count, last activity, cluster dot preview
- Search box to filter projects by name
- Click any card → navigate to Project Detail

Screen 3 — PROJECT DETAIL (route: /projects/:slug)
- Back button → Projects
- Project header: name, cloud, file count, created date
- Subfolder list (e.g. Our-Time-Promo/, Our-Time-Pitch-Deck/)
- File list: each file shows its filename + all 6 link types with one-click copy buttons
  Link types: Native, Clean, Universal, Markdown, Deep, Search
- Sibling file chips under each file
- Related projects section at bottom

Screen 4 — FILE DETAIL (route: /files/:docid)
- Back button → parent project
- File header: full filename, DOCID, cloud badge, version (e.g. v1-0), SHA8 hash
- Metadata row: category, subcategory, PARA bucket, processed timestamp
- Link table: 6 rows (one per link type) with the URL and a Copy button for each
- Bidirectional connections section:
  - Project hub link (with name and open button)
  - Sibling files list (with names and links)
  - Parent folder link
- Processing history timeline at bottom

Screen 5 — UNIVERSAL LINK RESOLVER (route/endpoint: GET /open?id=[DOCID])
This is a SERVER-SIDE route, not a React screen. It must:
- Accept GET /open?id=[DOCID] (also accept legacy UUID24 format)
- Look up DOCID in the Hub database → get the native_link
- If found: return HTTP 302 redirect to native_link
- If not found or URL dead: show a fallback React page with:
  "Link needs updating" message, last known filename, search link, and
  a button to search Raindrop.io for the file

DATA LAYER:
- All data from two APIs: Raindrop.io REST API (read collections/bookmarks)
  and HookVault internal REST API (file database, event log)
- Also accepts incoming webhooks: POST /api/hook with file payload
- Use realistic mock data for the initial build — real API wiring happens after export
- Hub stores all payloads in its own SQLite database (DOCID as primary key, upsert)

DESIGN PRINCIPLES:
- Dark mode by default
- Clean, minimal, information-dense (not sparse)
- Cloud badges are color-coded: gDrive=blue, pCloud=green, Dropbox=purple,
  MEGA=red, MediaFire=orange, iCloud=sky, sjlcloud=slate
- Copy buttons use a clipboard icon; flash green on successful copy
- Timestamps: relative for recent (2m ago), absolute for older (2026-06-29 14:30)
- Link type chips use emoji prefixes: 🔗 Native, 🧹 Clean, 🌐 Universal,
  📝 Markdown, 🎯 Deep, 🔍 Search
```

---

## 13. CONSTRAINTS AND RULES (Non-Negotiable)

These apply to every build decision, every config, every PR:

1. **No Docker.** Rootless Podman + systemd Quadlets only. Under the `sjl` user.
2. **No secrets in code or git.** Secrets via Podman secret store only. Never echo in chat.
3. **DOCID is the primary key.** Upsert, never insert duplicates. UUID24 accepted for legacy.
4. **The Universal Link resolver must be server-side.** A React client-side redirect cannot
   return HTTP 302 — it must be handled before the SPA is served.
5. **Bidirectional writes are atomic.** If updating file A to add sibling B, also update B
   to add A. If either write fails, roll both back.
6. **No mutations to the file corpus.** SJL Hub reads and displays. FileWarden writes.
   Hub never renames files, never moves files, never modifies cloud content.
7. **Export to GitHub immediately.** The moment Sprint 1 is stable in Lovable, export.
   The Lovable subscription must be cancellable without losing the app.
8. **Podman image build must use `Containerfile`, not `Dockerfile`.** The server's
   Podman install may not alias `Dockerfile` — use the canonical name.
9. **nginx config must include proper proxy headers** (`X-Real-IP`, `X-Forwarded-For`,
   `X-Forwarded-Proto`) so the Express server logs real client IPs.

---

## 14. POST-DEPLOYMENT VERIFICATION CHECKLIST

Before considering SJL Hub production-ready:

- [ ] `GET /open?id=SJL-CLOUD-0017` → returns 302 to the correct native Google Drive URL
- [ ] `GET /open?id=[dead-docid]` → returns fallback UI, not a 404 or error
- [ ] `POST /api/hook` with full HookVault payload → file appears in Dashboard activity feed
- [ ] Processing same DOCID twice → only one row in SQLite `files` table
- [ ] Project Hub card on Screen 2 shows correct file count after adding a new file via webhook
- [ ] All 6 copy buttons on File Detail → clipboard contains correct URL
- [ ] 40 folder tiles on Dashboard all render (even clouds with 0 files → show 0, not blank)
- [ ] Cloud health row reflects real API status, not mock data
- [ ] Podman container restarts automatically after `systemctl --user restart sjl-hub`
- [ ] nginx serves HTTPS correctly; HTTP → 301 redirect to HTTPS
- [ ] No secret values appear in any log, response body, or React component

---

*Governing document: `CLAUDE.md` in `shannonjlove/shannonjlove-github.io`*  
*Next session: CLAUDE.md Part 1 revision (six-digit code system + new canonical filename format)*
