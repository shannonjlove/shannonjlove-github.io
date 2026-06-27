# SJL PARA 5-Digit Numbering System

Unified code system applied across iDrive S3, Raindrop.io, Apple Notes, and TickTick.
Every bucket, folder, collection, note folder, and task list shares the same code.

---

## Code Structure

```
1xxxx  →  PROJECTS   (active, deadline-bound work)
2xxxx  →  AREAS      (ongoing responsibilities with no end date)
3xxxx  →  RESOURCES  (reference material, tools, knowledge)
4xxxx  →  ARCHIVES   (completed / inactive / legacy)
5xxxx  →  SERVICES   (cloud storage buckets mapped to live services)
```

Sub-items: `PPPPP-NN` where `PPPPP` is the parent code and `NN` is a two-digit sequence.

---

## Master Code Table

### PROJECTS — 1xxxx

| Code  | Name                    | iDrive S3 Bucket → Folder              |
|-------|-------------------------|----------------------------------------|
| 10000 | Projects (root)         | `projects-idrive-e2/`                  |
| 10001 | Web Projects            | `projects-idrive-e2/10001-web-projects/` |
| 10002 | Media Productions       | `projects-idrive-e2/10002-media-productions/` |
| 10003 | Dev Projects            | `projects-idrive-e2/10003-dev-projects/` |
| 10004 | Content Projects        | `projects-idrive-e2/10004-content-projects/` |

### AREAS — 2xxxx

| Code  | Name                    | iDrive S3 Bucket → Folder              |
|-------|-------------------------|----------------------------------------|
| 20000 | Areas (root)            | `areas-idrive-e2/`                     |
| 20001 | Infrastructure & Ops    | `areas-idrive-e2/20001-infrastructure-and-ops/` |
| 20002 | Content & Media         | `areas-idrive-e2/20002-content-and-media/` |
| 20003 | Personal Development    | `areas-idrive-e2/20003-personal-development/` |
| 20004 | Editing & Graphics      | `areas-idrive-e2/Editing & Graphics/` (legacy) |
| 20005 | Learning & Tutorials    | `areas-idrive-e2/learning & tutorials-areas-idrive-e2/` (legacy) |

### RESOURCES — 3xxxx

| Code  | Name                    | iDrive S3 Bucket → Folder              |
|-------|-------------------------|----------------------------------------|
| 30000 | Resources (root)        | `resources-idrive-e2/`                 |
| 30001 | Reference Materials     | `resources-idrive-e2/30001-reference-materials/` |
| 30002 | Tools & Software        | `resources-idrive-e2/30002-tools-and-software/` |
| 30003 | Design Resources        | `resources-idrive-e2/30003-design-resources/` |
| 30004 | Entertainment           | `resources-idrive-e2/entertainment-resources-idrive-e2/` (legacy) |

### ARCHIVES — 4xxxx

| Code  | Name                    | iDrive S3 Bucket → Folder              |
|-------|-------------------------|----------------------------------------|
| 40000 | Archives (root)         | `archives-idrive-e2/`                  |
| 40001 | Video Project Archives  | `archives-idrive-e2/40001-video-project-archives/` |
| 40002 | Project Archives        | `archives-idrive-e2/40002-project-archives/` |
| 40003 | Document Archives       | `archives-idrive-e2/40003-document-archives/` |
| 40004 | TheeUndergroundExp      | `archives-idrive-e2/TheeUndergroundExp Open Mic Promo Video Files/` (legacy) |

### SERVICES — 5xxxx

