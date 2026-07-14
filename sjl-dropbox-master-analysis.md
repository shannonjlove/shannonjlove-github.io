# SJL Dropbox Master Analysis
**Created:** 2026-07-12  
**Updated:** 2026-07-14 (personal account root fully audited — 33 folders / 4 files inventoried)  
**Accounts:** Personal (`shannonjlove@mac.com` tag: `dropbox`) + Business (tag: `dropbox-biz`)  
**Phase:** 4 of 7 per CLAUDE.md cloud migration plan  

> **SAFETY RULE:** No file is deleted, renamed, or moved until Shannon reviews and approves this list section by section.

---

## STATUS

| Account | PARA Folders | Root Audit | Cleanup | Dedup Check |
|---|---|---|---|---|
| Personal (`dropbox`) | 🔶 Old-format PARA exists — needs rename | ✅ Complete — 33 folders / 4 files | ⬜ Awaiting Shannon review | ⬜ |
| Business (`dropbox-biz`) | ⬜ Need token | ⬜ | ⬜ | ⬜ |

**Personal account audited 2026-07-14.** Account: `shannonjlove@mac.com`, team "LoveYOU", member folder `Shannon J. Love (DPBXpro)`.  
Root has 33 folders and 4 files — full inventory below. Old PARA folders exist with `=DRPBX_SJL` naming (non-standard); none match the target `@INBOX_dropbox` / `@PROJECTS_dropbox` etc. names.  
**Next step:** Shannon reviews inventory → approve PARA rename plan → execute.

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
| `@INBOX_dropbox` | 🔶 Create new + migrate from `@INBOX_DRPBX_SJL` | Old folder exists with wrong suffix |
| `@PROJECTS_dropbox` | 🔶 Create new + migrate from `=PROJECTS_DRPBX_SJL___Folder_2022-03-18_1023_` | 1023 items — review contents first |
| `@AREAS_dropbox` | 🔶 Create new + migrate from `=AREAS_DRPBX_SJL___Folder_2022-03-27_219_` | 219 items |
| `@RESOURCES_dropbox` | 🔶 Create new + migrate from `=RESOURCES_DRPBX_SJL___Folder_2022-03-13_601_` | 601 items |
| `@ARCHIVES_dropbox` | 🔶 Create new + migrate from `=ARCHIVES_DRPBX_SJL___Folder_2022-03-15_1000_` | 1000 items — largest, review first |

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
| `DEVans Dflat Music` | `@PROJECTS_dropbox/DFlat-DEvans-Music_PROJECTS_dropbox/` | Also exists in gDrive — cross-cloud-mirror candidate |
| `Mel LAG` | `@PROJECTS_dropbox/` or `@ARCHIVES_dropbox/` | Unclear — Shannon to identify |
| `Movie Magic` | `@RESOURCES_dropbox/` | Screenwriting software files / templates |
| `Movies (DVDs)` | `@ARCHIVES_dropbox/` | DVD rips / backups — archive |
| `Wake Up BGVS & ISO Parts` | `@PROJECTS_dropbox/` or `@ARCHIVES_dropbox/` | Audio/music project parts — Shannon to confirm active vs. archived |

#### System / App Backup Folders

| Name | Recommended PARA Route | Notes |
|---|---|---|
| `AE_camera_morph_v1.1.1` | `@RESOURCES_dropbox/` | After Effects plugin backup |
| `Air Video Server HD.app` | `@ARCHIVES_dropbox/` | Old iOS streaming app |
| `Apps` | `@ARCHIVES_dropbox/` | General app backups — review contents before archiving |
| `CheatSheet.app` | `@ARCHIVES_dropbox/` | Old macOS utility |
| `Corkulous App` | `@ARCHIVES_dropbox/` | Discontinued iOS app |
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
| `01162024 Dropbox unsorted` | `@INBOX_dropbox/` | Jan 16, 2024 batch — route to INBOX for processing |
| `07112024` | `@INBOX_dropbox/` | Jul 11, 2024 batch — route to INBOX for processing |
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
| `Vault` | `@AREAS_dropbox/` | Likely secure personal docs — Shannon to confirm |

#### Hidden / System Folders (safe to delete after review)

| Name | Recommended Action | Notes |
|---|---|---|
| `.Keka-279B2E5E-20C4-43FF-B543-FBFE1E6A8421` | Delete | Keka (archive app) temp folder — stale, safe to remove |

### Personal Account — Root Files (4 files)

| Name | Size | Recommended Action |
|---|---|---|
| `._Dear Evan Hansen.mp4` | 4.0 KB | Delete — macOS AppleDouble metadata file (not the actual video) |
| `._StellarVolumeOptimizer.dmg` | 4.0 KB | Delete — macOS AppleDouble metadata file |
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

*(None yet — awaiting audit)*

---

## EXECUTION ORDER (SECTION 11)

### Phase 4-A — Personal account PARA setup 🔶 IN PROGRESS
- [x] Run audit: `python3 dropbox-audit.py --token TOKEN_PERSONAL --account personal` — **complete 2026-07-14**
- [x] Generate root inventory — **33 folders / 4 files documented above**
- [ ] **Shannon reviews Root Inventory above** — approve recommended actions section by section
- [ ] **Inspect contents of old PARA folders** (especially the large ones):
  - `=PROJECTS_DRPBX_SJL___Folder_2022-03-18_1023_` (1023 items)
  - `=ARCHIVES_DRPBX_SJL___Folder_2022-03-15_1000_` (1000 items)
  - `=RESOURCES_DRPBX_SJL___Folder_2022-03-13_601_` (601 items)
- [ ] **Create new PARA folders** (dry run → Shannon approves → execute):
  - `@INBOX_dropbox`, `@PROJECTS_dropbox`, `@AREAS_dropbox`, `@RESOURCES_dropbox`, `@ARCHIVES_dropbox`
- [ ] **Migrate contents** from old `=DRPBX_SJL` folders into new `@*_dropbox` folders
- [ ] **Route non-PARA root items** to PARA (Shannon approves each batch per Root Inventory table)
- [ ] **Delete / trash** confirmed safe items: `.Keka-*` folder, `._*` AppleDouble files

### Phase 4-B — Business account PARA setup ⬜ PENDING
- [ ] Run audit: `python3 dropbox-audit.py --token TOKEN_BIZ --account biz`
- [ ] Review root inventory with Shannon
- [ ] Create missing PARA folders
- [ ] Route root items to PARA

### Phase 4-C — Cross-account dedup check ⬜ PENDING
- [ ] Compare inventories from both accounts
- [ ] Flag files/folders present in both
- [ ] Shannon decides: keep one canonical, tag as cross-cloud-mirror, or merge

---

*Dropbox is Phase 4 of the SJL 7-cloud migration plan.*  
*Prior phase: pCloud (Phase 3) — complete as of 2026-07-12. Root: 7 folders / 0 files.*  
*Next phase after Dropbox: MEGA (Phase 5), iCloud (Phase 6), S3 migration (Phase 7).*
