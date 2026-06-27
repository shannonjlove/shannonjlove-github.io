// SJL Sovereign Cloud — File Governance Engine
// Version: v1.0
// Compatible with: Scriptable for iOS/macOS
// Share Sheet: Yes — receives files, URLs, and text
//
// Canonical format: [PPPPP]_YYYY-MM-DD__DOCID__semantic-title__vMAJOR-MINOR__sha8.ext
// Example:          02000_2026-06-19__SJL-CLOUD-0017__persistent-metadata-manual__v7-2__843dc901.pdf

// ─────────────────────────────────────────────
// CONFIGURATION — edit these to match your setup
// ─────────────────────────────────────────────
const CONFIG = {
  // iCloud Drive folder where governed files land (relative to iCloud Drive root)
  iCloudInboxFolder: "SJL/01000_INBOX/01100_DEVICE-INTAKE",

  // Registry file path in iCloud Drive (JSON array of all governed file records)
  registryPath: "SJL/07000_SYSTEM-AUTOMATION/07400_MIRROR-REGISTRY/sjl-registry.json",

  // Sidecar folder inside iCloud Drive
  sidecarBase: "SJL/.sidecars",

  // n8n webhook endpoint — receives the sidecar payload for server-side processing
  // Set to null to skip (runs fully on-device)
  n8nWebhookURL: null, // e.g. "https://n8n.shannonjlove.cloud/webhook/sjl-intake"

  // DOCID prefix for new documents assigned on-device
  docidPrefix: "SJL-DEVICE",

  // Default PARA code when user skips classification
  defaultPARA: "01000",
};

// ─────────────────────────────────────────────
// PARA CLASSIFICATION TABLE
// ─────────────────────────────────────────────
const PARA = {
  "01000": "INBOX — Controlled intake, staging, and review",
  "02000": "PROJECTS — Active finite projects and deliverables",
  "03000": "AREAS — Ongoing responsibilities and operations",
  "04000": "RESOURCES — Reference material and reusable assets",
  "05000": "ARCHIVES — Inactive, completed, and retained records",
  "06000": "PRIVATE MEDIA — Restricted media and sensitive assets",
  "07000": "SYSTEM AUTOMATION — Scripts, agents, Quadlets, manifests",
  "08000": "APPLICATION DATA — Governed application exports",
  "09000": "QUARANTINE — Failures, conflicts, and review-required",
};

// ─────────────────────────────────────────────
// SHA-256 IMPLEMENTATION (pure JS, no dependencies)
// Based on the public-domain SHA-256 by Chris Veness
// ─────────────────────────────────────────────
function sha256(msgStr) {
  function rightRotate(value, amount) {
    return (value >>> amount) | (value << (32 - amount));
  }
  const mathPow = Math.pow;
  const maxWord = mathPow(2, 32);
  const lengthProperty = "length";
  let i, j;
  let result = "";

  const words = [];
  const asciiBitLength = msgStr[lengthProperty] * 8;

  let hash = (sha256.h = sha256.h || []);
  let k = (sha256.k = sha256.k || []);
  let primeCounter = k[lengthProperty];

  const isComposite = {};
  for (let candidate = 2; primeCounter < 64; candidate++) {
    if (!isComposite[candidate]) {
      for (i = 0; i < 313; i += candidate) {
        isComposite[i] = candidate;
      }
      hash[primeCounter] = (mathPow(candidate, 0.5) * maxWord) | 0;
      k[primeCounter++] = (mathPow(candidate, 1 / 3) * maxWord) | 0;
    }
  }

  msgStr += "\x80";
  while ((msgStr[lengthProperty] % 64) - 56) {
    msgStr += "\x00";
  }

  for (i = 0; i < msgStr[lengthProperty]; i++) {
    j = msgStr.charCodeAt(i);
    if (j >> 8) return null; // non-ASCII — use byte fallback
    words[i >> 2] |= j << (((3 - i) % 4) * 8);
  }
  words[words[lengthProperty]] = (asciiBitLength / maxWord) | 0;
  words[words[lengthProperty]] = asciiBitLength;

  for (j = 0; j < words[lengthProperty]; ) {
    const w = words.slice(j, (j += 16));
    const oldHash = hash.slice(0);
    hash = hash.slice(0, 8);

    for (i = 0; i < 64; i++) {
      const i2 = i + j - 16;
      const w15 = w[i - 15],
        w2 = w[i - 2];
      const a = hash[0],
        e = hash[4];
      const temp1 =
        hash[7] +
        (rightRotate(e, 6) ^ rightRotate(e, 11) ^ rightRotate(e, 25)) +
        ((e & hash[5]) ^ (~e & hash[6])) +
        k[i] +
        (w[i] =
          i < 16
            ? w[i]
            : (w[i - 16] +
                (rightRotate(w15, 7) ^
                  rightRotate(w15, 18) ^
                  (w15 >>> 3)) +
                w[i - 7] +
                (rightRotate(w2, 17) ^
                  rightRotate(w2, 19) ^
                  (w2 >>> 10))) |
              0);
      const temp2 =
        (rightRotate(a, 2) ^ rightRotate(a, 13) ^ rightRotate(a, 22)) +
        ((a & hash[1]) ^ (a & hash[2]) ^ (hash[1] & hash[2]));
      hash = [
        (temp1 + temp2) | 0,
        a,
        hash[1],
        hash[2],
        (hash[3] + temp1) | 0,
        e,
        hash[5],
        hash[6],
      ];
    }

    for (i = 0; i < 8; i++) {
      hash[i] = (hash[i] + oldHash[i]) | 0;
    }
  }

  for (i = 0; i < 8; i++) {
    for (j = 3; j + 1; j--) {
      const b = (hash[i] >> (j * 8)) & 255;
      result += (b < 16 ? "0" : "") + b.toString(16);
    }
  }
  return result;
}

