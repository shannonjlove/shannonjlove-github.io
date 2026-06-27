# SJL Sovereign Cloud — Canonical Five-Digit PARA Structure

**Authority class:** GOVERNANCE-NORMATIVE (derived from Canonical Architecture, File Governance, and Deployment Standard v1.0)  
**Owner:** Shannon J. Love  
**Last updated:** 2026-06-27  
**Canonical source:** `07000_20260621__SJLTEMP20260621000001__canonicalcloudarchitecturegovernancedeploymentstandard__v1-0`

---

## Canonical PARA Categories (01000 – 09000)

Per Section 3 of the governance standard. Four-digit paths are migration aliases only — all new content uses five digits.

| Code  | Category          | Definition |
|-------|-------------------|------------|
| 01000 | INBOX             | Controlled intake, stabilization, and review |
| 02000 | PROJECTS          | Finite active deliverables |
| 03000 | AREAS             | Continuing responsibilities and operations |
| 04000 | RESOURCES         | Reusable references and assets |
| 05000 | ARCHIVES          | Inactive and retained records |
| 06000 | PRIVATE MEDIA     | Restricted media and sensitive assets |
| 07000 | SYSTEM AUTOMATION | Scripts, agents, Quadlets, manifests, manuals, infrastructure |
| 08000 | APPLICATION DATA  | Controlled application exports and state packages |
| 09000 | QUARANTINE        | Conflicts, failures, unsupported data, remediation queues |

---

## Canonical Filename Pattern

```
[PPPPP]_YYYY-MM-DD__DOCID__semantic-title__vMAJOR-MINOR__sha8.ext
```

Example:
```
02001_2026-06-27__SJL-CLOUD-004821__sjl-web-project-brief__v1-0__ed4144cc.pdf
```

---

## iDrive E2 Bucket → PARA Mapping

iDrive E2 is the **off-site persistence layer**: versioned objects, sidecars, manifests, encrypted database backups, and disaster-recovery packages.

### 01000 INBOX → `inbox-idrive-e2`

| Sub-code | Folder | Purpose |
|----------|--------|---------|
| 01001 | `01001-uploads/` | Raw intake from FileWarden / iOS Share Sheet |
| 01002 | `01002-processing/` | Active FileWarden transaction in flight |
| 01003 | `01003-stabilization/` | Write-stable, awaiting hash + TEMPID |
| 01004 | `01004-review/` | Awaiting human review before DOCID promotion |

### 02000 PROJECTS → `projects-idrive-e2`

| Sub-code | Folder | Purpose |
|----------|--------|---------|
| 02001 | `02001-web-projects/` | www, pages, dashboard deliverables |
| 02002 | `02002-media-productions/` | Video, podcast, creative productions |
| 02003 | `02003-dev-projects/` | API, agent, software dev work |
| 02004 | `02004-content-projects/` | Social, writing, branding projects |
| —     | `GRAPHIC ASSETS/` | Legacy (pre-governance, unmigrated) |
| —     | `New Folder With Items/` | Legacy (pre-governance, unmigrated) |

### 03000 AREAS → `areas-idrive-e2`

| Sub-code | Folder | Purpose |
|----------|--------|---------|
| 03001 | `03001-infrastructure-and-ops/` | Cloud infra, VPS, Tailscale, Podman ops |
| 03002 | `03002-content-and-media/` | Ongoing content creation responsibility |
| 03003 | `03003-personal-development/` | Learning, growth, skills |
| 03004 | `03004-editing-and-graphics/` | Ongoing creative/editing work |
| 03005 | `03005-learning-and-tutorials/` | Education resources in active use |
| —     | `Editing & Graphics/` | Legacy (pre-governance, 4023 objects) |
| —     | `learning & tutorials-areas-idrive-e2/` | Legacy (pre-governance) |

### 04000 RESOURCES → `resources-idrive-e2`

| Sub-code | Folder | Purpose |
|----------|--------|---------|
| 04001 | `04001-reference-materials/` | Reference docs, specs, guides |
| 04002 | `04002-tools-and-software/` | Tool configs, software assets |
| 04003 | `04003-design-resources/` | Design kits, palettes, fonts |
| 04004 | `04004-entertainment/` | Entertainment reference media |
| —     | `entertainment-resources-idrive-e2/` | Legacy (pre-governance) |

