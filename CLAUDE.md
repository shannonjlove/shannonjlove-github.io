# CLAUDE.md — Shannon J. Love | shannonjlove.cloud
# Persistent Knowledge Base — Naming · Linking · File Architecture · Cloud Ops

---

## !! GOVERNING RULE — READ THIS FIRST, EVERY TIME !!

> **This section is the single most authoritative piece of information in this project.**
> No file is created, renamed, moved, uploaded, or migrated without following these rules.
> This applies to ALL cloud services, ALL tools, ALL automations, and ALL agents.
> When in doubt: name it, link it, route it, log it. In that order. Every time.

---

## PART 1 — SJL CANONICAL FILE NAMING CONVENTION

### Master Format

```
YYYY-MM-DD_HH-MM_category-subcategory_description_UUID24.ext
```

| Segment | Format | Rules | Example |
|---|---|---|---|
| Date | `YYYY-MM-DD` | ISO 8601 always. Never MMDDYYYY. | `2026-06-29` |
| Time | `HH-MM` (24h) | Use creation time, not today | `14-30` |
| Category | lowercase | Hyphen-separated, from taxonomy | `media` |
| Subcategory | lowercase | Hyphen-separated, from taxonomy | `video` |
| Description | lowercase | Hyphens only, max 40 chars | `austin-walk-thru` |
| UUID24 | 24-char hex | From uuid4().hex[:24] | `a1b2c3d4e5f6a1b2c3d4e5f6` |
| Extension | lowercase | Always lowercase | `.mov` |

**Full example:**
```
2026-06-29_14-30_media-video_austin-walk-thru_a1b2c3d4e5f6a1b2c3d4e5f6.mov
```

### Folder Naming Format (no time, no UUID)
```
YYYY-MM-DD_category-subcategory_description/
```
Or for PARA project folders:
```
Project-Name_PROJECTS_[cloud]/
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
| `hook` | `hub` · `link` · `deep` · `search` |
| `general` | `file` · `misc` |

### Date Format Rules
- **Always ISO 8601:** `YYYY-MM-DD` — never `MMDDYYYY`, never `MM-DD-YY`
- Use the file's original creation date, not today's date when processing old files
- For folders: omit time and UUID

---

## PART 2 — SJL FILE PROCESSING WORKFLOW

Every file that enters any cloud service passes through this exact sequence. No exceptions.

```
[1] ARRIVES IN @INBOX_[cloud]
          |
          v
[2] IDENTIFY
    - category + subcategory (from taxonomy above)
    - originating project or area
    - file type (native doc vs export duplicate)
    - is it a duplicate? → if yes, trash export, keep native
          |
          v
[3] APPLY SJL RENAME
    YYYY-MM-DD_HH-MM_cat-subcat_desc_UUID24.ext
    UUID24 is the permanent identity of this file forever
          |
          v
[4] GENERATE LINKS (Hook Layer)
    a) Cloud-native share URL (permanent, not temporary)
    b) Clean link: strip all tracking params (?utm_*, &ref=, etc.)
    c) Universal link: wrapped for cross-app / web-app use
    d) Markdown link: [SJL-filename](clean-url)
    e) Deep link (if PDF or video): include page/timestamp anchor
          |
          v
[5] ROUTE TO PARA FOLDER
    @PROJECTS / @AREAS / @RESOURCES / @ARCHIVES in that cloud
    Hook file to its PARA folder entry in Raindrop
          |
          v
[6] HOOKVAULT FIRES WEBHOOK -> RAINDROP.IO
    Full payload (see Part 3) including:
    - Raindrop collection = PARA bucket
    - Tags = cloud + category + subcategory + project
    - Related links = siblings already in same project cluster
    - Hub link = project hub Raindrop entry
    - Bidirectional: update hub entry to include this file's link
          |
          v
[7] TAG IN CLOUD NATIVE SYSTEM
    Apply cloud service's own labels/colors/tags
    Mirror: PARA bucket + category + project name
          |
          v
[8] LOG TO MASTER INVENTORY
    Google Sheets or Notion row: filename, cloud, UUID24, Raindrop URL,
    PARA bucket, project, date processed
          |
          v
[9] RESOLVE ORIGINALS
    Delete or trash duplicate exports
    Archive pre-rename versions if historically significant
    Confirm source file is now the canonical SJL-named version
```

**FileWarden** (`filewarden.py`) automates steps 3–6 on `shannonjlove.cloud`.
All other clouds: HookVault handles steps 4–6 via webhook automation.

---

## PART 3 — HOOKVAULT SYSTEM: FULL ARCHITECTURE

### What HookVault Is (in the SJL context)

HookVault is the server-side equivalent of **Hookmark** — the Mac app that makes every
file, email, task, and webpage linkable, hookable, and navigable from any context.

Hookmark's core insight: **the file is the anchor, not the folder.** From any file you
can reach every related file instantly, without searching, without navigating folder trees.

HookVault replicates this for cloud-based files:
- Every file gets a permanent, resilient, cross-app link the moment it's processed
- Every link fires to Raindrop.io, which becomes the universal navigation hub
- Raindrop serves as the "invoke Hookmark" equivalent: one interface to reach any file
  across all 8 cloud services, organized by PARA and clustered by project

---

### TRIGGER LAYER — What Creates a Hook

| Event | Hook Created |
|---|---|
| File arrives in @INBOX | Auto-hook: initial bookmark in Raindrop @INBOX collection |
| File renamed to SJL convention | Update existing hook (don't create new one — UUID is identity) |
| File routed to PARA folder | Hook file → folder; hook folder entry updated in Raindrop |
| New project folder created | Create Project Hub hook in Raindrop @PROJECTS + FOLDERS collections |
| File added to existing project | Hook file → project hub (bidirectional) |
| Webpage saved as PDF | Hook PDF ↔ source webpage (bidirectional pair) |
| File version/edit committed | Hook change entry → CHANGES collection |
| File shared with collaborator | Generate Universal Link (web-safe wrapper) |
| Duplicate detected | Hook both → parent entry noting duplicate resolution |
| File migrated between clouds | Hook: old location → new location (redirect entry) |

---

### LINK GENERATION LAYER — Every File Gets All of These

For every processed file, HookVault generates and stores all link forms:

```
1. NATIVE LINK       cloud-native permanent share URL
                     e.g. https://drive.google.com/file/d/[id]/view

2. CLEAN LINK        native URL stripped of tracking params
                     removes: ?utm_*, &ref=, &source=, &via=, &fbclid=, etc.
                     rule: keep only the minimum path to identify the file

3. UNIVERSAL LINK    web-app-safe wrapper (mirrors hookmark.net pattern)
                     format: https://hook.shannonjlove.cloud/open?id=[UUID24]
                     resolves to native link locally; safe to paste in any web app

4. MARKDOWN LINK     [YYYY-MM-DD_cat-subcat_description](clean-url)
                     for embedding in docs, notes, Notion, BookStack, etc.

5. DEEP LINK         for PDFs: native-url#page=[n]&highlight=[text-anchor]
                     for videos: native-url#t=[seconds]
                     for Google Docs: native-url?usp=sharing (direct edit link)

6. SEARCH LINK       hook://search?q=[UUID24]
                     triggers search across Raindrop + all connected tools
                     for finding the file even if its URL has changed
```

---

### BIDIRECTIONAL LINKING RULES

This is the most important Hookmark principle. Every link must go both ways.

**Rule 1: File ↔ Project Hub**
- When a file is added to a project, its Raindrop entry gets `hub_link` pointing to the project hub
- The project hub entry is simultaneously updated to include this file in its `related_links` array
- Result: from the hub you see all files; from any file you reach the hub

**Rule 2: File ↔ Sibling Files**
- All files in the same project have each other in their `related_links`
- This is maintained as a cluster, not individual pairs
- Hub entry is the source of truth for the cluster list

**Rule 3: Webpage ↔ PDF**
- When a webpage is archived as PDF (Hook to New PDF equivalent):
  - PDF Raindrop entry: `source_url` = original webpage URL
  - Raindrop bookmark for webpage: `pdf_link` = PDF's cloud URL
  - Both entries tagged `hook-linked-pair`

**Rule 4: File ↔ Folder**
- Every file's Raindrop entry includes `parent_folder_link` = Raindrop URL of its PARA folder entry
- Every PARA folder's Raindrop entry includes the count and list of files inside

**Rule 5: Change ↔ Source File**
- Every CHANGES entry links back to the file that was changed
- The source file's Raindrop entry is updated with `last_change_link`

**Rule 6: Cross-Cloud Duplicates**
- If the same logical file exists on 2 clouds (intentional mirror or accidental duplicate):
  - One is designated `canonical` (usually the highest-fidelity version)
  - Both entries in Raindrop link to each other with tag `cross-cloud-mirror`

---

### DEEP LINKING — Precision Navigation Inside Files

Hookmark's deep linking goes inside files, not just to them. We replicate this:

| File Type | Deep Link Format | Example |
|---|---|---|
| PDF | `url#page=N` | `/drive/file/...#page=12` |
| PDF selection | `url#highlight=base64text` | exact passage anchor |
| Video | `url#t=Ns` | `youtube.com/...#t=342` (5:42) |
| Google Doc | `url#heading=id` | section-level anchor |
| Google Sheet | `url#gid=N&range=A1:C10` | cell range anchor |
| Notion page | `url#block-id` | block-level anchor |

**When to create deep links:**
- Any PDF over 5 pages: link to the relevant section, not just the file
- Any video over 3 minutes: link to the relevant timestamp
- Any long Google Doc: link to the relevant heading
- Research sources: link to the specific passage cited

Deep links are stored in the Raindrop entry under `deep_link` field and in the Markdown link.

---

### ADAPTIVE / RESILIENT LINKS — Links That Survive Change

Hookmark's file links survive renames, moves, and cloud syncs. We replicate this via UUID24.

**The UUID24 is the file's permanent identity.** It never changes. Even if:
- The file is renamed (description changes) → UUID stays
- The file is moved to another folder → UUID stays
- The file is migrated to a different cloud → UUID stays
- The file is versioned or updated → UUID stays (new version = new UUID)

**When a file is renamed or moved:**
1. Do NOT create a new Raindrop entry
2. Find the existing entry by UUID24
3. UPDATE the title, link, and collection in place
4. Add a CHANGES entry noting the rename/move with old → new link
5. All existing bidirectional links remain valid because UUID is stable

**Raindrop Search Link as fallback:**
- If the native URL ever breaks (file deleted/moved without updating Raindrop):
- `hook://search?q=[UUID24]` triggers a search across all indexed clouds
- UUID24 in the filename makes the file findable even if the URL is dead

---

### PROJECT HUB RULES

Every project in `@PROJECTS_[cloud]` gets exactly ONE hub entry in Raindrop.
The hub is the cluster anchor. Every file in the project links to it; it links to all of them.

**Hub entry format:**
```
Title:      [Project-Name] HUB — [PARA_cloud]
Link:       Raindrop self-link or cloud folder URL
Excerpt:    Active project | [cloud] | Created: YYYY-MM-DD | Files: N
Tags:       hub, project, [cloud], [project-slug], sjl
Collection: @PROJECTS
Note:       [list of all file Raindrop URLs in this project]
Pinned:     YES (active projects are pinned)
```

**Hub lifecycle:**
- Created: when the project PARA folder is created in any cloud
- Updated: each time a file is added (file count incremented, link appended to Note)
- Unpinned: when project moves to @ARCHIVES (hub moves to @ARCHIVES collection)
- Archived: hub entry moves to @ARCHIVES collection; remains searchable

---

### FOLDER BOOKMARK RULES

Every PARA folder across all 8 clouds gets its own Raindrop entry. Folders are hookable.

**40 mandatory folder entries** (5 PARA × 8 clouds):
- Created when the folder is first set up in each cloud
- Stored in Raindrop `FOLDERS` collection
- Each folder entry contains: folder URL, cloud, PARA bucket, file count
- Tag: `folder`, `[cloud]`, `[para-bucket]`

**Why this matters:** You can navigate to any PARA folder on any cloud in one Raindrop search,
without opening the cloud service. The folder is a hookable entity, not just a container.

---

### RAINDROP.IO COLLECTION STRUCTURE

```
RAINDROP.IO
|
+-- @PROJECTS        Active project hubs (pinned) + individual project files
|     tagged: hub (hubs), [project-slug] (all files per project)
|
+-- @AREAS           Ongoing area files and area folder entries
|
+-- @RESOURCES       Reference files, templates, assets, tools
|
+-- @ARCHIVES        Completed project hubs + historical files
|
+-- @INBOX           Unprocessed items awaiting routing
|
+-- CHANGES          Audit trail: every rename, move, version, migration
|
+-- FOLDERS          All 40 PARA folder entries (5 x 8 clouds)
|
+-- PAIRS            Bidirectionally linked pairs (webpage <-> PDF, etc.)
|
+-- SEARCH-LINKS     hook://search entries for quick cross-cloud searches
```

### Raindrop Views to Maintain

| View | Purpose |
|---|---|
| **Pinned** | All active project hubs — the daily work surface |
| **Recent** | Last 50 items touched — quick return to context |
| **Tags > hub** | All project hubs across all clouds |
| **Tags > change** | Full change/audit log |
| **Tags > folder** | All 40 PARA folder entries |
| **Tags > [cloud]** | All files on a specific cloud service |

