# SJL Infrastructure — Claude Code Knowledge Base

This file gives Claude persistent context about Shannon Jeffrey Love's infrastructure,
tools, conventions, and the reference software each SJL tool emulates.
Every session starts from this baseline.

---

## Owner

**Shannon Jeffrey Love** — `sjlove@shannonjeffreylove.com`  
GitHub: `shannonjlove`  
Primary domain: `shannonjlove.cloud`  
Admin panel: `admin.shannonjlove.cloud`

---

## Nexus VPS (Hostinger, Ubuntu 24.04)

| Item | Value |
|---|---|
| Host | Nexus (Hostinger VPS) |
| OS | Ubuntu 24.04 |
| Container runtime | Rootless Podman + systemd quadlets |
| Quadlet dir | `~/.config/containers/systemd/` |
| Internal network | `sjl-infra.network` |
| Access | Tailscale IPs: `100.115.66.75`, `100.67.229.94` |
| Reverse proxy | Nginx Proxy Manager (NPM) on port `:81` |

Services are **rootless Podman containers** managed by **systemd quadlets** (`*.container`
files in `~/.config/containers/systemd/`). After adding or changing a quadlet:

```bash
systemctl --user daemon-reload
systemctl --user enable --now <service-name>
```

---

## SJL File Tools — Production v1.0.0

Three Python microservices stored in `tools/sjl-file-tools/`.  
Checksum: `fd374d5ac914192de693c76e8ee205645e7bdba8ef5822bc7572dd5175d1d410`
(file: `sjl-file-tools-production-v1.0.0.tar.gz`)

Each tool is a headless Linux/VPS equivalent of a macOS productivity app.
Understanding the reference app is essential for extending any SJL tool correctly.

---

## 1. FileWarden — emulates Hazel (Noodlesoft)

**Reference:** https://www.noodlesoft.com/manual/hazel/hazel-overview/

### What Hazel Does

Hazel is a macOS folder-watching automation app — "your personal housekeeper."
It monitors user-selected folders and applies rule-based actions to files as they arrive
or change. Rules match files by attribute conditions and then execute ordered actions.

#### Hazel: Complete Condition Attributes

| Attribute | Type | Operators available |
|---|---|---|
| `Name` | text | contains, does not contain, is, is not, starts with, ends with, matches pattern, does not match pattern |
| `Extension` | text | is, is not, contains, does not contain, matches pattern |
| `Full Name` | text | same as Name |
| `Date Added` | date | is, is not, is before, is after, is in range, is in the last N days/weeks |
| `Date Created` | date | same as Date Added |
| `Date Last Modified` | date | same as Date Added |
| `Date Last Opened` | date | same as Date Added |
| `Date Last Matched` | date | same as Date Added |
| `Current Time` | date | is before, is after, is between |
| `Kind` | list | is, is not (Document, Folder, Image, Movie, Music, PDF, Application, Archive, Other…) |
| `Tags` | tag list | contains tags, does not contain tags, match, do not match |
| `Color Label` | label | is, is not |
| `Comment` | text | contains, does not contain, is, is not, matches pattern |
| `Size` | number | is, is not, is greater than, is less than, is in range (bytes/KB/MB/GB) |
| `Locked` | boolean | is locked, is not locked |
| `Contents` | text | contain, do not contain, contain match, do not contain match, is blank, is not blank |
| `Source URL` | text | same as Name operators (for downloaded files) |
| `Subfolder Depth` | number | is, is not, greater than, less than |
| `Sub-file Count` | number | is, is not, greater than, less than |
| `Any File` | universal | matches everything (no conditions needed) |
| `Passes AppleScript` | script | custom boolean script |
| `Passes JavaScript` | script | custom boolean script |
| `Passes Shell Script` | script | custom boolean script returning exit 0/1 |
| Spotlight metadata | any | via "Other…" picker — size on disk, pixel dimensions, camera model, GPS, author, etc. |

Operators vary by type: text uses containment/pattern, dates use temporal comparison,
numbers use numeric comparison, booleans use is/is not.

**Match patterns** support `?` (any char), `*` (any sequence), `[abc]` (character class).
**Nested conditions** allow AND/OR groups within a rule.

#### Hazel: Complete Action List

