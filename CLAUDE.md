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
| `diffforge.py` | Same | Diff/comparison utility |
| `DEPLOY.sh` | Same | Deployment script |
| `config.yaml` | Same | FileWarden rules: inbox routing, categories, rename patterns |
| Raindrop.io | Cloud | Universal link browser; Hookmark equivalent for cloud files |
| SJL Hub | `hub.shannonjlove.cloud` | Custom cluster management UI (see Part 10) |
| n8n | shannonjlove.cloud | Automation platform; receives HookVault webhooks |
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
