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

## n8n Integration

- **TagBack ingest webhook:** `POST https://n8n.shannonjlove.cloud/webhook/tagback-ingest`
  - JSON body: `{"file": "$FW_FILE", "name": "$FW_NAME", "ext": "$FW_EXT"}`
  - Triggered by FileWarden `run_script` action on `/data/tagback/incoming`

---

## Claude Code Notes

- Always work on feature branches; never push directly to `main`
- `tools/sjl-file-tools/` in this repo is the source of truth for all three services
- When extending any SJL tool, consult the "NOT yet implemented" list above first
- Production SHA256: `fd374d5ac914192de693c76e8ee205645e7bdba8ef5822bc7572dd5175d1d410`
