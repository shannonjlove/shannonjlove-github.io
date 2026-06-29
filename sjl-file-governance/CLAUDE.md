# SJL Sovereign Cloud — Agent Constitution
# Governs all Claude Code sessions touching sjl-file-governance artifacts

## Canonical Naming Convention (MANDATORY)

Every governed file must follow this exact format:

```
[PPPPP]_YYYY-MM-DD__DOCID__semantic-title__vMAJOR-MINOR__sha8.ext
```

Example: `02000_2026-06-19__SJL-CLOUD-0017__persistent-metadata-manual__v7-2__843dc901.pdf`

No deviation is permitted. Every file touched by this agent must either already conform or be governed before the session closes.

## Identity Rules

- DOCID is permanent identity. Path and filename are mutable location.
- Never use a path as a document identifier.
- Moves and renames update the path record; the DOCID never changes.
- Every byte-level content change creates a new immutable version with an incremented version number and a new SHA-256.

## Version Discipline

- v1-0 → initial ingestion
- v1-1 → first content modification
- vN+1-0 → intentional major revision
- A metadata-only change does not increment the content version; it creates a metadata event.
- The prior version is always preserved before replacement.

## PARA Five-Digit Hierarchy

All directories must use five-digit PARA codes:

| Code  | Category          |
|-------|-------------------|
| 01000 | INBOX             |
| 02000 | PROJECTS          |
| 03000 | AREAS             |
| 04000 | RESOURCES         |
| 05000 | ARCHIVES          |
| 06000 | PRIVATE MEDIA     |
| 07000 | SYSTEM AUTOMATION |
| 08000 | APPLICATION DATA  |
| 09000 | QUARANTINE        |

## Change Rules

Before modifying any governed file this agent MUST:
1. Calculate SHA-256 of the current file.
2. Preserve the current version.
3. Increment the version number.
4. Generate a diff record.
5. Update the sidecar JSON.
6. Update the registry entry.
7. Mirror and checksum-verify the bundle.
8. Publish change summary to BookStack and archive to PaperParrot.

No change is complete until all eight steps are verified.

## Prohibited Actions

- Never overwrite a governed file without completing the change protocol above.
- Never perform a bulk rename without a dry run, backup, manifest, and rollback plan.
- Never expose, echo, or log credentials, tokens, or secrets.
- Never modify OS, database, container, package cache, or `.git` object paths.
- Never use Docker; always use rootless Podman with systemd Quadlets under the `sjl` user.
- Never claim a task complete until FileWarden state, Git history, backup evidence, service health, remote checksum, BookStack publication, and PaperParrot archival all agree.

## Branch and Commit Naming

Branches: `claude/07000-YYYY-MM-DD-short-change-slug`
Commits:  `[07000][DOCID][vMAJOR-MINOR] imperative change summary`
Artifacts: `[PPPPP]_YYYY-MM-DD__DOCID__semantic-title__vMAJOR-MINOR__sha8.ext`

## Source Artifact Reference

Full doctrine: `SJL-CLOUD-FILE-GOVERNANCE-v7.4.md`
Scriptable app: `scriptable/SJL-File-Governance.js`

## FileWarden v2 Skill Library

Location: `filewarden/skills/`

| Skill module | Stage | Purpose |
|---|---|---|
| skill_stabilize_timing | stabilize | Lock detection, size-stability polling |
| skill_docid_assign | identify | Sequential DOCID counter |
| skill_subfolder_traversal | analyze | Recursive inbox scan |
| skill_content_classify | analyze | Entity-list content routing |
| skill_screenshot_sort | analyze | Device resolution → PARA route |
| skill_pdf_ocr_detect | analyze | Text-layer detection + OCR queue |
| skill_image_gps_tag | analyze | EXIF GPS → Nominatim geocode |
| skill_yaml_tag_extract | analyze | Front-matter tag extraction |
| skill_xattr_tag | analyze/sidecar | macOS/Linux xattr read/write (Finder tags, SJL namespace) |
| skill_pdf_reduce_size | version | Ghostscript compression |
| skill_video_sort | rename | TV/Movie detection → 06000 routes |
| skill_video_convert | rename | HandBrake/ffmpeg H.265 conversion |
| skill_audio_convert | rename | DTS/FLAC → AC3 re-encode |
| skill_new_files_only | hook | Age-gate + batch window filter |
| skill_date_archive | hook | Monthly/yearly archive routing |
| skill_merge_backup | mirror | Multi-destination backup |
| skill_mp4_gather | mirror | Aggregate MP4 collector |
| skill_move_parent_folder | mirror | Companion-file bundle mover |
| skill_dmg_extract | mirror | DMG mount + extract |
| skill_notes_publish | publish | BookStack page creation |

Pipeline stages in order: `stabilize → identify → analyze → version → rename → sidecar → hook → mirror → register → publish`

## Quarantine Codes

| Code  | Condition |
|-------|-----------|
| 09100 | MISSING-SIDECAR |
| 09200 | HASH-MISMATCH |
| 09300 | METADATA-CONFLICT |
| 09400 | MIRROR-FAILURE |
| 09500 | VERSION-CHAIN-ERROR |

## xattr Key Reference (macOS)

| Key | Content |
|-----|---------|
| `com.apple.metadata:_kMDItemUserTags` | Finder tags (binary plist NSArray) |
| `com.apple.metadata:kMDItemKeywords` | Spotlight keywords |
| `com.apple.metadata:kMDItemComment` | Spotlight comment |
| `co.sjl.filewarden:docid#S` | DOCID (iCloud syncable) |
| `co.sjl.filewarden:para#S` | PARA zone |
| `co.sjl.filewarden:version#S` | Current version |
| `co.sjl.filewarden:sha256#S` | Full SHA-256 |

Tag color format: `"Name"` (plain, color 0) or `"Name\nN"` (N = Finder color 1–7)
PARA → color map: 01000→6(Orange), 02000→5(Red), 03000→4(Blue), 04000→2(Green), 05000→1(Gray), 06000→3(Purple), 07000/08000→7(Yellow), 09000→5(Red)