### 05000 ARCHIVES → `archives-idrive-e2`

| Sub-code | Folder | Purpose |
|----------|--------|---------|
| 05001 | `05001-video-project-archives/` | Completed video productions |
| 05002 | `05002-project-archives/` | Completed project deliverables |
| 05003 | `05003-document-archives/` | Retained documents and records |
| —     | `TheeUndergroundExp Open Mic Promo Video Files/` | Legacy (pre-governance, 468 objects) |

### 06000 PRIVATE MEDIA (three dedicated buckets)

**`private-idrive-e2`** — credentials, private documents:

| Sub-code | Folder |
|----------|--------|
| 06001 | `06001-credentials/` |
| 06002 | `06002-personal-docs/` |
| 06003 | `06003-server-configs/` |
| 06004 | `06004-legal/` |

**`shannon-photos-e2`** — photos (06010–06019):

| Sub-code | Folder |
|----------|--------|
| 06010 | `06010-ios-photos/` |
| 06011 | `06011-organized/` |
| 06012 | `06012-raw/` |
| 06013 | `06013-shared/` |

**`video-media-e2`** — video (06020–06029):

| Sub-code | Folder |
|----------|--------|
| 06020 | `06020-raw-footage/` |
| 06021 | `06021-edited/` |
| 06022 | `06022-exports/` |
| 06023 | `06023-thumbnails/` |
| 06024 | `06024-b-roll/` |

**`graphics-media-e2`** — graphics (06030–06039):

| Sub-code | Folder |
|----------|--------|
| 06030 | `06030-brand-assets/` |
| 06031 | `06031-templates/` |
| 06032 | `06032-stock/` |
| 06033 | `06033-exported/` |
| 06034 | `06034-mockups/` |

### 07000 SYSTEM AUTOMATION (three dedicated buckets)

**`agent-data-e2`** — AI agent / Claude Code (07010–07019):

| Sub-code | Folder |
|----------|--------|
| 07010 | `07010-context/` |
| 07011 | `07011-memory/` |
| 07012 | `07012-sessions/` |
| 07013 | `07013-logs/` |

**`assets-e2`** — static web assets (07020–07029):

| Sub-code | Folder |
|----------|--------|
| 07020 | `07020-css/` |
| 07021 | `07021-js/` |
| 07022 | `07022-images/` |
| 07023 | `07023-fonts/` |
| 07024 | `07024-icons/` |

**`stacks-backups-e2`** — Podman / Quadlet infrastructure (07030–07039):

| Sub-code | Folder |
|----------|--------|
| 07030 | `07030-compose-files/` |
| 07031 | `07031-volumes/` |
| 07032 | `07032-configs/` |
| 07033 | `07033-secrets/` |

### 08000 APPLICATION DATA (three dedicated buckets)

**`n8n-backups-e2`** — n8n automation (08010–08019):

| Sub-code | Folder |
|----------|--------|
| 08010 | `08010-workflows/` |
| 08011 | `08011-credentials/` |
| 08012 | `08012-executions/` |
| 08013 | `08013-exports/` |

**`bookstack-data-e2`** — BookStack wiki (08020–08029):

| Sub-code | Folder |
|----------|--------|
| 08020 | `08020-database-backups/` |
| 08021 | `08021-file-attachments/` |
| 08022 | `08022-exports/` |
| 08023 | `08023-themes/` |

**`paperless-docs-e2`** — Paperless-NGX / PaperParrot governed archive (08030–08039):

| Sub-code | Folder | Note |
|----------|--------|------|
| —     | `documents/` | Paperless-managed (originals, archive, thumbnails) — do not move |
| 08030 | `08030-database-backups/` | PostgreSQL mirror registry backups |
| 08031 | `08031-exports/` | Governed export packages |

### 09000 QUARANTINE → `quarantine-e2`

| Sub-code | Folder | Purpose |
|----------|--------|---------|
| 09001 | `09001-conflicts/` | Identity, hash, or path conflicts routed from FileWarden |
| 09002 | `09002-failures/` | Failed transactions requiring remediation |
| 09003 | `09003-unsupported/` | Unsupported formats or data types |
| 09004 | `09004-remediation/` | Items under active remediation review |

---

## Raindrop.io Collection Hierarchy