| Action | What it does |
|---|---|
| `Move` | Relocate file to folder; options: rename duplicates, replace, discard, trash |
| `Copy` | Duplicate to folder; subsequent actions apply to the copy |
| `Rename` | Change name using token patterns (date, counter, Spotlight attributes) |
| `Sort into subfolder` | Move into auto-created subfolder using pattern; supports multi-level paths |
| `Sync` | One-way copy of items added since last run |
| `Archive` | Compress to ZIP; subsequent actions apply to the archive |
| `Unarchive` | Decompress; subsequent actions apply to contents |
| `Add tags` | Apply static or metadata-derived tags |
| `Remove tags` | Remove specific or all tags |
| `Set color label` | Assign Finder color label |
| `Add comment` | Write to Spotlight comment field |
| `Toggle extension` | Show or hide file extension |
| `Toggle lock` | Lock or unlock file |
| `Open` | Open with default or specified app; optionally bring to front |
| `Show in Finder` | Reveal file in Finder |
| `Make alias` | Create alias at specified location |
| `Import into Music` | Add to Music library |
| `Import into Photos` | Add to Photos library |
| `Import into TV` | Add to TV app |
| `Upload` | Transfer via FTP, SFTP, or WebDAV |
| `Run Shortcut` | Execute an Apple Shortcuts workflow |
| `Run AppleScript` | Execute custom AppleScript; file exposed as variable |
| `Run JavaScript` | Execute JavaScript for Automation (JXA) |
| `Run Automator workflow` | Run an Automator workflow |
| `Run shell script` | Execute any shell command/script |
| `Run rules on folder contents` | Apply full rule list to all items inside a matched folder |
| `Continue matching rules` | Don't stop at this rule; keep evaluating subsequent ones |
| `Display notification` | Show macOS notification with optional sound and token patterns |
| `Pause` | Wait N seconds/minutes before next action |
| `Ignore` | Mark file as processed; block it from further rule matching |

**Token patterns** in Rename/Sort: `%date_added%`, `%extension%`, `%name%`, `%counter%`,
plus any Spotlight metadata attribute.

**Trash management (Hazel-specific):**
- Auto-delete items from Trash after N days or when Trash exceeds N GB
- **App Sweep:** when an `.app` is trashed, Hazel identifies orphaned support files
  (preferences, caches, Application Support folders) and offers to remove them

### What FileWarden Implements (SJL)

**Key files:**
- `tools/sjl-file-tools/filewarden.py` — main daemon
- `tools/sjl-file-tools/config.yaml` — PARA watch rules
- `tools/sjl-file-tools/Containerfile.filewarden`
- `tools/sjl-file-tools/quadlets/filewarden.container`
- `tools/sjl-file-tools/requirements-filewarden.txt`

**Deps:** `watchdog==4.0.1`, `pyyaml==6.0.1`, `click==8.1.7`

**Run:**
```bash
pip install watchdog pyyaml click
python filewarden.py --config /etc/filewarden/config.yaml
python filewarden.py --config config.yaml --dry-run --verbose
```

**Container image:** `localhost/filewarden:latest` (no exposed port — daemon only)

**Currently implemented condition attributes:**
- `extension` — file extension (operator: `is`, `is_not`, `contains`, `greater_than`, `less_than`, `matches_regex`)
- `size_mb` — file size in MB
- `name` — file stem (no extension)
- `stem` — alias for name

**Currently implemented actions:**
- `sjl_rename` — rename to SJL convention: `YYYY-MM-DD--{category}--{subcategory}--{slug}.{ext}`
- `mkdir_move` — create `{base}/{subdir_pattern}` and move file there
- `move` — move to destination directory
- `log` — write formatted message to log
- `run_script` — execute shell script with env vars `FW_FILE`, `FW_NAME`, `FW_EXT`

**SJL rename convention:**
```
YYYY-MM-DD--{category}--{subcategory}--{original-slug}.{ext}
```
Example: `invoice.pdf` → `2026-06-26--document--pdf--invoice.pdf`

**Config structure:**
```yaml
watches:
  - path: /data/inbox
    enabled: true
    recursive: false
    delay_seconds: 2        # settle time before processing
    rules:
      - name: "Rule description"
        enabled: true
        match: all           # all | any
        conditions:
          - attribute: extension
            operator: is     # is | is_not | contains | greater_than | less_than | matches_regex
            value: pdf
        actions:
          - type: sjl_rename
            params:
              category: document
              subcategory: pdf
          - type: mkdir_move
            params:
              base: /data/documents
              subdir_pattern: "{year}/{month}"
        stop_processing: true
```

**Volume layout on Nexus:**
```
/opt/filewarden/config.yaml → /etc/filewarden/config.yaml (ro)
/var/log/filewarden         → /var/log/filewarden
/var/lib/filewarden         → /var/lib/filewarden
/data/inbox                 → /data/inbox
/data/documents             → /data/documents
/data/media                 → /data/media
/data/downloads             → /data/downloads
/data/tagback               → /data/tagback
/data/unsorted              → /data/unsorted
```

**Production watched paths:**
- `/data/inbox` — sort all incoming; 2s settle; routes by extension to PARA locations
- `/data/downloads` — warn log on files >500 MB
- `/data/tagback/incoming` — sjl_rename + call n8n TagBack ingest webhook

