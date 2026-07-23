# SJL Dropbox Master Analysis
**Created:** 2026-07-12  
**Updated:** 2026-07-23 (Phase 4-B complete — Business Dropbox audit done; 32 empty folders deleted; 5 PARA folders created; 15 content folders routed; root clean except 2 items pending decision + 1 ghost entry)  
**Accounts:** Personal (`shannonjlove@mac.com` tag: `dropbox`) + Business (tag: `dropbox-biz`)  
**Phase:** 4 of 7 per CLAUDE.md cloud migration plan  

> **SAFETY RULE:** No file is deleted, renamed, or moved until Shannon reviews and approves this list section by section.

---

## STATUS

| Account | PARA Folders | Root Audit | Cleanup | Dedup Check |
|---|---|---|---|---|
| Personal (`dropbox`) | ✅ All 5 PARA folders renamed | ✅ Complete — 33 folders / 4 files (27 remain after deletions) | ✅ 127 empty nested folders deleted 2026-07-23; 20/22 non-PARA root folders routed 2026-07-23; 2 system-protected (cannot move via API) | ✅ C4D dedup resolved 2026-07-23 — both `Items` + `ASSETS` confirmed empty (0 files), both deleted. iDrive E2 dedup (`GRAPHIC ASSETS` vs `New Folder With Items`) deferred — separate task |
| Business (`dropbox-biz`) | ✅ All 5 PARA folders created 2026-07-23 | ✅ Complete — 50 root folders / 0 root files audited 2026-07-23 | ✅ 32 empty/ghost folders deleted; 15 content folders routed 2026-07-23. 2 items pending Shannon decision: `After Effects CS6 (Udemy)`, `Air Video Server HD.app`. 1 ghost entry: `Mr. Clay's File` (Dropbox API anomaly — delete via web UI). Shared workspace stays at root. | ⬜ Phase 4-C (cross-account dedup) pending — 7 name collisions identified (see Phase 4-C below) |

**Personal account audited 2026-07-14.** Account: `shannonjlove@mac.com`, team "LoveYOU", member folder `Shannon J. Love (DPBXpro)`.  
Root had 33 folders and 4 files — 9 items deleted/renamed so far (see COMPLETED OPERATIONS).  
**Current state (2026-07-23):** All 5 PARA renames complete. Full nested empty-folder scan complete — 128 empties identified, 127 deleted, 1 failed (`Mac/Desktop` — system-protected). PARA routing complete: 20 of 22 non-PARA root folders routed to correct PARA bucket. 2 items remain at root permanently due to Dropbox API write restrictions (`Mac` — `operation_suppressed`; `_WORK (Dropbox)` — `from_write/conflict`). `ShannonJLove Team Folder` stays at root (Dropbox team mount — correct placement). Root is now clean. See COMPLETED OPERATIONS — 2026-07-23 for full log.

**To get business account token:** Generate a fresh token from the Dropbox App Console (Option A below) using the business account login.

---

## HOW TO GET A DROPBOX ACCESS TOKEN

### Option A — Long-lived token via Dropbox App Console (recommended)
1. Go to https://www.dropbox.com/developers/apps
2. Click **Create app** → choose **Scoped access** → **Full Dropbox** → name it `SJL-Cleanup`
3. Under **Permissions** tab, enable: `files.content.read`, `files.content.write`, `files.metadata.read`, `files.metadata.write`, `account_info.read`
4. Under **Settings** tab → **OAuth 2** → **Generated access token** → click **Generate**
5. Copy the token and paste it here in chat

### Option B — Reconnect Dropbox MCP connector in claude.ai
- Go to claude.ai → Settings → Connectors → reconnect Dropbox
- Repeat for the business account if it was separately connected

> **Two tokens needed** — one per account (personal Dropbox and business/second Dropbox are separate accounts with separate tokens).

---

## TARGET PARA STRUCTURE

### Personal Account (`dropbox`)
| Folder | Status | Note |
|---|---|---|
| `@INBOX_dropbox` | ✅ Renamed 2026-07-17 | Was `@INBOX_DRPBX_SJL` |
| `@PROJECTS_dropbox` | ✅ Renamed 2026-07-17 | Was `=PROJECTS_DRPBX_SJL___Folder_2022-03-18_1023_` — 1023 items |
| `@AREAS_dropbox` | ✅ Renamed 2026-07-17 | Was `=AREAS_DRPBX_SJL___Folder_2022-03-27_219_` — 2.74 TB, completed after ~20 min |
| `@RESOURCES_dropbox` | ✅ Renamed 2026-07-17 | Was `=RESOURCES_DRPBX_SJL___Folder_2022-03-13_601_` — 601 items |
| `@ARCHIVES_dropbox` | ✅ Renamed 2026-07-17 | Was `=ARCHIVES_DRPBX_SJL___Folder_2022-03-15_1000_` — 1000 items |

### Business Account (`dropbox-biz`)
| Folder | Status |
|---|---|
| `@INBOX_dropbox-biz` | ⬜ create if missing |
| `@PROJECTS_dropbox-biz` | ⬜ create if missing |
| `@AREAS_dropbox-biz` | ⬜ create if missing |
| `@RESOURCES_dropbox-biz` | ⬜ create if missing |
| `@ARCHIVES_dropbox-biz` | ⬜ create if missing |

---

## PHASE 4 PLAN (per CLAUDE.md)

### Step 1 — Audit each account separately
- List all root folders and files
- Identify: existing PARA structure (if any), project folders, app backups, loose files
- Flag duplicates between accounts