```
📁 01000 • INBOX
📁 02000 • PROJECTS
    📁 02001 • Web Projects
    📁 02002 • Media Productions
    📁 02003 • Dev Projects
    📁 02004 • Content Projects
📁 03000 • AREAS
    📁 03001 • Infrastructure & Ops
    📁 03002 • Content & Media
    📁 03003 • Personal Development
    📁 03004 • Editing & Graphics
    📁 03005 • Learning & Tutorials
📁 04000 • RESOURCES
    📁 04001 • Reference Materials
    📁 04002 • Tools & Software
    📁 04003 • Design Resources
    📁 04004 • Entertainment
📁 05000 • ARCHIVES
    📁 05001 • Video Project Archives
    📁 05002 • Project Archives
    📁 05003 • Document Archives
📁 06000 • PRIVATE MEDIA
    📁 06001 • Credentials & Private Docs
    📁 06010 • Photos
    📁 06020 • Video Media
    📁 06030 • Graphics & Assets
📁 07000 • SYSTEM AUTOMATION
    📁 07010 • Agent (Claude Code)
    📁 07020 • Static Assets
    📁 07030 • Stacks & Quadlets
📁 08000 • APPLICATION DATA
    📁 08010 • n8n
    📁 08020 • BookStack
    📁 08030 • Paperless / PaperParrot
📁 09000 • QUARANTINE
    📁 09001 • Conflicts
    📁 09004 • Remediation
```

**Tag convention:** Every bookmark tagged `#02001`, `#07030`, etc. for cross-collection smart search.

---

## Apple Notes — Forever Notes Framework

```
📁 🗂 INDEX
    📄 SJL PARA Master Index      ← pinned; links to all category index notes

📁 01000 • INBOX
    📄 01000 Inbox Index

📁 02000 • PROJECTS
    📄 02000 Projects Index
    📄 02001 Web Projects
    📄 02002 Media Productions
    📄 02003 Dev Projects
    📄 02004 Content Projects

📁 03000 • AREAS
    📄 03000 Areas Index
    📄 03001 Infrastructure & Ops
    📄 03002 Content & Media
    📄 03003 Personal Development
    📄 03004 Editing & Graphics
    📄 03005 Learning & Tutorials

📁 04000 • RESOURCES
    📄 04000 Resources Index
    📄 04001 Reference Materials
    📄 04002 Tools & Software
    📄 04003 Design Resources
    📄 04004 Entertainment

📁 05000 • ARCHIVES
    📄 05000 Archives Index
    📄 05001 Video Project Archives
    📄 05002 Project Archives
    📄 05003 Document Archives

📁 06000 • PRIVATE MEDIA
    📄 06000 Private Media Index
    📄 06001 Credentials & Private Docs
    📄 06010 Photos (pics.shannonjlove.cloud)
    📄 06020 Video Media
    📄 06030 Graphics & Assets

📁 07000 • SYSTEM AUTOMATION
    📄 07000 System Automation Index
    📄 07010 Agent — Claude Code
    📄 07020 Static Assets
    📄 07030 Stacks & Quadlets

📁 08000 • APPLICATION DATA
    📄 08000 Application Data Index
    📄 08010 n8n (n8n.shannonjlove.cloud)
    📄 08020 BookStack (bookstack.shannonjlove.cloud)
    📄 08030 Paperless / PaperParrot

📁 09000 • QUARANTINE
    📄 09000 Quarantine Index
    📄 09001 Conflicts
    📄 09004 Remediation
```

**Forever Notes rules:**
- Every note title begins with its 5-digit code.
- Each category folder has a pinned Index note linking all child notes.
- Notes that go inactive migrate to the matching `05xxx` Archive folder (not a separate PARA Archive).
- Secrets, credentials, and tokens are never placed in note bodies.

---

## TickTick — Folders and Lists