---

### HOOKVAULT WEBHOOK PAYLOAD — FULL SPECIFICATION

Every HookVault webhook to Raindrop.io sends this complete payload:

```json
{
  "title":         "YYYY-MM-DD_HH-MM_cat-subcat_description_UUID24.ext",
  "link":          "https://[clean-cloud-native-url]",
  "universal_link":"https://hook.shannonjlove.cloud/open?id=[UUID24]",
  "markdown_link": "[title](clean-url)",
  "deep_link":     "https://[url]#[anchor-if-applicable]",
  "search_link":   "hook://search?q=[UUID24]",
  "excerpt":       "Cloud: [cloud] | PARA: [bucket] | Project: [name] | Cat: [cat-subcat]",
  "collection":    "[PARA bucket name]",
  "tags":          ["sjl", "[cloud]", "[category]", "[subcategory]", "[para-bucket]", "[project-slug]"],
  "hub_link":      "[Raindrop URL of project hub, if applicable]",
  "related_links": ["[sibling file URLs in same project cluster]"],
  "parent_folder_link": "[Raindrop URL of parent PARA folder entry]",
  "source_url":    "[original webpage URL, if this is a saved PDF]",
  "uuid24":        "[24-char permanent file identity]",
  "cloud":         "[gdrive | mediafire | pcloud | dropbox | dropbox-biz | mega | icloud | sjlcloud]",
  "para_bucket":   "[projects | areas | resources | archives | inbox]",
  "is_hub":        false,
  "is_folder":     false,
  "is_duplicate_of": null,
  "canonical":     true,
  "created":       "YYYY-MM-DDTHH:MM:SSZ",
  "processed_by":  "filewarden | hookvault | manual"
}
```

---

### PER-CLOUD RAINDROP TAGS

| Cloud | Primary Tag | Folder Tag Example |
|---|---|---|
| Google Drive | `gdrive` | `folder-gdrive-projects` |
| MediaFire | `mediafire` | `folder-mediafire-areas` |
| pCloud | `pcloud` | `folder-pcloud-resources` |
| Dropbox (personal) | `dropbox` | `folder-dropbox-archives` |
| Dropbox-biz (2nd acct) | `dropbox-biz` | `folder-dropbox-biz-projects` |
| MEGA | `mega` | `folder-mega-inbox` |
| iCloud Drive | `icloud` | `folder-icloud-projects` |
| shannonjlove.cloud | `sjlcloud` | `folder-sjlcloud-projects` |
| GitHub | `github` | `folder-github-code` |

---

### MARKDOWN LINK STANDARD

Every processed file must have a Markdown link stored in Raindrop's Note field:

```markdown
[2026-06-29_14-30_media-video_austin-walk-thru_a1b2c3d4e5f6a1b2c3d4e5f6.mov](https://drive.google.com/file/d/[id]/view)
```

For embedding in documents, notes, BookStack, and Notion:
- Use the Markdown link — never a raw URL
- Never use Google Drive "sharing" URLs with tracking params
- Always use the clean version of the URL

---

### AUTOMATION TRIGGERS (HookVault equivalents of Hookmark Shortcuts/AppleScript)

| Trigger | Tool | Action |
|---|---|---|
| File lands in @INBOX | FileWarden (watchdog) | Auto-rename + auto-hook |
| File renamed | FileWarden | Update Raindrop entry by UUID24 |
| n8n webhook received | n8n / HookVault | Fire Raindrop create/update |
| New project folder created | Shell script | Create hub entry in Raindrop |
| File shared | HookVault | Generate Universal Link + send to Raindrop |
| Change committed (Git) | Git post-commit hook | Log to CHANGES in Raindrop |
| PDF saved from webpage | HookVault | Create bidirectional pair in Raindrop PAIRS |
| File migrated to new cloud | Migration script | Update Raindrop link; add cross-cloud tag |

---

## PART 4 — KNOWLEDGE BASE: HOOKMARK SYSTEM CONCEPTS
*(Persistent reference — do not remove or summarize)*

### What Hookmark Is

Hookmark (formerly Hook) is a macOS system-wide linking, bookmarking, and context-navigation
tool. Built on 20+ years of R&D in cognitive productivity. It is not a bookmark manager —
it is a **relational fabric** woven between files, emails, tasks, notes, PDFs, and webpages
across all apps on the Mac.

**The core principle:** The file is the anchor. From any file, you see every related item.
You navigate *between* items without returning to folder hierarchies or search.

### Complete Hookmark Feature Set (integrated into SJL system)

**1. Contextual Bookmarking**
Create and manage bookmarks to files, emails, tasks, and more for rapid access.
SJL equivalent: Raindrop.io entries, auto-created by HookVault for every processed file.

**2. Bidirectional Linking**
Instantly create two-way links between any two resources.
After copying a link, "Hook to Copied Link" creates the bidirectional pair automatically.
SJL equivalent: hub_link + related_links in every HookVault webhook payload.

**3. Deep Linking**
Links to specific locations inside PDFs (text selection, page number) and QuickTime videos.
Links reopen the file at the precise location. Robust and shareable.
SJL equivalent: deep_link field in payload; #page= and #t= anchors in all PDF/video links.

**4. Adaptive / Resilient File Links**
File links survive renames, moves, cloud sync, and version control (Git/SVN).
Works with iCloud and Dropbox locally synced folders.
.hook files: plain-text, editable link files that can point to anything (Pro).
SJL equivalent: UUID24 in filename is the permanent identity; Raindrop updated in place.

**5. Hook to New**
Create a new item in any app, name it, tag it, and hook it to the current item — one action.
Ideal for linked notes and project scaffolding.
SJL equivalent: when creating a new project file, immediately fire HookVault to create hub link.

**6. Clean My Links™**
Auto-removes tracking cruft from URLs (utm_, ref=, fbclid, etc.).
Updates cleaning rules automatically without restart. Custom rules (Pro).
SJL equivalent: clean_link step in LINK GENERATION LAYER; strip all tracking params before storage.

**7. Universal Links (for web apps)**
Wraps custom app:// links in https://hookmark.net URLs so web-based tools can accept them.
Copy As Universal Link / Copy As Universal Markdown Link / Copy Selection and Universal Link.
SJL equivalent: https://hook.shannonjlove.cloud/open?id=[UUID24] universal wrapper.

**8. Links to Emails**
Direct links to specific email messages. Escape the inbox.
Paste into tasks, notes, project documents. Works with major Mac email clients.
SJL equivalent: email deep links hooked to project files via HookVault when relevant.

