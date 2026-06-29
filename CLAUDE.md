# CLAUDE.md — Shannon J. Love | shannonjlove.cloud

---

## !! GOVERNING RULE — READ THIS FIRST, EVERY TIME !!

> **This section is the single most authoritative piece of information in this entire project.**
> No file is created, renamed, moved, uploaded, or migrated without following these rules.
> This applies to ALL cloud services, ALL tools, ALL automations, and ALL manual actions.

---

## SJL Canonical File Naming Convention

Every file — regardless of cloud service, type, or purpose — must follow this format:

```
YYYY-MM-DD_HH-MM_category-subcategory_description_UUID24.ext
```

### Format breakdown

| Segment | Format | Example |
|---|---|---|
| Date | `YYYY-MM-DD` | `2026-06-29` |
| Time | `HH-MM` (24h) | `14-30` |
| Category | lowercase, hyphen-separated | `media` |
| Subcategory | lowercase, hyphen-separated | `video` |
| Description | lowercase, hyphens only, max 40 chars | `austin-walk-thru` |
| UUID24 | 24-char hex from uuid4 | `a1b2c3d4e5f6a1b2c3d4e5f6` |
| Extension | lowercase | `.mov` |

**Full example:**
```
2026-06-29_14-30_media-video_austin-walk-thru_a1b2c3d4e5f6a1b2c3d4e5f6.mov
```

### Approved Category · Subcategory Taxonomy

| Category | Subcategories |
|---|---|
| `document` | `pdf` · `text` · `spreadsheet` · `presentation` · `form` |
| `media` | `image` · `video` · `audio` · `raw` |
| `code` | `script` · `config` · `repo` · `deploy` |
| `finance` | `receipt` · `invoice` · `statement` · `budget` |
| `legal` | `contract` · `filing` · `correspondence` |
| `creative` | `writing` · `music` · `art` · `film` |
| `personal` | `id` · `health` · `family` · `correspondence` |
| `project` | `brief` · `plan` · `asset` · `deliverable` |
| `archive` | `backup` · `export` · `snapshot` |
| `tagback` | `asset` · `ingest` · `processed` |
| `general` | `file` · `misc` |

### Date Format Rules

- **Always ISO 8601:** `YYYY-MM-DD` — never `MMDDYYYY`, never `MM-DD-YY`
- When a file was created on a specific date, use that date, not today's date
- For folders, omit the time and UUID segments: `YYYY-MM-DD_category-subcategory_description`

---

## SJL File Processing Workflow

Every file that enters any cloud service passes through this workflow:

```
ARRIVES IN @INBOX
     |
     v
Identify: category + subcategory
     |
     v
Apply SJL rename: YYYY-MM-DD_HH-MM_cat-subcat_desc_UUID24.ext
     |
     v
Route to correct PARA folder in that cloud
     |
     v
Generate permanent share link (cloud-native URL)
     |
     v
HookVault webhook --> Raindrop.io  [see Linking section below]
     |
     v
Tag / label within that cloud's native tagging system
     |
     v
Log to master inventory (Google Sheets or Notion)
     |
     v
Remove original / resolve duplicates
```

**FileWarden** (`filewarden.py`) automates this on the personal server (`shannonjlove.cloud`).
All other cloud services follow this same logic manually or via automation rules.

---

## Universal Linking System -- HookVault -> Raindrop.io

Every file and every meaningful change is bi-directionally linked.
This mirrors what **Hookmark** does on macOS: every piece of content gets a permanent,
hookable URL that travels with it across every tool and service.

### How it works

1. File is processed (renamed + routed per SJL convention)
2. Permanent link is generated -- the cloud-native share URL for that file
3. HookVault fires a webhook to Raindrop.io with the structured payload (see below)
4. Raindrop.io receives the bookmark -- filed into the matching PARA collection
5. The Raindrop link = the permanent hookable identifier for that file across all tools

### HookVault Webhook Payload (per file)

```json
{
  "link":        "https://[cloud-share-url]",
  "title":       "YYYY-MM-DD_HH-MM_category-subcategory_description_UUID24.ext",
  "excerpt":     "Cloud: [cloud-name] | PARA: [bucket] | Project: [project-name]",
  "tags":        ["sjl", "[cloud]", "[category]", "[subcategory]", "[para-bucket]"],
  "collection":  "[PARA bucket name]",
  "created":     "YYYY-MM-DDTHH:MM:SSZ"
}
```