**Hazel features NOT yet in FileWarden (future work):**
- Date-based conditions (Date Added, Date Modified, Date Created)
- Kind/type detection beyond extension (MIME type)
- File contents search
- Tags and labels (no Finder on Linux, but extended attributes possible)
- Nested condition groups (AND inside OR)
- Copy, Archive/Unarchive, Sync actions
- Notification action
- Sort into subfolder with Hazel-style token patterns (`%date%`, `%counter%`)
- Trash management and App Sweep equivalents

---

## 2. HookVault — emulates Hookmark (hookproductivity.com)

**Reference:** https://hookproductivity.com/

### What Hookmark Does

Hookmark is a macOS productivity app that creates and manages **bidirectional contextual
links** between any digital resources — files, web pages, emails, tasks, notes, PDFs,
videos. The core idea: instead of searching for related documents, you hook them together
once and navigate between them instantly.

#### Linkable Resource Types in Hookmark

- Files and folders (via file paths; links survive rename and move)
- Web pages and URLs
- Emails (Apple Mail, Airmail, MailMate, Mimestream, Missive, Mailplane, Postbox, Spark)
- Tasks (OmniFocus, Things, Reminders, etc.)
- Notes (DEVONthink, Keep It, Evernote, Craft, Drafts, Obsidian, etc.)
- PDF text selections (deep link to exact highlighted text)
- Video timestamps (QuickTime — links open at exact time)
- Apple Photos items
- Items in any app that implements the Hookmark API

#### Hookmark: URL Scheme

Hookmark uses the `hook://` custom URL scheme:

```
hook://file/<percent-encoded-posix-path>     # file by path
hook://search/<encoded-query>                # triggers Spotlight search
https://hookmark.net/<wrapped-url>           # Universal Link (web-shareable)
```

Deep links use the app's own URL scheme (e.g., `devonthink://`, `omnifocus://`)
wrapped with Hookmark's bookmark system.

#### Hookmark: CLI (hookapp by ttscoff)

```bash
hook link|ln SOURCE... TARGET          # bidirectional hook between files/URLs
hook link --all SOURCE1 SOURCE2 ...    # link every item to every other
hook link --paste TARGET               # link clipboard URL to TARGET
hook list|ls FILE_OR_URL               # list all hooks on an item
hook list -o hooks|paths|markdown|verbose
hook find|search STRING                # search all bookmarks by title/path/URL
hook find --files-only                 # only return file paths
hook clip|cp FILE_OR_URL               # bookmark and copy its hook:// URL
hook clip --markdown                   # copy as Markdown link
hook clone SOURCE TARGET               # copy all hooks from one item to another
hook remove|rm FILE_OR_URL             # remove connections
hook remove --all                      # remove all hooks on item
hook open|gui FILE_OR_URL              # open in Hookmark GUI
hook select FILE_OR_URL                # show menu of hooked items, open selection
hook from APP_NAME                     # bookmark active doc in named app
hook browse PATH_OR_GLOB               # navigate hooks hierarchically
hook percent encode|decode STRING      # URL encoding utilities
hook scripts bash|zsh|fish             # shell completion scripts
```

#### Hookmark: API Requirements for App Integration

Apps must expose four capabilities (via AppleScript, x-callback-url, CLI, or JS):
1. **Get address** — return a URL/ID for the current item
2. **Get name** — return the display name of the current item
3. **Open resource** — open item given a URL/ID
4. **Create new item** — create a new document with a given name

Integration methods: AppleScript dictionary, x-callback-url, CLI, Shortcuts actions.

#### Hookmark: Key Features

- **Bidirectional linking:** hooking A→B automatically makes B→A
- **Adaptive file links:** survive rename, move, cloud sync (iCloud/Dropbox), Git
- **Deep linking:** PDF text selections and video timestamps
- **Auto-bookmarking:** every Hookmark operation bookmarks the item
- **Clean My Links:** strips tracking parameters from URLs
- **Markdown link generation:** copy links as `[title](url)` for notes apps
- **PDF creation:** save webpage as PDF and hook it
- **Universal Links:** wrap any hook URL in `https://hookmark.net/` for web sharing
- **Context window:** floating UI showing all items hooked to the current document
- **iCloud sync:** hook database syncs across Macs and iPhone/iPad
- **Privacy:** all data stored locally; no cloud processing
- **Integrations:** LaunchBar, Alfred, Raycast, Keyboard Maestro, Apple Shortcuts
- **AppleScript dictionary:** full scriptability

### What HookVault Implements (SJL)

