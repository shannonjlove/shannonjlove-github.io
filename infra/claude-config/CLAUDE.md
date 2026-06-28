# User Preferences

## Container Orchestration

Always use **Podman Quadlets** (systemd `.container` unit files) for all container workloads.

- Never create `docker-compose.yml`, `docker-compose.yaml`, or any Docker Compose files
- Never write `Dockerfile`-based Docker CLI instructions when Podman is the alternative
- Always use `podman` CLI, `podman-compose` (if compose syntax is unavoidable), or Quadlet `.container` units
- Quadlet units go in `/etc/containers/systemd/` (system) or `~/.config/containers/systemd/` (user)
- This applies systemwide and in all situations, without exception

---

## SJL Infrastructure

**VPS:** `shannonjlove.cloud` (72.61.74.250) — Ubuntu 24.04, 4 CPU, 16 GB RAM
**Wildcard DNS:** `*.shannonjlove.cloud` → 72.61.74.250

### Known Services

| Subdomain | Service |
|-----------|---------|
| shannonjlove.cloud | Main site |
| webtop.shannonjlove.cloud | WebTop browser desktop |
| bookstack.shannonjlove.cloud | BookStack knowledge base |
| n8n.shannonjlove.cloud | n8n automation |
| dashboard.shannonjlove.cloud | Dashboard |
| admin.shannonjlove.cloud | Admin panel |
| agent.shannonjlove.cloud | Agent |
| api.shannonjlove.cloud | API |
| status.shannonjlove.cloud | Status page |
| stacks.shannonjlove.cloud | Stacks |
| docs.shannonjlove.cloud | Docs |
| pages.shannonjlove.cloud | Pages |
| pics.shannonjlove.cloud | Pics |
| media.shannonjlove.cloud | Media |
| assets.shannonjlove.cloud | Assets |
| private.shannonjlove.cloud | Private |
| rclone-mcp.shannonjlove.cloud | Rclone MCP |

---

## Knowledge Base — BookStack

**URL:** https://bookstack.shannonjlove.cloud
**API base:** https://bookstack.shannonjlove.cloud/api/
**Auth header:** `Authorization: Token $BOOKSTACK_TOKEN_ID:$BOOKSTACK_TOKEN_SECRET`

Credentials are available as env vars `BOOKSTACK_TOKEN_ID` and `BOOKSTACK_TOKEN_SECRET`.
The SessionStart hook auto-fetches the books list at the start of each session.

Useful API calls:
- List books: `GET /api/books`
- Search: `GET /api/search?query=term`
- Get page: `GET /api/pages/{id}`
- Get page content: `GET /api/pages/{id}/export/plaintext`

---

## SJL Custom Tools

Three custom Python services deployed via Podman Quadlets on the VPS. Source files live in `/opt/{tool}/` on Nexus. All use `localhost/toolname:latest` images built from `python:3.12-slim`. Network: `sjl-infra.network`.

---

### HookVault (`hookvault.py`)
Server-side **Hookmark** replacement — bidirectional linking between files, URLs, notes, and any URI.

- **URL:** https://admin.shannonjlove.cloud/hooks (proxied by NPM)
- **Internal port:** `127.0.0.1:8086:8080`
- **Quadlet:** `~/.config/containers/systemd/hookvault.container`
- **DB:** `/data/hookvault/vault.db` (SQLite, WAL mode)
- **Env vars:** `HV_DB`, `HV_BASE_URL=https://admin.shannonjlove.cloud/hooks`, `HV_PORT=8080`

Key API endpoints:
- `POST /items` — register file, URL, note, or email
- `GET /items/{hook_id}` — get item with all its links
- `POST /links` — create bidirectional link between two hook IDs
- `GET /links/{hook_id}` — list all links for an item
- `GET /resolve?path=/data/...` — look up by file path or URL
- `GET /stats` — item/link counts by kind
- `GET /ui` — minimal web UI

Hook IDs are deterministic SHA-256 slugs: `hook:abcdef1234567890`