**9. Well-Formatted Links for Apple Mail**
Preserves link titles when pasting into Apple Mail (workaround for Mail's stripping behavior).
SJL equivalent: always use Markdown link format when embedding in email drafts.

**10. Hook to New PDF**
One command: create PDF of current webpage, save it, hook it to the source page, tag it,
bookmark it, open it. Saves to configured location.
SJL equivalent: when saving a webpage PDF to any cloud:
  - Rename to SJL convention
  - Create PAIRS entry in Raindrop linking PDF ↔ source URL
  - Store in @RESOURCES_[cloud] under appropriate category

**11. Effortless Bookmarking**
World's first universal automatic bookmarking system. Bookmark anything, not just webpages.
Auto-created as you work. Manual: ⌘D. Search: ⌥⌘F.
SJL equivalent: FileWarden auto-hooks everything; HookVault fires automatically.

**12. Bookmarks Window / Views**
Views: Pinned · All · Recent · Tags
Pin and tag bookmarks for projects and focus areas.
SJL equivalent: Raindrop Pinned (active project hubs) · All · Recent · Tags views.

**13. Integration with Other Bookmarking Software**
Integrates with DEVONthink, Pinboard, GoodLinks, Instapaper, Linkding.
Automatically adds bookmarks to those systems.
SJL equivalent: Raindrop is primary; secondary sync to Notion or Sheets as needed.

**14. Share the Previously Unshareable**
Share links to emails, files, Spotlight searches. Recipients land in the right context.
SJL equivalent: Universal Link wrapper makes any cloud file shareable to any collaborator.

**15. Markdown Innovation**
Universal Copy Markdown Link for anything.
Embed resilient file links in Markdown. .hook files can contain Markdown links.
SJL equivalent: Markdown link standard — every file has [title](clean-url) stored.

**16. Automation**
Apple Shortcuts actions for bookmarking and linking.
AppleScript support. LaunchBar, Alfred, Keyboard Maestro integration.
SJL equivalent: FileWarden (watchdog) + n8n webhooks + HookVault scripts.

**17. Customize and Auto-Update Software Integrations**
Edit and create integration scripts (Pro). Update without relaunching.
SJL equivalent: HookVault integration scripts in @PROJECTS_gDrive > SJL-Personal-Server > Auto/

**18. Reveal Current File in Finder (⌘R)**
Instantly reveal the current file in Finder.
SJL equivalent: cloud file reveal — every Raindrop entry links to cloud-native folder view.

**19. Works with Information Managers, Search Tools, Launchers**
DEVONthink, Keep It, Evernote. HoudahSpot. LaunchBar, Alfred, Raycast.
SJL equivalent: Raindrop search is the universal launcher for all cloud files.

**20. Sync Across Devices**
Sync across Macs. Hookmark Pal for iPhone/iPad. iCloud or folder-based sync.
SJL equivalent: Raindrop.io is cloud-native — accessible on all devices natively.

**21. hook://search Links**
Trigger Spotlight searches from links. Navigable from anywhere.
SJL equivalent: `hook://search?q=[UUID24]` stored as search_link in every Raindrop entry.

**22. Automatic Finder Tagging**
Tags applied in Finder when a hook is created.
SJL equivalent: cloud-native tags applied at routing step; mirrors PARA + category.

**23. Quick Look Support**
Preview files without opening them.
SJL equivalent: Raindrop preview cards + cloud-native preview URLs.

**24. Import/Export and Automatic Backups**
SJL equivalent: periodic Raindrop backup export to @ARCHIVES_gDrive.

**25. Privacy First**
All Hookmark bookmarks stored locally, never sent to developer.
SJL equivalent: UUID24 identifiers are opaque; no PII in link payloads; Raindrop uses secure auth.

**26. Open, Interoperable**
Hookmark champions interoperability and inter-app communication.
SJL equivalent: open webhook standard; universal links resolvable by any HTTP client.

---

## PART 5 — UNIVERSAL PARA STRUCTURE

Every cloud service uses the same 5-bucket PARA structure.
`@` prefix sorts all PARA folders to the top of any file listing.

### PARA Bucket Definitions

| Bucket | Definition | Contents |
|---|---|---|
| `@INBOX` | Landing zone only — nothing lives here | New files awaiting processing |
| `@PROJECTS` | Active work with a defined outcome and deadline | Project folders, active deliverables |
| `@AREAS` | Ongoing responsibilities with no end date | Health, finances, relationships, skills |
| `@RESOURCES` | Reference material, assets, templates | Research, stock media, tools, guides |
| `@ARCHIVES` | Completed, inactive, or historical | Finished projects, old files, backups |

### Cloud-Specific PARA Folder Names

| PARA | Google Drive | MediaFire | pCloud | Dropbox (personal) | Dropbox-biz | MEGA | iCloud | sjlcloud |
|---|---|---|---|---|---|---|---|---|
| Inbox | `@INBOX_gDrive` | `@INBOX_mediafire` | `@INBOX_pcloud` | `@INBOX_dropbox` | `@INBOX_dropbox-biz` | `@INBOX_mega` | `@INBOX_icloud` | `@INBOX` |
| Projects | `@PROJECTS_gDrive` | `@PROJECTS_mediafire` | `@PROJECTS_pcloud` | `@PROJECTS_dropbox` | `@PROJECTS_dropbox-biz` | `@PROJECTS_mega` | `@PROJECTS_icloud` | `@PROJECTS` |
| Areas | `@AREAS_gDrive` | `@AREAS_mediafire` | `@AREAS_pcloud` | `@AREAS_dropbox` | `@AREAS_dropbox-biz` | `@AREAS_mega` | `@AREAS_icloud` | `@AREAS` |
| Resources | `@RESOURCES_gDrive` | `@RESOURCES_mediafire` | `@RESOURCES_pcloud` | `@RESOURCES_dropbox` | `@RESOURCES_dropbox-biz` | `@RESOURCES_mega` | `@RESOURCES_icloud` | `@RESOURCES` |
| Archives | `@ARCHIVES_gDrive` | `@ARCHIVES_mediafire` | `@ARCHIVES_pcloud` | `@ARCHIVES_dropbox` | `@ARCHIVES_dropbox-biz` | `@ARCHIVES_mega` | `@ARCHIVES_icloud` | `@ARCHIVES` |

> Dropbox-biz = second/business Dropbox account.

### Project Subfolder Standard

```
Project-Name_PROJECTS_[cloud]/
  |
  +-- @INBOX_[project]/        incoming assets for this project
  +-- [files named per SJL convention]
```

### PARA Casing Rules
- `@INBOX`, `@PROJECTS`, `@AREAS`, `@RESOURCES`, `@ARCHIVES` — always uppercase
- Cloud suffix: `gDrive` (camelCase D), all others lowercase: `mediafire`, `pcloud`, `mega`, etc.
- Project names: Title-Case with hyphens: `Revelation-911`, `Built-For-This`

---

## PART 6 — GOOGLE DRIVE AUDIT & CLEANUP QUEUE

Account: `sjlove@shannonjeffreylove.com`

### Root PARA Buckets — Rename to Standard Casing

| Current | Rename to | Status |
|---|---|---|
| `@PROJECTS_gdrive` | `@PROJECTS_gDrive` | Pending |
| `@AREAS_gdrive` | `@AREAS_gDrive` | Pending |
| `@RESOURCES_gdrive` | `@RESOURCES_gDrive` | Pending |
| `@ARCHIVES_gdrive` | `@ARCHIVES_gDrive` | Pending |
| `@INBOX_gDrive` | `@INBOX_gDrive` | Correct |

### Stray Root Folders — Move to PARA

| Folder | Move to | Hook After Move |
|---|---|---|
| `SnAPPTrap` | `@PROJECTS_gDrive` | Yes — new hub entry |
| `Google AI Studio` | `@RESOURCES_gDrive` | Yes |
| `Collab Notebooks` | `@RESOURCES_gDrive` | Yes |
| `Downloads` | `@INBOX_gDrive` | Yes |
| `Saved from Chrome` (2026-06-07) | Merge → `@INBOX_gDrive` | Yes |
| `Saved from Chrome` (2025-12-03) | Merge → `@INBOX_gDrive` | Yes — deduplicate first |
| `Spent 2025` | `@ARCHIVES_gDrive` | Yes |
| `meta-2026-Jan-05-04-14-56` | Investigate → `@INBOX_gDrive` | Yes |

### Stray Root Files — Move & Deduplicate

| File | Issue | Action |
|---|---|---|
| `NappyBoy Thank You` (Google Doc) | Loose at root | Move → `@PROJECTS_gDrive > NappyBoy-Thank-You_PROJECTS_gDrive` |
| `NappyBoy Thank You.docx` | Duplicate .docx export | Trash — Google Doc is canonical |
| `Revelation 9-1-1 Outline...` (Google Doc) | Loose at root | Move → `@PROJECTS_gDrive > Revelation-911_PROJECTS_gDrive` |
| `Revelation 9-1-1 Outline...06102026.docx` | Duplicate export | Trash — Google Doc is canonical |
| `Austin apartment furniture` (Google Doc) | Loose at root | Move → `@PROJECTS_gDrive > Austin-Apartment_PROJECTS_gDrive` |

### @PROJECTS_gDrive — Folder Rename Queue

| Current Name | Rename to |
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
| `Filetagger ` | `Filetagger_PROJECTS_gDrive` |
| `53 anniversary ` | `53rd-Anniversary_PROJECTS_gDrive` |
| `Crockett Science B roll clips` | `Crockett-Science-Broll_PROJECTS_gDrive` |
| `DFlat DEvans Music` | `DFlat-DEvans-Music_PROJECTS_gDrive` |
| `Our Time` / `Our Time Adapation Project_Projects_gDrive` | `Our-Time_PROJECTS_gDrive` — **PARENT** feature film project folder (merge both into one) |
| `Our Time (Promo)` | Move INTO `Our-Time_PROJECTS_gDrive/Our-Time-Promo/` subfolder |
| *(create new)* | `Our-Time_PROJECTS_gDrive/Our-Time-Pitch-Deck/` — subfolder for PDF pitch deck |
| `TagBack Project Folder` | `TagBack_PROJECTS_gDrive` |
| `TV One Lawsuit_PROJECTS_gDRIVE` | `TV-One-Lawsuit_PROJECTS_gDrive` |
| `Fathers Master Plan_Projects_gDrive` | `Fathers-Master-Plan_PROJECTS_gDrive` |
| `Lord Of The Manners` | `Lord-Of-The-Manners_PROJECTS_gDrive` |
| `Enoch Series` | `Enoch-Series_PROJECTS_gDrive` |
| `Nicodemus Movie` | `Nicodemus-Movie_PROJECTS_gDrive` |
| `Covid vaccination spots ` | `Covid-Vaccination-Spots_PROJECTS_gDrive` |
| `Content Clutter Stock Media ` | `Content-Clutter-Stock-Media_PROJECTS_gDrive` |
| `LoveYou Concert series Promotion Rebranding` | `LoveYou-Concert-Promo-Rebrand_PROJECTS_gDrive` |
| `Mother dear nurse December 2025` | `Mother-Nurse-Dec-2025_PROJECTS_gDrive` |
| `SPENT NBN (Net Worth)` | `SPENT-NBN-Net-Worth_PROJECTS_gDrive` |
| `NET WORTH` | `Net-Worth_PROJECTS_gDrive` |
| `SJL .com` | `SJL-dotCom_PROJECTS_gDrive` |
| `WOMEN'S PROJECT` | `Womens-Project_PROJECTS_gDrive` |
| `UNDERGROUND IN MIDTOWN OPEN MIC PROJECT` | `Underground-Midtown-Open-Mic_PROJECTS_gDrive` |
| `HappyBirthdayAdrienneLove_Projects_gDrive` | `Happy-Birthday-Adrienne-Love_PROJECTS_gDrive` |
| `Butter P's (candied nuts project)` | `Butter-Ps-Candied-Nuts_PROJECTS_gDrive` |
| `For Ariel (ShannonJLove)` | `For-Ariel_PROJECTS_gDrive` |
| `Amadaeus & Ashley` | `Amadaeus-And-Ashley_PROJECTS_gDrive` |
| `Mom & Dad 50th Anniversary Pictures` | `Mom-Dad-50th-Anniversary_PROJECTS_gDrive` |
| `Cinema 4D Projects 2025` | `Cinema-4D-2025_PROJECTS_gDrive` |

### @PROJECTS_gDrive — Archive Queue (move to @ARCHIVES_gDrive)

Completed / inactive since 2014–2023:
`Love Family Portrait` · `90s Girl Group Project` · `Girls Cruise Files` ·
`SJL Recordings` · `SJL Songwriting Projects 2020` · `SWV_IF_ONLY_YOU_KNEW` ·
`AshaRuRu & SJL 2021 Writing Sessions` · `WOMEN'S PROJECT` · `Making Love Deck 2022` ·
`UNDERGROUND IN MIDTOWN OPEN MIC PROJECT` · `Amadaeus & Ashley` · `For Ariel (ShannonJLove)` ·
`HappyBirthdayAdrienneLove_Projects_gDrive` · `CCC Reception 06242023` ·
`Mom & Dad 50th Anniversary Pictures` · `NET WORTH`

### @ARCHIVES_gDrive — Fix Mixed Suffix

`SJL_Produced_Content_RESOURCES_iDrive` → `SJL-Produced-Content_ARCHIVES_gDrive`

### Open Questions (need answers before execution)

- [x] `Our Time` — **RESOLVED:** single feature film project; `Our-Time_PROJECTS_gDrive` is parent; Promo and Pitch Deck are subfolders
- [x] Dropbox account 2 — **RESOLVED:** label is `Dropbox-biz`
- [ ] `TGMGPYSM` — what is the full project name?

---

## PART 7 — CLOUD MIGRATION PLAN

### Phase 1 — Google Drive (current)
- [ ] Rename PARA root buckets to standardized casing
- [ ] Move stray root folders into PARA buckets
- [ ] Trash duplicate .docx exports
- [ ] Move stray root files to correct project folders
- [ ] Merge two `Saved from Chrome` folders
- [ ] Rename all project folders to standard convention (40+ renames)
- [ ] Archive 16 completed projects → @ARCHIVES_gDrive
- [ ] Create HookVault entry for all 5 gDrive PARA folders → Raindrop FOLDERS
- [ ] Create Project Hub entries for all active projects → Raindrop @PROJECTS

### Phase 2 — MediaFire
- [ ] Audit existing structure
- [ ] Create 5 PARA folders
- [ ] Apply SJL rename to all files
- [ ] Create Raindrop entries for all 5 folders + all files

### Phase 3 — pCloud
- [ ] Audit existing structure
- [ ] Create 5 PARA folders
- [ ] Apply SJL rename + hook all files

### Phase 4 — Dropbox (both accounts)
- [ ] Audit each account separately
- [ ] Create PARA in each
- [ ] Cross-account deduplication check

### Phase 5 — MEGA
- [ ] Audit + create PARA + hook all files

### Phase 6 — iCloud Drive
- [ ] Audit (manual or via Apple Shortcuts)
- [ ] Create PARA + hook all files
- [ ] iCloud Shortcuts can trigger HookVault webhooks on file events

### Phase 7 — S3 Migration
- All clouds cleaned, named, PARA-structured, and hooked before migration begins
- S3 key prefix mirrors PARA: `projects/` · `areas/` · `resources/` · `archives/`
- SJL canonical names carry over unchanged — no rename at migration
- UUID24 in filenames ensures Raindrop links update (not replace) on migration

---

## PART 8 — TOOLS REFERENCE

| Tool | Location | Purpose |
|---|---|---|
| `filewarden.py` | `SJL-Personal-Server_PROJECTS_gDrive/Auto/` | Watchdog: auto-rename + auto-hook |
| `hookvault.py` | Same | Webhook manager: fires HookVault payloads to Raindrop + SJL Hub |
| `tagbot.py` | `shannonjlove.cloud:8001` | Media recognition + auto-tagging service (see Part 11) |
| `diffforge.py` | Same | Diff/comparison utility |
| `DEPLOY.sh` | Same | Deployment script |
| `config.yaml` | Same | FileWarden rules: inbox routing, categories, rename patterns |
| Raindrop.io | Cloud | Universal link browser; Hookmark equivalent for cloud files |
| SJL Hub | `hub.shannonjlove.cloud` | Custom cluster management UI (see Part 10) |
| n8n | shannonjlove.cloud | Automation platform; LLM nodes point to Ollama (not Claude API) |
| Ollama | `shannonjlove.cloud:11434` | Self-hosted LLM server; replaces Claude/OpenAI API in all automations |
| PhotoPrism | `photos.shannonjlove.cloud` | Primary DAM; full EXIF/XMP/IPTC/GPS; YAML sidecars; pre-seeds TagBot (Docker) |
| Immich | Alt DAM | Secondary option — better mobile upload app; less metadata depth than PhotoPrism |
| ExifTool | `shannonjlove.cloud` (CLI) | Read/write all metadata fields; embed SJL XMP fields; create XMP sidecars |
| Nominatim | `shannonjlove.cloud:8088` | Self-hosted OSM street-level reverse geocoding (Docker, opt-in) |
| NeoFinder | RULED OUT | macOS-only, no Linux, no MCP, no WebTop path — replaced by Immich + ExifTool |
| Paper Parrot | TBD | Document export destination |

---

## PART 9 — PROJECT IDENTITY

| Field | Value |
|---|---|
| Owner | Shannon J. Love |
| Email | sjlove@shannonjeffreylove.com |
| Domain | shannonjlove.cloud / shannonjeffreylove.com |
| Role | Writer · Producer · Director |
| Repo | shannonjlove/shannonjlove-github.io |
| Branch convention | `claude/[task-slug]-[id]` |
| Master server | shannonjlove.cloud (personal server; FileWarden runs here) |
| Canonical cloud | Google Drive (sjlove@shannonjeffreylove.com) |
| Link hub | Raindrop.io |
| Cluster UI | SJL Hub at `hub.shannonjlove.cloud` (see Part 10) |
| Photo/Video DAM | PhotoPrism at `photos.shannonjlove.cloud` (see Part 11) |
| Automation | n8n at shannonjlove.cloud + HookVault webhooks |

---

## PART 10 — CLUSTER MANAGEMENT UI: SJL HUB

### What This Solves

Raindrop.io is the real-time webhook sink, universal link resolver, and search layer.
But it is a bookmark manager — it does not visualize file clusters, render bidirectional
relationship graphs, manage the processing queue, or serve as a human-readable project
dashboard. SJL Hub fills that gap as the visual layer on top of HookVault.

**Domain:** `hub.shannonjlove.cloud`
**Also serves as:** Universal Link resolver — `hub.shannonjlove.cloud/open?id=[UUID24]`
redirects to the file's native cloud URL via UUID lookup in the HookVault database.

---

### OPTION A — Wiki.js (Self-Hosted)

Wiki.js is a self-hosted, open-source wiki with a GraphQL API. Docker-deployable on
`shannonjlove.cloud`. HookVault fires to its API alongside Raindrop as a second sink.

**Strengths:**
- Hours to deploy (Docker + nginx config)
- Built-in full-text search across all pages
- Plugin ecosystem: diagrams, embeds, analytics
- Git-backed storage — wiki pages version-controlled
- $0 ongoing cost (server already exists)

**Limitations:**
- Generic wiki UX — not designed for the HookVault data model
- No cluster graph visualization
- Does not serve as Universal Link resolver
- Bidirectional linking via `[[page-link]]` syntax only — no visual relationship map
- Every file page must be manually structured or scripted

**Wiki.js Project Hub Page Structure:**
```markdown
# Our-Time_PROJECTS_gDrive
**Status:** Active | **Cloud:** gDrive | **Files:** 12 | **Hub Created:** 2026-06-29

## Files in This Project
- [[2026-06-29_creative-film_our-time-screenplay_UUID24.pdf]] — gDrive
- [[2026-06-15_media-video_our-time-promo-cut_UUID24.mov]] — pCloud
- [[2026-05-01_document-pdf_our-time-pitch-deck_UUID24.pdf]] — gDrive

## Related Projects
- [[Built-For-This_PROJECTS_gDrive]]

## Subfolders
- [[Our-Time-Promo/]] · [[Our-Time-Pitch-Deck/]]
```

**Wiki.js File Page Structure:**
```markdown
# 2026-06-29_creative-film_our-time-screenplay_UUID24.pdf
**Cloud:** gDrive | **PARA:** Projects | **Project:** [[Our-Time_PROJECTS_gDrive]]
**UUID24:** `a1b2c3d4e5f6a1b2c3d4e5f6`

| Link Type | URL |
|---|---|
| Native | https://drive.google.com/file/d/[id]/view |
| Universal | https://hub.shannonjlove.cloud/open?id=a1b2c3d4e5f6a1b2c3d4e5f6 |
| Deep | https://drive.google.com/file/d/[id]/view#page=1 |
| Markdown | `[filename](clean-url)` |
| Search | `hook://search?q=a1b2c3d4e5f6a1b2c3d4e5f6` |

**Siblings:** [[file2]] · [[file3]]
```

**HookVault → Wiki.js GraphQL Mutations:**
```graphql
# Create a new page
mutation CreatePage($title: String!, $content: String!, $path: String!) {
  pages {
    create(
      title: $title
      content: $content
      path: $path
      editor: "markdown"
      locale: "en"
      isPublished: true
    ) {
      responseResult { succeeded message }
      page { id path }
    }
  }
}

# Update existing page (idempotent — update by UUID24 slug, never create duplicate)
mutation UpdatePage($id: Int!, $content: String!) {
  pages {
    update(id: $id, content: $content) {
      responseResult { succeeded message }
    }
  }
}
```

HookVault fires to Wiki.js immediately after firing to Raindrop. If a page already
exists for this UUID24, it updates in place. UUID24 is the page slug — permanent identity.

---

### OPTION B — SJL Hub (Lovable → Self-Hosted) ✦ RECOMMENDED

A purpose-built React app generated in Lovable, exported to GitHub, and self-hosted
on `shannonjlove.cloud`. Designed from the ground up around the HookVault data model.

**IP Ownership:** Lovable generates standard React + TypeScript + Tailwind CSS + shadcn/ui.
Export to GitHub the moment the core is stable. Deploy anywhere. Cancel the Lovable
subscription — the code is yours permanently. No ongoing dependency on Lovable's
existence, pricing, or terms.

**Tech Stack:**
```
Frontend:    React 18 + TypeScript + Tailwind CSS + shadcn/ui
Routing:     React Router v6
Data layer:  Raindrop.io REST API + HookVault internal REST API
Graph:       React Flow (cluster visualization)
Hosting:     shannonjlove.cloud — nginx reverse proxy + pm2 process manager
Repo:        shannonjlove/sjl-hub
Domain:      hub.shannonjlove.cloud
```

**Screens — Sprint 1 (core, build in Lovable):**

```
1. DASHBOARD
   - PARA overview: 5 buckets × 8 clouds = 40 folder tiles with file counts
   - Recent activity feed: last 20 HookVault events (rename, route, hook)
   - Quick stats: total files, active projects, unprocessed inbox items
   - Cloud health indicators: which clouds are connected + synced

2. PROJECT HUB VIEW
   - Card grid of all active project hubs (pinned = top row)
   - Each card: project name, cloud, file count, last activity, cluster preview
   - Drill down → Project Detail page

3. PROJECT DETAIL
   - All files in the project listed with their 6 link types
   - Subfolders shown (e.g. Our-Time-Promo/, Our-Time-Pitch-Deck/)
   - Related projects linked
   - Hub Raindrop entry embedded

4. FILE DETAIL
   - All 6 links displayed and copyable (Native, Clean, Universal, Markdown, Deep, Search)
   - Bidirectional connections: Project Hub + sibling files
   - Cloud badge, PARA bucket, category/subcategory, UUID24
   - Processing status: when renamed, when hooked, when routed

5. UNIVERSAL LINK RESOLVER
   GET /open?id=[UUID24]
   → look up UUID24 in HookVault DB
   → 302 redirect to native cloud URL
   → if URL dead: show fallback with search_link + last-known location
```

**Screens — Sprint 2 (power features, build post-Lovable in code):**

```
6. CLUSTER GRAPH
   - React Flow canvas: project hubs as large nodes, files as smaller nodes
   - Edges = bidirectional relationships (hub↔file, file↔sibling, page↔PDF)
   - Color coded by cloud; filter by PARA bucket, cloud, project
   - Click any node → File Detail or Project Detail

7. INBOX QUEUE
   - All unprocessed files across all @INBOX folders
   - Trigger rename/categorize/route directly from UI
   - Batch actions: rename all, route all to PARA

8. PARA NAVIGATOR
   - Single tree view of all 8 clouds × 5 PARA buckets
   - Expand any folder to see its files
   - Cross-cloud search by UUID24, filename, category, or project

9. CHANGES LOG
   - Full audit trail: every rename, move, version, migration
   - Filter by file, project, cloud, date range
   - Link to before/after states

10. SETTINGS
    - Cloud API connections (gDrive, pCloud, MediaFire, Dropbox, MEGA, iCloud)
    - Raindrop.io API key
    - HookVault webhook endpoint
    - Wiki.js GraphQL endpoint (if using as secondary sink)
```

**HookVault → SJL Hub API Endpoint (alongside Raindrop):**
```
POST https://hub.shannonjlove.cloud/api/hook
Authorization: Bearer [HOOKVAULT_SECRET]
Content-Type: application/json

Body: same HookVault webhook payload (see Part 3)
```

Hub stores all payloads in its own SQLite/PostgreSQL database.
UUID24 is the primary key. Upsert on every incoming payload — idempotent.

**Deployment on shannonjlove.cloud:**
```bash
# Build
npm run build

# Serve via pm2
pm2 start npm --name sjl-hub -- start

# nginx reverse proxy
server {
    listen 443 ssl;
    server_name hub.shannonjlove.cloud;
    location / { proxy_pass http://localhost:3000; }
}
```

---

### SIDE-BY-SIDE COMPARISON

| Factor | Wiki.js | SJL Hub (Lovable) |
|---|---|---|
| Build time | Hours (Docker + config) | Days (Lovable sprint) |
| UX fit | Generic wiki | Purpose-built for SJL system |
| Cluster graph | Text [[links]] only | React Flow visual graph (Sprint 2) |
| Universal Link resolver (`/open?id=`) | No | Yes — built-in |
| Bidirectional linking | `[[wiki-links]]` | Full relationship model with graph |
| Inbox queue management | No | Yes (Sprint 2) |
| Full-text search | Built-in | Build or integrate Algolia/Fuse.js |
| IP ownership | Open source (MIT) | 100% yours after GitHub export |
| Lovable subscription needed | Never | Build phase only — cancel after |
| Ongoing cost | $0 | $0 (hosting on existing server) |
| Maintenance | Docker + plugin updates | Code you own; standard React app |
| HookVault integration | GraphQL mutations | REST POST to `/api/hook` |
| Git-backed content | Yes (built-in) | Via GitHub repo for the app itself |
| Secondary wiki/docs layer | IS the wiki | Can embed Wiki.js inside as `/docs` |

---

### DECISION AND RATIONALE

**Build SJL Hub in Lovable. Self-host on `hub.shannonjlove.cloud`.**

Wiki.js is a square peg. Its wiki-page structure fights the HookVault data model at every
turn — project hubs become wiki pages with awkward markup instead of first-class data
objects, and cluster visualization is impossible without heavy custom plugins.

Lovable generates the core app in days. Export to `shannonjlove/sjl-hub` on GitHub.
Deploy to `hub.shannonjlove.cloud`. Cancel Lovable. From that point it's a standard
React codebase — maintained, extended, and deployed the same way as any other project
on the server. The Lovable subscription was the scaffold, not the foundation.

Wiki.js remains useful as a lightweight secondary layer for long-form documentation
pages (this CLAUDE.md exported, tool guides, workflow notes) — mounted at
`hub.shannonjlove.cloud/docs` or `docs.shannonjlove.cloud` as a companion, not a replacement.

---

### BUILD PHASE PLAN

**Sprint 1 — Lovable (target: 3–5 days)**
- [ ] Write Lovable prompt from this spec (Screens 1–5 + `/open` resolver)
- [ ] Generate app in Lovable
- [ ] Export to GitHub repo `shannonjlove/sjl-hub`
- [ ] Connect Raindrop.io REST API (read collections + bookmarks)
- [ ] Connect HookVault internal API
- [ ] Deploy to `hub.shannonjlove.cloud` via nginx + pm2
- [ ] Wire HookVault to POST to `/api/hook` on every file event
- [ ] Test Universal Link resolution with 5 real UUID24 files
- [ ] Cancel Lovable subscription (code is exported and owned)

**Sprint 2 — Direct code (post-Lovable)**
- [ ] Add React Flow cluster graph (Screen 6)
- [ ] Add Inbox Queue (Screen 7)
- [ ] Add PARA Navigator cross-cloud tree (Screen 8)
- [ ] Add Changes Log (Screen 9)
- [ ] (Optional) Mount Wiki.js at `/docs` for long-form documentation

**Lovable Prompt Seed (use when starting the build):**
```
Build a file cluster management dashboard called "SJL Hub" for a personal cloud
file organization system. Tech stack: React 18, TypeScript, Tailwind CSS, shadcn/ui,
React Router v6.

The system manages files across 8 cloud services (Google Drive, MediaFire, pCloud,
Dropbox personal, Dropbox-biz, MEGA, iCloud, and a personal server) organized into
a PARA structure (Projects, Areas, Resources, Archives, Inbox) with 5 folders per cloud.

Every file has a UUID24 permanent identity and 6 link types: native, clean, universal,
markdown, deep, and search. Files belong to project clusters with bidirectional links
to a project hub and to sibling files.

Build these screens:
1. Dashboard — PARA bucket overview (5 × 8 = 40 folder tiles), recent activity feed,
   cloud health indicators
2. Project Hub View — pinned active project cards with file counts, drill to detail
3. Project Detail — file list with all 6 link types, subfolders, related projects
4. File Detail — all 6 links copyable, bidirectional connections, UUID24 display,
   cloud + PARA + category metadata
5. Universal Link Resolver — GET /open?id=[UUID24] → 302 redirect to native cloud URL,
   fallback UI if URL dead

Data comes from two REST APIs: Raindrop.io (bookmarks/collections) and HookVault
(internal file database, POST /api/hook for incoming file events). Use mock data
for the initial build.

Dark mode by default. Clean, minimal design. Mobile-responsive.
```

---

## PART 11 — MEDIA RECOGNITION & AUTO-TAGGING: TAGBOT

### What This Solves

FileWarden renames files by extension and routes them by type, but it has no awareness
of what is *inside* a file. TagBot is a self-hosted Python service that analyzes file
content and returns: a suggested description (for the SJL filename), category-confirmed
tags, a human-readable caption, and confidence scores. FileWarden calls TagBot before
completing the rename step so the UUID24 filename is semantically meaningful, not generic.

**Everything runs on `shannonjlove.cloud`. No cloud APIs. No per-file cost. No data leaves the server.**

**Service name:** `tagbot.py` (FastAPI service, internal port 8001)
**Called by:** FileWarden at Step 2.5 — between IDENTIFY and APPLY SJL RENAME
**Output feeds:** SJL filename description, Raindrop tags, SJL Hub metadata

---

### WHAT TAGBOT NEEDS TO HANDLE BY FILE TYPE

| File Type | Task | Key Challenges |
|---|---|---|
| Photo (JPG/PNG/RAW) | Scene + object tagging, caption, optional face ID | RAW decode, lighting variation, personal photo context |
| Video (MP4/MOV/MKV) | Scene tags from keyframes + speech transcription | Large files, temporal sampling, audio extraction |
| Audio (MP3/WAV/M4A) | Speech transcription, music vs speech detection | Background noise, music files have no useful transcript |
| PDF (text) | Text extraction, keyword summary, topic tags | Multi-column layouts, scanned vs digital |
| PDF (scanned) | OCR → text → keywords | Image quality, handwriting |
| DOCX/TXT/MD | Text extraction, keyword summary | Simple; already text |
| RAW camera files | Decode + treat as photo | Proprietary codecs (CR2, ARW, DNG) |

---

### OPTION MATRIX — SELF-HOSTED MODELS

#### IMAGES & PHOTOS

**Option A — CLIP (Recommended for tagging)**
```
Model:    openai/clip-vit-base-patch32 (fast) or clip-vit-large-patch14 (accurate)
Task:     Zero-shot image classification against a custom tag vocabulary
How:      Feed image + list of candidate tags; CLIP scores each tag by similarity
Speed:    ~200ms per image on CPU (base model)
GPU:      Not required
Install:  pip install transformers torch Pillow
Strength: Tag anything without training data — just describe it in words
Weakness: Doesn't generate captions; needs a predefined tag list to score against
```

**Option B — BLIP-2 / BLIP (Recommended for captions)**
```
Model:    Salesforce/blip-image-captioning-base (fast) or blip2-opt-2.7b (richer)
Task:     Generate a natural-language description of the image
How:      Image in → caption out ("a woman speaking at a podium outdoors")
Speed:    2–4 seconds per image on CPU (base); 10–30s for blip2 on CPU
GPU:      Optional for base; recommended for blip2
Install:  pip install transformers torch Pillow
Strength: Auto-generates the SJL filename description segment
Weakness: blip2 is slow on CPU; base model captions are simple
```

**Option C — YOLOv8 (Object detection layer)**
```
Model:    YOLOv8n (nano — fastest) to YOLOv8x (most accurate)
Task:     Detect and label objects + people in frame with bounding boxes
How:      Returns class labels + confidence scores for every detected object
Speed:    50–150ms per image on CPU (nano model)
GPU:      Not required for nano/small
Install:  pip install ultralytics
Strength: Fast, reliable object list; complements CLIP scene tags
Weakness: 80 COCO classes only — no custom categories without fine-tuning
```

**Option D — DeepFace (Face recognition — optional)**
```
Model:    VGG-Face, Facenet, ArcFace (selectable backend)
Task:     Detect faces, identify recurring people, estimate age/gender/emotion
How:      Builds a face database from known photos; matches new photos against it
Speed:    1–3 seconds per image on CPU
GPU:      Not required
Install:  pip install deepface
Strength: Tags family members by name across entire photo library
Weakness: Requires a labeled "known faces" seed set; privacy consideration
Use when: Processing personal/family photos only
```

**Option E — Ollama + LLaVA (Vision-language, richest output)**
```
Model:    LLaVA 7B (via Ollama) — llava:7b
Task:     Full visual question-answering; describe anything in natural language
How:      "Describe this image for a file tagging system. List: scene, objects,
           people, mood, setting, key colors." → rich structured response
Speed:    30–120 seconds per image on CPU (very slow without GPU)
GPU:      Strongly recommended; 8GB VRAM minimum for 7B
Install:  Install Ollama → ollama pull llava:7b
Strength: Most intelligent output; understands context, mood, composition
Weakness: Prohibitively slow on CPU for large photo libraries
```

**Recommended image stack (CPU-only server):**
```
CLIP (base)  → scene + category tags       [fast, always-on]
BLIP (base)  → caption → filename desc     [moderate speed]
YOLOv8n     → object labels               [very fast]
DeepFace     → face tags (opt-in per run)  [moderate speed]
```
Add Ollama/LLaVA only if you add a GPU to the server later.

---

#### VIDEO

**Option A — ffmpeg + image model pipeline (Recommended)**
```
Tool:   ffmpeg (already standard on Linux servers)
Task:   Extract keyframes at regular intervals → run image models on each frame
How:    ffmpeg -i video.mp4 -vf fps=1/10 frame_%04d.jpg
        (1 frame per 10 seconds → CLIP + BLIP + YOLO on each)
        Aggregate tags across all frames; take most frequent as file tags
Speed:  Extraction fast; image processing = N_frames × per-frame time
Strength: No new models needed; reuses the image stack
Weakness: Misses motion/action context; only sees still frames
```

**Option B — Whisper (Speech transcription from video audio)**
```
Model:    openai/whisper (self-hosted via faster-whisper or whisper.cpp)
Task:     Extract audio track → transcribe speech → keywords → tags
Models:   tiny (fastest), base, small (recommended), medium, large
Speed:    base model: ~5–10x realtime on CPU (60s video → 6–12s to transcribe)
          small model: ~3–5x realtime on CPU
          medium model: ~1–2x realtime on CPU
GPU:      Not required for base/small; medium works well on CPU
Install:  pip install faster-whisper  (faster than original openai-whisper on CPU)
Strength: Transcribes dialogue, narration, interviews — most content-rich signal
Weakness: Useless for music videos or no-dialogue footage
Use:      Always run on video; only use output if speech detected (VAD filter)
```

**Option C — Scene detection (PySceneDetect)**
```
Tool:   PySceneDetect
Task:   Detect scene cuts → extract one representative frame per scene
How:    More intelligent than uniform fps sampling; captures visual variety
Speed:  Fast (pure video analysis, no ML)
Install: pip install scenedetect[opencv]
Strength: Better keyframe selection than uniform interval
Use:    Replace ffmpeg fps= extraction with scene-aware extraction
```

**Recommended video pipeline:**
```
1. PySceneDetect   → find scene boundaries
2. ffmpeg           → extract 1 frame per scene (max 20 frames per file)
3. CLIP + YOLOv8n  → tag each keyframe
4. faster-whisper   → transcribe audio track (small model)
5. Aggregate        → union of frame tags + top transcript keywords
```

---

#### AUDIO

**Option A — faster-whisper (Recommended)**
```
Same as video audio pipeline above.
For music files: run Whisper; if < 10% speech detected (VAD), skip transcript,
tag as music-audio and extract metadata via mutagen (artist, album, BPM, genre).
```

**Option B — mutagen (Music metadata)**
```
Library: mutagen
Task:    Read ID3/MP4/FLAC tags: artist, album, year, genre, BPM, track title
Speed:   Instant (reads file headers, no ML)
Install: pip install mutagen
Use:     Always run on audio files before Whisper to capture embedded metadata
```

---

#### DOCUMENTS & PDFs

**Option A — Marker (Recommended for digital PDFs)**
```
Tool:   VikParuchuri/marker
Task:   Convert PDF → clean Markdown (preserves structure, tables, equations)
Speed:  ~5–15 seconds per page on CPU
Install: pip install marker-pdf
Strength: Best-in-class PDF → text for complex layouts (better than pdfminer)
Weakness: Slower than simple text extraction for text-only PDFs
Use:    Run on all PDFs; fall back to pdfminer for speed if needed
```

**Option B — Tesseract OCR (For scanned PDFs)**
```
Tool:   Tesseract 5 + pytesseract
Task:   OCR on scanned/image-based PDFs
Speed:  1–5 seconds per page on CPU
Install: apt install tesseract-ocr && pip install pytesseract pdf2image
Strength: Mature, accurate, 100+ languages
Weakness: Struggles with handwriting; needs image preprocessing for dirty scans
Use:    Run only when Marker/pdfminer returns < 100 characters of text (likely scanned)
```

**Option C — Unstructured.io (self-hosted Docker)**
```
Tool:   unstructured-io/unstructured (Docker container)
Task:   Universal document parser: PDF, DOCX, XLSX, HTML, images
Speed:  Variable; Docker overhead
Install: docker pull quay.io/unstructured-io/unstructured
Strength: One API handles all document types; partition() returns structured elements
Weakness: Docker dependency; overkill if only handling PDF + DOCX
Use:    Consider if document variety grows beyond PDF/DOCX
```

**Keyword/tag extraction from text (all document types):**
```
Tool:   KeyBERT (semantic keyword extraction)
Model:  all-MiniLM-L6-v2 (small, fast, CPU-friendly)
Task:   Extract the top 5–10 most relevant keywords from extracted text
Speed:  < 1 second per document on CPU
Install: pip install keybert sentence-transformers
Output: ["screenplay", "feature-film", "our-time", "dialogue", "second-act"]
        → becomes SJL filename description + Raindrop tags
```

---

### RECOMMENDED FULL STACK (CPU-ONLY, SELF-HOSTED)

```
FILE TYPE     TOOL CHAIN                                    OUTPUT
──────────    ─────────────────────────────────────────    ──────────────────────────
Photo         CLIP (tags) + BLIP-base (caption)            description, tags[]
              + YOLOv8n (objects)
              + DeepFace (opt-in, known faces only)        + person tags

Video         PySceneDetect (keyframes)                    tags[], transcript,
              + CLIP + YOLOv8n (per frame)                 description
              + faster-whisper small (speech)

Audio         mutagen (metadata) + faster-whisper small    tags[], transcript
              + VAD filter (skip whisper if music)

PDF (digital) Marker (PDF→text) + KeyBERT (keywords)      tags[], description
PDF (scanned) Tesseract OCR + KeyBERT                      tags[], description

DOCX/TXT/MD   python-docx / plain read + KeyBERT           tags[], description
RAW photo     rawpy (decode) → numpy array → CLIP+BLIP     same as photo
```

**Python packages total:**
```bash
pip install transformers torch Pillow              # CLIP, BLIP
pip install ultralytics                            # YOLOv8
pip install deepface                               # Face recognition (optional)
pip install faster-whisper                         # Audio/video transcription
pip install scenedetect[opencv]                    # Video scene detection
pip install marker-pdf                             # PDF parsing
pip install pytesseract pdf2image                  # Scanned PDF OCR
pip install mutagen                                # Audio metadata
pip install keybert sentence-transformers          # Keyword extraction
pip install rawpy                                  # RAW camera file decode
pip install fastapi uvicorn                        # TagBot API server
```

---

### TAGBOT SERVICE ARCHITECTURE

```
tagbot.py  —  FastAPI service running on shannonjlove.cloud:8001
```

**API endpoint:**
```
POST http://localhost:8001/tag
Content-Type: application/json

{
  "file_path": "/data/inbox/IMG_4821.jpg",
  "file_type": "image",           # image | video | audio | pdf | document
  "hints": {                      # optional — from FileWarden's initial detection
    "project": "Our-Time",
    "cloud": "gdrive"
  }
}
```

**Response:**
```json
{
  "suggested_description": "outdoor-speaking-event-podium",
  "caption": "A woman speaking at a podium at an outdoor event",
  "tags": ["media", "image", "outdoor", "speaking", "event", "people"],
  "category": "media",
  "subcategory": "image",
  "category_confidence": 0.94,
  "objects_detected": ["person", "microphone", "podium", "crowd"],
  "faces_detected": 1,
  "face_tags": [],
  "transcript": null,
  "keywords": [],
  "processing_time_ms": 840,
  "models_used": ["clip-vit-base-patch32", "blip-base", "yolov8n"]
}
```

**FileWarden integration (updated Step 2.5):**
```python
# In filewarden.py, between identify() and _sjl_rename()
def _call_tagbot(file_path: str, file_type: str, hints: dict) -> dict:
    resp = requests.post(
        "http://localhost:8001/tag",
        json={"file_path": str(file_path), "file_type": file_type, "hints": hints},
        timeout=120  # large files may take time
    )
    return resp.json() if resp.ok else {}

# TagBot output overrides FileWarden's generic description if confidence > 0.7
tagbot_result = _call_tagbot(file_path, file_type, hints)
if tagbot_result.get("category_confidence", 0) > 0.7:
    description = tagbot_result["suggested_description"]
    extra_tags  = tagbot_result["tags"]
```

**TagBot internal routing:**
```python
ROUTERS = {
    "image":    [run_clip, run_blip, run_yolo],
    "video":    [run_scene_detect, run_clip_frames, run_whisper],
    "audio":    [run_mutagen, run_whisper],
    "pdf":      [run_marker, run_keybert],
    "document": [run_text_extract, run_keybert],
}

@app.post("/tag")
async def tag_file(req: TagRequest):
    handlers = ROUTERS.get(req.file_type, [run_keybert])
    results = {}
    for handler in handlers:
        results.update(await handler(req.file_path, req.hints))
    return merge_results(results)
```

**Caching (avoid reprocessing):**
```python
# Hash file content → cache result in SQLite
# If file_hash exists in cache → return cached result instantly
# Cache lives in /data/tagbot/cache.db
```

---

### RESOURCE REQUIREMENTS

| Model | RAM (CPU) | Disk | First-load time | Per-file time |
|---|---|---|---|---|
| CLIP base | ~600 MB | 350 MB | ~8s | ~200ms |
| BLIP base | ~900 MB | 450 MB | ~12s | 2–4s |
| YOLOv8n | ~100 MB | 6 MB | ~1s | ~80ms |
| DeepFace | ~500 MB | 250 MB | ~10s | 1–3s |
| faster-whisper small | ~500 MB | 244 MB | ~5s | 3–5× realtime |
| KeyBERT (MiniLM) | ~120 MB | 80 MB | ~3s | <1s |
| Marker | ~1.5 GB | 1.2 GB | ~20s | 5–15s/page |
| **Total (all loaded)** | **~4.2 GB RAM** | **~2.6 GB disk** | — | — |

**Minimum server spec to run TagBot:**
- RAM: 6 GB available (8 GB total recommended)
- Disk: 5 GB for models + working space
- CPU: Any modern multi-core (models are parallelizable)
- GPU: Not required; add later to cut per-file time by 10–20×

Models are loaded once at startup and kept in memory. Per-file processing is fast
after the initial model load. TagBot runs as a persistent pm2 process alongside n8n
and HookVault.

---

### PROCESSING MODES

**Mode 1 — Real-time (default)**
FileWarden calls TagBot synchronously before rename. Max wait: 120s (large video).
Suitable for files processed one at a time from @INBOX.

**Mode 2 — Batch (for initial library processing)**
```bash
python tagbot_batch.py --path /data/inbox --workers 2
```
Processes entire directory with 2 parallel workers. Writes results to
`/data/tagbot/batch_results.jsonl` for FileWarden to consume.

**Mode 3 — Async queue (for large video files)**
FileWarden submits to TagBot queue → gets a job_id → continues with generic rename →
TagBot completes analysis → fires webhook back to FileWarden → FileWarden updates
Raindrop entry with enriched tags (UUID24 stays stable; Raindrop entry updated in place).

---

### BUILD PLAN

- [ ] Set up Python 3.11 venv on shannonjlove.cloud for TagBot
- [ ] Install model packages (see pip list above)
- [ ] Pre-download models on first run (HuggingFace cache: `~/.cache/huggingface/`)
- [ ] Build `tagbot.py` FastAPI service with ROUTERS dict
- [ ] Implement CLIP + BLIP handlers (images first — most common file type)
- [ ] Implement YOLOv8n handler
- [ ] Implement faster-whisper handler (video + audio)
- [ ] Implement Marker + KeyBERT handler (PDFs)
- [ ] Implement SQLite result cache
- [ ] Add TagBot call to `filewarden.py` between identify() and _sjl_rename()
- [ ] Deploy as pm2 process: `pm2 start tagbot.py --name tagbot`
- [ ] Test with sample files from each type (photo, video, PDF, audio)
- [ ] Add DeepFace handler (opt-in, configured per run or per folder)
- [ ] Add rawpy handler for RAW camera files
- [ ] Install Ollama + pull mistral:7b and phi3:mini (see below)
- [ ] Wire NeoFinder catalog export into TagBot cache pre-seed (see below)

---

### OLLAMA — SELF-HOSTED LLM LAYER (ZERO API COST)

Ollama runs open-source LLMs locally on `shannonjlove.cloud`. It serves two roles:

**Role 1 — Replace Claude/OpenAI API in n8n automations**
Any n8n workflow using an Anthropic or OpenAI node swaps to the Ollama node:
```
n8n Ollama node → base URL: http://localhost:11434
model: mistral:7b  (or phi3:mini for faster/lighter tasks)
```
Zero token cost. No external API calls. Runs offline.

**Role 2 — TagBot synthesis layer (text reasoning over ML outputs)**
After CLIP/YOLO/BLIP return raw tags, Ollama synthesizes them into a clean
SJL filename description and ranked tag set:
```python
prompt = f"""
You are a file naming assistant. Given these raw analysis results for a file,
return a clean 3-6 word hyphenated description (for a filename) and up to 8 tags.

CLIP tags: {clip_tags}
Objects detected: {yolo_objects}
Image caption: {blip_caption}
Speech transcript excerpt: {whisper_excerpt}

Respond as JSON: {{"description": "...", "tags": [...]}}
"""
response = ollama.chat(model="mistral:7b", messages=[{"role": "user", "content": prompt}])
```
This is the "glue" layer — takes noisy ML outputs and makes them SJL-clean.

**Recommended Ollama models for shannonjlove.cloud (CPU-only):**

| Model | Size | RAM | Speed on CPU | Best for |
|---|---|---|---|---|
| `phi3:mini` | 2.3 GB | 3 GB | Fast (~10s) | Simple tag synthesis, short text |
| `mistral:7b` | 4.1 GB | 6 GB | Moderate (~30s) | Richer reasoning, n8n workflows |
| `llama3.1:8b` | 4.7 GB | 7 GB | Moderate (~35s) | Best quality general reasoning |
| `llava:7b` | 4.5 GB | 7 GB | Slow (~60-120s) | Vision-language (replaces BLIP+CLIP if GPU added) |
| `nomic-embed-text` | 274 MB | 500 MB | Fast (~2s) | Semantic embeddings for SJL Hub search |

**Install:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull phi3:mini
ollama pull mistral:7b
ollama pull nomic-embed-text   # for semantic search in SJL Hub
pm2 start "ollama serve" --name ollama
```

**When to call Ollama in TagBot pipeline:**
```
IF blip_caption is generic ("a photo of a person")
OR clip_tags conflict with yolo_objects
OR description segment would exceed 40 chars
THEN call Ollama to synthesize → cleaner description + prioritized tags

FOR all documents/PDFs:
  always call Ollama to summarize KeyBERT keywords into a description
```

**n8n Ollama node swap (replaces any Claude/Anthropic node):**
```
Node type:    AI → Ollama Chat Model
Base URL:     http://localhost:11434
Model:        mistral:7b
Temperature:  0.3 (low — deterministic outputs for file naming)
```

---

### NEOFINDER — STATUS: RULED OUT FOR THIS STACK

**NeoFinder is macOS/iOS only.** No Linux version exists. No MCP server exists.
No WebTop/Docker/cloud deployment path. Its Windows counterpart is abeMeda
(same database format) but that also doesn't run on Linux.

Since the entire SJL stack runs in the cloud on `shannonjlove.cloud` (WebTop
environment — everything in browser, nothing on a local desktop), NeoFinder
cannot participate in the pipeline.

**Replaced by:**
- **ExifTool** — server-side metadata engine (CLI + Python, Linux-native)
- **Immich** — self-hosted Docker DAM with web UI, GPS maps, EXIF reading,
  face recognition, and mobile upload (fills the catalog + browse role)

See EXIF/GPS section below for the full replacement architecture.

---

### EXIF / GPS METADATA — FULL SPEC

#### The Goal

Every photo and video file in the SJL system must carry the full set of embedded
metadata permanently — GPS coordinates reverse-geocoded to a human-readable address,
all camera/equipment specs, date/time, and SJL-specific fields written into XMP
namespace. This metadata must survive cloud uploads and be verifiable after storage.

The address and equipment data feed directly into the SJL filename description
and Raindrop tags. A file should never be named `IMG_4821.jpg` or even
`2026-06-29_14-30_media-image_photo_UUID24.jpg` when it could be named
`2026-06-29_14-30_media-image_austin-6th-street-iphone15pro_UUID24.jpg`.

---

#### EXIFTOOL — THE METADATA ENGINE

ExifTool (Phil Harvey) is the universal standard for reading and writing metadata
on any platform. It handles every format: EXIF, IPTC, XMP, GPS, MakerNotes
(camera-manufacturer-specific fields), ID3, MP4 atoms, QuickTime, RIFF.

```bash
# Install on shannonjlove.cloud (Debian/Ubuntu)
apt install libimage-exiftool-perl

# Python wrapper
pip install pyexiftool
```

**What ExifTool reads from a photo (full field set):**
```
CAMERA / EQUIPMENT
  Make                   Apple
  Model                  iPhone 15 Pro
  LensModel              iPhone 15 Pro back triple camera 6.765mm f/1.78
  FNumber                1.8
  ISO                    800
  ShutterSpeedValue      1/120 s
  FocalLength            6.765 mm
  FocalLengthIn35mmFormat 24 mm
  ExposureMode           Auto
  ExposureProgram        Program AE
  MeteringMode           Multi-segment
  WhiteBalance           Auto
  Flash                  Off, Did not fire
  ColorSpace             sRGB
  BitsPerSample          8
  SceneType              Directly photographed

GPS / LOCATION
  GPSLatitude            30.2672° N
  GPSLongitude           97.7431° W
  GPSAltitude            150 m Above Sea Level
  GPSSpeed               0 km/h
  GPSImgDirection        214.3° (compass bearing)
  → Reverse geocoded:    "6th Street, Austin, Travis County, Texas, US"

DATE / TIME
  DateTimeOriginal       2026:06:29 14:30:22
  OffsetTimeOriginal     -05:00
  SubSecTimeOriginal     847

IMAGE TECHNICAL
  ImageWidth             4032
  ImageHeight            3024
  Orientation            Horizontal (normal)
  XResolution            72 dpi
  YResolution            72 dpi
  ThumbnailLength        (embedded thumbnail size)

SJL CUSTOM (written by TagBot into XMP namespace)
  XMP:SJLuuid24          a1b2c3d4e5f6a1b2c3d4e5f6
  XMP:SJLparabucket      projects
  XMP:SJLcloud           gdrive
  XMP:SJLproject         Our-Time
  XMP:SJLprocessed       2026-06-29T19:45:00Z
```

**What ExifTool reads from a video (MP4/MOV):**
```
  CreateDate             2026:06:29 14:30:22
  GPSCoordinates         30.2672 N, 97.7431 W (if shot on iPhone)
  Make / Model           Apple / iPhone 15 Pro
  VideoFrameRate         29.97
  ImageWidth / Height    3840 / 2160 (4K)
  Duration               0:02:34
  VideoCodec             HEVC
  AudioChannels          2
  AudioSampleRate        44100 Hz
  CompressorName         HEVC
  HandlerDescription     Core Media Video
```

**Python read (TagBot integration):**
```python
import exiftool

def read_full_exif(file_path: str) -> dict:
    with exiftool.ExifToolHelper() as et:
        metadata = et.get_metadata(file_path)[0]
    return metadata

def exif_richness_score(meta: dict) -> float:
    """Score 0.0–1.0: how much usable metadata is already embedded."""
    fields = ["EXIF:GPSLatitude", "EXIF:Make", "EXIF:Model",
              "EXIF:DateTimeOriginal", "EXIF:FNumber", "EXIF:ISO"]
    present = sum(1 for f in fields if meta.get(f))
    return present / len(fields)
```

**Python write-back (embed SJL fields + write GPS if missing):**
```python
def write_sjl_metadata(file_path: str, uuid24: str, para: str,
                        cloud: str, project: str, address: str):
    with exiftool.ExifToolHelper() as et:
        et.set_tags(file_path, {
            "XMP:SJLuuid24":    uuid24,
            "XMP:SJLparabucket": para,
            "XMP:SJLcloud":     cloud,
            "XMP:SJLproject":   project,
            "XMP:SJLaddress":   address,
            "XMP:SJLprocessed": datetime.utcnow().isoformat() + "Z",
            "IPTC:Keywords":    f"sjl {cloud} {para} {project}",
        })
```

---

#### GPS REVERSE GEOCODING — SELF-HOSTED, ZERO API COST

Two self-hosted options. Both run on `shannonjlove.cloud`. No Google Maps API.
No Mapbox API. No per-lookup cost.

**Option A — reverse_geocoder (Python library, fully offline)**
```bash
pip install reverse_geocoder
```
```python
import reverse_geocoder as rg

def gps_to_address(lat: float, lon: float) -> dict:
    result = rg.search((lat, lon))[0]
    # Returns: {'name': 'Austin', 'admin1': 'Texas', 'admin2': 'Travis County',
    #           'cc': 'US'}
    return result

# SJL filename segment: "austin-travis-county-texas"
def gps_to_slug(lat, lon) -> str:
    r = gps_to_address(lat, lon)
    return f"{r['name']}-{r['admin2']}-{r['admin1']}".lower().replace(" ", "-")
```
- Uses bundled GeoNames dataset (~50 MB, included in package)
- Returns: city, county/admin2, state/admin1, country code
- Speed: < 5ms per lookup (pure Python, in-memory dataset)
- Limitation: city-level precision only — no street address

**Option B — Nominatim self-hosted (street-level precision)**
```bash
docker run -d \
  -e PBF_URL=https://download.geofabrik.de/north-america/us/texas-latest.osm.pbf \
  -e REPLICATION_URL=https://planet.openstreetmap.org/replication/hour/ \
  -p 8088:8080 \
  --name nominatim \
  mediagis/nominatim:4.4
```
```python
import requests

def gps_to_street_address(lat: float, lon: float) -> str:
    resp = requests.get(
        "http://localhost:8088/reverse",
        params={"lat": lat, "lon": lon, "format": "json", "zoom": 18},
        timeout=2
    )
    data = resp.json()
    addr = data.get("address", {})
    # Returns street, house_number, suburb, city, state, postcode, country
    road = addr.get("road", "")
    city = addr.get("city") or addr.get("town") or addr.get("village", "")
    state = addr.get("state", "")
    return f"{road}-{city}-{state}".lower().replace(" ", "-")
```
- Full street-level address: "6th-street-austin-texas"
- Requires ~50 GB disk for US data (or subset per state)
- Initial import: 2–6 hours; then fast (< 20ms per lookup)
- Updates: hourly replication from OSM (always current)
- Limitation: disk space; Docker overhead; US-only if you only import US data

**Recommended:** `reverse_geocoder` for city-level (always-on, zero overhead),
Nominatim for street-level on specific project-sensitive files (opt-in per run).

**GPS → SJL filename pipeline:**
```
EXIF GPS: 30.2672° N, 97.7431° W
  → reverse_geocoder → "Austin, Travis County, Texas, US"
  → slug: "austin-texas"
  → SJL description: "austin-texas-outdoor-speaking"
  → Full filename: 2026-06-29_14-30_media-image_austin-texas-outdoor-speaking_UUID24.jpg
  → Tags: ["media", "image", "austin", "texas", "outdoor", "speaking", "iphone-15-pro"]
```

---

#### METADATA PERSISTENCE — CLOUD STRIPPING BEHAVIOR

Most clouds preserve EXIF on file storage but strip it on sharing or compression.
The SJL strategy: write everything into the file AND into an XMP sidecar before
any cloud upload. Verify after upload.

| Service | Stores EXIF? | GPS preserved? | Strips on share? | Notes |
|---|---|---|---|---|
| Google Drive | YES | YES | NO (drive link) | Original file intact; thumbnail may strip |
| Dropbox | YES | YES | NO | Full fidelity storage |
| pCloud | YES | YES | NO | Full fidelity storage |
| MEGA | YES | YES | NO | Full fidelity storage |
| iCloud Drive | YES | YES | NO | Originals preserved |
| MediaFire | PARTIAL | PARTIAL | YES | Recompresses images; may strip |
| Google Photos | YES (original) | YES (original) | YES (shared link) | Shared URLs serve stripped version |
| Any social share | NO | NO | YES | Always strips |

**Strategy for MediaFire (compresses on upload):**
- Store XMP sidecar alongside every media file on MediaFire
- Sidecar filename: same as image, `.xmp` extension, SJL-named
- Example: `2026-06-29_14-30_media-image_austin-texas_UUID24.xmp`
- XMP file is plain XML — survives any compression
- TagBot reads sidecar if main file's EXIF is stripped

**XMP sidecar write (before upload):**
```bash
# ExifTool creates sidecar automatically
exiftool -o %d%f.xmp -tagsfromfile @ -all:all photo.jpg
```

**Post-upload verification:**
```python
def verify_exif_survived(cloud_file_path: str, expected_uuid24: str) -> bool:
    with exiftool.ExifToolHelper() as et:
        meta = et.get_metadata(cloud_file_path)[0]
    return meta.get("XMP:SJLuuid24") == expected_uuid24
```
If verification fails → re-embed via ExifTool → re-upload.

---

#### PHOTOPRISM vs IMMICH — HEAD-TO-HEAD ON METADATA

The person who told you PhotoPrism is more granular on metadata is correct.
Here is the verified difference:

| Factor | PhotoPrism | Immich |
|---|---|---|
| **Metadata read depth** | **Deeper** — EXIF + XMP + IPTC + Google Photos JSON + YAML sidecars + ExifTool integration built-in | Good — EXIF + GPS + Google Takeout JSON |
| **ExifTool integration** | **Built-in** — uses ExifTool internally for full field extraction | Not built-in |
| **XMP sidecar reading** | **Yes** — reads standalone .xmp files automatically | Limited |
| **YAML sidecar output** | **Yes** — creates human-readable YAML alongside each file | No |
| **Metadata as search primitive** | **Every field** is indexed and searchable/filterable | Basic fields only |
| **Bulk metadata editing** | **Better** — fix wrong dates/geotags across hundreds of files at once | Minimal editing |
| **GPS / world map** | **Interactive map view** (Plus tier, $25/yr) | Yes (free) |
| **Face recognition** | Yes (community edition) | Yes (free) |
| **Write metadata back to originals** | **No (intentional)** — avoids data loss/conflicts | No |
| **Mobile upload app** | Web upload + PhotoSync compatible | **Better** — native iOS/Android app |
| **REST API completeness** | Good | **More complete** |
| **Cost** | Free CE + $25/yr Plus for maps/vector search | **100% free** |
| **Development pace** | Stable, mature | Faster (larger team, 2024–2026) |
| **RAW file support** | **Better** — more RAW formats, more metadata from RAW | Good |
| **IPTC fields** | **Yes** — Title, Description, Artist, Keywords, Copyright | Partial |
| **Lens metadata** | **Full** — focal length, aperture, lens model, 35mm equivalent | Basic |

**Critical finding:** Neither PhotoPrism nor Immich writes changed metadata
back to the original files. **ExifTool remains essential for all write-back**
regardless of which DAM is chosen. The two roles are cleanly separated:
- DAM (PhotoPrism or Immich): **reads** and organizes
- ExifTool: **writes** SJL XMP fields, GPS, IPTC back into the file permanently

---

#### PHOTOPRISM — PRIMARY DAM (RECOMMENDED) ✦

PhotoPrism is the right choice for the SJL system because metadata granularity
is the primary requirement — every EXIF field needs to be readable, searchable,
and available to TagBot for SJL filename generation and Raindrop tagging.

**Editions:**
- **Community Edition (CE):** Free, AGPL, full core functionality, Docker
- **Plus (~$25/year):** Interactive world maps, vector search, advanced filters
  → Worth it. GPS world map + vector search directly serve the SJL use case.

**Docker deployment on shannonjlove.cloud:**
```yaml
# docker-compose.yml (PhotoPrism)
services:
  photoprism:
    image: photoprism/photoprism:latest
    ports: ["2342:2342"]
    environment:
      PHOTOPRISM_ADMIN_PASSWORD: "${PHOTOPRISM_ADMIN_PASSWORD}"
      PHOTOPRISM_SITE_URL: "https://photos.shannonjlove.cloud/"
      PHOTOPRISM_ORIGINALS_LIMIT: 5000     # MB per file, -1 for unlimited
      PHOTOPRISM_HTTP_COMPRESSION: "gzip"
      PHOTOPRISM_LOG_LEVEL: "info"
      PHOTOPRISM_READONLY: "false"
      PHOTOPRISM_EXPERIMENTAL: "false"
      PHOTOPRISM_DISABLE_CHOWN: "false"
      PHOTOPRISM_DISABLE_BACKUPS: "false"
      PHOTOPRISM_DISABLE_EXIFTOOL: "false"  # KEEP ENABLED — uses ExifTool
      PHOTOPRISM_DISABLE_FACES: "false"
      PHOTOPRISM_DISABLE_CLASSIFICATION: "false"
      PHOTOPRISM_FFMPEG_ENCODER: "software"
      PHOTOPRISM_DATABASE_DRIVER: "mysql"
      PHOTOPRISM_DATABASE_SERVER: "mariadb:3306"
      PHOTOPRISM_DATABASE_NAME: "photoprism"
      PHOTOPRISM_DATABASE_USER: "photoprism"
      PHOTOPRISM_DATABASE_PASSWORD: "${MARIADB_PASSWORD}"
    volumes:
      - /data/photoprism/originals:/photoprism/originals  # SJL @PROJECTS/AREAS/RESOURCES media
      - /data/photoprism/storage:/photoprism/storage      # cache, sidecars, thumbnails
      - /data/inbox:/photoprism/import                    # @INBOX_sjlcloud maps here

  mariadb:
    image: mariadb:10.11
    environment:
      MARIADB_ROOT_PASSWORD: "${MARIADB_ROOT_PASSWORD}"
      MARIADB_DATABASE: "photoprism"
      MARIADB_USER: "photoprism"
      MARIADB_PASSWORD: "${MARIADB_PASSWORD}"
    volumes:
      - /data/photoprism/db:/var/lib/mysql
```

**Domain:** `photos.shannonjlove.cloud` (nginx → port 2342)

**What PhotoPrism handles automatically:**
- Full EXIF extraction (via built-in ExifTool) — every field
- XMP sidecar reading — standalone `.xmp` files auto-detected
- GPS reverse geocoding → city, state, country (OpenStreetMap)
- Interactive world map (Plus): navigate library by location
- Human-readable YAML sidecar files — one per media file, editable
- Face detection and clustering
- Object/scene classification (TensorFlow models)
- RAW file support: CR2, CR3, ARW, NEF, DNG, HEIC, and more
- Duplicate detection
- Timeline by date + location

**PhotoPrism YAML sidecar — what it looks like:**
```yaml
# /photoprism/storage/sidecar/2026-06-29/IMG_4821.yml
TakenAt: "2026-06-29T14:30:22Z"
TakenAtLocal: "2026-06-29T09:30:22"
TimeZone: "America/Chicago"
Title: "Austin 6th Street"
Description: ""
Keywords: "austin, texas, outdoor, speaking"
Notes: ""
Subject: ""
Artist: ""
Latitude: 30.2672
Longitude: -97.7431
Altitude: 150
Country: "us"
City: "Austin"
State: "Texas"
Camera: "Apple iPhone 15 Pro"
Lens: "iPhone 15 Pro back triple camera 6.765mm f/1.78"
FocalLength: 6
FNumber: 1.8
ISO: 800
Exposure: "1/120"
Quality: 3
Scan: false
Panorama: false
Private: false
```
This YAML file is the TagBot pre-seed source — richer than any API response.

**PhotoPrism REST API → TagBot integration:**
```python
import requests

PHOTOPRISM_URL = "http://localhost:2342"
PHOTOPRISM_TOKEN = ""  # set after login

def photoprism_login():
    resp = requests.post(f"{PHOTOPRISM_URL}/api/v1/session",
                         json={"username": "admin", "password": ADMIN_PASSWORD})
    global PHOTOPRISM_TOKEN
    PHOTOPRISM_TOKEN = resp.json()["id"]

def get_photoprism_photo(file_hash: str) -> dict | None:
    resp = requests.get(
        f"{PHOTOPRISM_URL}/api/v1/photos",
        params={"q": f"hash:{file_hash}", "count": 1},
        headers={"X-Auth-Token": PHOTOPRISM_TOKEN}
    )
    results = resp.json()
    return results[0] if results else None

def photoprism_to_tagbot_seed(photo: dict) -> dict:
    city  = photo.get("City", "")
    state = photo.get("State", "")
    cam   = photo.get("CameraModel", "").lower().replace(" ", "-")
    geo_slug = f"{city}-{state}".lower().replace(" ", "-") if city else ""
    desc = f"{geo_slug}-{cam}" if geo_slug else cam

    return {
        "suggested_description": desc[:40],   # SJL 40-char limit
        "tags": list(filter(None, [
            "media", "image",
            city.lower() if city else None,
            state.lower() if state else None,
            photo.get("CameraMake", "").lower() or None,
            cam or None,
        ])) + photo.get("Keywords", "").split(", "),
        "gps_lat":    photo.get("Lat"),
        "gps_lon":    photo.get("Lng"),
        "date_taken": photo.get("TakenAt"),
        "faces":      [f["Name"] for f in photo.get("Faces", [])],
        "source":     "photoprism",
        "skip_ml":    True   # rich metadata → bypass CLIP/BLIP/YOLO
    }
```

**PhotoPrism → SJL pipeline flow:**
```
File arrives in /data/inbox (= /photoprism/import)
  → PhotoPrism auto-imports: reads full EXIF + XMP + GPS
  → PhotoPrism writes YAML sidecar to /photoprism/storage/sidecar/
  → FileWarden detects file in originals (post-import)
  → TagBot: query PhotoPrism API by file hash → get pre-seed
  → If pre-seed richness > 0.6: skip CLIP/BLIP/YOLO entirely
  → Build SJL description from city + camera + keywords
  → ExifTool: write SJL XMP fields into original file
  → ExifTool: write XMP sidecar alongside original
  → Apply SJL rename (UUID24 stays as permanent identity)
  → Route to PARA folder
  → HookVault fires to Raindrop + SJL Hub
```

---

#### IMMICH — SECONDARY OPTION (MOBILE-FIRST USE CASE)

Immich remains the better choice **only if** mobile upload convenience is the
top priority and metadata granularity is secondary. Its native iOS/Android app
is more seamless than PhotoPrism's mobile upload experience.

**When to choose Immich instead of PhotoPrism:**
- You primarily upload from iPhone and want background auto-backup
- You need 100% free (no $25/year Plus)
- REST API completeness matters more than metadata depth
- You don't need IPTC, XMP sidecar reading, or YAML sidecars

**When to run BOTH (advanced setup):**
- PhotoPrism: metadata master, search, catalog, GPS map
- Immich: mobile upload receiver → auto-sync originals to PhotoPrism's originals folder
- Result: iPhone photos go to Immich (easy upload) → Immich writes to shared volume
  → PhotoPrism indexes from same folder → both have the library
- Overhead: two Docker stacks; more RAM; more complexity
- Only worth it if mobile background upload is a hard requirement

**Recommendation for SJL:** Single-DAM setup with PhotoPrism.
Use PhotoSync app (iOS, one-time purchase ~$4) for mobile upload to PhotoPrism
if background auto-backup from iPhone is needed.

---

#### UPDATED RANK 1 (REPLACES NEOFINDER)

**Rank 1 — PhotoPrism + ExifTool (WebTop-native, replaces NeoFinder)**
```
Cost:       $0 CE / $25/yr Plus (maps + vector search — worth it)
Speed:      EXIF read: <100ms | GPS geocode: built-in | YAML sidecar: instant
RAM:        ~600 MB (PhotoPrism + MariaDB)
Platform:   Linux Docker — runs on shannonjlove.cloud, browser accessible
Advantage:  Most granular metadata reading of any self-hosted DAM
            Uses ExifTool internally — every EXIF/XMP/IPTC field extracted
            YAML sidecar per file = human-readable TagBot pre-seed
            GPS world map (Plus) = visual location browse across all media
            RAW support — CR2/CR3/ARW/NEF/DNG/HEIC all indexed
            IPTC fields: Title, Artist, Keywords, Copyright — SJL-relevant
            Full lens/equipment metadata — focal length, aperture, ISO
            Neither writes to originals → ExifTool owns write-back cleanly
Drawback:   $25/yr Plus for maps (free CE has no map view)
            Mobile upload less seamless than Immich (use PhotoSync app)
            MariaDB dependency (slightly heavier than Immich's Postgres setup)
            Face recognition training is slow on first large library import
Decision:   PhotoPrism is the DAM. ExifTool is the write engine.
            These two roles are permanently separated and complementary.
            Immich remains viable if mobile-first upload is a hard requirement.
```

---

### COMPLETE STACK RANKING — ALL OPTIONS DELIBERATED

This ranks every recognition option available across the full SJL system, from
fastest/cheapest to slowest/heaviest. Build in this order — each tier adds value
on top of the last.

---

**TIER 1 — Always run. Zero ML. Instant. (Run first, always.)**

**Rank 1 — NeoFinder catalog pre-seed**
```
Cost:       $0 (licensed)
Speed:      Instant (cache lookup)
Coverage:   Any file NeoFinder has already cataloged on your Mac
RAM:        0 (file read, no model)
Advantage:  Perfect accuracy for what it reads; skips all ML entirely
            Handles photos with GPS/EXIF, audio with ID3, video with track data
            Works for files on disconnected drives and old archives
Drawback:   Mac-only; requires NeoFinder ran on the file first
            Useless for files that arrive on the server without passing through Mac
            No content intelligence — only reads what's already embedded
Decision:   ALWAYS run first. If pre-seed score > 0.6, skip ML pipeline entirely.
```

**Rank 2 — mutagen (audio/video metadata)**
```
Cost:       $0
Speed:      <50ms per file
Coverage:   MP3, AAC, FLAC, OGG, MP4, M4A, WAV
RAM:        Negligible
Advantage:  Reads embedded ID3/MP4 tags with 100% accuracy; no model needed
            Artist, album, genre, BPM, year, track title — all ready for SJL tags
Drawback:   Only reads what's already tagged; useless for untagged music or video
            No content analysis — doesn't understand what's in an untagged file
Decision:   ALWAYS run on audio/video before any ML. Free metadata is better than
            inferred metadata.
```

---

**TIER 2 — Fast ML. Run on every file after Tier 1. Low RAM, CPU-friendly.**

**Rank 3 — YOLOv8n (object detection)**
```
Cost:       $0
Speed:      50–150ms per image (nano model, CPU)
RAM:        100 MB
Coverage:   80 standard object classes (person, car, phone, book, dog, etc.)
Advantage:  Fastest ML model in the stack; extremely reliable for common objects
            Pairs perfectly with CLIP — YOLO finds objects, CLIP finds scene context
            YOLOv8s (small) adds accuracy for only 200ms more
Drawback:   Only 80 COCO classes — can't detect "screenplay" or "concert stage"
            No scene understanding; no captions; no custom categories without fine-tuning
Decision:   ALWAYS run on images. Cheap signal with no downside.
```

**Rank 4 — CLIP ViT-B/32 (zero-shot image tagging)**
```
Cost:       $0
Speed:      200ms per image (CPU)
RAM:        600 MB
Coverage:   Unlimited — any concept you can describe in words
Advantage:  No training data needed; give it YOUR tag vocabulary and it scores each
            Can distinguish "outdoor concert" from "studio session" from "church service"
            Perfect for SJL taxonomy: creative, media, personal, project categories
Drawback:   Scoring against a list — you must define the tag vocabulary upfront
            Doesn't generate text; only ranks pre-defined tags by similarity
            ViT-L/14 (large) is more accurate but 3x slower and 4x more RAM
Decision:   ALWAYS run on images alongside YOLO. These two together cover ~80% of
            tagging needs without heavier models.
```

**Rank 5 — faster-whisper small (speech transcription)**
```
Cost:       $0
Speed:      3–5× realtime on CPU (60s video → 12–20s to transcribe)
RAM:        500 MB
Coverage:   Any audio track — video, podcast, voice memo, interview
Advantage:  Best open-source transcription available; multilingual; 99% accuracy
            Transcript becomes searchable content AND source for keyword extraction
            VAD (voice activity detection) built-in — skips silence and music
            faster-whisper is 4× faster than openai-whisper on same hardware
Drawback:   Useless on music-only content (no lyrics transcription without fine-tuning)
            Long videos (60+ min) still take real processing time on CPU
            medium model: 2× better but 2× slower — use for important content only
Decision:   ALWAYS run on video and audio. Even a partial transcript is more useful
            than no content signal. Use base model by default; medium for key projects.
```

**Rank 6 — KeyBERT + all-MiniLM-L6-v2 (keyword extraction)**
```
Cost:       $0
Speed:      <1s per document
RAM:        120 MB
Coverage:   Any text input (transcripts, PDF text, DOCX content)
Advantage:  Semantic extraction — finds concepts, not just frequent words
            "feature film second act" beats "the and of a" (TF-IDF style)
            Tiny model; always loaded; adds negligible overhead
Drawback:   Downstream only — needs text input from Marker/Tesseract/Whisper first
            Not generative — extracts from existing text, doesn't reason about it
Decision:   ALWAYS run on text output from any other step. Zero reason not to.
```

---

**TIER 3 — Moderate ML. Run when Tier 2 doesn't provide enough signal.**

**Rank 7 — BLIP-base (image captioning)**
```
Cost:       $0
Speed:      2–4s per image (CPU)
RAM:        900 MB
Coverage:   Any image
Advantage:  Generates natural language — "a woman speaking at an outdoor podium"
            That sentence becomes the SJL filename description field directly
            Fills the gap CLIP leaves: CLIP tags, BLIP describes
Drawback:   Captions can be generic ("a person standing near a building")
            Slower than CLIP/YOLO; may not justify time for bulk processing
            BLIP-2 is far richer but far slower (see Rank 10)
Decision:   Run on images where CLIP+YOLO output is ambiguous or too sparse.
            Skip for bulk archive processing (use CLIP+YOLO tags as description instead).
```

**Rank 8 — Marker (digital PDF → Markdown)**
```
Cost:       $0
Speed:      5–15s per page (CPU)
RAM:        1.5 GB
Coverage:   Digital (non-scanned) PDFs with selectable text
Advantage:  Best PDF → structured text conversion available; preserves tables, headings
            Output feeds directly into KeyBERT for keyword extraction
            Far better than PyPDF2/pdfminer for complex multi-column layouts
Drawback:   Slow for large PDFs (50-page doc = several minutes)
            Overkill for simple single-column text PDFs (use pdfminer for speed)
            Not needed for scanned PDFs (use Tesseract instead)
Decision:   Run on PDFs over 5 pages or with complex layouts. Use pdfminer as fast
            fallback for simple text documents.
```

**Rank 9 — Tesseract 5 (OCR for scanned PDFs and images)**
```
Cost:       $0
Speed:      1–5s per page (CPU)
RAM:        Minimal
Coverage:   Scanned PDFs, image-based documents, photos of text
Advantage:  Mature, accurate, 100+ languages, handles most printed text well
            Necessary for any file that isn't digitally created (old scans, archives)
Drawback:   Struggles with handwriting, degraded paper, unusual fonts
            Needs preprocessing (deskew, denoise) for dirty scans
            Doesn't understand document structure — outputs raw text only
Decision:   Run only when Marker returns < 100 characters (likely a scanned file).
            Pair with opencv preprocessing for better results on old documents.
```

---

**TIER 4 — LLM synthesis layer. Run after Tier 2/3 to unify and clean outputs.**

**Rank 10 — Ollama + phi3:mini (fast synthesis)**
```
Cost:       $0 (self-hosted)
Speed:      8–15s per request on CPU
RAM:        3 GB
Coverage:   Any text synthesis, summarization, tag cleaning, n8n automation
Advantage:  Intelligent synthesis of noisy ML outputs into clean SJL descriptions
            Replaces ALL Claude/Anthropic API calls in n8n at zero token cost
            phi3:mini punches far above its weight — Microsoft's efficient model
            Runs alongside full TagBot stack (3GB RAM is additive to ~4.2GB)
Drawback:   Still 8-15s per file — adds meaningful time to real-time processing
            phi3 can hallucinate on domain-specific content (film/music terminology)
            Not multimodal — can't see images; only reasons about text/tag inputs
Decision:   Run as synthesis step for CLIP+YOLO+BLIP outputs when combined
            signal is ambiguous. ALWAYS use as n8n Claude API replacement.
```

**Rank 11 — Ollama + mistral:7b (richer synthesis)**
```
Cost:       $0 (self-hosted)
Speed:      25–45s per request on CPU
RAM:        6 GB
Coverage:   Same as phi3 but more capable reasoning
Advantage:  Better instruction-following than phi3; more reliable JSON output
            Better at understanding creative/film/music domain context
            Instruction-tuned variant (mistral-instruct) follows prompts cleanly
Drawback:   Adds 25–45s per file in real-time mode — significant for large batches
            6 GB RAM barely leaves headroom if full TagBot stack is running
            Swap with phi3:mini for batch jobs where speed matters
Decision:   Use for n8n automation reasoning tasks (longer context, better quality).
            Use phi3:mini for TagBot synthesis (speed matters more there).
```

---

**TIER 5 — Heavy ML. Requires GPU or significant patience on CPU.**

**Rank 12 — DeepFace (face recognition)**
```
Cost:       $0
Speed:      1–3s per image on CPU (after face DB is built)
RAM:        500 MB + face database
Coverage:   Photos containing human faces
Advantage:  Identifies the same person across thousands of photos automatically
            Tags family members, collaborators, subjects by name
            Enables queries like "all photos with Asha" across entire library
Drawback:   Requires a curated "seed" database of named faces to match against
            Privacy consideration — builds a biometric database of people
            False positives in low-light or partially obscured faces
            Ethical constraint: only use on your own photos of people who consent
Decision:   Opt-in only. Configure per-folder. Seed with family/collaborator photos.
            Do NOT run by default on all incoming files.
```

**Rank 13 — BLIP-2 (rich image captioning)**
```
Cost:       $0
Speed:      10–30s per image on CPU
RAM:        4–6 GB (opt-2.7b variant)
Coverage:   Any image
Advantage:  Dramatically richer captions than BLIP-base
            Can answer visual questions: "is this indoors or outdoors?"
            Better at complex scenes (concerts, events, multi-person shots)
Drawback:   4–6 GB RAM competes directly with Ollama for headspace
            30s per image is impractical for real-time processing of photo libraries
            The quality jump over BLIP-base rarely justifies the speed cost on CPU
Decision:   Skip unless GPU is added. BLIP-base + Ollama synthesis achieves
            comparable quality at lower total RAM and similar wall-clock time.
```

**Rank 14 — Ollama + LLaVA:7b (vision-language, richest possible output)**
```
Cost:       $0
Speed:      60–180s per image on CPU
RAM:        7–8 GB
Coverage:   Any image — understands composition, mood, context, text in image
Advantage:  One model replaces CLIP + BLIP + YOLO for images — unified pipeline
            Can read text in images (signs, titles, on-screen text)
            Understands creative intent: "dramatic low-key portrait lighting"
            Best possible single-model output for image description
Drawback:   60–180 seconds per image on CPU is untenable for any real volume
            Displaces Ollama text models from RAM if run simultaneously
            GPU (8GB VRAM minimum) is effectively required for practical use
Decision:   DO NOT run on CPU for production. Add to the stack ONLY when GPU
            is added to the server. With GPU: replaces CLIP + BLIP entirely for images.
            With GPU (RTX 3060 12GB or better): 3–5s per image — excellent.
```

---

### FINAL RECOMMENDED OPERATING STACK (CPU-ONLY, TODAY)

```
LAYER         TOOL                    WHEN                        TIME/FILE
──────────    ──────────────────────  ─────────────────────────   ──────────
Pre-seed      NeoFinder export        Always first                 <50ms
              mutagen                 Audio/video always           <50ms

Object/Scene  YOLOv8n                 All images                   ~100ms
              CLIP ViT-B/32           All images                   ~200ms

Captioning    BLIP-base               Images w/ low CLIP signal    2–4s

Speech        faster-whisper small    All video + audio            3–5× RT

Text          Marker (or pdfminer)    Digital PDFs                 5–15s/pg
              Tesseract               Scanned PDFs                 1–5s/pg
              KeyBERT + MiniLM        All text output              <1s

Synthesis     Ollama phi3:mini        Tag consolidation            8–15s
              (batch mode: async)     n8n workflow LLM             8–15s

Optional      DeepFace                Personal photos, opt-in      1–3s
              faster-whisper medium   Key project video            2× RT
```

**GPU upgrade path:** Add any RTX 3060 12GB or better to the server →
LLaVA:7b replaces CLIP+BLIP+YOLO for images (3–5s unified), Whisper medium
becomes real-time, BLIP-2 becomes practical. Total per-file time drops from
~15–30s to ~5–8s for a full media file.

**RAM budget summary (all running simultaneously):**
```
TagBot models (CLIP + BLIP + YOLO + Whisper + KeyBERT + Marker): ~4.2 GB
Ollama phi3:mini:                                                  ~3.0 GB
OS + FileWarden + HookVault + n8n:                                 ~2.0 GB
──────────────────────────────────────────────────────────────────────────
Total:                                                             ~9.2 GB
Recommended server RAM:                                            16 GB
```

If current server has < 16 GB: run Ollama on-demand (start/stop per job) rather
than always-on, and defer BLIP-base to batch mode only. Minimum viable is 8 GB
running CLIP + YOLO + Whisper + KeyBERT only (~3 GB model RAM).