### Raindrop.io Collection Structure (mirrors PARA)

```
@PROJECTS     -- one bookmark per project file, tagged by cloud
@AREAS        -- ongoing area files
@RESOURCES    -- reference assets, templates, tools
@ARCHIVES     -- completed / historical files
@INBOX        -- unprocessed / pending review
CHANGES       -- every meaningful edit, commit, or version gets a Raindrop entry
```

### Per-cloud Raindrop tags (auto-applied by HookVault)

| Cloud | Tag |
|---|---|
| Google Drive | `gdrive` |
| MediaFire | `mediafire` |
| pCloud | `pcloud` |
| Dropbox (personal) | `dropbox` |
| Dropbox (business/2nd) | `dropbox2` |
| MEGA | `mega` |
| iCloud Drive | `icloud` |
| shannonjlove.cloud | `sjlcloud` |
| GitHub | `github` |

### Change Linking Rule

Every meaningful change -- file rename, folder move, project update, code commit, migration
step -- gets its own Raindrop entry:
- **Title:** `[YYYY-MM-DD] [action] -- [file or folder name]`
- **Link:** direct URL to the file, commit, or folder
- **Tags:** `change` + `[cloud]` + `[category]` + `[para-bucket]`
- **Collection:** `CHANGES`

This creates a full audit trail browsable from Raindrop.io exactly like Hookmark's link history.

---

## Universal PARA Structure

Every cloud service uses the same 5-bucket PARA structure.
Each bucket is prefixed with `@` so it sorts to the top of any file listing.
Each bucket name carries the cloud-service suffix for cross-service identification.

### Folder naming template per cloud

```
@INBOX_[cloud]       ← landing zone; nothing stays here
@PROJECTS_[cloud]    ← active projects with a defined outcome
@AREAS_[cloud]       ← ongoing responsibilities with no end date
@RESOURCES_[cloud]   ← reference material, assets, templates
@ARCHIVES_[cloud]    ← completed, inactive, or historical items
```

### Cloud-specific folder names

| PARA Bucket | Google Drive | MediaFire | pCloud | Dropbox (personal) | Dropbox (biz/2nd) | MEGA | iCloud Drive | shannonjlove.cloud |
|---|---|---|---|---|---|---|---|---|
| Inbox | `@INBOX_gDrive` | `@INBOX_mediafire` | `@INBOX_pcloud` | `@INBOX_dropbox` | `@INBOX_dropbox2` | `@INBOX_mega` | `@INBOX_icloud` | `@INBOX` |
| Projects | `@PROJECTS_gDrive` | `@PROJECTS_mediafire` | `@PROJECTS_pcloud` | `@PROJECTS_dropbox` | `@PROJECTS_dropbox2` | `@PROJECTS_mega` | `@PROJECTS_icloud` | `@PROJECTS` |
| Areas | `@AREAS_gDrive` | `@AREAS_mediafire` | `@AREAS_pcloud` | `@AREAS_dropbox` | `@AREAS_dropbox2` | `@AREAS_mega` | `@AREAS_icloud` | `@AREAS` |
| Resources | `@RESOURCES_gDrive` | `@RESOURCES_mediafire` | `@RESOURCES_pcloud` | `@RESOURCES_dropbox` | `@RESOURCES_dropbox2` | `@RESOURCES_mega` | `@RESOURCES_icloud` | `@RESOURCES` |
| Archives | `@ARCHIVES_gDrive` | `@ARCHIVES_mediafire` | `@ARCHIVES_pcloud` | `@ARCHIVES_dropbox` | `@ARCHIVES_dropbox2` | `@ARCHIVES_mega` | `@ARCHIVES_icloud` | `@ARCHIVES` |

> **Note on Dropbox accounts:** `dropbox` = personal (sjlove@shannonjeffreylove.com).
> `dropbox2` = second account. Update these labels once both accounts are confirmed.

### Project subfolder naming standard

Inside any `@PROJECTS_[cloud]` folder, each project folder follows:
```
ProjectName_PROJECTS_[cloud]
```
Examples:
- `Revelation-911_PROJECTS_gDrive`
- `Built-For-This_PROJECTS_mediafire`
- `SJL-Personal-Server_PROJECTS_pcloud`