**Key files:**
- `tools/sjl-file-tools/hookvault.py`
- `tools/sjl-file-tools/Containerfile.hookvault`
- `tools/sjl-file-tools/quadlets/hookvault.container`
- `tools/sjl-file-tools/requirements-hookvault.txt`

**Deps:** `fastapi==0.111.0`, `uvicorn[standard]==0.30.1`, `pydantic==2.7.1`, `click==8.1.7`

**Run:**
```bash
uvicorn hookvault:app --host 0.0.0.0 --port 8080
python hookvault.py serve
```

**Container:** `localhost/hookvault:latest`  
**Internal port:** `8080` → Nexus publishes `127.0.0.1:8086:8080`  
**Public URL:** `https://hooks.shannonjlove.cloud` → NPM → `localhost:8086`

**Environment variables:**
```
HV_DB=/data/hookvault/vault.db        # SQLite WAL database
HV_BASE_URL=https://admin.shannonjlove.cloud/hooks
HV_PORT=8080
```

**Hook ID format:** `hook:{sha256[:16]}` — deterministic from file path or URL.
Same path → always same hook ID, so re-registering is idempotent.

**Data model:**
- `items` table: `id`, `hook_id`, `kind` (file|url|note|email|arbitrary), `path`, `url`, `title`, `content_hash`, `tags` (JSON), `meta` (JSON), `created_at`, `updated_at`
- `links` table: `id`, `src_hook`, `dst_hook`, `kind` (reference|etc.), `note`, `created_at` — every link is stored bidirectionally (A→B and B→A)

**REST API:**
| Method | Path | Description |
|---|---|---|
| `POST` | `/items` | Register item (idempotent — returns existing if already registered) |
| `GET` | `/items/{hook_id}` | Get item with all outgoing and incoming links |
| `PATCH` | `/items/{hook_id}` | Update title, tags, or meta |
| `DELETE` | `/items/{hook_id}` | Delete item and all its links |
| `GET` | `/items?tag=&kind=&q=&limit=&offset=` | Search/list items |
| `POST` | `/links` | Create bidirectional link between two hook IDs |
| `DELETE` | `/links/{src_hook}/{dst_hook}` | Remove link (both directions) |
| `GET` | `/links/{hook_id}` | Get outgoing and incoming links for item |
| `GET` | `/resolve?path=` or `?url=` | Lookup item by path or URL without knowing hook_id |
| `GET` | `/stats` | Count of items and links, breakdown by kind |
| `GET` | `/ui` | Minimal web UI (dark theme, JetBrains Mono) |

**CLI:**
```bash
python hookvault.py add-file /data/docs/report.pdf --title "Q3 Report" --tags "project,q3"
python hookvault.py add-url https://example.com --title "Example Site" --tags "reference"
python hookvault.py link hook:abc123def456789a hook:bcd234ef5678901b --note "related" --kind reference
python hookvault.py show hook:abc123def456789a
python hookvault.py search --q "report" --tag project --kind file
python hookvault.py serve --host 0.0.0.0 --port 8080
```

**Hookmark features NOT yet in HookVault (future work):**
- Deep links into PDF text selections or video timestamps
- Adaptive links (tracking file renames/moves — needs inotify integration)
- Content hash change detection / re-indexing on file modification
- Full-text search across file contents
- Markdown link copy output
- Universal Link wrapping (`https://hookmark.net/` equivalent)
- Browser extension / OS-level context menu
- Sync across devices (HookVault is single-node SQLite)

---

## 3. DiffForge — emulates DeltaWalker (Deltopia)

**Reference:** https://www.deltopia.com/en/products/deltawalker  
**Also:** https://www.deltawalker.com/

### What DeltaWalker Does

DeltaWalker is a professional cross-platform (Mac/Windows/Linux) file and folder
comparison and merge tool. Its philosophy is **folder-first**: understand entire
directory structures before drilling into individual file differences. It combines
comparison, inspection, and merge action in a unified interface.

#### DeltaWalker: Comparison Modes

| Mode | Editions |
|---|---|
| 2-way file comparison (text, side-by-side) | All |
| 3-way file comparison (file vs. file vs. ancestor) | Pro, Oro |
| 2-way folder comparison and sync | All |
| 3-way folder comparison and sync | Pro, Oro |
| Image comparison (pixel-by-pixel + attribute analysis) | All |
| XML structure view (text + structural elements) | Pro, Oro |
| HTML design view (text + browser-rendered) | All |

#### DeltaWalker: File Format Support

**Archives (open and compare inside):** BZ2, EAR, GZ, JAR, TAR, TBZ2, TGZ, ZIP  
**Remote protocols:** (S)FTP(S), WebDAV, HTTP(S) read-only  
**Syntax highlighting:** ~50 programming and markup languages  
**Image formats:** JPEG, PNG, GIF, TIFF, BMP, WebP, and more (widest range of any diff tool)  
**Office/compound documents:** Excel, Word, PDF (improved text extraction)  
**Any text file:** with configurable encoding support