| Code  | Bucket                | Cloud Service                    | Sub-folders |
|-------|-----------------------|----------------------------------|-------------|
| 50001 | `paperless-docs-e2`   | `docs.shannonjlove.cloud`        | `documents/{originals,archive,thumbnails}` |
| 50002 | `shannon-photos-e2`   | `pics.shannonjlove.cloud`        | `50002-01-ios-photos`, `50002-02-organized`, `50002-03-raw`, `50002-04-shared` |
| 50003 | `video-media-e2`      | `media.shannonjlove.cloud`       | `50003-01-raw-footage`, `50003-02-edited`, `50003-03-exports`, `50003-04-thumbnails`, `50003-05-b-roll` |
| 50004 | `graphics-media-e2`   | `assets.shannonjlove.cloud`      | `50004-01-brand-assets`, `50004-02-templates`, `50004-03-stock`, `50004-04-exported`, `50004-05-mockups` |
| 50005 | `private-idrive-e2`   | `private.shannonjlove.cloud`     | `50005-01-credentials`, `50005-02-personal`, `50005-03-server-configs`, `50005-04-legal` |
| 50006 | `inbox-idrive-e2`     | (staging pipeline)               | `50006-01-uploads`, `50006-02-processing`, `50006-03-completed`, `50006-04-failed` |
| 50007 | `assets-e2`           | `assets.shannonjlove.cloud`      | `50007-01-css`, `50007-02-js`, `50007-03-images`, `50007-04-fonts`, `50007-05-icons` |
| 50008 | `n8n-backups-e2`      | `n8n.shannonjlove.cloud`         | `50008-01-workflows`, `50008-02-credentials`, `50008-03-executions`, `50008-04-exports` |
| 50009 | `bookstack-data-e2`   | `bookstack.shannonjlove.cloud`   | `50009-01-database-backups`, `50009-02-file-attachments`, `50009-03-exports`, `50009-04-themes` |
| 50010 | `agent-data-e2`       | `agent.shannonjlove.cloud`       | `50010-01-context`, `50010-02-memory`, `50010-03-sessions`, `50010-04-logs` |
| 50011 | `stacks-backups-e2`   | `stacks.shannonjlove.cloud`      | `50011-01-compose-files`, `50011-02-volumes`, `50011-03-configs`, `50011-04-secrets` |

---

## Raindrop.io Collection Hierarchy

Mirror this exact structure in Raindrop.io collections:

```
📁 10000 • PROJECTS
    📁 10001 • Web Projects
    📁 10002 • Media Productions
    📁 10003 • Dev Projects
    📁 10004 • Content Projects

📁 20000 • AREAS
    📁 20001 • Infrastructure & Ops
    📁 20002 • Content & Media
    📁 20003 • Personal Development
    📁 20004 • Editing & Graphics
    📁 20005 • Learning & Tutorials

📁 30000 • RESOURCES
    📁 30001 • Reference Materials
    📁 30002 • Tools & Software
    📁 30003 • Design Resources
    📁 30004 • Entertainment

📁 40000 • ARCHIVES
    📁 40001 • Video Project Archives
    📁 40002 • Project Archives
    📁 40003 • Document Archives

📁 50000 • SJL CLOUD SERVICES
    📁 50001 • Docs (Paperless)
    📁 50002 • Photos
    📁 50003 • Video Media
    📁 50004 • Graphics & Assets
    📁 50005 • Private
    📁 50006 • Inbox
    📁 50007 • Static Assets
    📁 50008 • n8n
    📁 50009 • BookStack
    📁 50010 • Agent
    📁 50011 • Stacks
```

**Raindrop tagging convention:** Tag every bookmark with its PARA code (e.g., `#10001`, `#30002`) for cross-collection search.

---

## Apple Notes — Forever Notes Framework

Folder structure for Apple Notes. Each numbered folder contains:
- An **Index note** (pinned) that links to all notes within
- **Topic notes** named starting with the 5-digit code

```
📁 🗂 INDEX
    📄 SJL PARA Master Index    ← links to all 1xxxx–5xxxx index notes

📁 10000 • PROJECTS
    📄 10000 Projects Index
    📄 10001 Web Projects
    📄 10002 Media Productions
    📄 10003 Dev Projects
    📄 10004 Content Projects

📁 20000 • AREAS
    📄 20000 Areas Index
    📄 20001 Infrastructure & Ops
    📄 20002 Content & Media
    📄 20003 Personal Development
    📄 20004 Editing & Graphics
    📄 20005 Learning & Tutorials

📁 30000 • RESOURCES
    📄 30000 Resources Index
    📄 30001 Reference Materials
    📄 30002 Tools & Software
    📄 30003 Design Resources
    📄 30004 Entertainment

📁 40000 • ARCHIVES
    📄 40000 Archives Index
    📄 40001 Video Project Archives
    📄 40002 Project Archives
    📄 40003 Document Archives

📁 50000 • SJL CLOUD
    📄 50000 Cloud Services Index
    📄 50001 Paperless Docs
    📄 50002 Photos (pics.shannonjlove.cloud)
    📄 50003 Video Media
    📄 50004 Graphics & Assets
    📄 50005 Private
    📄 50006 Inbox / Pipeline
    📄 50007 Static Assets
    📄 50008 n8n Automation
    📄 50009 BookStack Wiki
    📄 50010 AI Agent
    📄 50011 Stacks & Infra
```

**Forever Notes convention:** Each note's title begins with the 5-digit code.
Index notes use a checklist linking to child notes by name.
Notes that age out of active use move to the matching 4xxxx Archive folder.

---

## TickTick — Projects & Lists

