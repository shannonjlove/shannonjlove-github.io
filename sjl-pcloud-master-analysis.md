# SJL pCloud Master Analysis
**Generated:** 2026-06-29  
**Updated:** 2026-07-12 (Phase 5 complete — root cleanup DONE)  
**Account:** shannonjlove@mac.com  
**Token type:** Non-expiring pCloud access token  
**Storage:** ~2.2 TB used  
**Root item count:** 7 folders, 0 files — down from 62 folders / 118 files before Phase 3

> **SAFETY RULE:** No file is deleted, renamed, or moved until Shannon reviews and approves this list section by section.

---

## COMPLETED OPERATIONS — 2026-07-11

All operations below were approved by Shannon and executed via pCloud REST API. No file was deleted without explicit approval.

### Phase 1 — PARA Folder Renames ✓ (5/5 complete)
| Old Name | New Name |
|---|---|
| `_InBox To Be Sorted pCloud` | `@INBOX_pcloud` |
| `_PROJECTS (pCloud)` | `@PROJECTS_pcloud` |
| `_AREAS (pCloud)` | `@AREAS_pcloud` |
| `_RESOURCES (pCloud)` | `@RESOURCES_pcloud` |
| `_ARCHIVES (pCloud)` | `@ARCHIVES_pcloud` |

### Phase 2 — Destination Subfolders Created ✓ (6/6)
- `@ARCHIVES_pcloud/Rock-The-Bells_ARCHIVES_pcloud/`
- `@ARCHIVES_pcloud/DW-SparseBUNDLE/`
- `@ARCHIVES_pcloud/Unidentified-Video/`
- `@ARCHIVES_pcloud/iDrive-Sync-Archive/`
- `@RESOURCES_pcloud/Graphics-Assets/`
- `@AREAS_pcloud/Stash/`

### File & Folder Moves ✓ (10/10 complete)
| Item | From | To |
|---|---|---|
| `81630.psd` (142.7 MB) | pCloud root | `@RESOURCES_pcloud/Graphics-Assets/` |
| `397404c6...MP4` (57 MB) | `@INBOX_pcloud` | `@PROJECTS_pcloud/UJC/UNREPORTED/` |
| Elephant `.M4V` (41 MB) | `@RESOURCES_pcloud` root | `@AREAS_pcloud/Stash/` |
| `SOTS.library` | pCloud root | `@AREAS_pcloud/Stash/` |
| `RTB_pCloud` folder | `@PROJECTS_pcloud` | `@ARCHIVES_pcloud/Rock-The-Bells_ARCHIVES_pcloud/` |
| `SSC` folder | `@PROJECTS_pcloud` | `@ARCHIVES_pcloud/` |
| `CHAZ` folder | `@PROJECTS_pcloud` | `@ARCHIVES_pcloud/` |
| `DW.sparsebundle` | pCloud root | `@ARCHIVES_pcloud/DW-SparseBUNDLE/` |
| `SJL WORK (iDrive Sync)` | pCloud root | `@ARCHIVES_pcloud/iDrive-Sync-Archive/` |
| `RESOURCES.dtBase2` | `_Live (pCloud)` | `@RESOURCES_pcloud/` |

> **IMG_8009.MOV (32.6 GB) and IMG_8010.MOV (22.9 GB):** Confirmed already located inside `@PROJECTS_pcloud/UJC/UNREPORTED/Terrance Hale/` — no move needed.

### Deletions ✓
| Item | Reason |
|---|---|
| `_BugReport.zip` | pCloud system bug report — Shannon approved |
| `_BugReport.txt` | pCloud system bug report — Shannon approved |
| `_Projects (pCloud) (3)` (empty collision folder) | pCloud sync conflict duplicate, confirmed empty |
| **390 × `Untitled N@YYYYMMDD_HHMMSS`** C4D auto-saves | Unnamed C4D sessions — Shannon approved batch delete |

**Storage freed from C4D deletion: 562 MB across 390 files.**

### Stash App Note
`SOTS.library` (FCPX library) and the elephant `.M4V` video are now in `@AREAS_pcloud/Stash/`. Configure your Stash app to point to `@AREAS_pcloud/Stash/` in pCloud to have these files appear in your Stash library.

---

### Phase 2 — Root Cleanup (2026-07-11) ✓

All items below were approved by Shannon (answers: "1. yes / 2. yes / 3. ok / 4. ok / 5. deploy") and executed.

#### Phase 2-A: GI Render Cache Deletion ✓ (16 files, ~81.5 MB freed)
| Extension | Files | Action |
|---|---|---|
| `.gil` | 3 | Deleted |
| `.gi` | 2 | Deleted |
| `.gi2` | 3 | Deleted |
| `.ao` | 4 | Deleted |
| `.gir` | 4 | Deleted |

#### Phase 2-B: UUID PSDs → Graphics-Assets ✓
| File | Size | Moved To |
|---|---|---|
| `06c40886-..._1.psd` (id=70251376112) | 27.3 MB | `@RESOURCES_pcloud/Graphics-Assets/` |
| `06c40886-....psd` (id=70172937513) | 25.3 MB | `@RESOURCES_pcloud/Graphics-Assets/` |

#### Phase 2-C: Named C4D Auto-Saves Routed ✓ (503 files)
| Destination | Files | Description |
|---|---|---|
| `@RESOURCES_pcloud/C4D-Scenes/` | 10 | WindowLightStudio × 10 auto-saves |
| `@AREAS_pcloud/SJL-Brand/` | several | Files matching `sjl logo`, `sjl_logo`, `sjllogo`, `sjl socials` |
| `@ARCHIVES_pcloud/C4D-Autosaves-Named/` | remainder | All other named project auto-saves + standalone .c4d files |

#### Phase 2-D: `_Live (pCloud)` Dissolved ✓
| Item | Moved To |
|---|---|
| `Automator` | `@ARCHIVES_pcloud/Mac-App-Backups/` |
| `Backups` | `@ARCHIVES_pcloud/pCloud-Backups-2020s/` |
| `Inspirational (pCloud)` | `@RESOURCES_pcloud/Inspirational/` |
| `Love Lessons Memes` | `@AREAS_pcloud/Love-Lessons-Memes/` |
| `Mom's Computer Backup 9-2020` | `@ARCHIVES_pcloud/Moms-Computer-Backup-2020/` |
| `SJL LEARNING & Training Tutorials` | `@RESOURCES_pcloud/SJL-Learning-Tutorials/` |
| `SJL Pics` | `@AREAS_pcloud/SJL-Photos/` |
| `Stock Audio Library (pCloud)` | `@RESOURCES_pcloud/Stock-Audio-Library/` |
| `.DS_Store` | Deleted |
| `_Live (pCloud)` folder itself | Deleted (folder was empty after all moves) |

> Note: `RESOURCES.dtBase2` had already been moved out of `_Live` in Phase 1. Not present when Phase 2 ran.

#### Phase 2-E: `_Work (pCloud)` Dissolved ✓
| Item | Moved To |
|---|---|
| `3D Graphic Assets` | `@RESOURCES_pcloud/3D-Assets/` |
| `C4D Apps Scripts Plugins` | `@RESOURCES_pcloud/C4D-Plugins/` |
| `FCPXBrushVecHelper.app` | `@ARCHIVES_pcloud/Mac-App-Backups/` |
| `Four Page Portfolio Brochure (Indesign Template)` | `@RESOURCES_pcloud/Portfolio-Brochure-Template/` |
| `FreeStoryboardTemplate` | `@RESOURCES_pcloud/Storyboard-Template/` |
| `_Writing (pCloud)` | `@AREAS_pcloud/Writing/` |
| `.DS_Store` | Deleted |
| `_Work (pCloud)` folder itself | Deleted (folder was empty after all moves) |

