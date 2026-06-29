# SJL pCloud Master Analysis
**Generated:** 2026-06-29  
**Account:** shannonjlove@mac.com  
**Token type:** Non-expiring pCloud access token  
**Storage:** ~2.2 TB used  
**Root item count:** 1,103 (files + folders)

> **SAFETY RULE:** No file is deleted, renamed, or moved until Shannon reviews and approves this list section by section.

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

## SECTION 10 — QUESTIONS FOR SHANNON (BEFORE ANY CHANGES)

The following require your input before we can route or archive:

1. **IMG_8009.MOV (32.6 GB) and IMG_8010.MOV (22.9 GB)** in `_PROJECTS/` root — what event/shoot is this footage from? Which project do they belong to?

2. **`81630.psd` (142.7 MB)** at pCloud root — what project is this for?

3. **`_Work/_Projects (pCloud) (3)`** — pCloud renamed this folder because a collision occurred. What's in it? Should it be merged into @PROJECTS_pcloud?

4. **`DW.sparsebundle`** at root — what is this encrypted disk image? It could be important data (DW = Disk Warrior? or Dropbox Wardrobe? or something else?).

5. **`RTB_pCloud`** — what is RTB? What project?

6. **`SSC`** — what is SSC?

7. **`CHAZ`** — what project is CHAZ?

8. **`UJC`** — what is UJC?

9. **`SJL WORK (iDrive Sync)` (id=5801354350)** at root — is this an old iDrive backup that has since been migrated? Safe to archive?

10. **`SOTS.library` (id=24275722290)** — FCP X library; what project is "SOTS"?

11. **`_BugReport.zip` / `_BugReport.txt`** — are these pCloud bug reports you submitted? Safe to delete?

12. **Cinema 4D unnamed autosaves** — the ~400 `Untitled N@YYYYMMDD_HHMMSS` files: do you want to review these before archiving, or batch-archive them all to `@ARCHIVES_pcloud/C4D-Autosaves-Unnamed-2024-2025/`?

13. **`RESOURCES.dtBase2`** (DEVONthink database in _Live) — is this a backup of your DEVONthink RESOURCES database? Safe to move to @ARCHIVES_pcloud/DEVONthink-Backup/?

14. **`elephant tramples...M4V` (41 MB) in _RESOURCES** — this appears to be a YouTube download that ended up in _RESOURCES. Delete or archive?

15. **`397404c6-2cf6-4ea2-8951-410780c9b88f.MP4` (57 MB) in _InBox** — UUID filename means this was likely a pCloud share link download or auto-generated. Do you remember what video this is?

---

## SECTION 11 — RECOMMENDED EXECUTION ORDER

Once Shannon approves, changes execute in this order (no file deleted until all moves confirmed):

### Phase 1 — Rename PARA buckets (5 renames, no content moved)
1. `_InBox To Be Sorted pCloud` → `@INBOX_pcloud`
2. `_PROJECTS (pCloud)` → `@PROJECTS_pcloud`
3. `_AREAS (pCloud)` → `@AREAS_pcloud`
4. `_RESOURCES (pCloud)` → `@RESOURCES_pcloud`
5. `_ARCHIVES (pCloud)` → `@ARCHIVES_pcloud`

### Phase 2 — Create missing standard subfolders
- `@ARCHIVES_pcloud/C4D-Autosaves-Named-2024/` — for named project C4D auto-saves
- `@ARCHIVES_pcloud/C4D-Autosaves-Unnamed-2024-2025/` — for ~400 Untitled@ files
- `@ARCHIVES_pcloud/Mac-App-Backups/` — for app bundles
- `@ARCHIVES_pcloud/C4D-System-Cache-2025/` — for C4D system dirs
- `@RESOURCES_pcloud/Graphics-Assets/` — for design files
- `@RESOURCES_pcloud/C4D-Scenes/` — for reusable C4D scenes

### Phase 3 — Delete junk (zero-risk files)
- All `.DS_Store` files (7+ instances)
- `Cinema C4D Files Presets Plugins (Archive Files 2023).dmg.sb-87997749-3zgpJi` (macOS temp sandbox dir)
- `StudioBinder: Call Sheet.pdf.sb-ae8b0766-LUF0bL` (macOS temp sandbox dir — not a real folder)
- All C4D GI render cache files (`.ao`, `.gi`, `.gi2`, `.gil`, `.gir`) — these have no standalone value
- `_BugReport.zip` and `_BugReport.txt` (pending confirmation from Shannon)

### Phase 4 — Batch-archive C4D auto-saves
- Move all `Untitled N@YYYYMMDD_HHMMSS` files → `@ARCHIVES_pcloud/C4D-Autosaves-Unnamed-2024-2025/`
- Move named project auto-saves → appropriate `@PROJECTS_pcloud/[ProjectFolder]/C4D-Autosaves/`

### Phase 5 — Route design files at root
- Move PSD/PNG design files → `@RESOURCES_pcloud/Graphics-Assets/`
- Route app bundles → `@ARCHIVES_pcloud/Mac-App-Backups/`

### Phase 6 — Route C4D system dirs
- Batch-move all C4D system dirs (IDs: 24711905...) → `@ARCHIVES_pcloud/C4D-System-Cache-2025/`

### Phase 7 — Dissolve _Live and _Work
- Route each subfolder to correct PARA bucket per Section 7 and 8 above
- Delete the now-empty _Live and _Work folders

### Phase 8 — Route remaining root folders
- Per Section 2D above, route each named folder to correct PARA bucket

### Phase 9 — Resolve _PROJECTS questions
- Route IMG_8009 and IMG_8010 after identification
- Rename all project subfolders to SJL convention
- Archive completed projects

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

*This document was generated by Claude Code from the pCloud API. No changes have been made.*  
*All recommended actions require Shannon's explicit approval before execution.*