// SHA-256 for binary Data object via hex string of bytes
function sha256FromData(data) {
  const bytes = data.getBytes();
  let str = "";
  for (let i = 0; i < bytes.length; i++) {
    str += String.fromCharCode(bytes[i]);
  }
  return sha256(str);
}

// ─────────────────────────────────────────────
// DOCID GENERATOR
// Format: SJL-DEVICE-YYYYMMDD-HHMMSS-XXXX
// ─────────────────────────────────────────────
function generateDocID() {
  const now = new Date();
  const pad = (n) => String(n).padStart(2, "0");
  const datePart =
    now.getFullYear().toString() +
    pad(now.getMonth() + 1) +
    pad(now.getDate());
  const timePart = pad(now.getHours()) + pad(now.getMinutes()) + pad(now.getSeconds());
  const rand = Math.floor(Math.random() * 9999)
    .toString()
    .padStart(4, "0");
  return `${CONFIG.docidPrefix}-${datePart}-${timePart}-${rand}`;
}

// ─────────────────────────────────────────────
// DATE UTILITIES
// ─────────────────────────────────────────────
function isoDate(d) {
  const pad = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
}

function isoTimestamp(d) {
  return d.toISOString();
}

// ─────────────────────────────────────────────
// SLUGIFY — creates the semantic-title segment
// ─────────────────────────────────────────────
function slugify(text) {
  return text
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 60);
}

// ─────────────────────────────────────────────
// FILE EXTENSION — normalized to lowercase
// ─────────────────────────────────────────────
function getExtension(filename) {
  const parts = filename.split(".");
  return parts.length > 1 ? parts.pop().toLowerCase() : "bin";
}

function stripExtension(filename) {
  const parts = filename.split(".");
  if (parts.length > 1) parts.pop();
  return parts.join(".");
}

// ─────────────────────────────────────────────
// VERSION PARSER / INCREMENTER
// ─────────────────────────────────────────────
function parseVersion(vStr) {
  const match = vStr.match(/^v?(\d+)-(\d+)$/);
  if (match) return { major: parseInt(match[1]), minor: parseInt(match[2]) };
  return { major: 1, minor: 0 };
}

function formatVersion(v) {
  return `v${v.major}-${v.minor}`;
}

function incrementMinor(v) {
  return { major: v.major, minor: v.minor + 1 };
}

// ─────────────────────────────────────────────
// REGISTRY — load and save from iCloud Drive
// ─────────────────────────────────────────────
const fm = FileManager.iCloud();

function loadRegistry() {
  const path = fm.joinPath(fm.documentsDirectory(), CONFIG.registryPath);
  if (fm.fileExists(path)) {
    try {
      const raw = fm.readString(path);
      return JSON.parse(raw);
    } catch (e) {
      return [];
    }
  }
  return [];
}