CLI usage:
```bash
python hookvault.py add-file /data/docs/report.pdf --tags "project,q3"
python hookvault.py link hook:abc123 hook:def456
python hookvault.py show hook:abc123
python hookvault.py search --tag project
```

**Raindrop ↔ HookVault connection:** When adding a bookmark to Raindrop, also register its URL in HookVault as a `url` kind item so it can be bidirectionally linked to local files and notes.

---

### FileWarden (`filewarden.py`)
Server-side **Hazel** replacement — inotify-based file watcher with condition/action rules.

- **No web UI** — background daemon only
- **Quadlet:** `~/.config/containers/systemd/filewarden.container`
- **Config:** `/opt/filewarden/config.yaml` (mounted read-only at `/etc/filewarden/config.yaml`)
- **State DB:** `/var/lib/filewarden/state.db`
- **Logs:** `/var/log/filewarden/filewarden.log`
- **Env vars:** `FW_LOG_DIR`, `FW_STATE_DB`

Watched directories (PARA layout):
- `/data/inbox` — sorts, SJL-renames, routes by extension
- `/data/downloads` — logs files > 500 MB
- `/data/tagback/incoming` — SJL-renames, then POSTs to `n8n.shannonjlove.cloud/webhook/tagback-ingest`

**SJL canonical naming format:**
`YYYY-MM-DD_HH-MM_category-subcategory_description_UUID24.ext`

Action types: `move`, `copy`, `rename`, `delete`, `trash`, `run_script`, `log`, `sjl_rename`, `mkdir_move`

---

### DiffForge (`diffforge.py`)
Server-side **DeltaWalker** replacement — web-based file & directory diff tool.

- **URL:** https://diff.shannonjlove.cloud (proxied by NPM)
- **Internal port:** `127.0.0.1:8087:8082`
- **Quadlet:** `~/.config/containers/systemd/diffforge.container`
- **Env vars:** `DF_PORT=8082`, `DF_ALLOW_PATHS=/data`

API endpoints:
- `POST /diff/text` — compare two text strings
- `POST /diff/files` — compare two uploaded files
- `POST /diff/paths` — compare two server file paths (must be under `/data`)
- `POST /diff/dirs` — compare two directories (returns only_left/only_right/modified/same)
- `GET /` — full web UI (text, file upload, server paths, directory tabs)

---

### Deployment
All three use Podman Quadlets at `~/.config/containers/systemd/`.
Build + deploy script: `DEPLOY.sh` (encode as base64, run via NeoServer).
NPM proxy access restricted to Tailscale IPs: `100.115.66.75`, `100.67.229.94`.

```bash
# Rebuild and restart a tool
podman build -t localhost/hookvault:latest /opt/hookvault
systemctl --user restart hookvault
```

---

## Bookmarks — Raindrop.io

**URL:** https://app.raindrop.io
**Account:** shannonjlove@mac.com
**API:** https://api.raindrop.io/rest/v1
**Auth header:** `Authorization: Bearer $RAINDROP_TOKEN`

Credentials available as env vars `RAINDROP_TOKEN`, `RAINDROP_CLIENT_ID`, `RAINDROP_CLIENT_SECRET`.
All SJL subdomains are bookmarked in the **SJL Infrastructure** collection.
Run `~/.claude/scripts/raindrop-add-infra.sh` to re-sync bookmarks.

---

## SJL Tool Reference: Hazel / Hookmark / DeltaWalker Equivalents

These three Mac tools are emulated by FileWarden, HookVault, and DiffForge respectively on the VPS.

---

### FileWarden ↔ Hazel

#### Condition Attributes
| Attribute | Description |
|-----------|-------------|
| `name` | File stem (no extension) |
| `full_name` | Full filename including extension |
| `extension` | Extension without leading dot |
| `path` | Parent directory path string |
| `size_kb` | File size in kilobytes |
| `size_mb` | File size in megabytes |
| `size_bytes` | File size in bytes |
| `date_modified` | Modification date as `YYYY-MM-DD` |
| `year_modified` | Modification year |
| `month_modified` | Modification month (zero-padded) |
| `mime_type` | MIME type string (e.g. `application/pdf`) |
| `content` | Full text content of file (for text matching) |

