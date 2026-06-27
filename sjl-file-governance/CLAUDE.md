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

Full doctrine: `SJL-CLOUD-FILE-GOVERNANCE-v7.3.md`
Scriptable app: `scriptable/SJL-File-Governance.js`
