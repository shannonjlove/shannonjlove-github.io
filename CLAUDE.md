# SJL Infrastructure — Claude Code Knowledge Base

This file gives Claude persistent context about Shannon Jeffrey Love's infrastructure,
tools, and conventions so every session starts informed.

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

### 1. FileWarden

**What it is:** Hazel-style file automation daemon. Watches directories and applies
YAML-configured rules to incoming files. Background-only, no web UI.

**Key files:**
- `tools/sjl-file-tools/filewarden.py` — main daemon
- `tools/sjl-file-tools/config.yaml` — PARA watch rules
- `tools/sjl-file-tools/Containerfile.filewarden`
- `tools/sjl-file-tools/quadlets/filewarden.container`
- `tools/sjl-file-tools/requirements-filewarden.txt`

**Deps:** `watchdog==4.0.1`, `pyyaml==6.0.1`, `click==8.1.7`

**Run (bare metal):**
```bash
pip install watchdog pyyaml click
python filewarden.py --config /etc/filewarden/config.yaml
python filewarden.py --config config.yaml --dry-run   # preview only
```

**Container image:** `localhost/filewarden:latest`  
**No exposed port** — background daemon only.

**Volume layout on Nexus:**
```
/opt/filewarden/config.yaml  → /etc/filewarden/config.yaml (ro)
/var/log/filewarden          → /var/log/filewarden
/var/lib/filewarden          → /var/lib/filewarden
/data/inbox                  → /data/inbox
/data/documents              → /data/documents
/data/media                  → /data/media
/data/downloads              → /data/downloads
/data/tagback                → /data/tagback
/data/unsorted               → /data/unsorted
```

**SJL rename convention:**
```
YYYY-MM-DD--{category}--{subcategory}--{original-slug}.{ext}
```
Example: `invoice.pdf` with category=`document`, subcategory=`pdf` becomes:
`2026-06-26--document--pdf--invoice.pdf`

**Config rule structure (`config.yaml`):**
```yaml
watches:
  - path: /data/inbox
    enabled: true
    recursive: false
    delay_seconds: 2
    rules:
      - name: "Rule description"
        enabled: true
        match: all          # all | any
        conditions:
          - attribute: extension   # extension | size_mb | name | stem
            operator: is           # is | is_not | contains | greater_than | less_than | matches_regex
            value: pdf
        actions:
          - type: sjl_rename       # sjl_rename | mkdir_move | move | log | run_script
            params:
              category: document
              subcategory: pdf
          - type: mkdir_move
            params:
              base: /data/documents
              subdir_pattern: "{year}/{month}"
        stop_processing: true
```

**Watched directories (production):**
- `/data/inbox` — sort all incoming files; 2s settle delay
- `/data/downloads` — warn on files >500 MB
- `/data/tagback/incoming` — ingest assets, call n8n webhook

**Action env vars (run_script):** `FW_FILE`, `FW_NAME`, `FW_EXT`

---

### 2. HookVault

**What it is:** Server-side Hookmark replacement. Bidirectional linking between files,
URLs, notes, and any URI. FastAPI REST API + minimal web UI + CLI.

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

**Container image:** `localhost/hookvault:latest`  
**Internal port:** `8080`  
**Published on Nexus:** `127.0.0.1:8086:8080`  
**Public URL:** `https://hooks.shannonjlove.cloud` → NPM → `localhost:8086`

**Environment variables:**
```
HV_DB=/data/hookvault/vault.db
HV_BASE_URL=https://admin.shannonjlove.cloud/hooks
HV_PORT=8080
```

**Key API endpoints:**
| Method | Path | Description |
|---|---|---|
| `POST` | `/items` | Register file/URL/note |
| `GET` | `/items/{hook_id}` | Get item + links |
| `PATCH` | `/items/{hook_id}` | Update title/tags/meta |
| `DELETE` | `/items/{hook_id}` | Remove item |
| `GET` | `/items?tag=&kind=&q=` | Search/list |
| `POST` | `/links` | Create bidirectional link |
| `DELETE` | `/links/{src}/{dst}` | Remove link |
| `GET` | `/links/{hook_id}` | List item's links |
| `GET` | `/resolve?path=` | Lookup by file path |
| `GET` | `/stats` | Counts by kind |
| `GET` | `/ui` | Web UI |