```
📁 01000 INBOX
    📋 01001 • Uploads & Intake
    📋 01004 • Review Queue

📁 02000 PROJECTS
    📋 02001 • Web Projects
    📋 02002 • Media Productions
    📋 02003 • Dev Projects
    📋 02004 • Content Projects

📁 03000 AREAS
    📋 03001 • Infrastructure & Ops
    📋 03002 • Content & Media
    📋 03003 • Personal Development
    📋 03004 • Editing & Graphics
    📋 03005 • Learning & Tutorials

📁 04000 RESOURCES
    📋 04001 • Reference Materials
    📋 04002 • Tools & Software
    📋 04003 • Design Resources

📁 05000 ARCHIVES
    📋 05002 • Project Archives
    📋 05003 • Document Archives

📁 07000 SYSTEM AUTOMATION
    📋 07010 • Agent Tasks
    📋 07030 • Stacks & Infra Ops

📁 08000 APPLICATION DATA
    📋 08010 • n8n Tasks
    📋 08020 • BookStack Tasks
    📋 08030 • Paperless Tasks

📁 09000 QUARANTINE
    📋 09001 • Conflicts
    📋 09004 • Remediation
```

**Tag convention:** Every task tagged `#02001`, `#03001`, etc. Use TickTick Smart Lists to filter by PARA code across all lists.

---

## Cross-Platform Quick Reference

| Code  | Name                     | iDrive E2 Bucket             | Raindrop       | Apple Notes Folder | TickTick List      |
|-------|--------------------------|------------------------------|----------------|--------------------|--------------------|
| 01000 | INBOX                    | `inbox-idrive-e2`            | 01000          | 01000              | 01000              |
| 02001 | Web Projects             | `projects-idrive-e2`         | 02000 › 02001  | 02000 › 02001      | 02000 › 02001      |
| 02002 | Media Productions        | `projects-idrive-e2`         | 02000 › 02002  | 02000 › 02002      | 02000 › 02002      |
| 02003 | Dev Projects             | `projects-idrive-e2`         | 02000 › 02003  | 02000 › 02003      | 02000 › 02003      |
| 02004 | Content Projects         | `projects-idrive-e2`         | 02000 › 02004  | 02000 › 02004      | 02000 › 02004      |
| 03001 | Infrastructure & Ops     | `areas-idrive-e2`            | 03000 › 03001  | 03000 › 03001      | 03000 › 03001      |
| 03002 | Content & Media          | `areas-idrive-e2`            | 03000 › 03002  | 03000 › 03002      | 03000 › 03002      |
| 03003 | Personal Development     | `areas-idrive-e2`            | 03000 › 03003  | 03000 › 03003      | 03000 › 03003      |
| 04001 | Reference Materials      | `resources-idrive-e2`        | 04000 › 04001  | 04000 › 04001      | 04000 › 04001      |
| 04002 | Tools & Software         | `resources-idrive-e2`        | 04000 › 04002  | 04000 › 04002      | 04000 › 04002      |
| 05001 | Video Archives           | `archives-idrive-e2`         | 05000 › 05001  | 05000 › 05001      | 05000 › 05001      |
| 05002 | Project Archives         | `archives-idrive-e2`         | 05000 › 05002  | 05000 › 05002      | 05000 › 05002      |
| 06001 | Credentials / Private    | `private-idrive-e2`          | 06000 › 06001  | 06000 › 06001      | —                  |
| 06010 | Photos                   | `shannon-photos-e2`          | 06000 › 06010  | 06000 › 06010      | —                  |
| 06020 | Video Media              | `video-media-e2`             | 06000 › 06020  | 06000 › 06020      | —                  |
| 06030 | Graphics & Assets        | `graphics-media-e2`          | 06000 › 06030  | 06000 › 06030      | —                  |
| 07010 | Agent (Claude Code)      | `agent-data-e2`              | 07000 › 07010  | 07000 › 07010      | 07000 › 07010      |
| 07020 | Static Assets            | `assets-e2`                  | 07000 › 07020  | 07000 › 07020      | —                  |
| 07030 | Stacks & Quadlets        | `stacks-backups-e2`          | 07000 › 07030  | 07000 › 07030      | 07000 › 07030      |
| 08010 | n8n                      | `n8n-backups-e2`             | 08000 › 08010  | 08000 › 08010      | 08000 › 08010      |
| 08020 | BookStack                | `bookstack-data-e2`          | 08000 › 08020  | 08000 › 08020      | 08000 › 08020      |
| 08030 | Paperless / PaperParrot  | `paperless-docs-e2`          | 08000 › 08030  | 08000 › 08030      | 08000 › 08030      |
| 09000 | QUARANTINE               | `quarantine-e2`              | 09000          | 09000              | 09000              |