### Areas subfolder naming standard

```
AreaName_AREAS_[cloud]
```

### Resources subfolder naming standard

```
ResourceName_RESOURCES_[cloud]
```

---

## Google Drive — Current Status & Cleanup Tasks

Account: `sjlove@shannonjeffreylove.com`

### Root-level PARA buckets (existing — rename to standard)

| Current name | Rename to |
|---|---|
| `@PROJECTS_gdrive` | `@PROJECTS_gDrive` |
| `@AREAS_gdrive` | `@AREAS_gDrive` |
| `@RESOURCES_gdrive` | `@RESOURCES_gDrive` |
| `@ARCHIVES_gdrive` | `@ARCHIVES_gDrive` |
| `@INBOX_gDrive` | `@INBOX_gDrive` ✓ already correct |

### Stray root-level folders → move to PARA

| Folder | Move to |
|---|---|
| `SnAPPTrap` | `@PROJECTS_gDrive` |
| `Google AI Studio` | `@RESOURCES_gDrive` |
| `Collab Notebooks` | `@RESOURCES_gDrive` |
| `Downloads` | `@INBOX_gDrive` |
| `Saved from Chrome` (2026-06-07) | merge into `@INBOX_gDrive` → review & route |
| `Saved from Chrome` (2025-12-03) | merge into `@INBOX_gDrive` → review & route |
| `Spent 2025` | `@ARCHIVES_gDrive` |
| `meta-2026-Jan-05-04-14-56` | investigate → `@INBOX_gDrive` |

### Stray root-level files → move & deduplicate

| File | Issue | Action |
|---|---|---|
| `NappyBoy Thank You` (Google Doc) | Loose at root | Move to `@PROJECTS_gDrive > NappyBoy-Thank-You_PROJECTS_gDrive` |
| `NappyBoy Thank You.docx` | Duplicate .docx export | Trash — native Google Doc is canonical |
| `Revelation 9-1-1 Outline... 06102026` (Google Doc) | Loose at root | Move to `@PROJECTS_gDrive > Revelation-911_PROJECTS_gDrive` |
| `Revelation 9-1-1 Outline... 06102026.docx` | Duplicate .docx export | Trash — native Google Doc is canonical |
| `Austin apartment furniture` (Google Doc) | Loose at root | Move to `@PROJECTS_gDrive > Austin-Apartment_PROJECTS_gDrive` |

### @PROJECTS_gDrive — folder renames needed