#### Phase 2-F: Uncharted Backup Folders ✓ / ⚠️
| Folder | Action | Result |
|---|---|---|
| `pCloud Save` (id=27822996614) | → `@ARCHIVES_pcloud/pCloud-Save/` | ✓ Success |
| `icloud drive backup 2025` (id=28826664033) | → `@ARCHIVES_pcloud/iCloud-Backup-2025/` | ✓ Success |
| `pCloud Backup` (id=10614072655) | → `@ARCHIVES_pcloud/pCloud-Backup/` | ⚠️ **FAILED — error 2340** (name conflict: a `pCloud-Backup` folder likely already exists in @ARCHIVES) |

**pCloud Backup next step:** Need to inspect @ARCHIVES contents to see if a `pCloud-Backup` folder already exists there. If yes, merge or use a different name like `pCloud-Backup-Root/`.

#### Phase 2-G: Inventories (No Action Yet — Pending Shannon Decision)

**SJL STUFF TO KEEP** (id=14440336710):
- 1 subfolder, 0 files
- Contains: `Trash It! 7.5` — a macOS application (Trash It! cleaner app backup)
- **Decision needed:** This is a macOS app backup. Route to `@ARCHIVES_pcloud/Mac-App-Backups/` or delete?

**SJL-MIGRATION-STAGING** (id=32149996212):
- 17 folders, 0 files
- Contains: 17 iDrive E2 server infrastructure staging directories:
  `_SYSTEM`, `agent-data-e2`, `archives-idrive-e2`, `areas-idrive-e2`, `assets-e2`,
  `bookstack-data-e2`, `graphics-media-e2`, `inbox-idrive-e2`, `n8n-backups-e2`,
  `paperless-docs-e2`, `private-idrive-e2`, `projects-idrive-e2`, `quarantine-e2`,
  `resources-idrive-e2`, `shannon-photos-e2`, `stacks-backups-e2`, `video-media-e2`
- **Decision needed:** These are server migration staging folders (iDrive E2 structure). Options:
  a) Leave in place — if actively used as migration staging
  b) Move to `@PROJECTS_pcloud/SJL-Personal-Server_PROJECTS_pcloud/` as active infrastructure project
  c) Move to `@ARCHIVES_pcloud/` if the migration is complete

---

---

### Phase 3 — Root Cleanup (2026-07-12) ✓ — 100% success, all 7 batches

All operations approved by Shannon ("batch 1 keep 4d files presets dmg but delete tmp files... batch 7 keep presets, scrivener items, delete terron austin concert") and executed via pCloud REST API.

#### Batch 1 — Junk/cache/tmp deletion ✓
| Item | Result |
|---|---|
| `.DS_Store` (72329370917) | Deleted |
| `updatelist` (70172492733) | Deleted |
| `_trigger.txt` (70251809831) | Deleted |
| `symbolcache` (70172605919) | Deleted |
| `databaseid` (70172492795) | Deleted |
| `cache1` + 2 conflicted copies | Deleted (3 files) |
| `directorycache` + 5 conflicted copies | Deleted (6 files) |
| `.sb-87997749-3zgpJi` sandbox temp folder (18646943716) | Recursively deleted |
| 74 × `net.maxon.*.bin` module registry files | Deleted (74/74) |

#### Batch 2 — C4D System Cache Archive ✓
- Created `@ARCHIVES_pcloud/C4D-System-Cache-2025/` (id=32330803465)
- 32 C4D system folders moved in (01252025 prefs, 2dec64cb, browser, builtinrepository, cache, featurehighlighting, GorillaCam, GSG TRANSFORM, Gumroad HDRI Pack, hair, HDRI Link 1.05 ZIP, layout, libs, light_stroke_intro, materialpreview, materials_*, maxon_generated, plugins, rm, schemes, scripts, sketch, Spiralator and Gridify, SuperText, Trailer Text Effect, Transform, Transform C4D Broadcast Version, Umami v1.2, users, utilities_*, xgroup, xnode)
- `Cinema 4D.prf`, `template.prf`, `template.l4d` moved in
- `Cinema4D-21.026_Mac_Fullinstaller copy.dmg` (268 MB) kept and moved in per Shannon

#### Batch 2 (graphics) — Graphics-Assets ✓
All 14 files → `@RESOURCES_pcloud/Graphics-Assets/` (14/14 ✓):
`Orange stroke.psd` (67.1 MB) · `ce6cdda6...psd` (26.1 MB) · `Cracked Coal Normal.png` (19.3 MB) · `black background.png` (11.4 MB) · `v878-mind-47 copy.psd` (9.2 MB) · 2 vecteezy PNGs (6.4 + 6.3 MB) · `Brush stroke5.png` (5.1 MB) · `Earth map .png` (804 KB) · `brush_stroke.png` (383 KB) · `Steel_Prepared_D.jpg` (370 KB) · `Bumpy_Plastic_DIFF.jpg` (264 KB) · `Brush stroke7@2x.png` (16.6 KB) · `brush_stroke6.png` (3.0 KB)

#### Batch 4 — Getty Images ✓
- `Getty Images Files June 10 2025` (27726075812) renamed `Getty-Images-2025` → `@RESOURCES_pcloud/`
- 9 loose Getty images collected from root into `Getty-Images-2025/` (total ~178 MB)

#### Batch 5 — Mac App Bundles ✓
All 4 → `@ARCHIVES_pcloud/Mac-App-Backups/` (32313437862):
`AirServer 2.app` (20005487062) · `AirServer.app` (20005486020) · `Alfred workflows` (24088968938) · `Adobe` → renamed `Adobe-AppSupport` (20043757780)

#### Batch 6 — Tools → @RESOURCES ✓
| Folder | Renamed To | Result |
|---|---|---|
| `Creative Cloud Libraries` | `Creative-Cloud-Libraries` | ✓ → @RESOURCES |
| `CVToolbox Plugins` | `FCPX-Plugins` | ✓ → @RESOURCES |
| `Graphic & Design tutorials` | `Design-Tutorials` | ✓ → @RESOURCES |
| `Motion Templates` | `Motion-Templates` | ✓ → @RESOURCES |
| Created `C4D-Plugins/` (id=21859934392) | — | ✓ in @RESOURCES |
| `light_stroke_intro.zip` (57853055158) | — | ✓ → C4D-Plugins/ |
| `GSG TRANSFORM.zip` (70172918197) | — | ✓ → C4D-Plugins/ |
| `Stock Video Files.library` | `Stock-Video-Library` | ✓ → @RESOURCES |
| `STOCK VIDEOS LIBRARY.library` (12721937564) | — | ✓ → Stock-Video-Library/ (nested) |

#### Batch 7 — Archives + Terron delete ✓
| Item | Action | Result |
|---|---|---|
| `Backups` (29644739219) | → `@ARCHIVES_pcloud/` as-is | ✓ |
| `Cinema C4D Files Presets Plugins (Archive Files 2023)` (19931395021) | → `@ARCHIVES_pcloud/Cinema-C4D-Archive-2023/` | ✓ |
| `Scrivener Copied Items 9-2-18` (14410451018) | → `@ARCHIVES_pcloud/Scrivener-2018/` | ✓ |
| `Terron Austin Concert FCPX Files.fcpbundle` (18048039310) | **Recursively deleted** per Shannon | ✓ |