**Hook ID format:** `hook:{sha256[:16]}` derived from path or URL (deterministic).

**CLI:**
```bash
python hookvault.py add-file /data/docs/report.pdf --tags "project,q3"
python hookvault.py add-url https://example.com --title "Example"
python hookvault.py link hook:abc123 hook:def456 --note "related"
python hookvault.py show hook:abc123
python hookvault.py search --tag project
```

**Data storage:** SQLite WAL at `HV_DB` path. Tables: `items`, `links`.

---

### 3. DiffForge

**What it is:** Server-side DeltaWalker replacement. Web-based file and directory
comparison with side-by-side diff, char-level highlighting, file upload, and server-path access.

**Key files:**
- `tools/sjl-file-tools/diffforge.py`
- `tools/sjl-file-tools/Containerfile.diffforge`
- `tools/sjl-file-tools/quadlets/diffforge.container`
- `tools/sjl-file-tools/requirements-diffforge.txt`

**Deps:** `fastapi==0.111.0`, `uvicorn[standard]==0.30.1`, `pydantic==2.7.1`, `python-multipart==0.0.9`

**Run:**
```bash
uvicorn diffforge:app --host 0.0.0.0 --port 8082
python diffforge.py --port 8082
```

**Container image:** `localhost/diffforge:latest`  
**Internal port:** `8082`  
**Published on Nexus:** `127.0.0.1:8087:8082`  
**Public URL:** `https://diff.shannonjlove.cloud` → NPM → `localhost:8087`

**Environment variables:**
```
DF_PORT=8082
DF_ALLOW_PATHS=/data   # comma-separated allowed root paths
```

**Key API endpoints:**
| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Web UI |
| `POST` | `/diff/text` | Compare two text strings |
| `POST` | `/diff/files` | Compare two uploaded files |
| `POST` | `/diff/paths` | Compare two server file paths |
| `POST` | `/diff/dirs` | Compare two server directories |

**Web UI tabs:** Text / Upload Files / Server Paths / Directories  
**Data mounted:** `/data` read-only so DiffForge can access server files.

---

## PARA Data Layout on Nexus

```
/data/
├── inbox/              ← FileWarden entry point (all new files)
├── documents/
│   ├── YYYY/MM/        ← PDFs, DOCX, TXT, MD after sjl_rename
├── media/
│   ├── images/YYYY/MM/ ← JPG, PNG, WEBP, HEIC
│   └── video/YYYY/     ← MP4, MOV, MKV
├── downloads/
│   └── archives/       ← ZIP, TAR.GZ, 7Z
├── tagback/
│   └── incoming/       ← TagBack asset ingest (→ n8n webhook)
├── unsorted/           ← Catch-all for unmatched files
└── hookvault/
    └── vault.db        ← HookVault SQLite database
```

---

## Build & Deploy (on Nexus via NeoServer)

Full build script: `tools/sjl-file-tools/DEPLOY.sh`

Quick reference:
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

# Check status
systemctl --user status filewarden hookvault diffforge
```

---

## NPM Proxy Config (Nginx Proxy Manager)

| Domain | → | Upstream |
|---|---|---|
| `hooks.shannonjlove.cloud` | → | `http://localhost:8086` |
| `diff.shannonjlove.cloud` | → | `http://localhost:8087` |

Settings for all: Enable "Block Common Exploits", force SSL, restrict to Tailscale IPs.

FileWarden has no web UI — background daemon only.

---

## n8n Integration

- **TagBack ingest webhook:** `POST https://n8n.shannonjlove.cloud/webhook/tagback-ingest`
  - Body: `{"file": "$FW_FILE", "name": "$FW_NAME", "ext": "$FW_EXT"}`
  - Triggered by FileWarden `run_script` action on `/data/tagback/incoming`

---

## Claude Code Notes

- Always work on feature branches; never push directly to `main`
- This repo (`shannonjlove-github.io`) is the canonical store for SJL infra tooling
- The `tools/sjl-file-tools/` directory is the source of truth for all three services
- Production SHA256 checksum: `fd374d5ac914192de693c76e8ee205645e7bdba8ef5822bc7572dd5175d1d410`