| Current | Rename to |
|---|---|
| `Austin apartment` | `Austin-Apartment_PROJECTS_gDrive` |
| `Revelation 911` | `Revelation-911_PROJECTS_gDrive` |
| `TGMGPYSM` | `TGMGPYSM_PROJECTS_gDrive` *(clarify full name)* |
| `Asha 2026 bday` | `Asha-2026-Birthday_PROJECTS_gDrive` |
| `SJL Personal Server Cloud Project` | `SJL-Personal-Server_PROJECTS_gDrive` |
| `Built For This_gDrive` | `Built-For-This_PROJECTS_gDrive` |
| `CCC 2025 Welcodm` | `CCC-2025-Welcome_PROJECTS_gDrive` *(typo fixed)* |
| `CCC Writing Room 2025` | `CCC-Writing-Room-2025_PROJECTS_gDrive` |
| `CCC Welcome Team Scripts` | `CCC-Welcome-Team-Scripts_PROJECTS_gDrive` |
| `CCC Reception 06242023` | `CCC-Reception-2023-06-24_PROJECTS_gDrive` |
| `Crockettscience` | `Crockett-Science_PROJECTS_gDrive` |
| `Filetagger ` *(trailing space)* | `Filetagger_PROJECTS_gDrive` |
| `53 anniversary ` *(trailing space)* | `53rd-Anniversary_PROJECTS_gDrive` |
| `Crockett Science B roll clips` | `Crockett-Science-Broll_PROJECTS_gDrive` |
| `DFlat DEvans Music` | `DFlat-DEvans-Music_PROJECTS_gDrive` |
| `Our Time Adapation Project_Projects_gDrive` | `Our-Time-Adaptation_PROJECTS_gDrive` *(typo fixed)* |
| `Our Time (Promo)` | `Our-Time-Promo_PROJECTS_gDrive` |
| `Our Time` | `Our-Time_PROJECTS_gDrive` *(confirm if separate from above)* |
| `TagBack Project Folder` | `TagBack_PROJECTS_gDrive` |
| `TV One Lawsuit_PROJECTS_gDRIVE` | `TV-One-Lawsuit_PROJECTS_gDrive` |
| `Fathers Master Plan_Projects_gDrive` | `Fathers-Master-Plan_PROJECTS_gDrive` |
| `Lord Of The Manners` | `Lord-Of-The-Manners_PROJECTS_gDrive` |
| `Enoch Series` | `Enoch-Series_PROJECTS_gDrive` |
| `Nicodemus Movie` | `Nicodemus-Movie_PROJECTS_gDrive` |
| `Covid vaccination spots ` *(trailing space)* | `Covid-Vaccination-Spots_PROJECTS_gDrive` |
| `Content Clutter Stock Media ` *(trailing space)* | `Content-Clutter-Stock-Media_PROJECTS_gDrive` |
| `LoveYou Concert series Promotion Rebranding` | `LoveYou-Concert-Promo-Rebrand_PROJECTS_gDrive` |
| `Mother dear nurse December 2025` | `Mother-Nurse-Dec-2025_PROJECTS_gDrive` |
| `SPENT NBN (Net Worth)` | `SPENT-NBN-Net-Worth_PROJECTS_gDrive` |
| `NET WORTH` | `Net-Worth_PROJECTS_gDrive` |
| `SJL .com` | `SJL-dotCom_PROJECTS_gDrive` |
| `WOMEN'S PROJECT` | `Womens-Project_PROJECTS_gDrive` |
| `UNDERGROUND IN MIDTOWN OPEN MIC PROJECT` | `Underground-In-Midtown-Open-Mic_PROJECTS_gDrive` |
| `HappyBirthdayAdrienneLove_Projects_gDrive` | `Happy-Birthday-Adrienne-Love_PROJECTS_gDrive` |
| `Butter P's (candied nuts project)` | `Butter-Ps-Candied-Nuts_PROJECTS_gDrive` |
| `For Ariel (ShannonJLove)` | `For-Ariel_PROJECTS_gDrive` |
| `Amadaeus & Ashley` | `Amadaeus-And-Ashley_PROJECTS_gDrive` |
| `Mom & Dad 50th Anniversary Pictures` | `Mom-Dad-50th-Anniversary_PROJECTS_gDrive` |
| `Cinema 4D Projects 2025` | `Cinema-4D-2025_PROJECTS_gDrive` |

### @PROJECTS_gDrive — archive these (completed / inactive since 2014–2023)

Move to `@ARCHIVES_gDrive`:
- `Love Family Portrait` (2014)
- `90s Girl Group Project` (2020)
- `Girls Cruise Files` (2020)
- `SJL Recordings` (2020)
- `SJL Songwriting Projects 2020`
- `SWV_IF_ONLY_YOU_KNEW` (2020)
- `AshaRuRu & SJL 2021 Writing Sessions`
- `WOMEN'S PROJECT` (2021)
- `Making Love Deck 2022`
- `UNDERGROUND IN MIDTOWN OPEN MIC PROJECT` (2022)
- `Amadaeus & Ashley` (2023)
- `For Ariel (ShannonJLove)` (2023)
- `HappyBirthdayAdrienneLove_Projects_gDrive` (2023)
- `CCC Reception 06242023` (2023)
- `Mom & Dad 50th Anniversary Pictures` (2023)
- `NET WORTH` (2023)

### @ARCHIVES_gDrive — fix suffix

| Current | Rename to |
|---|---|
| `SJL_Produced_Content_RESOURCES_iDrive` | `SJL-Produced-Content_ARCHIVES_gDrive` |

---

## MediaFire — Target PARA Structure (to be created)

```
@INBOX_mediafire/
@PROJECTS_mediafire/
@AREAS_mediafire/
@RESOURCES_mediafire/
@ARCHIVES_mediafire/
```

Status: Audit pending — requires MediaFire API or manual review session.

---

## pCloud — Target PARA Structure (to be created)

```
@INBOX_pcloud/
@PROJECTS_pcloud/
@AREAS_pcloud/
@RESOURCES_pcloud/
@ARCHIVES_pcloud/
```

Status: Audit pending — requires pCloud API or manual review session.