#### Condition Operators
`contains`, `does_not_contain`, `starts_with`, `ends_with`, `is`, `is_not`, `equals`, `matches_regex`, `greater_than`, `less_than`

#### Action Types
| Type | Params | Description |
|------|--------|-------------|
| `move` | `destination` | Move file to path (supports tokens) |
| `copy` | `destination` | Copy file to path |
| `rename` | `name` | Rename using template tokens |
| `delete` | — | Permanently delete |
| `trash` | `trash_dir` (opt) | Move to trash dir (default: `/tmp/filewarden_trash`) |
| `run_script` | `script` | Run inline shell script |
| `log` | `message` | Log a message (supports tokens) |
| `sjl_rename` | `category`, `subcategory`, `description` (opt) | Apply SJL canonical naming |
| `mkdir_move` | `base`, `subdir_pattern` | Create dated subdir and move file |

#### Template Tokens (usable in `rename`, `move`, `log`, `mkdir_move`)
`{name}`, `{full_name}`, `{extension}`, `{date}`, `{time}`, `{year}`, `{month}`, `{day}`, `{date_modified}`, `{year_modified}`, `{uuid24}`, `{uuid8}`

#### Run Script Environment Variables
`FW_FILE` (full path), `FW_NAME` (stem), `FW_EXT` (extension), `FW_DIR` (parent dir)

#### Rule Config Structure
```yaml
- name: "Rule name"
  enabled: true
  match: all            # all = AND logic, any = OR logic
  conditions:
    - attribute: extension
      operator: is
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
  stop_processing: true  # stop here if matched; false = keep checking rules
```

#### One-Shot Scan (manual trigger)
```bash
python filewarden.py --once --config /etc/filewarden/config.yaml
```

#### Hazel → FileWarden Feature Map
| Hazel | FileWarden |
|-------|-----------|
| File rules | `rules:` list in config.yaml |
| All/any condition matching | `match: all` / `match: any` |
| Move to folder | `type: move` |
| Sort into subfolders | `type: mkdir_move` |
| Rename file | `type: rename` with tokens |
| SJL custom naming | `type: sjl_rename` (built-in) |
| Run shell script | `type: run_script` |
| Run AppleScript | `type: run_script` (shell equivalent) |
| Add comment | `type: log` |
| Trash | `type: trash` |
| Delete | `type: delete` |
| Continue matching rules | `stop_processing: false` |
| Stop processing | `stop_processing: true` |
| Run rules on folder contents | `--once` flag |

Hazel features **not** in FileWarden (macOS-only): Add/Remove tags, color labels, Open in app, Show in Finder, Make alias, Import into Photos, Run JavaScript.

---

### HookVault ↔ Hookmark

#### AppleScript → REST API Translation

Hookmark AppleScript pattern (from createhookmarklink.txt):
```applescript
tell application "Hookmark"
    set fileBookmark to make new bookmark with properties {location:filePath}
    set tags of fileBookmark to {"category:resources", "type:skill"}
    set note of fileBookmark to "description..."
    set bookStackBookmark to make new bookmark with properties {location:bookStackURL}
    make new link from fileBookmark to bookStackBookmark
    set hookLink to hook link of fileBookmark  -- returns hook://...
end tell
```

HookVault REST equivalent:
```bash
# 1. Register file
FILE_HOOK=$(curl -s -X POST http://localhost:8080/items \
  -H "Content-Type: application/json" \
  -d '{"kind":"file","path":"/data/docs/report.md","title":"Report",
       "tags":["category:resources","type:skill"],
       "meta":{"note":"description..."}}' | jq -r '.hook_id')

# 2. Register BookStack URL
URL_HOOK=$(curl -s -X POST http://localhost:8080/items \
  -H "Content-Type: application/json" \
  -d '{"kind":"url","url":"https://bookstack.shannonjlove.cloud/books/1/page/42",
       "title":"Report (BookStack)"}' | jq -r '.hook_id')

# 3. Create bidirectional link (reverse link auto-created)
curl -s -X POST http://localhost:8080/links \
  -H "Content-Type: application/json" \
  -d "{\"src_hook\":\"$FILE_HOOK\",\"dst_hook\":\"$URL_HOOK\",
       \"kind\":\"reference\",\"note\":\"BookStack copy\"}"

# 4. Get stable hook ID (equivalent to hook:// link)
echo "Hook ID: $FILE_HOOK"
```