function saveRegistry(registry) {
  const path = fm.joinPath(fm.documentsDirectory(), CONFIG.registryPath);
  const dir = path.split("/").slice(0, -1).join("/");
  if (!fm.fileExists(dir)) fm.createDirectory(dir, true);
  fm.writeString(path, JSON.stringify(registry, null, 2));
}

function findByDocID(registry, docid) {
  return registry.find((r) => r.docid === docid) || null;
}

// ─────────────────────────────────────────────
// SIDECAR JSON — write .sjl.json companion file
// ─────────────────────────────────────────────
function writeSidecar(sidecarData, docid) {
  const sidecarDir = fm.joinPath(
    fm.documentsDirectory(),
    CONFIG.sidecarBase,
    docid
  );
  if (!fm.fileExists(sidecarDir)) fm.createDirectory(sidecarDir, true);

  const sidecarPath = fm.joinPath(sidecarDir, "provenance.json");
  fm.writeString(sidecarPath, JSON.stringify(sidecarData, null, 2));
  return sidecarPath;
}

// ─────────────────────────────────────────────
// PARA CLASSIFICATION MENU
// ─────────────────────────────────────────────
async function choosePARA() {
  const alert = new Alert();
  alert.title = "SJL — PARA Classification";
  alert.message = "Select the five-digit PARA destination for this file.";
  const codes = Object.keys(PARA);
  for (const code of codes) {
    alert.addAction(`${code} — ${PARA[code].split(" — ")[0]}`);
  }
  alert.addCancelAction("Use Default (01000 INBOX)");
  const idx = await alert.presentSheet();
  if (idx === -1) return CONFIG.defaultPARA;
  return codes[idx];
}

// ─────────────────────────────────────────────
// SEMANTIC TITLE INPUT
// ─────────────────────────────────────────────
async function getSemanticTitle(suggestedTitle) {
  const alert = new Alert();
  alert.title = "SJL — Semantic Title";
  alert.message =
    "Enter a descriptive title for this file.\nIt will be slugified automatically.\n\nSuggestion: " +
    suggestedTitle;
  alert.addTextField("semantic-title", suggestedTitle);
  alert.addAction("Confirm");
  alert.addCancelAction("Use Suggestion");
  const result = await alert.present();
  if (result === -1) return suggestedTitle;
  return alert.textFieldValue(0) || suggestedTitle;
}

// ─────────────────────────────────────────────
// VERSION INPUT (for existing documents)
// ─────────────────────────────────────────────
async function getVersionChoice(existingVersion) {
  const next = incrementMinor(existingVersion);
  const alert = new Alert();
  alert.title = "SJL — Version";
  alert.message = `Current version: ${formatVersion(existingVersion)}`;
  alert.addAction(`Auto-increment → ${formatVersion(next)}`);
  alert.addAction("Major revision (v+1-0)");
  alert.addAction("Keep current (metadata-only change)");
  alert.addCancelAction("Cancel");
  const idx = await alert.present();
  if (idx === 0) return next;
  if (idx === 1) return { major: existingVersion.major + 1, minor: 0 };
  if (idx === 2) return existingVersion;
  return null;
}

// ─────────────────────────────────────────────
// DOCID INPUT — new vs existing
// ─────────────────────────────────────────────
async function resolveDocID(suggestedDocID) {
  const alert = new Alert();
  alert.title = "SJL — Document Identity";
  alert.message =
    "Is this a NEW file (auto-assign DOCID) or an EXISTING governed file (enter its DOCID)?";
  alert.addAction("New file — auto-assign DOCID");
  alert.addAction("Existing file — enter DOCID");
  alert.addCancelAction("Cancel");
  const idx = await alert.present();
  if (idx === -1) return null;
  if (idx === 0) return suggestedDocID;

  const docAlert = new Alert();
  docAlert.title = "SJL — Enter DOCID";
  docAlert.addTextField("DOCID", "");
  docAlert.addAction("Confirm");
  docAlert.addCancelAction("Cancel");
  const result = await docAlert.present();
  if (result === -1) return null;
  return docAlert.textFieldValue(0).trim() || suggestedDocID;
}

