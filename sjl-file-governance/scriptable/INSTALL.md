# SJL File Governance — Scriptable App Install Guide

## What This Does

Applies the full SJL Sovereign Cloud canonical naming convention to any file
shared from the iOS Share Sheet:

```
[PPPPP]_YYYY-MM-DD__DOCID__semantic-title__vMAJOR-MINOR__sha8.ext
```

It also writes a `.sjl.json` sidecar, a `.sha256` checksum file, and
updates a local registry in iCloud Drive. Optionally fires an n8n webhook
so Nexus FileWarden completes full server-side governance automatically.

## Requirements

- [Scriptable](https://scriptable.app) — free on the App Store
- iCloud Drive enabled

## Install Steps

1. Open the App Store and install **Scriptable**.
2. Open `SJL-File-Governance.js` in this folder.
3. Copy the entire contents.
4. Open Scriptable → tap **+** (new script) → paste the code.
5. Name the script exactly: `SJL File Governance`
6. Tap the **wrench icon** → enable **"Show in Share Sheet"**.
7. Tap **Done**.

## Configure

Near the top of the script, edit the `CONFIG` block:

```javascript
const CONFIG = {
  iCloudInboxFolder: "SJL/01000_INBOX/01100_DEVICE-INTAKE",
  registryPath: "SJL/07000_SYSTEM-AUTOMATION/07400_MIRROR-REGISTRY/sjl-registry.json",
  sidecarBase: "SJL/.sidecars",
  n8nWebhookURL: null, // paste your n8n webhook URL here to enable server governance
  docidPrefix: "SJL-DEVICE",
  defaultPARA: "01000",
};
```

Set `n8nWebhookURL` to your n8n webhook (e.g. `https://n8n.shannonjlove.cloud/webhook/sjl-intake`) to automatically trigger Nexus FileWarden for full server-side governance (OCR, vision, mirroring, BookStack, PaperParrot).

## Usage

1. In any iOS app, share a file → tap **Share** → scroll to **Scriptable**.
2. Select **SJL File Governance** from the script list.
3. The script will walk you through:
   - DOCID assignment (new or existing document)
   - PARA five-digit classification
   - Semantic title entry
   - Version selection (for existing documents)
   - Confirmation of the canonical filename
4. The governed file lands in iCloud Drive at:
   `SJL/01000_INBOX/01100_DEVICE-INTAKE/<canonical-filename>`
5. Three companion files are also written:
   - `<canonical-filename>.sjl.json` — full sidecar metadata
   - `<canonical-filename>.sha256` — checksum record
   - `.sidecars/<DOCID>/provenance.json` — persistent sidecar copy
6. If n8n is configured, Nexus picks it up and completes OCR, mirroring, BookStack publication, and PaperParrot archival automatically.

## iCloud Drive Folder Structure Created

```
iCloud Drive/
└── SJL/
    ├── 01000_INBOX/
    │   └── 01100_DEVICE-INTAKE/      ← governed files land here
    ├── 07000_SYSTEM-AUTOMATION/
    │   └── 07400_MIRROR-REGISTRY/
    │       └── sjl-registry.json     ← running registry of all governed files
    └── .sidecars/
        └── <DOCID>/
            ├── provenance.json       ← persistent sidecar
            └── (future: ocr.txt, vision.json, diffs/)
```

## Quarantine

Files that fail SHA-256 verification or have metadata conflicts should be
routed to `09000_QUARANTINE/` on Nexus by FileWarden automatically when
the n8n webhook fires.

## Updating the Script

This file lives at:
`sjl-file-governance/scriptable/SJL-File-Governance.js`

When the doctrine is updated (version bumped in the governance manual),
update the script to match and increment the version comment at the top.