**Root after Phase 3 (2026-07-12):**
```
14 folders:  @ARCHIVES_pcloud, @AREAS_pcloud, @INBOX_pcloud, @PROJECTS_pcloud, @RESOURCES_pcloud,
             Company Brochure, Computer & Technology, File Attributes SJL,
             Install macOS Ventura.app, Love Family Portrait, MoviePrints from reel,
             pCloud Backup, SJL Reel Clip Category Excerpts, SJL-MIGRATION-STAGING
1 file:      outline-blank-transparent-world-map-b1b.png (112.9 KB)
```

---

## EXECUTIVE SUMMARY

pCloud has three major problems to solve:

1. **~600 Cinema 4D auto-save files dumped at root** — C4D auto-saves every 5 minutes and stores them in pCloud; these are version files, not standalone projects. Most are `Untitled N@YYYYMMDD_HHMMSS` (unnamed C4D sessions) or named project auto-saves. They can be batch-archived into a `C4D-Autosaves_ARCHIVES_pcloud` subfolder.

2. **Two 55 GB iPhone video files in `_PROJECTS/` root** — `IMG_8009.MOV` (32.6 GB) and `IMG_8010.MOV` (22.9 GB) sitting at the root of the Projects folder. These need to be identified, routed to their project, or archived.

3. **PARA structure exists but uses wrong prefix** — `_ARCHIVES`, `_AREAS`, `_PROJECTS`, `_RESOURCES`, `_InBox To Be Sorted pCloud` exist but use `_` prefix instead of the SJL standard `@` prefix. Also `_Live` and `_Work` are non-standard PARA buckets with no equivalent in the SJL spec.

---

## SECTION 1 — PARA FOLDER INVENTORY

### Current PARA-like folders (need renaming)

| Current Name | Rename To | Items | Notes |
|---|---|---|---|
| `_InBox To Be Sorted pCloud` (id=21145763113) | `@INBOX_pcloud` | 1 file | 1 MP4 (57 MB, UUID filename) |
| `_PROJECTS (pCloud)` (id=10248185073) | `@PROJECTS_pcloud` | 38 items | 36 folders + 2 massive videos at root |
| `_AREAS (pCloud)` (id=10248188025) | `@AREAS_pcloud` | 6 items | Has an app bundle inside (wrong PARA) |
| `_RESOURCES (pCloud)` (id=10248190794) | `@RESOURCES_pcloud` | 19 items | Has elephant video file (41 MB) |
| `_ARCHIVES (pCloud)` (id=10248193524) | `@ARCHIVES_pcloud` | 8 items | Correctly scoped content |

### Non-standard PARA folders (need routing decision)

| Folder | id | Contents | Recommended Disposition |
|---|---|---|---|
| `_Live (pCloud)` (id=5985587663) | 5985587663 | 9 subfolders — personal stuff, SJL Pics, backups, DEVONthink DB | **Merge into PARA:** most → `@AREAS_pcloud`, backups → `@ARCHIVES_pcloud` |
| `_Work (pCloud)` (id=5985589297) | 5985589297 | 7 subfolders — C4D apps, 3D assets, writing, a duplicate `_Projects (pCloud) (3)` | **Merge into PARA:** assets/tools → `@RESOURCES_pcloud`; writing → `@AREAS_pcloud` |

---

## SECTION 2 — ROOT CLUTTER ANALYSIS

The pCloud root has **70 folders and ~1,033 files**. Nearly all the files are Cinema 4D auto-saves or design files that belong in project folders. The folders include many C4D system cache directories and misplaced app bundles.

### 2A — Cinema 4D AUTO-SAVE FILES AT ROOT (bulk of the clutter)

C4D auto-saves to pCloud/root by default when projects are stored there. These are NOT standalone files — they are versioned backups of named projects. They appear as:
- `ProjectName.c4d@YYYYMMDD_HHMMSS` — auto-saves of named projects
- `Untitled N@YYYYMMDD_HHMMSS` — auto-saves of unsaved/unnamed projects
- `.gil`, `.gi`, `.gi2`, `.ao`, `.gir` files — Cinema 4D Global Illumination render cache

**Named project auto-saves found at root:**

| Project | Auto-save count (est.) | Size range/file | Action |
|---|---|---|---|
| `Bounce Back c4d` / `BounceBacksample_012024` | ~15 | 0.5–4.2 MB | Move all to `_PROJECTS/BounceBack/C4D-Autosaves/` |
| `bet-network-logo-svg-vector` | ~6 | 0.2–1.5 MB | Move all to `_PROJECTS/BounceBack/C4D-Autosaves/` (or appropriate project) |
| `2024 film strip attempt` | 2 | 1.5 MB each | Archive (likely dead project) |
| `3LightProductStudio` | 2 | 0.7 MB each | Move to `_RESOURCES/C4D-Scenes/` |
| `10-245v3LIVE` | 4 | 0.5–1.8 MB | Identify project → move to that folder |
| `CCC Logo attempt` / `CCC Logo 01252026` / `CCC Logo V2` | many | **130+ MB each** | Move to `_PROJECTS/DFlat-DEvans-Music_PROJECTS_pcloud/` or CCC project |
| `Crockett Science Channel Intro` | multiple | varies | Move to `_PROJECTS/` Crockett Science folder |
| `DFlat_DEvans_Intro-New` / `DFlat_DEvans-Animation-01` / `DFlat DEvans Full Animated Logo` | multiple | varies | Move to `_PROJECTS/DFlat DEvans Music/` |
| `Entertainment Now Logo` | multiple | varies | Identify project |
| `Enoch Animated Logo` | multiple | varies | Move to `_PROJECTS/Enoch Series Project_pCloud/` |
| `Gay Pride Logo` | multiple | varies | Archive or route to LGBTQ+ project |
| `LoGo LoGo Logo` | multiple | varies | Identify project |
| `Logo-2` | multiple | varies | Identify project |
| `MaxSignal` | multiple | varies | Identify project |
| `Nicodemus Logo` | multiple | varies | Route to Nicodemus Movie project |
| `NUYU Logo Start` | multiple | varies | Identify project |
| `SJL logo BIG` / `SJL logo Final` / `SJL Socials` | multiple | varies | Move to `@AREAS_pcloud/SJL-Brand/` |
| `tv-one-seeklogo` | ~8 | 0.2–1.4 MB | Archive (TV One Lawsuit project) |
| `Vegan Wars Logo Logo in C4D` | 8 | 1.2–1.4 MB each | Archive (Vegan Wars project) |
| `WindowLightStudio` | 10 | 1.3–3.6 MB each | Move to `_RESOURCES/C4D-Scenes/` |
| `Untitled.c4d` (3 versions) | 3 | 2.0 MB each | Archive — unnamed project |
| `Untitled 6.c4d` / `Untitled 5.c4d` | few | 0.5–0.8 MB | Archive — unnamed project |

**Unnamed auto-saves (`Untitled N@YYYYMMDD_HHMMSS`):**
- Approximately **400+ files** in this pattern
- Sizes: mostly 0.1–12 MB; some (Untitled 6 @20250106_200128) as large as **123.6 MB**
- Date range: 2024-01-04 through 2025-02-04
- These are C4D sessions that were never saved to a proper file name
- **Recommended:** Archive all to `@ARCHIVES_pcloud/C4D-Autosaves-Unnamed/` as a batch