// ─────────────────────────────────────────────
// CONFIRMATION SUMMARY
// ─────────────────────────────────────────────
async function confirmRename(canonicalName, sidecarSummary) {
  const alert = new Alert();
  alert.title = "SJL — Confirm Governance";
  alert.message =
    `Canonical filename:\n${canonicalName}\n\n` +
    `DOCID: ${sidecarSummary.docid}\n` +
    `PARA: ${sidecarSummary.para}\n` +
    `Version: ${sidecarSummary.version}\n` +
    `SHA-256 (8): ${sidecarSummary.sha8}\n\n` +
    `Destination:\niCloud Drive/${CONFIG.iCloudInboxFolder}/`;
  alert.addAction("Apply Governance");
  alert.addCancelAction("Cancel");
  const idx = await alert.present();
  return idx === 0;
}

// ─────────────────────────────────────────────
// SEND TO N8N WEBHOOK (optional)
// ─────────────────────────────────────────────
async function sendToN8n(sidecarData) {
  if (!CONFIG.n8nWebhookURL) return;
  try {
    const req = new Request(CONFIG.n8nWebhookURL);
    req.method = "POST";
    req.headers = { "Content-Type": "application/json" };
    req.body = JSON.stringify(sidecarData);
    await req.loadJSON();
  } catch (e) {
    console.log("n8n webhook failed (non-fatal): " + e.message);
  }
}

// ─────────────────────────────────────────────
// MAIN — Share Sheet Entry Point
// ─────────────────────────────────────────────
async function main() {
  // ── 1. Receive shared content ────────────────
  if (!args.fileURLs || args.fileURLs.length === 0) {
    const alert = new Alert();
    alert.title = "SJL File Governance";
    alert.message =
      "No file received.\n\nShare a file to this script from the iOS Share Sheet, or use the Files app.";
    alert.addAction("OK");
    await alert.present();
    return;
  }

  for (const fileURL of args.fileURLs) {
    await processFile(fileURL);
  }
}