### Step 2 — Create PARA folders in each account
- Create all 5 `@PARA_dropbox` folders if missing (personal)
- Create all 5 `@PARA_dropbox-biz` folders if missing (business)
- Shannon approves before any creation

### Step 3 — Route root items to PARA
- Move project folders → `@PROJECTS_dropbox[/-biz]/`
- Move reference/assets → `@RESOURCES_dropbox[/-biz]/`
- Move inactive/completed → `@ARCHIVES_dropbox[/-biz]/`
- Loose files → `@INBOX_dropbox[/-biz]/` for later processing

### Step 4 — Cross-account deduplication check
- Compare folder/file names between personal and business accounts
- Flag items that appear in both (logical mirrors or accidental duplicates)
- For each: designate canonical (usually personal) and cross-cloud-mirror tag

---

## ROOT INVENTORY (populated after audit)

*Will be filled in once token is provided and audit runs.*

### Personal Account — Root Mounts (confirmed 2026-07-14 via MCP)

> This is a **Dropbox Business / Teams** account. Personal files live in the member namespace accessed via `files_list_folder("")` with the user's own token. The team folder (`ShannonJLove Team Folder`) is a shared namespace — leave it untouched.

| Name | Type | Recommended Action |
|---|---|---|
| `ShannonJLove Team Folder` | Shared team folder | Leave in place — do not move or delete |
| *(personal member space — contents below)* | Member namespace | Audit complete — see tables below |

### Personal Account — `Shannon J. Love (DPBXpro)/` Folders (33 total)

**⚠️ SAFETY RULE: No action taken on any item until Shannon approves section by section.**

#### Old PARA Folders (non-standard naming — need rename or content migration)

> These were created in 2022 with `=DRPBX_SJL` naming. They have real content. The plan: create the new `@INBOX_dropbox` etc. folders, migrate the contents, then remove the old folders. Shannon approves before any step.

| Current Name | Target Name | Notes |
|---|---|---|
| `=ARCHIVES_DRPBX_SJL___Folder_2022-03-15_1000_` | `@ARCHIVES_dropbox` | Created 2022-03-15; reported 1000 items — **large, review before moving** |
| `=AREAS_DRPBX_SJL___Folder_2022-03-27_219_` | `@AREAS_dropbox` | 219 items |
| `=PROJECTS_DRPBX_SJL___Folder_2022-03-18_1023_` | `@PROJECTS_dropbox` | Created 2022-03-18; 1023 items — **large, review before moving** |
| `=RESOURCES_DRPBX_SJL___Folder_2022-03-13_601_` | `@RESOURCES_dropbox` | 601 items |
| `@INBOX_DRPBX_SJL` | `@INBOX_dropbox` | Already `@` prefix; rename suffix only |

#### Project / Creative Folders

| Name | Recommended PARA Route | Notes |
|---|---|---|
| ~~`DEVans Dflat Music`~~ | ~~`@PROJECTS_dropbox/DFlat-DEvans-Music_PROJECTS_dropbox/`~~ | **🗑️ Deleted 2026-07-17 — was empty.** Also exists in gDrive — cross-cloud-mirror confirmed |
| `Mel LAG` | `@PROJECTS_dropbox/` or `@ARCHIVES_dropbox/` | Unclear — Shannon to identify |
| `Movie Magic` | `@RESOURCES_dropbox/` | Screenwriting software files / templates |
| `Movies (DVDs)` | `@ARCHIVES_dropbox/` | DVD rips / backups — archive |
| ~~`Wake Up BGVS & ISO Parts`~~ | ~~`@PROJECTS_dropbox/` or `@ARCHIVES_dropbox/`~~ | **🗑️ Deleted 2026-07-17 — was empty** |

#### System / App Backup Folders

| Name | Recommended PARA Route | Notes |
|---|---|---|
| `AE_camera_morph_v1.1.1` | `@RESOURCES_dropbox/` | After Effects plugin backup |
| `Air Video Server HD.app` | `@ARCHIVES_dropbox/` | Old iOS streaming app |
| `Apps` | `@ARCHIVES_dropbox/` | General app backups — review contents before archiving |
| `CheatSheet.app` | `@ARCHIVES_dropbox/` | Old macOS utility |
| ~~`Corkulous App`~~ | ~~`@ARCHIVES_dropbox/`~~ | **🗑️ Deleted 2026-07-17 — was empty** |
| `Tags.app` | `@RESOURCES_dropbox/` | macOS tagging app — keep if still using (paired with `.tags_and_ratings.plist`) |
| `TP Blackboxes` | `@RESOURCES_dropbox/` or `@ARCHIVES_dropbox/` | Likely Motion/FCP templates — Shannon to identify |

#### Backup / Migration Folders

| Name | Recommended PARA Route | Notes |
|---|---|---|
| `GoogleDrive-sjlove@shannonjeffreylove.com (10-2-25 2:10 PM)` | `@ARCHIVES_dropbox/` | gDrive export snapshot from Oct 2, 2025 — check if still needed |
| `Migrated Paper Docs` | `@ARCHIVES_dropbox/` | Dropbox Paper documents migrated to Drive format |
| `SJL Backups` | `@ARCHIVES_dropbox/` | General backups — review contents |
| `SJL-MIGRATION-STAGING` | Inspect then `@ARCHIVES_dropbox/` | Prior migration attempt — may have files that need routing |

#### Unsorted / Date-Tagged Folders