#### DeltaWalker: Editing & Merging

- Full in-place text editor with syntax awareness (all editions)
- One-click merge with directional arrows (all editions)
- Automatic text file merging with conflict highlighting (Pro, Oro)
- 3-way merge with common ancestor (Pro, Oro)
- Automatic non-conflicting folder merge (Pro, Oro)
- Unlimited undo/redo
- Real-time search within comparison editors

#### DeltaWalker: Folder Synchronization

- **2-way sync:** fine-grained operations: Copy, Move, Delete on individual files or selections
- **High-level 2-way sync:** Update (copy newer) and Mirror (make identical)
- **3-way sync:** merge changes from two folders into their common ancestor (Oro only)
- **Automatic sync:** non-conflicting differences merged automatically (Pro, Oro)
- **Alignment override filters:** handle mismatched filenames across folders (Pro, Oro)
- Shell expression folder filters for excluding files/patterns
- Regular expression text filters

#### DeltaWalker: Integration & Export

- **Version control:** Git, Mercurial (Hg), Bazaar, SVN — use DeltaWalker as external diff/merge tool
- **Command-line interface:** open comparisons from terminal
- **UNIX Diff patches:** output in 4 formats (normal, context, unified, ed)
- **Reports:** HTML and XML comparison reports (all editions)
- **JavaScript scripting:** (Oro edition)
- **Print/print preview** with customizable headers and footers

#### DeltaWalker: Editions

| Edition | License | Extra capabilities |
|---|---|---|
| Standard | Single platform (Mac or Win or Linux) | Core 2-way compare, folder sync, image, HTML diff |
| Pro | Single platform | + 3-way compare/merge, XML structure, scripting |
| Oro | All platforms | + Auto folder sync, JS scripting, priority support |

### What DiffForge Implements (SJL)

**Key files:**
- `tools/sjl-file-tools/diffforge.py`
- `tools/sjl-file-tools/Containerfile.diffforge`
- `tools/sjl-file-tools/quadlets/diffforge.container`
- `tools/sjl-file-tools/requirements-diffforge.txt`

**Deps:** `fastapi==0.111.0`, `uvicorn[standard]==0.30.1`, `pydantic==2.7.1`, `python-multipart==0.0.9`

**Run:**
```bash
uvicorn diffforge:app --host 0.0.0.0 --port 8082
python diffforge.py --host 0.0.0.0 --port 8082
```

**Container:** `localhost/diffforge:latest`  
**Internal port:** `8082` → Nexus publishes `127.0.0.1:8087:8082`  
**Public URL:** `https://diff.shannonjlove.cloud` → NPM → `localhost:8087`

**Environment variables:**
```
DF_PORT=8082
DF_ALLOW_PATHS=/data    # comma-separated allowed root paths for server-path mode
```

**Diff engine:** Python `difflib.SequenceMatcher` with grouped opcodes.
Returns per-hunk, per-line typed output: `context`, `added`, `removed`, `changed`.
Similarity ratio and addition/deletion counts included in every response.

**REST API:**
| Method | Path | Request body | Description |
|---|---|---|---|
| `GET` | `/` | — | Web UI (HTML) |
| `POST` | `/diff/text` | `{left, right, context}` | Compare two text strings |
| `POST` | `/diff/files` | multipart: `left`, `right` files | Compare two uploaded files |
| `POST` | `/diff/paths` | `{left_path, right_path, context}` | Compare two server-side file paths |
| `POST` | `/diff/dirs` | `{left_dir, right_dir}` | Directory comparison (only_left, only_right, modified, same + stats) |

**Security:** `DF_ALLOW_PATHS` enforces that server-path and dir operations stay within
allowed root directories. Paths outside those roots return HTTP 403.

**Web UI:** Dark-themed, monospace (JetBrains Mono/Fira Code), four tabs:
- **Text** — paste content directly, adjustable context lines (0/3/5/10)
- **Upload Files** — upload two files for comparison
- **Server Paths** — compare files already on the server by absolute path
- **Directories** — compare two server directories; click modified files to diff them
- Character/word-level inline highlights within changed lines
- Similarity percentage badge, +/- line count stats

**Data mounted:** `/data` read-only in container so DiffForge can access server files.