**C4D Global Illumination cache files (also at root):**

| File | Size |
|---|---|
| `Untitled 100000.gil` | 11.4 MB |
| `Untitled 200000.gil` | 6.9 MB |
| `Untitled 300000.gil` | 1.7 MB |
| `Untitled 100000.gi2` | 5.4 MB |
| `Untitled 200000.gi2` | 1.1 MB |
| `Untitled 300000.gi2` | 9.4 MB |
| `Untitled 100000.ao` | 3.3 MB |
| `Untitled 200000.ao` | 8.9 MB |
| `Untitled 200041.ao` | 8.5 MB |
| `Untitled 300000.ao` | 4.3 MB |
| `Untitled 200000.gir` | 23.9 MB |
| Various `.gi` files | 0.2 MB each |

**Recommended for all GI cache files:** Delete — these are render computation caches, not source files. C4D regenerates them on render. They have no value without the originals they're cached from.

---

### 2B — APP BUNDLES AND SYSTEM FILES AT ROOT

These should NOT be in cloud storage at root. Apps belong on the Mac, not in pCloud.

| Name | Type | Size | Recommended Action |
|---|---|---|---|
| `AirServer 2.app` (id=20005487062) | macOS app bundle folder | unknown | Move to `@ARCHIVES_pcloud/Downloaded-App-Packages/` |
| `AirServer.app` (id=20005486020) | macOS app bundle folder | unknown | Same |
| `Install macOS Ventura.app` (id=19859048699) | ~12 GB macOS installer | large | Move to `@ARCHIVES_pcloud/Downloaded-App-Packages/` — or delete if no longer needed |
| `DW.sparsebundle` (id=20009922614) | encrypted disk image | unknown | Investigate — this could be important data; move to `@ARCHIVES_pcloud/` |
| `.DS_Store` (id=72329370917) | macOS metadata junk | ~0 | Delete (standard cleanup) |
| `updatelist` (id=70172492733) | unknown text file | ~0 | Investigate — delete if system artifact |
| `_BugReport.zip` (id=70251810009) | bug report archive | ~0 | Delete after review |
| `_BugReport.txt` (id=70172584932) | bug report text | 0.7 MB | Delete after review |

**App-related system folders at root (C4D system dirs — all IDs start with `24711905...`):**
These appear to be Cinema 4D application cache/config directories that pCloud synced from the Mac:
`01252025 prefs`, `2dec64cb`, `browser`, `builtinrepository`, `cache`, `featurehighlighting`, `GorillaCam`, `GSG TRANSFORM`, `Gumroad - 50+ High Quality Studio HDRI Pack`, `HDRI Link 1.05 ZIP`, `hair`, `layout`, `libs`, `light_stroke_intro`, `materials_fnt5i25glflvdmzap7bely`, `materialpreview`, `maxon_generated`, `plugins`, `rm`, `schemes`, `scripts`, `sketch`, `Spiralator and Gridify`, `SuperText`, `Trailer Text Effect`, `Transform C4D Broadcast Version`, `Transform`, `Umami v1.2`, `users`, `utilities_yqf84j9jn9xtaubc5gtgng`, `xgroup`, `xnode`

**Recommended for C4D system dirs:** Move all to `@ARCHIVES_pcloud/C4D-System-Cache-2025/` as a batch — they're C4D application support files accidentally synced. No project value; may not even be compatible with current C4D version.

**Other app/tool folders at root:**
- `Adobe` (id=20043757780) — Adobe application support; → `@ARCHIVES_pcloud/Adobe-AppSupport/`
- `Creative Cloud Libraries` (id=20043780480) — CC Libraries sync folder; → `@RESOURCES_pcloud/Creative-Cloud-Libraries/`
- `CVToolbox Plugins` (id=24969239797) — FCP X plugin; → `@RESOURCES_pcloud/FCPX-Plugins/`
- `Alfred workflows` (id=24088968938) — Alfred macOS launcher workflows; → `@ARCHIVES_pcloud/Mac-App-Backups/`
- `Alfredapp` (in _RESOURCES) — same; consolidate with above
- `Automator` (in _Live) — Mac automations; → `@ARCHIVES_pcloud/Mac-App-Backups/`

---

### 2C — DESIGN FILES AT ROOT (significant size)

| File | Size | Recommended Action |
|---|---|---|
| `81630.psd` (id=70173052648) | **142.7 MB** | Identify what project — route to project folder |
| `vecteezy_yellow-acrylic-paint-stroke-and-splash-brush_39244956 copy.psd` (id=70173008893) | **70.4 MB** | → `@RESOURCES_pcloud/Graphics-Assets/` |
| `vecteezy_yellow-acrylic-paint-stroke-and-splash-brush_39244956-Recovered copy.psd` (id=70172969002) | 33.7 MB | Same (recovered version — delete if copy above is clean) |
| `06c40886-be2f-4469-b866-8c030d5998a0_1.psd` (id=70251376112) | 27.3 MB | Identify (UUID filename = likely downloaded asset) → `@RESOURCES_pcloud/Graphics-Assets/` |
| `06c40886-be2f-4469-b866-8c030d5998a0.psd` (id=70172937513) | 25.3 MB | Same — pair with above |
| `vecteezy_yellow-acrylic-paint-stroke-and-splash-brush_39244956.png` (id=70172760722) | 6.6 MB | → `@RESOURCES_pcloud/Graphics-Assets/` |
| `vecteezy_yellow-acrylic-paint-stroke-and-splash-brush_392449562.png` (id=70493372824) | 6.7 MB | Same |
| `black background.png` (id=70172827141) | 12.0 MB | Route to project where it's used |
| `v878-mind-47 copy.psd` (id=70172774260) | 9.7 MB | Identify project |

---

### 2D — MISCELLANOUS ROOT FOLDERS (non-system)

