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
| `hookvault.py` | Same | Webhook manager: fires HookVault payloads to Raindrop |
| `diffforge.py` | Same | Diff/comparison utility |
| `DEPLOY.sh` | Same | Deployment script |
| `config.yaml` | Same | FileWarden rules: inbox routing, categories, rename patterns |
| Raindrop.io | Cloud | Universal link browser; Hookmark equivalent for cloud files |
| n8n | shannonjlove.cloud | Automation platform; receives HookVault webhooks |
| BookStack | TBD | Internal documentation wiki; this CLAUDE.md is the source |
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
| Automation | n8n at shannonjlove.cloud + HookVault webhooks |