**DeltaWalker features NOT yet in DiffForge (future work):**
- 3-way merge (requires ancestor concept and conflict resolution UI)
- Archive opening (zip/tar inspection)
- Remote protocol support (FTP/SFTP/WebDAV sources)
- Syntax highlighting in diff view (~50 languages)
- Image comparison (pixel-by-pixel visual diff)
- XML structure view
- HTML rendered view
- Patch export (unified diff / context diff download)
- HTML/XML report generation
- Version control integration (git diff, git merge-tool)
- In-editor merge (currently read-only diff output)

---

## PARA Data Layout on Nexus

```
/data/
├── inbox/              ← FileWarden entry point (all new files drop here)
├── documents/
│   └── YYYY/MM/        ← PDFs, DOCX, TXT, MD after sjl_rename + mkdir_move
├── media/
│   ├── images/YYYY/MM/ ← JPG, PNG, WEBP, HEIC
│   └── video/YYYY/     ← MP4, MOV, MKV
├── downloads/
│   └── archives/       ← ZIP, TAR.GZ, 7Z
├── tagback/
│   └── incoming/       ← TagBack asset ingest (→ n8n webhook)
├── unsorted/           ← Catch-all for unmatched files
└── hookvault/
    └── vault.db        ← HookVault SQLite WAL database
```

---

## Build & Deploy (on Nexus via NeoServer)

Full build script: `tools/sjl-file-tools/DEPLOY.sh`

```bash
# Build all images
podman build -t localhost/filewarden:latest /opt/filewarden
podman build -t localhost/hookvault:latest  /opt/hookvault
podman build -t localhost/diffforge:latest  /opt/diffforge

# Install quadlets
QDIR="${XDG_CONFIG_HOME:-$HOME/.config}/containers/systemd"
cp quadlets/*.container "$QDIR/"
systemctl --user daemon-reload
systemctl --user enable --now filewarden hookvault diffforge

# Status
systemctl --user status filewarden hookvault diffforge
journalctl --user -u filewarden -f
```

---

## NPM Proxy Config (Nginx Proxy Manager)

| Domain | → | Upstream |
|---|---|---|
| `hooks.shannonjlove.cloud` | → | `http://localhost:8086` |
| `diff.shannonjlove.cloud` | → | `http://localhost:8087` |

All: Enable "Block Common Exploits", force SSL, Access List = Tailscale IPs only.  
FileWarden has no web UI — background daemon only.

---

## BookStack Sync (CLAUDE.md live updates)

**Script:** `tools/sjl-file-tools/bookstack_sync.py`  
**Deps:** `requests>=2.31.0`, `pyyaml==6.0.1`, `click==8.1.7`

BookStack is a self-hosted wiki/documentation platform with a full REST API.
`bookstack_sync.py` keeps CLAUDE.md (and other Markdown files) live-synced with
a BookStack page — push on save, pull to local, or run as a watcher.

**Environment variables:**
```
BS_URL             https://docs.shannonjlove.cloud   # BookStack instance
BS_TOKEN_ID        API token ID (from Profile → API Tokens)
BS_TOKEN_SECRET    API token secret
BS_PAGE_ID         Target page ID (optional; can be embedded in frontmatter)
BS_BOOK_ID         Default book for new page creation
BS_CHAPTER_ID      Default chapter for new page creation (overrides book)
```

**Auth header:** `Authorization: Token {token_id}:{token_secret}`

**CLI:**
```bash
# Push CLAUDE.md to its BookStack page (page_id from frontmatter or BS_PAGE_ID)
python bookstack_sync.py push CLAUDE.md

# Watch and push on every save (5s poll)
python bookstack_sync.py watch CLAUDE.md --interval 5

# Pull page 42 down to a local file
python bookstack_sync.py pull --page-id 42 --output CLAUDE.md

# List all pages in book 1
python bookstack_sync.py list-pages --book-id 1
```

**Frontmatter embedding:** On first push to a new page, the script writes the
assigned page ID back into the file's YAML frontmatter so future pushes are
idempotent without needing `BS_PAGE_ID`:
```yaml
---
bookstack_page_id: 42
title: SJL Infrastructure
---
```

**BookStack REST API reference:**
| Method | Path | Action |
|---|---|---|
| `GET` | `/api/pages` | List all pages |
| `POST` | `/api/pages` | Create page (requires `book_id` or `chapter_id`, `name`, `html` or `markdown`) |
| `GET` | `/api/pages/{id}` | Get page |
| `PUT` | `/api/pages/{id}` | Update page |
| `DELETE` | `/api/pages/{id}` | Delete page |
| `GET` | `/api/pages/{id}/export/markdown` | Export as Markdown |
| `GET` | `/api/books` | List books |
| `GET` | `/api/chapters` | List chapters |
| `GET` | `/api/search?query=` | Full-text search |

---

## Raindrop.io Integration

**Reference:** https://raindrop.io — bookmark manager with REST API and MCP server.