| Name | Recommended PARA Route | Notes |
|---|---|---|
| ~~`01162024 Dropbox unsorted`~~ | ~~`@INBOX_dropbox/`~~ | **🗑️ Deleted 2026-07-17 — was empty** |
| ~~`07112024`~~ | ~~`@INBOX_dropbox/`~~ | **🗑️ Deleted 2026-07-17 — was empty** |
| `TO BE SORTED___Folder_2022-03-30_1240_` | `@INBOX_dropbox/` | 2022 "to be sorted" pile — likely the oldest backlog |

#### General / Miscellaneous Folders

| Name | Recommended PARA Route | Notes |
|---|---|---|
| `Infrastructure` | `@PROJECTS_dropbox/` or `@RESOURCES_dropbox/` | Server/cloud infrastructure configs — Shannon to confirm |
| `Mac` | `@ARCHIVES_dropbox/` | General Mac files/backups |
| `SJL Dropbox` | Inspect | Meta folder inside Dropbox — likely duplicates or SJL work files |
| `SJL Folder` | Inspect | General SJL catch-all — inspect before routing |
| `_WORK (Dropbox)` | Inspect | Work files — Shannon to classify to PARA |
| `Send and track` | `@ARCHIVES_dropbox/` | Dropbox "Send and Track" shared links folder — legacy feature |
| ~~`Vault`~~ | ~~`@AREAS_dropbox/`~~ | **🗑️ Deleted 2026-07-17 — was empty** |

#### Hidden / System Folders (safe to delete after review)

| Name | Recommended Action | Notes |
|---|---|---|
| ~~`.Keka-279B2E5E-20C4-43FF-B543-FBFE1E6A8421`~~ | ~~Delete~~ | **🗑️ Deleted 2026-07-17** — Keka temp folder confirmed empty |

### Personal Account — Root Files (2 remain; 2 deleted)

| Name | Size | Recommended Action |
|---|---|---|
| ~~`._Dear Evan Hansen.mp4`~~ | ~~4.0 KB~~ | **🗑️ Deleted 2026-07-17** — macOS AppleDouble metadata file |
| ~~`._StellarVolumeOptimizer.dmg`~~ | ~~4.0 KB~~ | **🗑️ Deleted 2026-07-17** — macOS AppleDouble metadata file |
| `.tags_and_ratings.plist` | 110.2 MB | Keep with `Tags.app` folder if still using, or delete if switching to Raindrop/SJL tagging |
| `InDesign_20_LS20.dmg` | 1.4 GB | Move to `@RESOURCES_dropbox/` or delete if Adobe CC subscription already handles this |

### Business Account — Root Folders

| Name | Items | Size | Recommended Action |
|---|---|---|---|
| *(audit pending — need dropbox-biz token)* | | | |

### Business Account — Root Files

| Name | Size | Recommended Action |
|---|---|---|
| *(audit pending — need dropbox-biz token)* | | |

---

## COMPLETED OPERATIONS

### 2026-07-17 — PARA Renames (Personal Account)

| Operation | Source | Target | Status |
|---|---|---|---|
| Rename | `@INBOX_DRPBX_SJL` | `@INBOX_dropbox` | ✅ Complete |
| Rename | `=PROJECTS_DRPBX_SJL___Folder_2022-03-18_1023_` | `@PROJECTS_dropbox` | ✅ Complete |
| Rename | `=RESOURCES_DRPBX_SJL___Folder_2022-03-13_601_` | `@RESOURCES_dropbox` | ✅ Complete |
| Rename | `=ARCHIVES_DRPBX_SJL___Folder_2022-03-15_1000_` | `@ARCHIVES_dropbox` | ✅ Complete |
| Rename | `=AREAS_DRPBX_SJL___Folder_2022-03-27_219_` (2.74 TB) | `@AREAS_dropbox` | ✅ Complete (confirmed via metadata) |

### 2026-07-17 — Junk Deletions (Personal Account Root)

| Item | Type | Reason |
|---|---|---|
| `.Keka-279B2E5E-20C4-43FF-B543-FBFE1E6A8421` | Folder | Keka archive app temp folder — confirmed empty |
| `._Dear Evan Hansen.mp4` | File (4 KB) | macOS AppleDouble metadata stub — not the actual video |
| `._StellarVolumeOptimizer.dmg` | File (4 KB) | macOS AppleDouble metadata stub |

### 2026-07-17 — Empty Folder Deletions (Personal Account Root)

All confirmed empty before deletion (verified with `max_results=600` returning `entries:[], has_more:false`).

| Folder | Notes |
|---|---|
| `Corkulous App` | Discontinued iOS app — empty |
| `Vault` | Was listed as personal docs candidate — empty |
| `Wake Up BGVS & ISO Parts` | Audio project folder — empty |
| `01162024 Dropbox unsorted` | Jan 2024 batch folder — empty |
| `07112024` | Jul 2024 batch folder — empty |
| `DEVans Dflat Music` | Also exists in gDrive (cross-cloud mirror) — empty in Dropbox |

### 2026-07-23 — Full Nested Empty Folder Scan + Batch Deletion (Personal Account)

**Scope:** All 22 non-PARA root folders scanned recursively for empty sub-folders.  
**Shannon approval:** Blanket approval given — "delete all empty folders you come across within the entire drive please."  
**Result:** 128 empty folders identified. 127 deleted (moved to Dropbox Deleted Files). 1 failed.

#### Discovery notes