// ─────────────────────────────────────────────
// PROCESS ONE FILE
// ─────────────────────────────────────────────
async function processFile(fileURL) {
  // ── 2. Read file data ────────────────────────
  const originalFilename = decodeURIComponent(fileURL.split("/").pop());
  const ext = getExtension(originalFilename);
  const baseName = stripExtension(originalFilename);

  let fileData;
  try {
    fileData = Data.fromFile(fileURL);
  } catch (e) {
    const alert = new Alert();
    alert.title = "Read Error";
    alert.message = `Could not read file: ${originalFilename}\n\n${e.message}`;
    alert.addAction("OK");
    await alert.present();
    return;
  }

  // ── 3. SHA-256 ──────────────────────────────
  const fullHash = sha256FromData(fileData) || "00000000000000000000000000000000";
  const sha8 = fullHash.slice(0, 8);

  // ── 4. DOCID ────────────────────────────────
  const autoDocID = generateDocID();
  const registry = loadRegistry();
  const docid = await resolveDocID(autoDocID);
  if (!docid) return; // user cancelled

  // ── 5. Version ──────────────────────────────
  const existingRecord = findByDocID(registry, docid);
  let version;
  if (existingRecord) {
    const existingVersion = parseVersion(existingRecord.version || "v1-0");
    version = await getVersionChoice(existingVersion);
    if (!version) return;
  } else {
    version = { major: 1, minor: 0 };
  }

  // ── 6. PARA Classification ──────────────────
  const paraCode = await choosePARA();

  // ── 7. Semantic Title ───────────────────────
  const rawTitle = await getSemanticTitle(baseName);
  const semanticTitle = slugify(rawTitle);

  // ── 8. Date ─────────────────────────────────
  const now = new Date();
  const dateStr = isoDate(now);

  // ── 9. Canonical Filename ───────────────────
  const versionStr = formatVersion(version);
  const canonicalName = `${paraCode}_${dateStr}__${docid}__${semanticTitle}__${versionStr}__${sha8}.${ext}`;

  // ── 10. Sidecar payload ─────────────────────
  const sidecarData = {
    schema_version: "1.0",
    docid: docid,
    canonical_filename: canonicalName,
    original_filename: originalFilename,
    para: paraCode,
    para_label: PARA[paraCode] || "Unknown",
    semantic_title: semanticTitle,
    raw_title: rawTitle,
    version: versionStr,
    sha256_full: fullHash,
    sha256_8: sha8,
    extension: ext,
    mime_type: null,
    date_document: dateStr,
    date_ingested: isoTimestamp(now),
    date_modified: isoTimestamp(now),
    origin_device: Device.name(),
    origin_app: "Scriptable",
    intake_method: "ios-share-sheet",
    canonical_path: `iCloud/${CONFIG.iCloudInboxFolder}/${canonicalName}`,
    historical_paths: existingRecord ? existingRecord.historical_paths || [] : [],
    ocr_state: "pending",
    vision_state: "pending",
    mirror_state: "pending",
    mirror_verified: false,
    hook_id: null,
    registry_record_id: null,
    sensitivity: "standard",
    retention: "standard",
    review_status: "pending-server-governance",
    prior_version: existingRecord ? existingRecord.version : null,
    prior_sha256: existingRecord ? existingRecord.sha256_full : null,
    sidecar_created_by: "SJL-File-Governance-Scriptable-v1.0",
    note: "On-device pre-governance record. Nexus FileWarden will complete full governance.",
  };

  // ── 11. Confirm ─────────────────────────────
  const confirmed = await confirmRename(canonicalName, sidecarData);
  if (!confirmed) return;

  // ── 12. Write governed file to iCloud Drive ──
  const destDir = fm.joinPath(
    fm.documentsDirectory(),
    CONFIG.iCloudInboxFolder
  );
  if (!fm.fileExists(destDir)) fm.createDirectory(destDir, true);

  const destPath = fm.joinPath(destDir, canonicalName);
  fm.write(destPath, fileData);

  // ── 13. Write sidecar ───────────────────────
  const sidecarDir = fm.joinPath(
    fm.documentsDirectory(),
    CONFIG.sidecarBase,
    docid
  );
  if (!fm.fileExists(sidecarDir)) fm.createDirectory(sidecarDir, true);
  const sidecarPath = fm.joinPath(sidecarDir, "provenance.json");
  fm.writeString(sidecarPath, JSON.stringify(sidecarData, null, 2));

  // Also write inline .sjl.json alongside the governed file
  const inlineSidecarPath = destPath + ".sjl.json";
  fm.writeString(inlineSidecarPath, JSON.stringify(sidecarData, null, 2));

  // Write .sha256 checksum file
  const checksumPath = destPath + ".sha256";
  fm.writeString(checksumPath, `${fullHash}  ${canonicalName}\n`);

  // ── 14. Update registry ─────────────────────
  const registryEntry = {
    docid: docid,
    canonical_filename: canonicalName,
    version: versionStr,
    sha256_full: fullHash,
    para: paraCode,
    semantic_title: semanticTitle,
    date_ingested: isoTimestamp(now),
    canonical_path: `iCloud/${CONFIG.iCloudInboxFolder}/${canonicalName}`,
    historical_paths: sidecarData.historical_paths,
    mirror_state: "pending",
    origin_device: Device.name(),
  };

  const existingIdx = registry.findIndex((r) => r.docid === docid);
  if (existingIdx >= 0) {
    const old = registry[existingIdx];
    registryEntry.historical_paths = [
      ...(old.historical_paths || []),
      old.canonical_path,
    ].filter(Boolean);
    registry[existingIdx] = registryEntry;
  } else {
    registry.push(registryEntry);
  }
  saveRegistry(registry);

  // ── 15. Send to n8n for server-side governance ──
  await sendToN8n(sidecarData);

  // ── 16. Success notification ─────────────────
  const notification = new Notification();
  notification.title = "SJL — File Governed";
  notification.body = canonicalName;
  notification.sound = "default";
  await notification.schedule();

  const successAlert = new Alert();
  successAlert.title = "Governance Complete";
  successAlert.message =
    `✓ Renamed:\n${canonicalName}\n\n` +
    `✓ Saved to:\niCloud/${CONFIG.iCloudInboxFolder}/\n\n` +
    `✓ Sidecar written\n` +
    `✓ SHA-256 checksum written\n` +
    `✓ Registry updated\n\n` +
    (CONFIG.n8nWebhookURL
      ? "✓ Sent to n8n for server-side governance"
      : "⚠ n8n webhook not configured — Nexus FileWarden will govern on next sync");
  successAlert.addAction("Done");
  await successAlert.present();
}

// ─────────────────────────────────────────────
// RUN
// ─────────────────────────────────────────────
await main();