### Raindrop.io REST API

**Base URL:** `https://api.raindrop.io/rest/v1`  
**Auth:** `Authorization: Bearer {RAINDROP_TOKEN}`  
**Rate limit:** 120 requests/minute per user

**Key raindrop (bookmark) fields:**
```json
{
  "_id":        12345,
  "link":       "https://example.com",
  "title":      "Example",
  "excerpt":    "Page description",
  "note":       "My personal note",
  "tags":       ["tag1", "tag2"],
  "type":       "link|article|image|video|document|audio",
  "cover":      "https://...",
  "collection": {"$id": 0},
  "important":  false,
  "highlights": [],
  "domain":     "example.com",
  "created":    "ISO8601",
  "lastUpdate": "ISO8601"
}
```

**Raindrop endpoints:**
| Method | Path | Action |
|---|---|---|
| `GET` | `/raindrop/{id}` | Get single bookmark |
| `POST` | `/raindrop` | Create bookmark (send `pleaseParse:{}` for auto metadata) |
| `PUT` | `/raindrop/{id}` | Update bookmark |
| `DELETE` | `/raindrop/{id}` | Move to Trash |
| `GET` | `/raindrops/{collection_id}` | List/search collection (`?search=&page=&perpage=`) |
| `POST` | `/raindrops` | Bulk create |
| `PUT` | `/raindrops` | Bulk update |
| `DELETE` | `/raindrops/{collection_id}` | Bulk delete from collection |
| `GET` | `/collections` | List all collections |
| `POST` | `/collection` | Create collection |
| `GET` | `/tags/{collection_id}` | List tags in collection |

**Collection IDs:** `0` = Unsorted, `-1` = All, `-99` = Trash, `-1` with search = all

**MCP server (Pro users):**
- Endpoint: `https://api.raindrop.io/rest/v2/ai/mcp`
- Transport: Streamable HTTP
- Auth: OAuth 2.1 or Bearer token
- Claude Code can connect to this MCP server to manage bookmarks in conversation

### HookVault ↔ Raindrop Integration

**Environment variable:** `RAINDROP_TOKEN`, `RAINDROP_AUTO_PUSH=1`

**New endpoints in HookVault:**
| Method | Path | Description |
|---|---|---|
| `POST` | `/sync/raindrop/push/{hook_id}` | Push single URL item to Raindrop |
| `POST` | `/sync/raindrop/import` | Import from Raindrop collection into HookVault |
| `GET` | `/sync/raindrop/collections` | List Raindrop collections |

**Auto-push:** Set `RAINDROP_AUTO_PUSH=1` to push every new `kind=url` item to Raindrop
automatically. The Raindrop `_id` is stored in the item's `meta.raindrop_id` for future syncs.

**CLI:**
```bash
python hookvault.py raindrop-import --collection-id 0 --overwrite
python hookvault.py raindrop-import --collection-id 12345 --tag work --tag project
```

### Raindrop Automations

Raindrop.io supports automation via **n8n**, **Make.com**, and **Zapier**:

**n8n (self-hosted, running on Nexus):**
- Trigger: "New Bookmark Added", "Bookmark Modified"
- Actions: create/update/delete raindrops, search, manage collections
- SJL n8n instance: `https://n8n.shannonjlove.cloud`

**Common automation flows:**
1. FileWarden `run_script` → n8n webhook → Raindrop bookmark creation
2. Raindrop new bookmark → n8n → HookVault `/shortcut/add-url`
3. Raindrop new bookmark → n8n → BookStack page update
4. Raindrop tag applied → n8n → HookVault tag sync

---

## iOS Automation — Scriptable & Apple Shortcuts

### Scriptable (https://scriptable.app)

JavaScript automation app for iOS/iPadOS. Uses Apple's JavaScriptCore (ES6+).
Scripts run from the app, home screen widgets, Siri, or Share Sheet.

**Key APIs:**
| Module | What it does |
|---|---|
| `Request` | HTTP GET/POST/PUT/DELETE/PATCH with headers, JSON body, response parsing |
| `FileManager` | Read/write files in iCloud Drive, local storage, and Files.app |
| `Keychain` | Securely store API tokens and secrets |
| `Pasteboard` | Read/write clipboard |
| `CallbackURL` | x-callback-url scheme — call other apps and get responses |
| `URLScheme` | Open any URL scheme (including `hook://`, `hookmark://`) |
| `Safari` | Open URLs in Safari or SFSafariViewController |
| `ListWidget` | iOS home screen widgets with text, images, stacks |
| `UITable` | Scrollable table UI with rows and cells |
| `Alert` | Dialogs with text fields, buttons |
| `ShareSheet` | Share content from/to other apps |
| `Notification` | Schedule local notifications |
| `Calendar` / `Reminder` | Read/write calendar events and reminders |
| `Location` | GPS coordinates |
| `Photos` | Access photo library |
| `Mail` / `Message` | Send email or SMS |
| `Speech` | Text-to-speech |
| `Device` | Device info, screen size, battery, language |
| `Timer` | Delayed execution |
| `DrawContext` | Draw images, generate charts |

