# iDrive E2 (S3) Storage Organization

**Account endpoint:** `p3h2.va.idrivee2-48.com`  
**Region:** `us-east-1`  
**Last organized:** 2026-06-27

---

## Bucket Map — Cloud Services

| Bucket | Cloud Service | Purpose |
|--------|--------------|---------|
| `assets-e2` | `assets.shannonjlove.cloud` | Static web assets (CSS, JS, images, fonts, icons) |
| `agent-data-e2` | `agent.shannonjlove.cloud` | AI agent context, memory, sessions, logs |
| `n8n-backups-e2` | `n8n.shannonjlove.cloud` | n8n workflow exports, credentials, execution logs |
| `bookstack-data-e2` | `bookstack.shannonjlove.cloud` | BookStack DB backups, file attachments, exports |
| `stacks-backups-e2` | `stacks.shannonjlove.cloud` | Docker compose files, volume backups, configs |
| `paperless-docs-e2` | `docs.shannonjlove.cloud` | Paperless-NGX originals, archives, thumbnails |
| `shannon-photos-e2` | `pics.shannonjlove.cloud` | iOS photos, organized library, raw/shared |
| `video-media-e2` | `media.shannonjlove.cloud` | Raw footage, edited cuts, exports, thumbnails |
| `graphics-media-e2` | `media.shannonjlove.cloud` / `assets.shannonjlove.cloud` | Brand assets, design templates, stock, mockups |
| `private-idrive-e2` | `private.shannonjlove.cloud` | Credentials, personal docs, server configs, legal |
| `inbox-idrive-e2` | (staging) | Upload queue, processing pipeline, completed/failed |

---

## Bucket Map — PARA Organization

| Bucket | Category | Purpose |
|--------|----------|---------|
| `projects-idrive-e2` | Projects | Active project work (web, media, dev, content) |
| `areas-idrive-e2` | Areas | Ongoing responsibilities (editing/graphics, content, ops, learning) |
| `resources-idrive-e2` | Resources | Reference materials, tools, design resources |
| `archives-idrive-e2` | Archives | Completed video projects, project archives, document archives |

---

## Folder Structure

### `assets-e2/`
```
css/
js/
images/
fonts/
icons/
```

### `agent-data-e2/`
```
context/
memory/
sessions/
logs/
```

### `n8n-backups-e2/`
```
workflows/
credentials/
executions/
exports/
```

### `bookstack-data-e2/`
```
database-backups/
file-attachments/
exports/
themes/
```

### `stacks-backups-e2/`
```
compose-files/
volumes/
configs/
secrets/
```

### `paperless-docs-e2/`
```
documents/
  originals/
  archive/
  thumbnails/
```

### `shannon-photos-e2/`
```
ios-photos/
organized/
  YYYY/
raw/
shared/
```

### `video-media-e2/`
```
raw-footage/
edited/
exports/
thumbnails/
b-roll/
```

### `graphics-media-e2/`
```
brand-assets/
templates/
stock/
exported/
mockups/
```

### `private-idrive-e2/`
```
credentials/
personal/
server-configs/
legal/
```

### `inbox-idrive-e2/`
```
uploads/
processing/
completed/
failed/
```

### `projects-idrive-e2/`
```
web-projects/       ← www, pages, dashboard
media-productions/  ← video, podcast, creative
dev-projects/       ← API, agent, software
content-projects/   ← social, writing, branding
GRAPHIC ASSETS/     ← (legacy — mockup templates)
```

### `areas-idrive-e2/`
```
Editing & Graphics/             ← (legacy C4D / FCPX work)
learning & tutorials-.../       ← (legacy)
infrastructure-and-ops/
content-and-media/
personal-development/
```

### `resources-idrive-e2/`
```
entertainment-resources-.../    ← (legacy)
reference-materials/
tools-and-software/
design-resources/
```

### `archives-idrive-e2/`
```
TheeUndergroundExp Open Mic.../  ← (legacy FCPX project)
video-project-archives/
project-archives/
document-archives/
```

---

## DNS → Storage Mapping

| Subdomain | Bucket(s) |
|-----------|-----------|
| `www.shannonjlove.cloud` | (served from VPS, no S3 backing) |
| `agent.shannonjlove.cloud` | `agent-data-e2` |
| `status.shannonjlove.cloud` | (served from VPS) |
| `assets.shannonjlove.cloud` | `assets-e2`, `graphics-media-e2` |
| `stacks.shannonjlove.cloud` | `stacks-backups-e2` |
| `pages.shannonjlove.cloud` | (served from VPS) |
| `docs.shannonjlove.cloud` | `paperless-docs-e2` |
| `pics.shannonjlove.cloud` | `shannon-photos-e2` |
| `media.shannonjlove.cloud` | `video-media-e2`, `graphics-media-e2` |
| `n8n.shannonjlove.cloud` | `n8n-backups-e2` |
| `bookstack.shannonjlove.cloud` | `bookstack-data-e2` |
| `api.shannonjlove.cloud` | (served from VPS) |
| `private.shannonjlove.cloud` | `private-idrive-e2` |
| `dashboard.shannonjlove.cloud` | (served from VPS) |
| `admin.shannonjlove.cloud` | (served from VPS) |
| `webtop.shannonjlove.cloud` | (served from VPS) |
| `rclone-mcp.shannonjlove.cloud` | (MCP server on VPS) |