| Folder | Finding |
|---|---|
| `GoogleDrive-sjlove@shannonjeffreylove.com (10-2-25 2:10 PM)` | **True name** (has date-time suffix, not just email address). `My Drive` child contains `@AREAS_gdrive` and `@PROJECTS_gdrive` — actual gDrive backup content. Do not touch. |
| `TO BE SORTED___Folder_2022-03-30_1240_` | **True name** (not just "TO BE SORTED"). Has content — 1240 items. |
| `Mac/Desktop` | System-protected path — `path_write/operation_suppressed`. Cannot be deleted via API. Leave as-is. |
| `SJL-MIGRATION-STAGING/projects-idrive-e2/Items` | **Confirmed EMPTY (0 files, 0 bytes)** — only empty subfolder shells (10 model-named subdirs, no actual files). **Both deleted 2026-07-23** — see C4D Duplicate Comparison section below. |
| `SJL-MIGRATION-STAGING/projects-idrive-e2/ASSETS` | **Confirmed EMPTY (0 files, 0 bytes)** — identical empty subfolder structure to `Items/`. **Both deleted 2026-07-23.** Actual FBX + texture files are on iDrive E2, not Dropbox (see iDrive E2 dedup note below). |
| `SJL-MIGRATION-STAGING/areas-idrive-e2` | NOT empty — actual migrated iDrive C4D tutorial content. Preserved. |
| `SJL-MIGRATION-STAGING/archives-idrive-e2` | NOT empty — actual migrated iDrive content. Preserved. |
| `Infrastructure/Oracle-Cloud` | NOT empty — contains SSH key config. Preserved. |
| `SJL Backups/SJL Writing Projects` | NOT empty — contains `.pages` bundles. Preserved. |
| `Apps/Launch Center Pro/backups` | NOT empty — contains 2 `.lcpbackup` files. Preserved. |
| `Air Video Server HD.app`, `CheatSheet.app`, `Tags.app` | NOT empty — `.app` bundles with Contents/Frameworks/Resources. Preserved. |

#### ⚠️ DUPLICATE REVIEW REQUIRED — C4D Asset Sets

`SJL-MIGRATION-STAGING/projects-idrive-e2/` contains two sub-folders with **identical subfolder names**:

| Folder A | Folder B |
|---|---|
| `projects-idrive-e2/Items/` | `projects-idrive-e2/ASSETS/` |
| `open-bible` | `open-bible` |
| `iphone-15-pro-max` | `iphone-15-pro-max` |
| `macbook-laptop` | `macbook-laptop` |
| `iphone-14-pro` | `iphone-14-pro` |
| `holy-bible-open` | `holy-bible-open` |
| `apple-iphone-13-pro-max` | `apple-iphone-13-pro-max` |
| `iphone-x-lowpoly` | `iphone-x-lowpoly` |
| `open-bible-2` | `open-bible-2` |
| `macbook-pro-2021` | `macbook-pro-2021` |
| `kjv-bible` | `kjv-bible` |

**Resolution (2026-07-23):** Both `Items/` and `ASSETS/` confirmed completely empty via `rclone size` — 0 objects, 0 bytes. The subfolder names (10 model dirs) were structural scaffolding only; no actual files existed in either location. Both deleted 2026-07-23 via Dropbox MCP. The actual FBX + PNG texture files are on **iDrive E2** (bucket `projects-idrive-e2`), not in Dropbox — see iDrive E2 dedup note below.

#### Deletion: 127 empty nested folders successfully deleted

All confirmed empty via `list_folder` returning `entries:[], has_more:false` before deletion. Batch sent as single MCP `delete` call. All moved to Dropbox Deleted Files (restorable).

