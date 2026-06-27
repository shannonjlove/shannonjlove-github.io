# iDrive E2 (S3) Storage Organization

**Account endpoint:** `p3h2.va.idrivee2-48.com`  
**Region:** `us-east-1`  
**Last organized:** 2026-06-27  
**Authority:** Derived from SJL Sovereign Cloud Canonical Architecture v1.0 (GOVERNANCE-NORMATIVE)  
**Numbering:** See [para-numbering-system.md](./para-numbering-system.md) — 5-digit canonical codes 01000–09000, mirrored in Raindrop.io, Apple Notes, and TickTick.

iDrive E2 role (per governance standard): **off-site persistence layer** — versioned objects, sidecars, manifests, encrypted database backups, and disaster-recovery packages. No operational runbook or convenience shortcut may override the canonical standard.

---

## Bucket Summary (16 total)

| PARA Code | Bucket | Cloud Service / Purpose |
|-----------|--------|------------------------|
| 01000 | `inbox-idrive-e2` | FileWarden intake pipeline |
| 02000 | `projects-idrive-e2` | Active deliverables (PARA Projects) |
| 03000 | `areas-idrive-e2` | Ongoing responsibilities (PARA Areas) |
| 04000 | `resources-idrive-e2` | Reference and reusable assets (PARA Resources) |
| 05000 | `archives-idrive-e2` | Inactive retained records (PARA Archives) |
| 06000 | `private-idrive-e2` | Restricted private docs / credentials |
| 06000 | `shannon-photos-e2` | Photo library (`pics.shannonjlove.cloud`) |
| 06000 | `video-media-e2` | Video media (`media.shannonjlove.cloud`) |
| 06000 | `graphics-media-e2` | Graphics and design assets |
| 07000 | `agent-data-e2` | Claude Code / AI agent (`agent.shannonjlove.cloud`) |
| 07000 | `assets-e2` | Static web assets (`assets.shannonjlove.cloud`) |
| 07000 | `stacks-backups-e2` | Podman / Quadlet infrastructure (`stacks.shannonjlove.cloud`) |
| 08000 | `n8n-backups-e2` | n8n automation data (`n8n.shannonjlove.cloud`) |
| 08000 | `bookstack-data-e2` | BookStack wiki data (`bookstack.shannonjlove.cloud`) |
| 08000 | `paperless-docs-e2` | Paperless-NGX governed archive (`docs.shannonjlove.cloud`) |
| 09000 | `quarantine-e2` | Conflicts, failures, remediation queue |

---

## Folder Structure by Bucket

### `inbox-idrive-e2` (01000 INBOX)
```
01001-uploads/
01002-processing/
01003-stabilization/
01004-review/
```

### `projects-idrive-e2` (02000 PROJECTS)
```
02001-web-projects/
02002-media-productions/
02003-dev-projects/
02004-content-projects/
GRAPHIC ASSETS/             ← legacy, pre-governance (279 objects)
New Folder With Items/      ← legacy, pre-governance
```

### `areas-idrive-e2` (03000 AREAS)
```
03001-infrastructure-and-ops/
03002-content-and-media/
03003-personal-development/
03004-editing-and-graphics/
03005-learning-and-tutorials/
Editing & Graphics/                         ← legacy (4023 objects)
learning & tutorials-areas-idrive-e2/       ← legacy
```

### `resources-idrive-e2` (04000 RESOURCES)
```
04001-reference-materials/
04002-tools-and-software/
04003-design-resources/
04004-entertainment/
entertainment-resources-idrive-e2/          ← legacy
```

### `archives-idrive-e2` (05000 ARCHIVES)
```
05001-video-project-archives/
05002-project-archives/
05003-document-archives/
TheeUndergroundExp Open Mic Promo Video Files/  ← legacy (468 objects)
```

### `private-idrive-e2` (06000 PRIVATE MEDIA)
```
06001-credentials/
06002-personal-docs/
06003-server-configs/
06004-legal/
```

### `shannon-photos-e2` (06000 · 06010–06019)
```
06010-ios-photos/
06011-organized/
06012-raw/
06013-shared/
```

### `video-media-e2` (06000 · 06020–06029)
```
06020-raw-footage/
06021-edited/
06022-exports/
06023-thumbnails/
06024-b-roll/
```

### `graphics-media-e2` (06000 · 06030–06039)
```
06030-brand-assets/
06031-templates/
06032-stock/
06033-exported/
06034-mockups/
```

### `agent-data-e2` (07000 · 07010–07019)
```
07010-context/
07011-memory/
07012-sessions/
07013-logs/
```

### `assets-e2` (07000 · 07020–07029)
```
07020-css/
07021-js/
07022-images/
07023-fonts/
07024-icons/
```

### `stacks-backups-e2` (07000 · 07030–07039)
```
07030-compose-files/
07031-volumes/
07032-configs/
07033-secrets/
```

### `n8n-backups-e2` (08000 · 08010–08019)
```
08010-workflows/
08011-credentials/
08012-executions/
08013-exports/
```

### `bookstack-data-e2` (08000 · 08020–08029)
```
08020-database-backups/
08021-file-attachments/
08022-exports/
08023-themes/
```

### `paperless-docs-e2` (08000 · 08030–08039)
```
documents/                  ← Paperless-NGX managed (originals, archive, thumbnails — do not move)
08030-database-backups/
08031-exports/
```

### `quarantine-e2` (09000 QUARANTINE)
```
09001-conflicts/
09002-failures/
09003-unsupported/
09004-remediation/
```

---

## System-of-Record Boundaries (per governance standard)

| System | Authority |
|--------|-----------|
| BookStack | Human-readable architecture, manuals, change narratives |
| PostgreSQL Registry | DOCIDs, hashes, versions, paths, events, mirror status |
| Git | Scripts, Quadlets, schemas, tests, agent-context files |
| Paperless / PaperParrot | Finalized manuals, governed archival records, compliance copies |
| **iDrive E2** | **Off-site objects, sidecars, manifests, encrypted DB backups, DR packages** |

No platform may silently become authoritative for data outside its assigned role.

---

## DNS → Bucket Mapping

| Subdomain | Bucket | PARA Code |
|-----------|--------|-----------|
| `agent.shannonjlove.cloud` | `agent-data-e2` | 07000 · 07010 |
| `assets.shannonjlove.cloud` | `assets-e2`, `graphics-media-e2` | 07000 · 07020 / 06000 · 06030 |
| `bookstack.shannonjlove.cloud` | `bookstack-data-e2` | 08000 · 08020 |
| `docs.shannonjlove.cloud` | `paperless-docs-e2` | 08000 · 08030 |
| `media.shannonjlove.cloud` | `video-media-e2` | 06000 · 06020 |
| `n8n.shannonjlove.cloud` | `n8n-backups-e2` | 08000 · 08010 |
| `pics.shannonjlove.cloud` | `shannon-photos-e2` | 06000 · 06010 |
| `private.shannonjlove.cloud` | `private-idrive-e2` | 06000 · 06001 |
| `stacks.shannonjlove.cloud` | `stacks-backups-e2` | 07000 · 07030 |
| `www / pages / dashboard` | (served from VPS — no S3 backing) | — |
| `admin / api / status` | (Tailscale-only — no S3 backing) | — |