---

## Dropbox (Account 1 — Personal) — Target PARA Structure

```
@INBOX_dropbox/
@PROJECTS_dropbox/
@AREAS_dropbox/
@RESOURCES_dropbox/
@ARCHIVES_dropbox/
```

Status: Audit pending.

---

## Dropbox (Account 2 — Business/Secondary) — Target PARA Structure

```
@INBOX_dropbox2/
@PROJECTS_dropbox2/
@AREAS_dropbox2/
@RESOURCES_dropbox2/
@ARCHIVES_dropbox2/
```

Status: Audit pending. Confirm account email and label (dropbox2 or a descriptive suffix).

---

## MEGA — Target PARA Structure (to be created)

```
@INBOX_mega/
@PROJECTS_mega/
@AREAS_mega/
@RESOURCES_mega/
@ARCHIVES_mega/
```

Status: Audit pending — requires MEGA API or manual review session.

---

## iCloud Drive — Target PARA Structure (to be created)

```
@INBOX_icloud/
@PROJECTS_icloud/
@AREAS_icloud/
@RESOURCES_icloud/
@ARCHIVES_icloud/
```

Status: Audit pending — iCloud Drive not directly accessible via MCP; manual creation required or use Shortcuts/iCloud automation.

---

## shannonjlove.cloud (Personal Server) — Master PARA Structure

This is the canonical master — all other clouds mirror this structure.

```
@INBOX/
@PROJECTS/
@AREAS/
@RESOURCES/
@ARCHIVES/
```

FileWarden watches `@INBOX/` and auto-routes per `config.yaml` rules.

---

## Cloud Migration Plan (Pre-S3)

**Phase 1 — Google Drive (current phase)**
- [ ] Rename PARA root buckets to standardized casing
- [ ] Move stray root folders into PARA buckets
- [ ] Trash duplicate .docx exports (keep native Google Docs)
- [ ] Move stray root files to correct project folders
- [ ] Merge two `Saved from Chrome` folders
- [ ] Rename all project folders to standard convention
- [ ] Archive 16 completed projects from @PROJECTS → @ARCHIVES
- [ ] Clarify: `Our Time` vs `Our Time (Promo)` — same project?
- [ ] Clarify: `TGMGPYSM` — full project name?
- [ ] Clarify: Dropbox account 2 label

**Phase 2 — MediaFire**
- [ ] Audit existing structure
- [ ] Create PARA buckets
- [ ] Rename and sort files per SJL convention
- [ ] Deduplicate

**Phase 3 — pCloud**
- [ ] Audit existing structure
- [ ] Create PARA buckets
- [ ] Rename and sort files
- [ ] Deduplicate

**Phase 4 — Dropbox (both accounts)**
- [ ] Audit each account separately
- [ ] Create PARA buckets in each
- [ ] Cross-account deduplication check

**Phase 5 — MEGA**
- [ ] Audit existing structure
- [ ] Create PARA buckets
- [ ] Rename and sort files
- [ ] Deduplicate

**Phase 6 — iCloud Drive**
- [ ] Audit existing structure (manual or via Shortcuts)
- [ ] Create PARA buckets
- [ ] Rename and sort files

**Phase 7 — S3 Migration**
- All clouds cleaned, named, and PARA-structured before any migration begins
- S3 bucket key prefix mirrors PARA: `projects/`, `areas/`, `resources/`, `archives/`
- Files carry SJL canonical names — no rename needed at migration

---

## Tools Reference

| Tool | Purpose |
|---|---|
| `filewarden.py` | Server-side file watcher; auto-renames via SJL convention |
| `diffforge.py` | Diff/comparison utility |
| `hookvault.py` | Webhook hook manager |
| `DEPLOY.sh` | Deployment script |
| `config.yaml` | FileWarden rules config (inbox routing, categories) |

All tools live in `@PROJECTS_gDrive > SJL-Personal-Server_PROJECTS_gDrive > Auto/`

---

## Project Identity

- **Owner:** Shannon J. Love
- **Email:** sjlove@shannonjeffreylove.com
- **Domain:** shannonjlove.cloud / shannonjeffreylove.com
- **Role:** Writer · Producer · Director
- **Repo:** shannonjlove/shannonjlove-github.io
- **Branch convention:** `claude/[task-slug]-[id]`