| Folder | id | Recommended Disposition |
|---|---|---|
| `pCloud Backup` (id=10614072655) | 10614072655 | → `@ARCHIVES_pcloud/pCloud-Backup/` |
| `pCloud Save` (id=27822996614) | 27822996614 | Investigate → `@ARCHIVES_pcloud/` |
| `icloud drive backup 2025` (id=28826664033) | 28826664033 | → `@ARCHIVES_pcloud/iCloud-Backup-2025/` |
| `Backups` (id=29644739219) | 29644739219 | → merge into `@ARCHIVES_pcloud/` |
| `SJL STUFF TO KEEP` (id=14440336710) | 14440336710 | Audit contents → distribute to appropriate PARA buckets |
| `SJL WORK (iDrive Sync)` (id=5801354350) | 5801354350 | Audit contents — may be an old iDrive mirror |
| `SJL Reel Clip Category Excerpts` (id=24164186635) | 24164186635 | → `@PROJECTS_pcloud/SJL-Reel-Resume-2023_pcloud/` or `@ARCHIVES_pcloud/` |
| `Motion Templates` (id=14548027791) | 14548027791 | → `@RESOURCES_pcloud/Motion-Templates/` |
| `Scrivener Copied Items 9-2-18` (id=14410451018) | 14410451018 | → `@ARCHIVES_pcloud/Scrivener-2018/` |
| `Company Brochure` (id=18626866689) | 18626866689 | Identify project → route to PARA |
| `Cinema C4D Files Presets Plugins (Archive Files 2023)` (id=19931395021) | 19931395021 | → `@ARCHIVES_pcloud/Cinema-C4D-Archive-2023/` |
| `Cinema C4D Files Presets Plugins (Archive Files 2023).dmg.sb-87997749-3zgpJi` | 18646943716 | Delete — this is a macOS sandbox temp file (`.sb-XXXXXXXX-XXXXXX` suffix) |
| `Computer & Technology` (id=26383084016) | 26383084016 | Merge into `@AREAS_pcloud/Computer-Technology_pcloud/` |
| `File Attributes SJL` (id=29469767945) | 29469767945 | Investigate — possible metadata files |
| `Getty Images Files June 10 2025` (id=27726075812) | 27726075812 | → `@RESOURCES_pcloud/Getty-Images-2025/` |
| `Graphic & Design tutorials` (id=23962240640) | 23962240640 | → `@RESOURCES_pcloud/Design-Tutorials/` |
| `Love Family Portrait` (id=19890121053) | 19890121053 | → `@ARCHIVES_pcloud/` or `@AREAS_pcloud/family_pcloud/` |
| `MoviePrints from reel` (id=20813303784) | 20813303784 | → `@PROJECTS_pcloud/SJL-Reel-Resume-2023_pcloud/` |
| `SOTS.library` (id=24275722290) | 24275722290 | FCP X library — identify project |
| `Stock Video Files.library` (id=18055122446) | 18055122446 | → `@RESOURCES_pcloud/Stock-Video-Library/` |
| `STOCK VIDEOS LIBRARY.library` (id=12721937564) | 12721937564 | Merge with above |
| `Terron Austin Concert FCPX Files.fcpbundle` (id=18048039310) | 18048039310 | → `@ARCHIVES_pcloud/Terron-Austin-Concert/` |

---

## SECTION 3 — _PROJECTS (pCloud) CONTENTS

**Path:** `_PROJECTS (pCloud)` → rename to `@PROJECTS_pcloud`  
**Total items:** 38 (36 folders + 2 files)

### CRITICAL: Two massive video files at _PROJECTS root

| File | Size | id | Action Needed |
|---|---|---|---|
| `IMG_8009.MOV` | **32.6 GB** | 76051400246 | IDENTIFY what this footage is → route to correct project folder |
| `IMG_8010.MOV` | **22.9 GB** | 75842300726 | Same |

> These two files account for ~55 GB. They are iPhone-named files (IMG_XXXX) — likely raw event footage. Do you know what shoot these are from?

### Project subfolders

| Current Folder Name | Rename To | Notes |
|---|---|---|
| `2 Milk choc promo Text Promo Fly in & Cam zoom (9-2018)` | `Milk-Choc-Promo-2018_PROJECTS_pcloud` | 2018 archive → move to @ARCHIVES_pcloud |
| `Amadaeus & Ashley_pCloud` | `Amadaeus-And-Ashley_PROJECTS_pcloud` | Likely completed → @ARCHIVES_pcloud |
| `BounceBack` | `BounceBack_PROJECTS_pcloud` | Keep in @PROJECTS if active |
| `Cabby & Leo Compton Wedding` | `Cabby-Leo-Compton-Wedding_PROJECTS_pcloud` | Completed → @ARCHIVES_pcloud |
| `CHAZ` | `CHAZ_PROJECTS_pcloud` | Identify project |
| `Content Clutter Tech Overload Stock Media ` | `Content-Clutter-Stock-Media_PROJECTS_pcloud` | Stock media folder? → @RESOURCES_pcloud |
| `Covid Vaccination Spots (2021)` | `Covid-Vaccination-Spots-2021_PROJECTS_pcloud` | Completed 2021 → @ARCHIVES_pcloud |
| `DFlat DEvans Music` | `DFlat-DEvans-Music_PROJECTS_pcloud` | Active? Keep in @PROJECTS |
| `Enoch Series Project_pCloud` | `Enoch-Series_PROJECTS_pcloud` | Active? Keep in @PROJECTS |
| `Genkin Stuff` | `Genkin_PROJECTS_pcloud` | Identify |
| `jdubose` | `JDubose_PROJECTS_pcloud` | Identify |
| `Marve` | `Marve_PROJECTS_pcloud` | Identify |
| `Mel's Open Mic` | `Mels-Open-Mic_PROJECTS_pcloud` | Keep or archive |
| `Melonie Celebration_pCloud` | `Melonie-Celebration_PROJECTS_pcloud` | Completed → @ARCHIVES_pcloud |
| `Melonie Roberson interview With terrance 01132024` | `Melonie-Roberson-Interview-2024_PROJECTS_pcloud` | Archive (2024 completed) |
| `NYPD Grinch Production` | `NYPD-Grinch-Production_PROJECTS_pcloud` | Keep if active |
| `NYPD GRINCH REHEARSALS 11262024` | Move INTO `NYPD-Grinch-Production_PROJECTS_pcloud/` as subfolder | Consolidate |
| `O T Bank ` | `OT-Bank_PROJECTS_pcloud` | Identify |
| `OThybulle 2023 Rent Receipts` | `OThybulle-2023-Rent-Receipts_PROJECTS_pcloud` | 2023 completed → @ARCHIVES_pcloud |
| `OThybulle 2023 Rent Receipts PSD` | Merge into above | Consolidate |
| `Projects.library` | `Projects_FCPX_pcloud` | FCP X library — keep with FCPX projects |
| `RACHAEL FIGUEROA RESUME 2022` | `Rachael-Figueroa-Resume-2022_PROJECTS_pcloud` | 2022 → @ARCHIVES_pcloud |
| `Rachael Resume 2024` | `Rachael-Resume-2024_PROJECTS_pcloud` | 2024 → @ARCHIVES_pcloud (completed) |
| `RTB_pCloud` | `RTB_PROJECTS_pcloud` | Identify (RTB =?) |
| `Shattered (Movie)` | `Shattered-Movie_PROJECTS_pcloud` | Keep if active |
| `SJL Reel Resume 2023` | `SJL-Reel-Resume-2023_PROJECTS_pcloud` | 2023 archive → @ARCHIVES_pcloud |
| `SPENT 2022 ` | `SPENT-2022_PROJECTS_pcloud` | 2022 archive → @ARCHIVES_pcloud |
| `SSC` | `SSC_PROJECTS_pcloud` | Identify |
| `Stock Images African Dancer Project.library` | `African-Dancer-Stock_PROJECTS_pcloud` | Stock library → @RESOURCES_pcloud |
| `StudioBinder: Call Sheet.pdf.sb-ae8b0766-LUF0bL` | DELETE | macOS sandbox temp file (`.sb-XXXXXX-XXXXXX` suffix) — not a real folder |
| `The Stories We Carry \| The Livestream Experience Sessions 1-4 (2)` | `Stories-We-Carry-Livestream_PROJECTS_pcloud` | Identify status |
| `THEE Underground Experience_pCloud` | `Underground-Experience_PROJECTS_pcloud` | Identify status |
| `UJC` | `UJC_PROJECTS_pcloud` | Identify |
| `untitled folder` | DELETE or INVESTIGATE | Empty or accidental |
| `Wakeup The Musical 2024` | `Wakeup-The-Musical-2024_PROJECTS_pcloud` | 2024 completed? → @ARCHIVES_pcloud |

---

