// HookVault — Scriptable script for iOS
// Provides a menu-driven interface to HookVault running on Nexus VPS.
// Install in Scriptable, configure BASE_URL and optionally add to home screen as widget.
//
// Features:
//   - Search and browse hooks
//   - Add URL from clipboard or Share Sheet
//   - View item links
//   - Open hook:// URLs in Hookmark PAL
//   - Works from Shortcuts via CallbackURL

const BASE_URL = "https://hooks.shannonjlove.cloud";  // HookVault public URL

// ── Helpers ───────────────────────────────────────────────────────────────────

async function apiGet(path, params = {}) {
  const qs = Object.entries(params).map(([k, v]) => `${k}=${encodeURIComponent(v)}`).join("&");
  const url = `${BASE_URL}${path}${qs ? "?" + qs : ""}`;
  const req = new Request(url);
  req.method = "GET";
  return req.loadJSON();
}

async function apiPost(path, body) {
  const req = new Request(`${BASE_URL}${path}`);
  req.method = "POST";
  req.headers = { "Content-Type": "application/json" };
  req.body = JSON.stringify(body);
  return req.loadJSON();
}

function hookUrl(item) {
  // Generate hook:// URL for Hookmark PAL
  if (item.hook_url) return item.hook_url;
  if (item.kind === "file" && item.path) {
    return "hook://file/" + encodeURIComponent(item.path);
  }
  return item.url || "";
}

async function openInHookmarkPal(item) {
  const url = hookUrl(item);
  if (!url) { await showAlert("No URL", "This item has no openable URL."); return; }
  Safari.open(url);
}

async function showAlert(title, msg) {
  const a = new Alert();
  a.title = title;
  a.message = msg;
  a.addAction("OK");
  await a.present();
}

// ── Main menu ─────────────────────────────────────────────────────────────────

async function mainMenu() {
  const alert = new Alert();
  alert.title = "⛓ HookVault";
  alert.addAction("🔍 Search");
  alert.addAction("🕐 Recent");
  alert.addAction("📎 Add from Clipboard");
  alert.addAction("📊 Stats");
  alert.addCancelAction("Cancel");
  const choice = await alert.present();

  if (choice === 0) await searchMenu();
  else if (choice === 1) await recentMenu();
  else if (choice === 2) await addFromClipboard();
  else if (choice === 3) await showStats();
}

// ── Search ────────────────────────────────────────────────────────────────────

async function searchMenu() {
  const alert = new Alert();
  alert.title = "Search HookVault";
  alert.addTextField("Title, path, or URL…");
  alert.addAction("Search");
  alert.addCancelAction("Cancel");
  if (await alert.present() !== 0) return;

  const q = alert.textFieldValue(0).trim();
  const results = await apiGet("/shortcut/search", { q, limit: 30 });
  await showItemList(results, `Results for "${q}"`);
}

// ── Recent ────────────────────────────────────────────────────────────────────

async function recentMenu() {
  const results = await apiGet("/shortcut/recent", { limit: 20 });
  await showItemList(results, "Recent Items");
}

// ── Item list ─────────────────────────────────────────────────────────────────

async function showItemList(items, title) {
  if (!items || items.length === 0) {
    await showAlert(title, "No items found."); return;
  }
  const table = new UITable();
  table.showSeparators = true;

  for (const item of items) {
    const row = new UITableRow();
    row.height = 60;
    const nameCell = row.addText(item.title || item.url || item.hook_id,
                                  (item.tags || []).join(", ") || item.kind);
    nameCell.widthWeight = 85;
    const kindCell = row.addText(item.kind);
    kindCell.widthWeight = 15;
    kindCell.rightAligned();

    row.onSelect = async () => {
      await itemMenu(item);
    };
    table.addRow(row);
  }
  await table.present();
}

// ── Item actions ──────────────────────────────────────────────────────────────

async function itemMenu(item) {
  const alert = new Alert();
  alert.title = item.title || item.hook_id;
  alert.message = item.url || item.path || "";
  alert.addAction("Open in Hookmark PAL");
  alert.addAction("Open URL");
  alert.addAction("Copy hook:// URL");
  alert.addAction("View Links");
  alert.addCancelAction("Back");
  const choice = await alert.present();

  if (choice === 0) await openInHookmarkPal(item);
  else if (choice === 1 && item.url) Safari.open(item.url);
  else if (choice === 2) {
    Pasteboard.copyString(hookUrl(item));
    await showAlert("Copied", hookUrl(item));
  }
  else if (choice === 3) await viewLinks(item.hook_id);
}

async function viewLinks(hookId) {
  const data = await apiGet(`/links/${hookId}`);
  const all = [...(data.outgoing || []), ...(data.incoming || [])];
  if (all.length === 0) { await showAlert("Links", "No links yet."); return; }
  const names = all.map(l => `${l.title || l.hook_id} [${l.kind}]`).join("\n");
  await showAlert("Links", names);
}

// ── Add from clipboard ────────────────────────────────────────────────────────

async function addFromClipboard() {
  const url = Pasteboard.pasteString();
  if (!url || !url.startsWith("http")) {
    await showAlert("Nothing to add", "Copy a URL first, then run this."); return;
  }
  const titleAlert = new Alert();
  titleAlert.title = "Add URL";
  titleAlert.message = url;
  titleAlert.addTextField("Title (optional)");
  titleAlert.addTextField("Tags (comma-separated)");
  titleAlert.addAction("Save");
  titleAlert.addCancelAction("Cancel");
  if (await titleAlert.present() !== 0) return;

  const title = titleAlert.textFieldValue(0).trim() || url;
  const tags  = titleAlert.textFieldValue(1).trim();

  const result = await apiGet("/shortcut/add-url", { url, title, tags });
  await showAlert("Saved", `${result.hook_id}\n${title}`);
}

// ── Stats ─────────────────────────────────────────────────────────────────────

async function showStats() {
  const s = await apiGet("/stats");
  const by_kind = Object.entries(s.by_kind || {})
    .map(([k, n]) => `  ${k}: ${n}`).join("\n");
  await showAlert("HookVault Stats",
    `Items: ${s.items}\nLinks: ${s.links}\n\nBy kind:\n${by_kind}`);
}

// ── Entry point ───────────────────────────────────────────────────────────────

// Support Share Sheet: if args has a URL, add it directly
if (args.urls && args.urls.length > 0) {
  const url = args.urls[0].toString();
  const result = await apiPost("/shortcut/add-url", {});
  // Use GET form since it accepts query params
  const req = new Request(`${BASE_URL}/shortcut/add-url?url=${encodeURIComponent(url)}&title=${encodeURIComponent(url)}`);
  req.method = "POST";
  const data = await req.loadJSON();
  Script.setShortcutOutput(data.hook_id || "saved");
  Script.complete();
} else {
  await mainMenu();
  Script.complete();
}