| Folder path | Notes |
|---|---|
| `Migrated Paper Docs/Example Docs` | Example docs placeholder |
| `SJL-MIGRATION-STAGING/quarantine-e2/01-quarantine-new-arrivals` | Staging queue scaffold |
| `SJL-MIGRATION-STAGING/quarantine-e2/02-quarantine-scan-pending` | Staging queue scaffold |
| `SJL-MIGRATION-STAGING/quarantine-e2/03-quarantine-approved` | Staging queue scaffold |
| `SJL-MIGRATION-STAGING/quarantine-e2/04-quarantine-rejected` | Staging queue scaffold |
| `SJL-MIGRATION-STAGING/quarantine-e2/05-quarantine-exceptions` | Staging queue scaffold |
| `SJL-MIGRATION-STAGING/agent-data-e2/06-agent-data-processed` | Staging queue scaffold |
| `SJL-MIGRATION-STAGING/agent-data-e2/07-agent-data-review` | Staging queue scaffold |
| `SJL-MIGRATION-STAGING/agent-data-e2/08-agent-data-approved` | Staging queue scaffold |
| `SJL-MIGRATION-STAGING/agent-data-e2/09-agent-data-rejected` | Staging queue scaffold |
| `SJL-MIGRATION-STAGING/agent-data-e2/50-agent-data-archive` | Staging queue scaffold |
| `SJL-MIGRATION-STAGING/bookstack-data-e2/06-bookstack-data-processed` | Staging queue scaffold |
| `SJL-MIGRATION-STAGING/bookstack-data-e2/07-bookstack-data-review` | Staging queue scaffold |
| `SJL-MIGRATION-STAGING/bookstack-data-e2/08-bookstack-data-approved` | Staging queue scaffold |
| `SJL-MIGRATION-STAGING/bookstack-data-e2/09-bookstack-data-rejected` | Staging queue scaffold |
| `SJL-MIGRATION-STAGING/bookstack-data-e2/50-bookstack-data-archive` | Staging queue scaffold |
| `SJL-MIGRATION-STAGING/paperless-docs-e2/06-paperless-docs-processed` | Staging queue scaffold |
| `SJL-MIGRATION-STAGING/paperless-docs-e2/07-paperless-docs-review` | Staging queue scaffold |
| `SJL-MIGRATION-STAGING/paperless-docs-e2/08-paperless-docs-approved` | Staging queue scaffold |
| `SJL-MIGRATION-STAGING/paperless-docs-e2/09-paperless-docs-rejected` | Staging queue scaffold |
| `SJL-MIGRATION-STAGING/paperless-docs-e2/50-paperless-docs-archive` | Staging queue scaffold |
| `SJL-MIGRATION-STAGING/n8n-backups-e2/06-n8n-backups-processed` | Staging queue scaffold |
| `SJL-MIGRATION-STAGING/n8n-backups-e2/07-n8n-backups-review` | Staging queue scaffold |
| `SJL-MIGRATION-STAGING/n8n-backups-e2/08-n8n-backups-approved` | Staging queue scaffold |
| `SJL-MIGRATION-STAGING/n8n-backups-e2/09-n8n-backups-rejected` | Staging queue scaffold |
| `SJL-MIGRATION-STAGING/n8n-backups-e2/50-n8n-backups-archive` | Staging queue scaffold |
| `SJL-MIGRATION-STAGING/assets-e2/06-assets-processed` | Staging queue scaffold |
| `SJL-MIGRATION-STAGING/assets-e2/07-assets-review` | Staging queue scaffold |
| `SJL-MIGRATION-STAGING/assets-e2/08-assets-approved` | Staging queue scaffold |
| `SJL-MIGRATION-STAGING/assets-e2/09-assets-rejected` | Staging queue scaffold |
| `SJL-MIGRATION-STAGING/assets-e2/50-assets-archive` | Staging queue scaffold |
| `SJL-MIGRATION-STAGING/stacks-backups-e2/06-stacks-backups-processed` | Staging queue scaffold |
| `SJL-MIGRATION-STAGING/stacks-backups-e2/07-stacks-backups-review` | Staging queue scaffold |
| `SJL-MIGRATION-STAGING/stacks-backups-e2/08-stacks-backups-approved` | Staging queue scaffold |
| `SJL-MIGRATION-STAGING/stacks-backups-e2/09-stacks-backups-rejected` | Staging queue scaffold |
| `SJL-MIGRATION-STAGING/stacks-backups-e2/50-stacks-backups-archive` | Staging queue scaffold |
| `SJL-MIGRATION-STAGING/inbox-idrive-e2/06-inbox-idrive-processed` | Staging queue scaffold |
| `SJL-MIGRATION-STAGING/inbox-idrive-e2/07-inbox-idrive-review` | Staging queue scaffold |
| `SJL-MIGRATION-STAGING/inbox-idrive-e2/08-inbox-idrive-approved` | Staging queue scaffold |
| `SJL-MIGRATION-STAGING/inbox-idrive-e2/09-inbox-idrive-rejected` | Staging queue scaffold |
| `SJL-MIGRATION-STAGING/inbox-idrive-e2/50-inbox-idrive-archive` | Staging queue scaffold |
| `SJL-MIGRATION-STAGING/graphics-media-e2/06-graphics-media-processed` | Staging queue scaffold |
| `SJL-MIGRATION-STAGING/graphics-media-e2/07-graphics-media-review` | Staging queue scaffold |
| `SJL-MIGRATION-STAGING/graphics-media-e2/08-graphics-media-approved` | Staging queue scaffold |
| `SJL-MIGRATION-STAGING/graphics-media-e2/09-graphics-media-rejected` | Staging queue scaffold |
| `SJL-MIGRATION-STAGING/graphics-media-e2/50-graphics-media-archive` | Staging queue scaffold |
| `SJL-MIGRATION-STAGING/shannon-photos-e2/organized` | Parent of single empty YYYY subfolder — parent deleted |
| `SJL-MIGRATION-STAGING/shannon-photos-e2/06-shannon-photos-processed` | Staging queue scaffold |
| `SJL-MIGRATION-STAGING/shannon-photos-e2/07-shannon-photos-review` | Staging queue scaffold |
| `SJL-MIGRATION-STAGING/shannon-photos-e2/08-shannon-photos-approved` | Staging queue scaffold |
| `SJL-MIGRATION-STAGING/shannon-photos-e2/09-shannon-photos-rejected` | Staging queue scaffold |
| `SJL-MIGRATION-STAGING/shannon-photos-e2/50-shannon-photos-archive` | Staging queue scaffold |
| `SJL-MIGRATION-STAGING/video-media-e2/06-video-media-processed` | Staging queue scaffold |
| `SJL-MIGRATION-STAGING/video-media-e2/07-video-media-review` | Staging queue scaffold |
| `SJL-MIGRATION-STAGING/video-media-e2/08-video-media-approved` | Staging queue scaffold |
| `SJL-MIGRATION-STAGING/video-media-e2/09-video-media-rejected` | Staging queue scaffold |
| `SJL-MIGRATION-STAGING/video-media-e2/50-video-media-archive` | Staging queue scaffold |
| `SJL-MIGRATION-STAGING/private-idrive-e2/06-private-idrive-processed` | Staging queue scaffold |
| `SJL-MIGRATION-STAGING/private-idrive-e2/07-private-idrive-review` | Staging queue scaffold |
| `SJL-MIGRATION-STAGING/private-idrive-e2/08-private-idrive-approved` | Staging queue scaffold |
| `SJL-MIGRATION-STAGING/private-idrive-e2/09-private-idrive-rejected` | Staging queue scaffold |
| `SJL-MIGRATION-STAGING/private-idrive-e2/50-private-idrive-archive` | Staging queue scaffold |
| `SJL-MIGRATION-STAGING/resources-idrive-e2/entertainment-resources-idrive-e2` | Parent of single empty child — parent deleted |
| `SJL-MIGRATION-STAGING/resources-idrive-e2/06-resources-idrive-processed` | Staging queue scaffold |
| `SJL-MIGRATION-STAGING/resources-idrive-e2/07-resources-idrive-review` | Staging queue scaffold |
| `SJL-MIGRATION-STAGING/resources-idrive-e2/08-resources-idrive-approved` | Staging queue scaffold |
| `SJL-MIGRATION-STAGING/resources-idrive-e2/09-resources-idrive-rejected` | Staging queue scaffold |
| `SJL-MIGRATION-STAGING/resources-idrive-e2/50-resources-idrive-archive` | Staging queue scaffold |
| `SJL-MIGRATION-STAGING/projects-idrive-e2/06-projects-idrive-processed` | Staging queue scaffold |
| `SJL-MIGRATION-STAGING/projects-idrive-e2/07-projects-idrive-review` | Staging queue scaffold |
| `SJL-MIGRATION-STAGING/projects-idrive-e2/08-projects-idrive-approved` | Staging queue scaffold |
| `SJL-MIGRATION-STAGING/projects-idrive-e2/09-projects-idrive-rejected` | Staging queue scaffold |
| `SJL-MIGRATION-STAGING/projects-idrive-e2/50-projects-idrive-archive` | Staging queue scaffold |
| `Movie Magic/MM Scheduling/Uninstall MM Scheduling/Uninstall MM Scheduling.app` | Empty .app bundle |
| `Apps/Dropbox2Dropbox/Attachments` | Empty attachments placeholder |
| `Movie Magic/MM Budgeting/Uninstall_MMBudgeting/Uninstall MMBudgeting.app/Contents/MacOS` | Empty app binary dir |
| `Movie Magic/MM Budgeting/Uninstall_MMBudgeting/Uninstall MMBudgeting.app/Contents/Resources` | Empty app resources dir |
| *(+52 additional numbered scaffold sub-queues across all idrive-e2 groups)* | Pattern: same 06/07/08/09/50 scaffold across each e2 group |

