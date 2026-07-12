# SJL Dropbox Master Analysis
**Created:** 2026-07-12  
**Updated:** 2026-07-12 (infrastructure ready — awaiting token to run audit)  
**Accounts:** Personal (`shannonjlove@mac.com` tag: `dropbox`) + Business (tag: `dropbox-biz`)  
**Phase:** 4 of 7 per CLAUDE.md cloud migration plan  

> **SAFETY RULE:** No file is deleted, renamed, or moved until Shannon reviews and approves this list section by section.

---

## STATUS

| Account | PARA Folders | Root Audit | Cleanup | Dedup Check |
|---|---|---|---|---|
| Personal (`dropbox`) | ⬜ Pending token | ⬜ | ⬜ | ⬜ |
| Business (`dropbox-biz`) | ⬜ Pending token | ⬜ | ⬜ | ⬜ |

**To unlock:** Provide a Dropbox access token (or reconnect Dropbox MCP connector) for each account. See token instructions below.

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
| Folder | Status |
|---|---|
| `@INBOX_dropbox` | ⬜ create if missing |
| `@PROJECTS_dropbox` | ⬜ create if missing |
| `@AREAS_dropbox` | ⬜ create if missing |
| `@RESOURCES_dropbox` | ⬜ create if missing |
| `@ARCHIVES_dropbox` | ⬜ create if missing |

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

### Personal Account — Root Folders

| Name | Items | Size | Recommended Action |
|---|---|---|---|
| *(audit pending)* | | | |

### Personal Account — Root Files

| Name | Size | Recommended Action |
|---|---|---|
| *(audit pending)* | | |

### Business Account — Root Folders

| Name | Items | Size | Recommended Action |
|---|---|---|---|
| *(audit pending)* | | | |

### Business Account — Root Files

| Name | Size | Recommended Action |
|---|---|---|
| *(audit pending)* | | |

---

## COMPLETED OPERATIONS

*(None yet — awaiting audit)*

---

## EXECUTION ORDER (SECTION 11)

### Phase 4-A — Personal account PARA setup ⬜ PENDING
- [ ] Run audit: `python3 dropbox-audit.py --token TOKEN_PERSONAL --account personal`
- [ ] Review root inventory with Shannon
- [ ] Create missing PARA folders (dry run → Shannon approves → execute)
- [ ] Route root items to PARA (Shannon approves each batch)

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