**HTTP request pattern:**
```javascript
const req = new Request("https://hooks.shannonjlove.cloud/shortcut/recent");
req.method = "GET";
const data = await req.loadJSON();
```

**POST with JSON:**
```javascript
const req = new Request("https://hooks.shannonjlove.cloud/shortcut/add-url?url=https://example.com&title=Example");
req.method = "POST";
const result = await req.loadJSON();
```

**Keychain (store API tokens securely):**
```javascript
Keychain.set("hookvault_token", "your-token-here");
const token = Keychain.get("hookvault_token");
```

**SJL Scriptable script:** `tools/sjl-file-tools/ios/HookVault.js`
- Full menu-driven HookVault browser
- Search, Recent, Add from Clipboard, Stats
- Opens items in Hookmark PAL via `hook://` URLs
- Works from Share Sheet (adds shared URL to HookVault)

### Apple Shortcuts (iOS + macOS)

Shortcuts can call any REST API via "Get Contents of URL":

**GET request:**
1. "Get Contents of URL" → URL = `https://hooks.shannonjlove.cloud/shortcut/recent`
2. "Get Dictionary Value" → from result, key = items

**POST with JSON body:**
1. "Get Contents of URL"
   - URL: `https://hooks.shannonjlove.cloud/shortcut/add-url`
   - Method: POST
   - Headers: `Content-Type: application/json`
   - Request Body: JSON, keys: `url`, `title`, `tags`

**Useful Shortcuts for HookVault:**
- "Hook current URL" — Share Sheet → Shortcuts → POST to `/shortcut/add-url`
- "Search hooks" — Ask for input → GET `/shortcut/search?q={input}`
- "Recent hooks" — GET `/shortcut/recent` → show list → open selection

**macOS note:** Automations tab is unavailable on macOS (available on iOS/iPadOS only).
On macOS, Shortcuts run manually or from menu bar, keyboard shortcut, or Siri.

### Hookmark PAL (iOS)

**Reference:** https://hookproductivity.com/iphone-ipad/

Hookmark PAL is the iOS companion to Hookmark for Mac. Syncs via iCloud.

**Capabilities:**
- Browse and navigate bidirectional links created on any device
- Create new hooks (bidirectional links) on iOS
- Tag and pin bookmarks
- Search by tag, title, URL
- View pinned items across apps
- Open `hook://` URLs directly

**hook:// URL scheme (opens in Hookmark PAL):**
```
hook://file/<percent-encoded-posix-path>   # open file by path
hook://search/<encoded-query>              # trigger Spotlight search
```

**HookVault ↔ Hookmark PAL integration:**
HookVault exposes these iOS-compatible endpoints:

| Endpoint | Use in PAL / Shortcuts |
|---|---|
| `GET /hook-url/{hook_id}` | Get `hook://` URL for any item |
| `GET /shortcut/recent?limit=20` | Recent items list for Shortcuts |
| `GET /shortcut/search?q=&tag=&kind=` | Search for Shortcuts |
| `POST /shortcut/add-url?url=&title=&tags=` | Quick-add (no JSON body needed) |

**Shortcut to open item in Hookmark PAL:**
1. GET `/shortcut/search?q=<input>` → parse JSON array
2. Choose item from list (repeat menu)
3. GET `/hook-url/{hook_id}` → get `hook_url`
4. Open `hook_url` — Hookmark PAL opens with that item's context

---

## n8n Integration

**Instance:** `https://n8n.shannonjlove.cloud`

**Active webhooks:**
- `POST /webhook/tagback-ingest` — FileWarden TagBack: `{"file": "$FW_FILE", "name": "$FW_NAME", "ext": "$FW_EXT"}`

**Planned automation flows:**
- Raindrop new bookmark → HookVault import
- HookVault new item → BookStack page update
- FileWarden processed file → HookVault register-file

---

## Claude Code Notes

- Always work on feature branches; never push directly to `main`
- `tools/sjl-file-tools/` in this repo is the source of truth for all three services
- When extending any SJL tool, consult the "NOT yet implemented" list above first
- `RAINDROP_TOKEN` and `BS_TOKEN_ID`/`BS_TOKEN_SECRET` must be set in the container env
- Production SHA256: `fd374d5ac914192de693c76e8ee205645e7bdba8ef5822bc7572dd5175d1d410`