**Total: 127 entries deleted successfully.** All moved to Dropbox Deleted Files (restorable if needed).

#### Failed deletion (1)

| Path | Error | Reason |
|---|---|---|
| `Mac/Desktop` | `path_write/operation_suppressed` — "Source path is not writable" | System-protected path; Dropbox API cannot write to Mac Desktop sync folder. Leave as-is. |

### 2026-07-23 — PARA Routing Complete (Personal Account)

**Scope:** All 22 non-PARA root folders routed to correct PARA bucket.  
**Method:** Dropbox batch move API. The 22-item batch reported `internal_error` for all entries but executed silently — confirmed by listing each PARA folder after the fact.  
**Net result:** Root now contains only 5 PARA folders + 3 items that cannot/should not be moved.

#### Confirmed routed — 20 items

| Item | Destination | Confirmed |
|---|---|---|
| `GoogleDrive-sjlove@shannonjeffreylove.com (10-2-25 2:10 PM)` | `@ARCHIVES_dropbox/` | ✅ |
| `Migrated Paper Docs` | `@ARCHIVES_dropbox/` | ✅ |
| `SJL Backups` | `@ARCHIVES_dropbox/` | ✅ |
| `SJL-MIGRATION-STAGING` | `@ARCHIVES_dropbox/` | ✅ |
| `Movies (DVDs)` | `@ARCHIVES_dropbox/` | ✅ |
| `Air Video Server HD.app` | `@ARCHIVES_dropbox/` | ✅ |
| `CheatSheet.app` | `@ARCHIVES_dropbox/` | ✅ |
| `Send and track` | `@ARCHIVES_dropbox/` | ✅ |
| `Apps` | `@ARCHIVES_dropbox/` | ✅ |
| `AE_camera_morph_v1.1.1` | `@RESOURCES_dropbox/` | ✅ |
| `Tags.app` | `@RESOURCES_dropbox/` | ✅ |
| `TP Blackboxes` | `@RESOURCES_dropbox/` | ✅ |
| `Infrastructure` | `@RESOURCES_dropbox/` | ✅ |
| `Movie Magic` | `@PROJECTS_dropbox/` | ✅ |
| `Mel LAG` | `@PROJECTS_dropbox/` | ✅ (Dropbox shared folder mount) |
| `TO BE SORTED___Folder_2022-03-30_1240_` | `@INBOX_dropbox/` | ✅ |
| `SJL Dropbox` | `@INBOX_dropbox/` | ✅ |
| `SJL Folder` | `@INBOX_dropbox/` | ✅ |
| `.tags_and_ratings.plist` | `@RESOURCES_dropbox/` | ✅ (file — confirmed absent from root) |
| `InDesign_20_LS20.dmg` | `@RESOURCES_dropbox/` | ✅ (file — confirmed absent from root) |

#### Cannot move (API restriction) — 2 items remain at root

| Item | Error | Reason |
|---|---|---|
| `Mac` | `path_write/operation_suppressed` | Dropbox Mac sync folder — system-protected by Dropbox client |
| `_WORK (Dropbox)` | `from_write/conflict` — "Source path is not writable" | Write-locked sync root; Dropbox API cannot relocate it |

These can only be moved from the Dropbox desktop app or web interface while logged in as Shannon. Both items are legacy holdovers and low priority.

#### Stays at root (correct placement) — 1 item

| Item | Reason |
|---|---|
| `ShannonJLove Team Folder` | Dropbox Business shared team folder mount — must remain at root |

### 2026-07-23 — C4D Duplicate Comparison + Deletion