## SECTION 4 — _AREAS (pCloud) CONTENTS

**Path:** `_AREAS (pCloud)` → rename to `@AREAS_pcloud`

| Current Name | Recommended Action |
|---|---|
| `AirServer.app` | Move OUT of @AREAS → `@ARCHIVES_pcloud/Mac-App-Backups/` (apps don't belong in AREAS) |
| `Computer & Technology_pCloud` | Keep — merge with root's `Computer & Technology` folder (duplicate names) |
| `Databases` | Keep in @AREAS |
| `Entertainment ` | Keep in @AREAS |
| `family_pcloud` | Keep in @AREAS |
| `.DS_Store` | Delete |

---

## SECTION 5 — _RESOURCES (pCloud) CONTENTS

**Path:** `_RESOURCES (pCloud)` → rename to `@RESOURCES_pcloud`

| Current Name | Recommended Action |
|---|---|
| `2018 SJL Producer Folders` | → @ARCHIVES_pcloud (2018 content) |
| `3D Assets.library` | Keep in @RESOURCES |
| `Adobe Templates Scripts Presets.library` | Keep in @RESOURCES |
| `Alfredapp` | → `@ARCHIVES_pcloud/Mac-App-Backups/` |
| `Apple Loops` | Keep in @RESOURCES (audio assets) |
| `Audio Assets.library` | Keep in @RESOURCES |
| `Audio Library.library` | Merge with Audio Assets.library |
| `CDL School Bus Images` | Identify context |
| `Corel ParticleShop 1.3.0.570 Plugin for Photoshop & Lightroom 2` | → `@ARCHIVES_pcloud/Mac-App-Backups/` |
| `EagleFiler Library Files` | → `@ARCHIVES_pcloud/` (if not using EagleFiler anymore) |
| `Entertainment` | Merge with `_AREAS/Entertainment` — pick one PARA bucket |
| `Graphics_Resources_pCloud` | Keep in @RESOURCES |
| `Resume Templates Collection (pCloud)` | Keep in @RESOURCES |
| `SJL Archived Produced Projects.library` | → @ARCHIVES_pcloud |
| `TV SERIES BIBLE TEMPLATES.library` | Keep in @RESOURCES |
| `Videos To Keep 2024` | → @ARCHIVES_pcloud/Videos-2024/ |
| `_Play (pCloud)` | Identify (non-standard name) → probably @RESOURCES |
| `elephant tramples and crushes its caretaker to death_YouTube_2024-06-22T12-09-27-07-00_videoplayback_ 2024-07-13 15-15-38_Merge(1).M4V` (41.1 MB) | This shouldn't be at root of @RESOURCES with that title — move to personal archives or delete |
| `.DS_Store` | Delete |

---

## SECTION 6 — _ARCHIVES (pCloud) CONTENTS

**Path:** `_ARCHIVES (pCloud)` → rename to `@ARCHIVES_pcloud`  
**Status:** Best organized of all PARA buckets. Mostly correct content.

| Current Name | Action |
|---|---|
| `Cloud-Drive` | Investigate — may be a cloud service backup |
| `Downloaded App  Packages & Archives` | Keep (correct location for app archives) |
| `Getty Downloads.library` | Keep |
| `Irondale 2024 Improv` | Keep |
| `Stock IMAGES 2023.library` | Keep |
| `Stock Stuff 2024` | Keep |
| `_SJL Past Produced Projects_pCloud` | Keep — rename to `SJL-Past-Produced-Projects_pcloud` (remove leading `_`) |
| `.DS_Store` | Delete |

---

## SECTION 7 — _Live (pCloud) — ROUTING DECISIONS NEEDED

**`_Live` is NOT a standard PARA bucket.** Contents need routing to correct buckets.

| Subfolder | Route To |
|---|---|
| `Automator` | → `@ARCHIVES_pcloud/Mac-App-Backups/` |
| `Backups` | → `@ARCHIVES_pcloud/pCloud-Backups-2020s/` |
| `Inspirational (pCloud)` | → `@RESOURCES_pcloud/Inspirational/` |
| `Love Lessons Memes` | → `@AREAS_pcloud/Entertainment/` or `@PROJECTS_pcloud` if active project |
| `Mom's Computer Backup 9-2020` | → `@ARCHIVES_pcloud/Moms-Computer-Backup-2020/` |
| `RESOURCES.dtBase2` | **IMPORTANT:** This is a DEVONthink database backup → `@ARCHIVES_pcloud/DEVONthink-Backup/` |
| `SJL LEARNING & Training Tutorials` | → `@RESOURCES_pcloud/SJL-Learning-Tutorials/` |
| `SJL Pics` | → `@AREAS_pcloud/SJL-Photos/` or `@RESOURCES_pcloud/SJL-Brand/` |
| `Stock Audio Library (pCloud)` | → `@RESOURCES_pcloud/Stock-Audio-Library/` |

---

## SECTION 8 — _Work (pCloud) — ROUTING DECISIONS NEEDED

**`_Work` is NOT a standard PARA bucket.** Contents need routing.

| Subfolder | Route To |
|---|---|
| `3D Graphic Assets` | → `@RESOURCES_pcloud/3D-Assets/` (consolidate with `3D Assets.library`) |
| `C4D Apps Scripts Plugins` | → `@RESOURCES_pcloud/C4D-Plugins/` |
| `FCPXBrushVecHelper.app` | → `@ARCHIVES_pcloud/Mac-App-Backups/` |
| `Four Page Portfolio Brochure (Indesign Template)` | → `@RESOURCES_pcloud/Resume-Templates/` |
| `FreeStoryboardTemplate` | → `@RESOURCES_pcloud/Production-Templates/` |
| `_Projects (pCloud) (3)` | **Investigate** — the " (3)" suffix means pCloud auto-renamed it to avoid collision. This is a duplicate conflict. Look at contents; merge with `@PROJECTS_pcloud` |
| `_Writing (pCloud)` | → `@AREAS_pcloud/Writing/` |

---

## SECTION 9 — _InBox CONTENTS

**Path:** `_InBox To Be Sorted pCloud` → rename to `@INBOX_pcloud`  
**Items:** 1

| File | Size | id | Action |
|---|---|---|---|
| `397404c6-2cf6-4ea2-8951-410780c9b88f.MP4` | 56.9 MB | 68802819627 | UUID filename = likely a pCloud share link download. Identify contents, rename, route to project. |

---

## SECTION 10 — QUESTIONS FOR SHANNON (RESOLVED + OPEN)

### Resolved ✅
1. ~~**IMG_8009.MOV / IMG_8010.MOV**~~ — Already in `@PROJECTS_pcloud/UJC/UNREPORTED/Terrance Hale/`. No action needed.
2. ~~**`81630.psd`**~~ — Moved to `@RESOURCES_pcloud/Graphics-Assets/` per Shannon.
3. ~~**`_Work/_Projects (pCloud) (3)`**~~ — Confirmed empty. Deleted.
4. ~~**`DW.sparsebundle`**~~ — Archived to `@ARCHIVES_pcloud/DW-SparseBUNDLE/` per Shannon.
5. ~~**`RTB_pCloud`**~~ — Rock The Bells. Archived to `@ARCHIVES_pcloud/Rock-The-Bells_ARCHIVES_pcloud/`.
6. ~~**`SSC`**~~ — Archived to `@ARCHIVES_pcloud/` per Shannon.
7. ~~**`CHAZ`**~~ — Archived to `@ARCHIVES_pcloud/` per Shannon.
8. ~~**`UJC`**~~ — Active project. IMG_8009/8010 footage routed to `@PROJECTS_pcloud/UJC/UNREPORTED/`.
9. ~~**`SJL WORK (iDrive Sync)`**~~ — Archived to `@ARCHIVES_pcloud/iDrive-Sync-Archive/` per Shannon.
10. ~~**`SOTS.library`**~~ — Stash app integration. Moved to `@AREAS_pcloud/Stash/`.
11. ~~**Bug reports**~~ — Deleted per Shannon.
12. ~~**390 × Unnamed C4D auto-saves**~~ — Deleted per Shannon. 562 MB freed.
13. ~~**`RESOURCES.dtBase2`**~~ — Moved to `@RESOURCES_pcloud/` per Shannon.
14. ~~**Elephant `.M4V`**~~ — Stash app integration. Moved to `@AREAS_pcloud/Stash/`.
15. ~~**UUID MP4 in @INBOX**~~ — Moved to `@PROJECTS_pcloud/UJC/UNREPORTED/` per Shannon.

### Resolved in Phase 2 ✅ (2026-07-11)
16. ~~**GI cache files**~~ — Deleted. 16 files (~81.5 MB) removed.
17. ~~**UUID PSDs** (06c40886..., 27.3 MB + 25.3 MB)~~ — Moved to `@RESOURCES_pcloud/Graphics-Assets/`.
18. ~~**Named C4D auto-saves at root** (503 files)~~ — Routed: WindowLightStudio → C4D-Scenes, SJL logo/socials → SJL-Brand, all others → C4D-Autosaves-Named.
19. ~~**`_Live (pCloud)` folder**~~ — All 8 subfolders routed to PARA; folder deleted.
20. ~~**`_Work (pCloud)` folder**~~ — All 6 subfolders routed to PARA; folder deleted.
21. ~~**`pCloud Save`**~~ — Moved to `@ARCHIVES_pcloud/pCloud-Save/`.
22. ~~**`icloud drive backup 2025`**~~ — Moved to `@ARCHIVES_pcloud/iCloud-Backup-2025/`.

### Resolved — Phase 2 Wrap-up ✅ (2026-07-11)
23. ~~**`SJL STUFF TO KEEP`**~~ — `Trash It! 7.5` moved to `@ARCHIVES_pcloud/Mac-App-Backups/`; empty wrapper folder deleted.

### Permanent / Leave In Place (Shannon decision)
- **`pCloud Backup`** (id=10614072655) — pCloud system-managed folder (Mac backup feature). Cannot be moved via API (error 2340: "You can't move this folder outside its parent folder."). Contains 4 Mac device backups. Shannon decision: **leave in place**.
- **`SJL-MIGRATION-STAGING`** (id=32149996212) — 17 iDrive E2 server infrastructure folders (active staging area). Shannon decision: **leave in place**.

### Resolved ✅
24. ~~**`vecteezy_yellow-acrylic...psd` (70.4 MB) and recovered version (33.7 MB)**~~ — Both moved to `@RESOURCES_pcloud/Graphics-Assets/`. Note: the `-Recovered` version may be a duplicate — review and delete if the main copy is clean.

### Resolved in Phase 3 ✅ (2026-07-12)
All 7 batches executed with 100% success. Root reduced to 14 folders / 1 file.

25. ~~**Batch 1 — Junk/cache/tmp deletion**~~ — 14 junk files deleted (.DS_Store, updatelist, _trigger.txt, symbolcache, databaseid, cache1 ×3, directorycache ×5); sandbox temp folder `.sb-87997749-3zgpJi` recursively deleted; 74 net.maxon.*.bin module registry files deleted.
26. ~~**Batch 2 — C4D system folders**~~ — All 32 C4D system cache/config folders archived to `@ARCHIVES_pcloud/C4D-System-Cache-2025/` (id=32330803465). C4D pref files (`Cinema 4D.prf`, `template.prf`, `template.l4d`) archived with them. `Cinema4D-21.026_Mac_Fullinstaller copy.dmg` (268 MB) kept per Shannon, archived to same folder.
27. ~~**Batch 2 (graphics) — 14 graphics files → Graphics-Assets**~~ — All 14 files (Orange stroke.psd 67.1 MB, ce6cdda6 PSD 26.1 MB, Cracked Coal Normal.png 19.3 MB, black background.png 11.4 MB, v878-mind-47 copy.psd 9.2 MB, 2× vecteezy PNGs, Brush stroke5.png, Earth map.png, brush_stroke.png, Steel_Prepared_D.jpg, Bumpy_Plastic_DIFF.jpg, Brush stroke7@2x.png, brush_stroke6.png) → `@RESOURCES_pcloud/Graphics-Assets/`.
28. ~~**Batch 4 — Getty Images**~~ — `Getty Images Files June 10 2025` folder (id=27726075812) renamed to `Getty-Images-2025` and moved to `@RESOURCES_pcloud/`. 9 loose Getty image files from root moved into it (Seamless Denim Background 33.7 MB, GettyImages-1629042166 26.8 MB, GettyImages-114283115 25.9 MB, GettyImages-878198966 25.6 MB, GettyImages-1981623172 18.0 MB, GettyImages-1405961965 14.8 MB, GettyImages-1529576564 14.3 MB, GettyImages-1416809594 12.8 MB, GettyImages-1295865290 5.3 MB).
29. ~~**Batch 5 — Mac app bundles**~~ — `AirServer 2.app`, `AirServer.app`, `Alfred workflows` → `@ARCHIVES_pcloud/Mac-App-Backups/`. `Adobe` folder renamed `Adobe-AppSupport` and moved to `@ARCHIVES_pcloud/Mac-App-Backups/`.
30. ~~**Batch 6 — Tools → @RESOURCES**~~ — `Creative Cloud Libraries` → `Creative-Cloud-Libraries`, `CVToolbox Plugins` → `FCPX-Plugins`, `Graphic & Design tutorials` → `Design-Tutorials`, `Motion Templates` → `Motion-Templates`. Created `C4D-Plugins` subfolder (id=21859934392); moved `light_stroke_intro.zip` and `GSG TRANSFORM.zip` into it. `Stock Video Files.library` renamed `Stock-Video-Library` → `@RESOURCES_pcloud/`; `STOCK VIDEOS LIBRARY.library` nested inside `Stock-Video-Library/`.
31. ~~**Batch 7 — Archives + delete**~~ — `Backups` folder → `@ARCHIVES_pcloud/` (as-is). `Cinema C4D Files Presets Plugins (Archive Files 2023)` renamed `Cinema-C4D-Archive-2023` → `@ARCHIVES_pcloud/`. `Scrivener Copied Items 9-2-18` renamed `Scrivener-2018` → `@ARCHIVES_pcloud/`. `Terron Austin Concert FCPX Files.fcpbundle` (id=18048039310) recursively deleted per Shannon.

### Resolved in Phase 4 ✅ (2026-07-12)
32. ~~**B: `Company Brochure`** (18626866689)~~ — moved to `@RESOURCES_pcloud/Graphics-Assets/` per Shannon.
33. ~~**C: `Love Family Portrait`** (19890121053)~~ — moved to `@ARCHIVES_pcloud/`.
34. ~~**D: `SJL Reel Clip Category Excerpts`** (24164186635)~~ — moved to `@ARCHIVES_pcloud/`.
35. ~~**E: `MoviePrints from reel`** (20813303784)~~ — moved to `@ARCHIVES_pcloud/` alongside D.
36. ~~**F: `Computer & Technology`** (26383084016, root)~~ — was **empty**; deleted. Canonical copy lives in `@AREAS_pcloud/Computer & Technology_pCloud/` (id=10342939641).
37. ~~**H: `outline-blank-transparent-world-map-b1b.png`** (70678388805)~~ — moved to `@RESOURCES_pcloud/Graphics-Assets/`.

**Root after Phase 4:** 9 folders, 0 files (5 PARA + pCloud Backup + SJL-MIGRATION-STAGING + 2 pending)

### Resolved in Phase 5 ✅ (2026-07-12)
| # | Item | id | Action |
|---|---|---|---|
| A | `Install macOS Ventura.app` | 19859048699 | **Recursively deleted** (~12 GB recovered) per Shannon ("A delere") |
| G | `File Attributes SJL` | 29469767945 | Renamed `File-Attributes-Reference`, moved to `@AREAS_pcloud/` per Shannon — contains 41 PNG screenshots (Dec 24 2025 session) + `Tags_metadata.pdf` to be manually uploaded by Shannon |

**Root after Phase 5: 7 folders, 0 files — pCloud root cleanup COMPLETE ✅**
```
[10248193524]  @ARCHIVES_pcloud
[10248188025]  @AREAS_pcloud
[21145763113]  @INBOX_pcloud
[10248185073]  @PROJECTS_pcloud
[10248190794]  @RESOURCES_pcloud
[10614072655]  pCloud Backup          ← system-protected (error 2340), leave in place
[32149996212]  SJL-MIGRATION-STAGING  ← active iDrive E2 staging, leave in place
```

> **Manual action needed:** Shannon to upload `Tags_metadata.pdf` directly to `@AREAS_pcloud/File-Attributes-Reference/` in pCloud. The 41 screenshots are already there; the PDF completes the reference folder.

---

## SECTION 11 — RECOMMENDED EXECUTION ORDER

Once Shannon approves, changes execute in this order (no file deleted until all moves confirmed):

### Phase 1 — Rename PARA buckets ✅ COMPLETE (2026-07-11)
1. ~~`_InBox To Be Sorted pCloud`~~ → `@INBOX_pcloud` ✓
2. ~~`_PROJECTS (pCloud)`~~ → `@PROJECTS_pcloud` ✓
3. ~~`_AREAS (pCloud)`~~ → `@AREAS_pcloud` ✓
4. ~~`_RESOURCES (pCloud)`~~ → `@RESOURCES_pcloud` ✓
5. ~~`_ARCHIVES (pCloud)`~~ → `@ARCHIVES_pcloud` ✓

### Phase 2 — Create missing standard subfolders ✅ PARTIALLY COMPLETE (2026-07-11)
- ✓ `@ARCHIVES_pcloud/Rock-The-Bells_ARCHIVES_pcloud/` — created
- ✓ `@ARCHIVES_pcloud/DW-SparseBUNDLE/` — created
- ✓ `@ARCHIVES_pcloud/Unidentified-Video/` — created
- ✓ `@ARCHIVES_pcloud/iDrive-Sync-Archive/` — created
- ✓ `@RESOURCES_pcloud/Graphics-Assets/` — created
- ✓ `@AREAS_pcloud/Stash/` — created
- `@ARCHIVES_pcloud/C4D-Autosaves-Named-2024/` — still needed
- `@ARCHIVES_pcloud/Mac-App-Backups/` — still needed
- `@ARCHIVES_pcloud/C4D-System-Cache-2025/` — still needed
- `@RESOURCES_pcloud/C4D-Scenes/` — still needed

### Phase 3 — Root Cleanup ✅ COMPLETE (2026-07-12)
- ✓ **Batch 1:** 14 junk files deleted + sandbox temp folder + 74 net.maxon.*.bin files
- ✓ **Batch 2:** 32 C4D system folders → `@ARCHIVES_pcloud/C4D-System-Cache-2025/`; 3 C4D pref files + DMG → same archive
- ✓ **Batch 2 (graphics):** 14 graphics files → `@RESOURCES_pcloud/Graphics-Assets/`
- ✓ **Batch 4:** Getty folder renamed `Getty-Images-2025` → `@RESOURCES_pcloud/`; 9 Getty images collected inside
- ✓ **Batch 5:** AirServer 2.app, AirServer.app, Alfred workflows, Adobe-AppSupport → `@ARCHIVES_pcloud/Mac-App-Backups/`
- ✓ **Batch 6:** Creative-Cloud-Libraries, FCPX-Plugins, Design-Tutorials, Motion-Templates, C4D-Plugins/, Stock-Video-Library (nested) → `@RESOURCES_pcloud/`
- ✓ **Batch 7:** Backups, Cinema-C4D-Archive-2023, Scrivener-2018 → `@ARCHIVES_pcloud/`; Terron Austin Concert FCPX bundle deleted

**Root state after Phase 3:** 14 folders / 1 file → Phase 4 → 9 folders / 0 files → Phase 5 → **7 folders / 0 files ✅ COMPLETE**

### Phase 4 — Root cleanup continuation ✅ COMPLETE (2026-07-12)
- ✓ `Company Brochure` → `@RESOURCES_pcloud/Graphics-Assets/`
- ✓ `Love Family Portrait` → `@ARCHIVES_pcloud/`
- ✓ `SJL Reel Clip Category Excerpts` → `@ARCHIVES_pcloud/`
- ✓ `MoviePrints from reel` → `@ARCHIVES_pcloud/`
- ✓ `Computer & Technology` (root, empty) → deleted; @AREAS canonical copy intact
- ✓ `outline-blank-transparent-world-map-b1b.png` → `@RESOURCES_pcloud/Graphics-Assets/`
- **Root: 9 folders, 0 files**

### Phase 5 — Final 2 root items ✅ COMPLETE (2026-07-12)
- ✓ `Install macOS Ventura.app` (id=19859048699) — **recursively deleted** (~12 GB recovered)
- ✓ `File Attributes SJL` (id=29469767945) — renamed `File-Attributes-Reference` → `@AREAS_pcloud/`
- **Root: 7 folders, 0 files — DONE**
- ⬜ Manual: Shannon to upload `Tags_metadata.pdf` to `@AREAS_pcloud/File-Attributes-Reference/`

### Phase 5 — @PROJECTS cleanup (future)
- Rename all project subfolders to SJL convention
- Archive completed projects (Bounce Back, DFlat DEvans, etc.)
- Resolve NYPD Grinch nested subfolder

---

## APPENDIX — FILES NOT YET INVENTORIED (need recursive listing)

These folders need their own recursive listing before we can act on them:
- `SJL STUFF TO KEEP` (id=14440336710)
- `SJL WORK (iDrive Sync)` (id=5801354350)
- `pCloud Backup` (id=10614072655)
- `pCloud Save` (id=27822996614)
- `icloud drive backup 2025` (id=28826664033)
- `_Work/_Projects (pCloud) (3)` (id=6005343571)
- All 36 project subfolders in _PROJECTS (need file counts/sizes to prioritize)

---

*Phase 1 operations executed 2026-07-11. All changes were approved by Shannon before execution.*  
*All future actions require Shannon's explicit approval before execution. No file is deleted without review.*