TickTick uses **Folders** (PARA categories) containing **Lists** (sub-items).

```
📁 10000 PROJECTS
    📋 10001 • Web Projects
    📋 10002 • Media Productions
    📋 10003 • Dev Projects
    📋 10004 • Content Projects

📁 20000 AREAS
    📋 20001 • Infrastructure & Ops
    📋 20002 • Content & Media
    📋 20003 • Personal Development
    📋 20004 • Editing & Graphics
    📋 20005 • Learning & Tutorials

📁 30000 RESOURCES
    📋 30001 • Reference Materials
    📋 30002 • Tools & Software
    📋 30003 • Design Resources
    📋 30004 • Entertainment

📁 40000 ARCHIVES
    📋 40001 • Video Project Archives
    📋 40002 • Project Archives
    📋 40003 • Document Archives

📁 50000 SJL CLOUD OPS
    📋 50005 • Private / Credentials
    📋 50006 • Inbox Tasks
    📋 50008 • n8n Workflows
    📋 50009 • BookStack
    📋 50010 • Agent
    📋 50011 • Stacks & Infra
```

**TickTick task tagging convention:**
- Tag every task with its PARA code: `#10001`, `#20001`, etc.
- Use Smart Lists / filters on these tags to create cross-list views per PARA category.

---

## Cross-Platform Quick Reference

| Code  | Name                 | S3 Bucket                  | Raindrop            | Apple Notes Folder    | TickTick List          |
|-------|----------------------|----------------------------|---------------------|----------------------|------------------------|
| 10001 | Web Projects         | projects-idrive-e2         | 10000 › 10001       | 10000 › 10001        | 10000 › 10001          |
| 10002 | Media Productions    | projects-idrive-e2         | 10000 › 10002       | 10000 › 10002        | 10000 › 10002          |
| 10003 | Dev Projects         | projects-idrive-e2         | 10000 › 10003       | 10000 › 10003        | 10000 › 10003          |
| 10004 | Content Projects     | projects-idrive-e2         | 10000 › 10004       | 10000 › 10004        | 10000 › 10004          |
| 20001 | Infra & Ops          | areas-idrive-e2            | 20000 › 20001       | 20000 › 20001        | 20000 › 20001          |
| 20002 | Content & Media      | areas-idrive-e2            | 20000 › 20002       | 20000 › 20002        | 20000 › 20002          |
| 20003 | Personal Dev         | areas-idrive-e2            | 20000 › 20003       | 20000 › 20003        | 20000 › 20003          |
| 30001 | Reference            | resources-idrive-e2        | 30000 › 30001       | 30000 › 30001        | 30000 › 30001          |
| 30002 | Tools & Software     | resources-idrive-e2        | 30000 › 30002       | 30000 › 30002        | 30000 › 30002          |
| 30003 | Design Resources     | resources-idrive-e2        | 30000 › 30003       | 30000 › 30003        | 30000 › 30003          |
| 40001 | Video Archives       | archives-idrive-e2         | 40000 › 40001       | 40000 › 40001        | 40000 › 40001          |
| 40002 | Project Archives     | archives-idrive-e2         | 40000 › 40002       | 40000 › 40002        | 40000 › 40002          |
| 50001 | Paperless Docs       | paperless-docs-e2          | 50000 › 50001       | 50000 › 50001        | —                      |
| 50002 | Photos               | shannon-photos-e2          | 50000 › 50002       | 50000 › 50002        | —                      |
| 50003 | Video Media          | video-media-e2             | 50000 › 50003       | 50000 › 50003        | —                      |
| 50004 | Graphics             | graphics-media-e2          | 50000 › 50004       | 50000 › 50004        | —                      |
| 50005 | Private              | private-idrive-e2          | 50000 › 50005       | 50000 › 50005        | 50000 › 50005          |
| 50006 | Inbox                | inbox-idrive-e2            | 50000 › 50006       | 50000 › 50006        | 50000 › 50006          |
| 50007 | Static Assets        | assets-e2                  | 50000 › 50007       | 50000 › 50007        | —                      |
| 50008 | n8n                  | n8n-backups-e2             | 50000 › 50008       | 50000 › 50008        | 50000 › 50008          |
| 50009 | BookStack            | bookstack-data-e2          | 50000 › 50009       | 50000 › 50009        | 50000 › 50009          |
| 50010 | Agent                | agent-data-e2              | 50000 › 50010       | 50000 › 50010        | 50000 › 50010          |
| 50011 | Stacks               | stacks-backups-e2          | 50000 › 50011       | 50000 › 50011        | 50000 › 50011          |