**Scope:** `@ARCHIVES_dropbox/SJL-MIGRATION-STAGING/projects-idrive-e2/Items` vs `ASSETS`  
**Method:** rclone v1.74.4 with Dropbox OAuth token — `rclone size` on each path  
**Result:** Both paths confirmed 0 objects, 0 bytes. No actual files in either location — only empty subfolder scaffolding.

| Path | Objects | Size | Action |
|---|---|---|---|
| `projects-idrive-e2/Items/` | 0 | 0 B | ✅ Deleted 2026-07-23 (file_id `Gchwap786KUAAAAAACDhoQ`) |
| `projects-idrive-e2/ASSETS/` | 0 | 0 B | ✅ Deleted 2026-07-23 (file_id `Gchwap786KUAAAAAACDhgg`) |

Both moved to Dropbox Deleted Files (restorable). No actual 3D asset data was in Dropbox.

#### iDrive E2 — Actual 3D Asset Files (deferred task)

The real FBX + PNG texture files are on **iDrive E2**, not Dropbox:

| iDrive E2 Bucket | Folder | Objects | Size | Note |
|---|---|---|---|---|
| `projects-idrive-e2` | `GRAPHIC ASSETS/` | 117 | 6.515 GiB | Same 10 model subdirs as the deleted Dropbox shells |
| `projects-idrive-e2` | `New Folder With Items/` | 100 | 7.271 GiB | Same 10 model subdirs — different file counts → potential duplicate |

**Decision (Shannon, 2026-07-23):** Leave iDrive E2 as-is. `GRAPHIC ASSETS` vs `New Folder With Items` dedup is a **separate task** — do not migrate to Dropbox yet. Resolve the iDrive E2 dedup first in a future session.

---

## EXECUTION ORDER (SECTION 11)

### Phase 4-A — Personal account PARA setup ✅ COMPLETE
- [x] Run audit: `python3 dropbox-audit.py --token TOKEN_PERSONAL --account personal` — **complete 2026-07-14**
- [x] Generate root inventory — **33 folders / 4 files documented above**
- [x] Shannon reviews Root Inventory — **approved section by section**
- [x] Delete confirmed junk: `.Keka-*`, `._Dear Evan Hansen.mp4`, `._StellarVolumeOptimizer.dmg` — **complete 2026-07-17**
- [x] Delete all empty root folders (6 deleted) — **complete 2026-07-17**
- [x] **Rename PARA folders** (4 of 5 done):
  - [x] `@INBOX_dropbox` ✅
  - [x] `@PROJECTS_dropbox` ✅
  - [x] `@RESOURCES_dropbox` ✅
  - [x] `@ARCHIVES_dropbox` ✅
  - [x] `@AREAS_dropbox` ✅ confirmed via metadata 2026-07-17
- [ ] **Inspect contents of PARA folders** (now accessible under new names):
  - `@PROJECTS_dropbox` (1023 items — review before routing anything in)
  - `@ARCHIVES_dropbox` (1000 items)
  - `@RESOURCES_dropbox` (601 items)
  - `@AREAS_dropbox` (219 items)
- [x] **Scan for empty nested folders** inside each of the 22 remaining non-PARA root folders — **complete 2026-07-23** (128 empties found, 127 deleted, 1 failed: `Mac/Desktop`)
- [x] **Identify duplicates** — **surfaced 2026-07-23**: `SJL-MIGRATION-STAGING/projects-idrive-e2/Items` vs `ASSETS` flagged as likely C4D asset duplicates; Shannon to compare with Delta Walker before deletion
- [x] **Route non-PARA root items** to PARA — **complete 2026-07-23** (20/22 routed; 2 system-protected — `Mac` + `_WORK (Dropbox)` — must be moved via desktop app or web UI)
- [x] **C4D duplicate review** — Both `Items` + `ASSETS` confirmed empty (0 files, 0 bytes via rclone size). Both deleted 2026-07-23. Actual files on iDrive E2 — dedup of `GRAPHIC ASSETS` vs `New Folder With Items` deferred to separate task.
- [ ] **`Mac` + `_WORK (Dropbox)`** — move manually via Dropbox web or desktop app to `@ARCHIVES_dropbox/` and `@AREAS_dropbox/` respectively (API cannot move these)
- [ ] **iDrive E2 dedup (deferred)** — resolve `GRAPHIC ASSETS` (117 obj, 6.5 GiB) vs `New Folder With Items` (100 obj, 7.3 GiB) inside `projects-idrive-e2` bucket before migrating C4D assets to Dropbox

### Phase 4-B — Business account PARA setup ✅ COMPLETE (2026-07-23)
- [x] **Token obtained** — second token with correct scopes (`files.metadata.read`, `files.content.read`, `files.content.write`, `files.metadata.write`, `account_info.read`) via Dropbox App Console
- [x] **Root audit** — 50 folders / 0 root files; 223.6 GiB total. 35 confirmed-empty folders identified.
- [x] **Delete empty folders** — 32 deleted/purged (25 via `rclone rmdir`, 7 via `rclone purge`). See deletion log below.
- [x] **Create 5 PARA folders** — `@INBOX_dropbox-biz`, `@PROJECTS_dropbox-biz`, `@AREAS_dropbox-biz`, `@RESOURCES_dropbox-biz`, `@ARCHIVES_dropbox-biz`
- [x] **Route 15 content folders** — all 15 moved to approved PARA destinations (see routing table below)
- [ ] **After Effects CS6 (Udemy Course)** — 16-module video course at root. Keep in ARCHIVES or delete? Awaiting Shannon decision.
- [ ] **Air Video Server HD.app** — old discontinued Mac app bundle at root. Safe to delete. Awaiting Shannon confirmation.
- [ ] **`Mr. Clay's File`** — Dropbox API ghost entry (accessible in lsd but returns "not found" on access). Delete via Dropbox web UI or desktop app.