#### Hook ID Format
`hook:{sha256[:16] of path_or_url}` — deterministic, stable across sessions. Same file always gets the same ID.

#### Hookmark → HookVault Feature Map
| Hookmark | HookVault |
|----------|----------|
| Create bookmark from file | `POST /items` kind=file |
| Create bookmark from URL | `POST /items` kind=url |
| Add tags | `tags` array in POST, or `PATCH /items/{hook_id}` |
| Add note | `meta.note` in POST body |
| Bidirectional link | `POST /links` (auto-creates reverse) |
| `hook://` URI | `hook:{id}` stable identifier |
| Copy hook link | `hook_id` field in response |
| Search by tag | `GET /items?tag=tagname` |
| View item links | `GET /links/{hook_id}` |
| Resolve file → hook | `GET /resolve?path=/data/file.pdf` |
| Web UI | `GET /ui` → https://admin.shannonjlove.cloud/hooks/ui |

#### CLI Quickref
```bash
python hookvault.py add-file /data/docs/report.pdf --tags "project,q3"
python hookvault.py add-url https://bookstack... --title "Name" --tags "docs"
python hookvault.py link hook:abc123 hook:def456 --note "BookStack copy"
python hookvault.py show hook:abc123
python hookvault.py search --tag project
python hookvault.py search --q "report"
```

---

### DiffForge ↔ DeltaWalker

#### DiffForge Capabilities (Implemented)
- Side-by-side diff with word-level character highlighting
- Similarity ratio (0–100%), addition/deletion counts
- Text paste comparison
- File upload and comparison (UTF-8 decoded)
- Server file path comparison (paths must be under `DF_ALLOW_PATHS=/data`)
- Directory tree comparison: only_left / only_right / modified / same
- Click modified file in directory view → auto-loads path compare
- Configurable context lines (0, 3, 5, 10)
- Web UI tabs: Text, Upload Files, Server Paths, Directories

#### API Quickref
```bash
# Text diff
curl -s -X POST https://diff.shannonjlove.cloud/diff/text \
  -H "Content-Type: application/json" \
  -d '{"left":"old text","right":"new text","context":3}'

# Server path diff
curl -s -X POST https://diff.shannonjlove.cloud/diff/paths \
  -H "Content-Type: application/json" \
  -d '{"left_path":"/data/v1/config.yaml","right_path":"/data/v2/config.yaml"}'

# Directory diff
curl -s -X POST https://diff.shannonjlove.cloud/diff/dirs \
  -H "Content-Type: application/json" \
  -d '{"left_dir":"/data/deploy-v1","right_dir":"/data/deploy-v2"}'
```

Response shape: `{"ratio":0.85,"additions":5,"deletions":2,"hunks":[{"header":"...","lines":[...]}]}`
Directory response: `{"only_left":[],"only_right":[],"modified":[],"same":[],"stats":{...}}`

#### DeltaWalker → DiffForge Feature Map
| DeltaWalker | DiffForge |
|-------------|----------|
| Side-by-side file diff | ✓ all modes |
| Character-level highlighting | ✓ word-level in web UI |
| Open two files | ✓ Upload Files tab |
| Compare server files | ✓ Server Paths tab |
| Directory compare | ✓ Directories tab |
| Similarity percentage | ✓ `ratio` field |
| Context line count | ✓ `context` param |
| Click dir file → diff | ✓ `compareFile()` in UI |
| 3-way merge | ✗ Not implemented |
| In-place editing / merging | ✗ Read-only |
| SVN/Git integration | ✗ Not implemented |
| Syntax highlighting | ✗ Monospace only |
| Ignore whitespace | ✗ Not implemented |
| Save as patch file | ✗ Not implemented |
| CLI (`deltawalk`) | ✗ Use API directly |