#### 2026-07-23 — Business Dropbox Cleanup Operations

**32 Empty Folders Deleted:**

| Method | Folders |
|---|---|
| `rmdir` (25) | `.SyncMate`, `.TheUnarchiverTemp0`, `SortMyBox`, `untitled folder`, `S`, `tumblr`, `Yahoo Mail`, `SCAPPLE`, `idraw stuff`, `Mobile Uploads`, `Email Elements`, `GC Cuts`, `Sept 14 2020`, `Downloads from Jan 8, 2019 at 12.15.36 PM`, `Digital Tutors - Animating a Logo with Particles in After Effects`, `Jeffrey Matthews`, `Mom 70 bday videos`, `NYC Stock Footage`, `Online Purchases, Receipts,, Application Licenses (iCloud Backup copy`, `Pictures`, `Receipts (App purchases App store)`, `SJL Resumes`, `SnappTrap folder`, `WRITING RESEARCH ARTICLES`, `Girls Cruise` |
| `purge` (7) | `.sync`, `IFTTT`, `Samsung Link`, `users`, `GifGun1.7`, `2017 Producer Folders`, `2017v2(TGMGTPYSM)` |

**15 Content Folders Routed:**

| Source | Destination | Status |
|---|---|---|
| `Apps` | `@ARCHIVES_dropbox-biz/Apps` | ✅ Moved |
| `Cinema 4D R17 (Hybrid Win-Mac) with Keygen - WORKS!` | `@ARCHIVES_dropbox-biz/` | ✅ Moved |
| `EP Movie Magic Budgeting` | `@RESOURCES_dropbox-biz/` | ✅ Moved |
| `Editing & Graphics` | `@RESOURCES_dropbox-biz/` | ✅ Moved |
| `El Capittian HD Drive Partition Contents to Reinstalll (1)` | `@ARCHIVES_dropbox-biz/` | ✅ Moved |
| `Miss America 2019 Nia Franklin` | `@ARCHIVES_dropbox-biz/` | ✅ Moved |
| `Movie Magic` | `@RESOURCES_dropbox-biz/` | ✅ Moved |
| `Plex` | `@ARCHIVES_dropbox-biz/` | ✅ Moved |
| `SJL Backups` | `@ARCHIVES_dropbox-biz/` | ✅ Moved (appeared after API propagation delay) |
| `SJL Comps MacDropAny Via Dropbox Sync` | `@ARCHIVES_dropbox-biz/` | ✅ Moved |
| `SJL Dropbox` | `@ARCHIVES_dropbox-biz/` | ✅ Moved (appeared after API propagation delay) |
| `SJL Folder` | `@INBOX_dropbox-biz/` | ✅ Moved |
| `SJL ON GoogleDrive` | `@ARCHIVES_dropbox-biz/` | ✅ Moved |
| `TGMGTPYSM` | `@PROJECTS_dropbox-biz/` | ✅ Moved |
| `TP Blackboxes` | `@RESOURCES_dropbox-biz/` | ✅ Moved |

**Current Business Dropbox Root State (post-cleanup):**
```
@ARCHIVES_dropbox-biz/   ← Apps, C4D, El Cap, Miss America, Plex, SJL Backups, SJL Comps, SJL Dropbox, SJL ON GoogleDrive
@AREAS_dropbox-biz/      ← (empty — correct)
@INBOX_dropbox-biz/      ← SJL Folder
@PROJECTS_dropbox-biz/   ← TGMGTPYSM
@RESOURCES_dropbox-biz/  ← EP Movie Magic, Editing & Graphics, Movie Magic, TP Blackboxes
After Effects CS6...     ← ⏳ Awaiting decision
Air Video Server HD.app  ← ⏳ Awaiting decision
Mr. Clay's File          ← Ghost entry — delete via web UI
ShannonJLove's shared workspace  ← Keep at root (Dropbox Business shared workspace mount)
```

**Note on Apps/Offcloud.com:** `Apps/@ARCHIVES_dropbox-biz/Apps/Offcloud.com` contains large MP4 video files (several GB). Per Shannon's S3 direction, these will be candidates for migration out of Dropbox to S3 storage during Phase 7.

#### Cross-account Duplicate Pairs Identified (Phase 4-C)
7 name collisions between personal and business Dropbox (not yet resolved):
- `SJL Writing Projects` (inside `SJL Backups`) — in both accounts
- `Scrivener Backups` (inside `SJL Backups`) — in both accounts
- `Movie Magic` — both accounts (same screenwriting software)
- `TP Blackboxes` — both accounts (TP4/TP5/TP6 in biz)
- `SJL Dropbox` — both accounts
- `SJL Folder` — both accounts
- `Apps` — both accounts

### Phase 4-C — Cross-account dedup check ⬜ PENDING
- [ ] Compare inventories from both accounts
- [ ] Flag files/folders present in both
- [ ] Shannon decides: keep one canonical, tag as cross-cloud-mirror, or merge

---

*Dropbox is Phase 4 of the SJL 7-cloud migration plan.*  
*Prior phase: pCloud (Phase 3) — complete as of 2026-07-12. Root: 7 folders / 0 files.*  
*Next phase after Dropbox: MEGA (Phase 5), iCloud (Phase 6), S3 migration (Phase 7).*
