#!/usr/bin/env python3
"""
HookVault — server-side Hookmark replacement
Bidirectional linking between files, URLs, notes, and any URI.
Runs as a FastAPI REST service. CLI included at bottom.

Integrations:
  - Raindrop.io: push URL items to Raindrop; import Raindrop collections
  - Hookmark PAL (iOS): hook:// URL generation, Apple Shortcuts-compatible JSON
  - iOS Scriptable: machine-readable JSON endpoints for automation scripts

Usage (server):
    uvicorn hookvault:app --host 0.0.0.0 --port 8080

Usage (CLI):
    python hookvault.py add-file /data/docs/report.pdf --tags "project,q3"
    python hookvault.py link hook:abc123 hook:def456
    python hookvault.py show hook:abc123
    python hookvault.py search --tag project
    python hookvault.py raindrop-import --collection-id 0

Environment variables:
    HV_DB              Path to SQLite database (default: /data/hookvault/vault.db)
    HV_BASE_URL        Public base URL for hook:// links
    HV_PORT            Server port (default: 8080)
    RAINDROP_TOKEN     Raindrop.io API Bearer token (for sync features)
    RAINDROP_AUTO_PUSH Set to "1" to auto-push URL items to Raindrop on creation
"""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import sys
import uuid
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from urllib.parse import quote

import click
import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

# ─── Config ──────────────────────────────────────────────────────────────────

DB_PATH         = Path(os.environ.get("HV_DB",   "/data/hookvault/vault.db"))
BASE_URL        = os.environ.get("HV_BASE_URL",  "https://admin.shannonjlove.cloud/hooks")
PORT            = int(os.environ.get("HV_PORT",  "8080"))
RAINDROP_TOKEN  = os.environ.get("RAINDROP_TOKEN", "")
RAINDROP_AUTO   = os.environ.get("RAINDROP_AUTO_PUSH", "0") == "1"

RAINDROP_API    = "https://api.raindrop.io/rest/v1"

# ─── Database ────────────────────────────────────────────────────────────────

@contextmanager
def db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS items (
                id          TEXT PRIMARY KEY,
                hook_id     TEXT UNIQUE NOT NULL,
                kind        TEXT NOT NULL,          -- file | url | note | email | arbitrary
                path        TEXT,
                url         TEXT,
                title       TEXT NOT NULL,
                content_hash TEXT,
                tags        TEXT DEFAULT '[]',      -- JSON array
                meta        TEXT DEFAULT '{}',      -- JSON object
                created_at  TEXT NOT NULL,
                updated_at  TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS links (
                id          TEXT PRIMARY KEY,
                src_hook    TEXT NOT NULL,
                dst_hook    TEXT NOT NULL,
                kind        TEXT DEFAULT 'reference',
                note        TEXT,
                created_at  TEXT NOT NULL,
                FOREIGN KEY (src_hook) REFERENCES items(hook_id),
                FOREIGN KEY (dst_hook) REFERENCES items(hook_id),
                UNIQUE (src_hook, dst_hook)
            );

            CREATE INDEX IF NOT EXISTS idx_hook_id   ON items(hook_id);
            CREATE INDEX IF NOT EXISTS idx_links_src ON links(src_hook);
            CREATE INDEX IF NOT EXISTS idx_links_dst ON links(dst_hook);
        """)


# ─── Raindrop.io client ──────────────────────────────────────────────────────

def _raindrop_headers() -> dict:
    if not RAINDROP_TOKEN:
        raise HTTPException(503, "RAINDROP_TOKEN not configured")
    return {"Authorization": f"Bearer {RAINDROP_TOKEN}",
            "Content-Type": "application/json"}


def raindrop_create(url: str, title: str, tags: list,
                    note: str = "", collection_id: int = 0) -> dict:
    """Push a URL bookmark to Raindrop.io. Returns the created raindrop object."""
    import requests
    payload = {
        "link":       url,
        "title":      title,
        "excerpt":    note,
        "tags":       tags,
        "collection": {"$id": collection_id},
        "pleaseParse": {},  # ask Raindrop to auto-fetch metadata
    }
    r = requests.post(f"{RAINDROP_API}/raindrop",
                      headers=_raindrop_headers(), json=payload, timeout=15)
    r.raise_for_status()
    return r.json().get("item", {})


def raindrop_update(raindrop_id: int, title: str, tags: list, note: str = "") -> dict:
    import requests
    payload = {"title": title, "tags": tags, "excerpt": note}
    r = requests.put(f"{RAINDROP_API}/raindrop/{raindrop_id}",
                     headers=_raindrop_headers(), json=payload, timeout=15)
    r.raise_for_status()
    return r.json().get("item", {})


def raindrop_search(search: str = "", collection_id: int = 0,
                    tags: Optional[list] = None, page: int = 0) -> list:
    import requests
    params: dict = {"search": search, "page": page, "perpage": 50}
    if tags:
        params["search"] = " ".join(f"#{t}" for t in tags) + f" {search}".strip()
    r = requests.get(f"{RAINDROP_API}/raindrops/{collection_id}",
                     headers=_raindrop_headers(), params=params, timeout=15)
    r.raise_for_status()
    return r.json().get("items", [])


def raindrop_get_collections() -> list:
    import requests
    r = requests.get(f"{RAINDROP_API}/collections",
                     headers=_raindrop_headers(), timeout=15)
    r.raise_for_status()
    return r.json().get("items", [])


# ─── hook:// URL helpers ──────────────────────────────────────────────────────

def make_hook_url(item: dict) -> str:
    """
    Generate a hook:// URL for use with Hookmark PAL on iOS/Mac.
    Files get hook://file/<encoded-path>, URLs pass through directly,
    notes get a hookmark.net universal link.
    """
    kind = item.get("kind", "")
    path = item.get("path")
    url  = item.get("url")

    if kind == "file" and path:
        encoded = quote(path, safe="")
        return f"hook://file/{encoded}"
    if url:
        return url
    # Fallback: HookVault resolve URL (readable by Shortcuts/Scriptable)
    hook_id = item.get("hook_id", "")
    return f"{BASE_URL}/items/{hook_id}"


# ─── Core helpers ─────────────────────────────────────────────────────────────

def make_hook_id(seed: str) -> str:
    """Deterministic, stable hook ID derived from file path or URL."""
    digest = hashlib.sha256(seed.encode()).hexdigest()[:16]
    return f"hook:{digest}"


def file_hash(path: Path) -> Optional[str]:
    if not path.exists() or not path.is_file():
        return None
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def row_to_dict(row) -> dict:
    d = dict(row)
    for key in ("tags", "meta"):
        if d.get(key):
            try:
                d[key] = json.loads(d[key])
            except Exception:
                pass
    return d


def enrich(item: dict) -> dict:
    """Add resolved links to an item dict."""
    with db() as conn:
        out_rows = conn.execute("""
            SELECT l.*, i.title, i.path, i.url, i.kind
            FROM links l JOIN items i ON l.dst_hook = i.hook_id
            WHERE l.src_hook = ?
        """, (item["hook_id"],)).fetchall()

        in_rows = conn.execute("""
            SELECT l.*, i.title, i.path, i.url, i.kind
            FROM links l JOIN items i ON l.src_hook = i.hook_id
            WHERE l.dst_hook = ?
        """, (item["hook_id"],)).fetchall()

    item["links_out"] = [row_to_dict(r) for r in out_rows]
    item["links_in"]  = [row_to_dict(r) for r in in_rows]
    return item


# ─── FastAPI app ──────────────────────────────────────────────────────────────

app = FastAPI(title="HookVault", version="1.0.0",
              description="Bidirectional file/URL linking — server-side Hookmark")

app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["*"], allow_headers=["*"])


@app.on_event("startup")
async def startup():
    init_db()


# ── Schemas ──────────────────────────────────────────────────────────────────

class ItemIn(BaseModel):
    kind:  str             # file | url | note | email | arbitrary
    path:  Optional[str] = None
    url:   Optional[str] = None
    title: str
    tags:  List[str] = []
    meta:  dict      = {}


class LinkIn(BaseModel):
    src_hook: str
    dst_hook: str
    kind:     str           = "reference"
    note:     Optional[str] = None


class ItemPatch(BaseModel):
    title: Optional[str]      = None
    tags:  Optional[List[str]]= None
    meta:  Optional[dict]     = None


class RaindropImportIn(BaseModel):
    collection_id: int      = 0     # 0 = Unsorted, -1 = All
    tags_filter:   List[str] = []
    overwrite:     bool      = False  # update existing items if hook_id matches


# ── Items ────────────────────────────────────────────────────────────────────

@app.post("/items", status_code=201)
async def create_item(body: ItemIn):
    seed    = body.path or body.url or body.title
    hook_id = make_hook_id(seed)
    now     = datetime.utcnow().isoformat()
    item_id = str(uuid.uuid4())
    chash   = file_hash(Path(body.path)) if body.path else None

    # Merge raindrop_id from meta if provided externally
    meta = dict(body.meta)

    with db() as conn:
        existing = conn.execute(
            "SELECT * FROM items WHERE hook_id = ?", (hook_id,)
        ).fetchone()
        if existing:
            return row_to_dict(existing)

        conn.execute("""
            INSERT INTO items
              (id, hook_id, kind, path, url, title, content_hash, tags, meta, created_at, updated_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """, (
            item_id, hook_id, body.kind, body.path, body.url, body.title,
            chash, json.dumps(body.tags), json.dumps(meta), now, now,
        ))

    with db() as conn:
        row = conn.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
    item = row_to_dict(row)

    # Auto-push URL items to Raindrop.io if configured
    if RAINDROP_AUTO and RAINDROP_TOKEN and body.kind == "url" and body.url:
        try:
            rd = raindrop_create(body.url, body.title, body.tags)
            # Store raindrop_id in meta for future sync
            new_meta = {**meta, "raindrop_id": rd.get("_id")}
            with db() as conn:
                conn.execute(
                    "UPDATE items SET meta=? WHERE hook_id=?",
                    (json.dumps(new_meta), hook_id),
                )
            item["meta"] = new_meta
        except Exception:
            pass  # Non-fatal: Raindrop push failure doesn't block item creation

    return item


@app.get("/items/{hook_id}")
async def get_item(hook_id: str):
    with db() as conn:
        row = conn.execute("SELECT * FROM items WHERE hook_id = ?", (hook_id,)).fetchone()
    if not row:
        raise HTTPException(404, "Item not found")
    return enrich(row_to_dict(row))


@app.patch("/items/{hook_id}")
async def patch_item(hook_id: str, body: ItemPatch):
    now = datetime.utcnow().isoformat()
    sets, params = [], []
    if body.title is not None:
        sets.append("title = ?"); params.append(body.title)
    if body.tags is not None:
        sets.append("tags = ?");  params.append(json.dumps(body.tags))
    if body.meta is not None:
        sets.append("meta = ?");  params.append(json.dumps(body.meta))
    if not sets:
        raise HTTPException(400, "Nothing to update")
    sets.append("updated_at = ?"); params.append(now)
    params.append(hook_id)
    with db() as conn:
        conn.execute(f"UPDATE items SET {', '.join(sets)} WHERE hook_id = ?", params)
        row = conn.execute("SELECT * FROM items WHERE hook_id = ?", (hook_id,)).fetchone()
    if not row:
        raise HTTPException(404, "Item not found")
    return row_to_dict(row)


@app.delete("/items/{hook_id}", status_code=204)
async def delete_item(hook_id: str):
    with db() as conn:
        conn.execute("DELETE FROM links WHERE src_hook=? OR dst_hook=?", (hook_id, hook_id))
        conn.execute("DELETE FROM items WHERE hook_id=?", (hook_id,))


@app.get("/items")
async def list_items(
    tag:  Optional[str] = Query(None),
    kind: Optional[str] = Query(None),
    q:    Optional[str] = Query(None),
    limit: int          = Query(100, le=500),
    offset: int         = Query(0),
):
    sql, params = "SELECT * FROM items WHERE 1=1", []
    if tag:
        sql += ' AND tags LIKE ?'; params.append(f'%"{tag}"%')
    if kind:
        sql += ' AND kind = ?'; params.append(kind)
    if q:
        sql += ' AND (title LIKE ? OR path LIKE ? OR url LIKE ?)'
        params.extend([f"%{q}%", f"%{q}%", f"%{q}%"])
    sql += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    with db() as conn:
        rows = conn.execute(sql, params).fetchall()
    return [row_to_dict(r) for r in rows]


# ── Links ────────────────────────────────────────────────────────────────────

@app.post("/links", status_code=201)
async def create_link(body: LinkIn):
    now = datetime.utcnow().isoformat()
    with db() as conn:
        # Verify both ends exist
        for hook_id in (body.src_hook, body.dst_hook):
            if not conn.execute("SELECT 1 FROM items WHERE hook_id=?", (hook_id,)).fetchone():
                raise HTTPException(404, f"Item not found: {hook_id}")
        link_id = str(uuid.uuid4())
        try:
            conn.execute("""
                INSERT INTO links (id, src_hook, dst_hook, kind, note, created_at)
                VALUES (?,?,?,?,?,?)
            """, (link_id, body.src_hook, body.dst_hook, body.kind, body.note, now))
            # Create reverse link — bidirectional like Hookmark
            conn.execute("""
                INSERT OR IGNORE INTO links (id, src_hook, dst_hook, kind, note, created_at)
                VALUES (?,?,?,?,?,?)
            """, (
                str(uuid.uuid4()), body.dst_hook, body.src_hook,
                body.kind, f"↩ {body.note or ''}", now,
            ))
        except sqlite3.IntegrityError:
            raise HTTPException(409, "Link already exists")
    return {"id": link_id, "src": body.src_hook, "dst": body.dst_hook, "kind": body.kind}


@app.delete("/links/{src_hook}/{dst_hook}", status_code=204)
async def delete_link(src_hook: str, dst_hook: str):
    with db() as conn:
        conn.execute(
            "DELETE FROM links WHERE (src_hook=? AND dst_hook=?) OR (src_hook=? AND dst_hook=?)",
            (src_hook, dst_hook, dst_hook, src_hook),
        )


@app.get("/links/{hook_id}")
async def item_links(hook_id: str):
    with db() as conn:
        out = conn.execute("""
            SELECT l.*, i.title, i.path, i.url, i.kind AS item_kind
            FROM links l JOIN items i ON l.dst_hook = i.hook_id
            WHERE l.src_hook = ?
        """, (hook_id,)).fetchall()
        inc = conn.execute("""
            SELECT l.*, i.title, i.path, i.url, i.kind AS item_kind
            FROM links l JOIN items i ON l.src_hook = i.hook_id
            WHERE l.dst_hook = ?
        """, (hook_id,)).fetchall()
    return {"outgoing": [dict(r) for r in out], "incoming": [dict(r) for r in inc]}


# ── Utility ──────────────────────────────────────────────────────────────────

@app.get("/resolve")
async def resolve(path: Optional[str] = None, url: Optional[str] = None):
    """Get item by file path or URL without knowing hook_id."""
    seed = path or url
    if not seed:
        raise HTTPException(400, "Provide path or url")
    hook_id = make_hook_id(seed)
    with db() as conn:
        row = conn.execute("SELECT * FROM items WHERE hook_id=?", (hook_id,)).fetchone()
    if not row:
        raise HTTPException(404, "Not registered")
    return enrich(row_to_dict(row))


@app.get("/stats")
async def stats():
    with db() as conn:
        n_items = conn.execute("SELECT COUNT(*) FROM items").fetchone()[0]
        n_links = conn.execute("SELECT COUNT(*) FROM links").fetchone()[0]
        kinds   = conn.execute(
            "SELECT kind, COUNT(*) as n FROM items GROUP BY kind"
        ).fetchall()
    return {"items": n_items, "links": n_links,
            "by_kind": {r["kind"]: r["n"] for r in kinds}}


# ── Raindrop.io Integration ───────────────────────────────────────────────────

@app.post("/sync/raindrop/push/{hook_id}", status_code=200)
async def push_to_raindrop(hook_id: str, collection_id: int = 0):
    """Push a single HookVault URL item to Raindrop.io."""
    with db() as conn:
        row = conn.execute("SELECT * FROM items WHERE hook_id=?", (hook_id,)).fetchone()
    if not row:
        raise HTTPException(404, "Item not found")
    item = row_to_dict(row)
    if item["kind"] != "url" or not item.get("url"):
        raise HTTPException(400, "Only URL items can be pushed to Raindrop")

    meta = item.get("meta") or {}
    existing_id = meta.get("raindrop_id")

    try:
        if existing_id:
            rd = raindrop_update(existing_id, item["title"], item.get("tags") or [])
        else:
            rd = raindrop_create(
                item["url"], item["title"], item.get("tags") or [],
                collection_id=collection_id,
            )
            new_meta = {**meta, "raindrop_id": rd.get("_id")}
            with db() as conn:
                conn.execute("UPDATE items SET meta=? WHERE hook_id=?",
                             (json.dumps(new_meta), hook_id))
    except Exception as e:
        raise HTTPException(502, f"Raindrop API error: {e}")

    return {"hook_id": hook_id, "raindrop_id": rd.get("_id"), "action": "updated" if existing_id else "created"}


@app.post("/sync/raindrop/import")
async def import_from_raindrop(body: RaindropImportIn):
    """
    Pull bookmarks from a Raindrop.io collection and register them as HookVault items.
    Returns counts of created vs. skipped items.
    """
    try:
        raindrops = raindrop_search(
            collection_id=body.collection_id,
            tags=body.tags_filter or None,
        )
    except Exception as e:
        raise HTTPException(502, f"Raindrop API error: {e}")

    created = skipped = 0
    now = datetime.utcnow().isoformat()

    for rd in raindrops:
        url   = rd.get("link", "")
        title = rd.get("title", url)
        tags  = rd.get("tags", [])
        rd_id = rd.get("_id")

        if not url:
            continue

        hook_id = make_hook_id(url)
        with db() as conn:
            existing = conn.execute(
                "SELECT hook_id FROM items WHERE hook_id=?", (hook_id,)
            ).fetchone()
            if existing and not body.overwrite:
                skipped += 1
                continue

            meta = json.dumps({"raindrop_id": rd_id,
                               "excerpt": rd.get("excerpt", ""),
                               "domain":  rd.get("domain", "")})
            if existing:
                conn.execute(
                    "UPDATE items SET title=?,tags=?,meta=?,updated_at=? WHERE hook_id=?",
                    (title, json.dumps(tags), meta, now, hook_id),
                )
            else:
                conn.execute("""
                    INSERT INTO items
                      (id,hook_id,kind,path,url,title,content_hash,tags,meta,created_at,updated_at)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?)
                """, (str(uuid.uuid4()), hook_id, "url", None, url,
                      title, None, json.dumps(tags), meta, now, now))
            created += 1

    return {"imported": created, "skipped": skipped,
            "collection_id": body.collection_id}


@app.get("/sync/raindrop/collections")
async def list_raindrop_collections():
    """List all Raindrop.io collections."""
    try:
        cols = raindrop_get_collections()
    except Exception as e:
        raise HTTPException(502, f"Raindrop API error: {e}")
    return [{"id": c.get("_id"), "title": c.get("title"),
             "count": c.get("count", 0)} for c in cols]


# ── iOS / Hookmark PAL / Apple Shortcuts ──────────────────────────────────────

@app.get("/hook-url/{hook_id}")
async def get_hook_url(hook_id: str):
    """
    Return the hook:// URL for this item — for use with Hookmark PAL on iOS/Mac.
    Files return hook://file/<encoded-posix-path>.
    URLs return the URL directly.
    """
    with db() as conn:
        row = conn.execute("SELECT * FROM items WHERE hook_id=?", (hook_id,)).fetchone()
    if not row:
        raise HTTPException(404, "Item not found")
    item = row_to_dict(row)
    return {"hook_id": hook_id, "hook_url": make_hook_url(item), "title": item["title"]}


@app.get("/shortcut/recent")
async def shortcut_recent(limit: int = 20):
    """
    iOS Shortcuts / Scriptable compatible endpoint.
    Returns a flat list of recent items — designed for use in Shortcuts
    'Get Contents of URL' actions and Scriptable scripts.
    Each item includes hook_url for direct Hookmark PAL handoff.
    """
    with db() as conn:
        rows = conn.execute(
            "SELECT * FROM items ORDER BY updated_at DESC LIMIT ?", (limit,)
        ).fetchall()
    return [
        {
            "hook_id":  r["hook_id"],
            "title":    r["title"],
            "kind":     r["kind"],
            "url":      r["url"],
            "path":     r["path"],
            "tags":     json.loads(r["tags"] or "[]"),
            "hook_url": make_hook_url(dict(r)),
            "updated":  r["updated_at"],
        }
        for r in rows
    ]


@app.get("/shortcut/search")
async def shortcut_search(q: str = "", tag: str = "", kind: str = "", limit: int = 50):
    """
    iOS Shortcuts / Scriptable search — returns hook_url in every result.
    Call from Shortcuts 'Get Contents of URL' with query parameters.
    """
    sql, params = "SELECT * FROM items WHERE 1=1", []
    if q:
        sql += " AND (title LIKE ? OR path LIKE ? OR url LIKE ?)"
        params.extend([f"%{q}%", f"%{q}%", f"%{q}%"])
    if tag:
        sql += ' AND tags LIKE ?'
        params.append(f'%"{tag}"%')
    if kind:
        sql += " AND kind = ?"
        params.append(kind)
    sql += " ORDER BY updated_at DESC LIMIT ?"
    params.append(limit)
    with db() as conn:
        rows = conn.execute(sql, params).fetchall()
    return [
        {
            "hook_id":  r["hook_id"],
            "title":    r["title"],
            "kind":     r["kind"],
            "url":      r["url"],
            "path":     r["path"],
            "tags":     json.loads(r["tags"] or "[]"),
            "hook_url": make_hook_url(dict(r)),
        }
        for r in rows
    ]


@app.post("/shortcut/add-url")
async def shortcut_add_url(url: str, title: str = "", tags: str = ""):
    """
    iOS Shortcuts / Scriptable quick-add endpoint.
    Accepts flat query parameters (no JSON body) for easy Shortcuts integration.
    Push to Raindrop.io automatically if RAINDROP_AUTO_PUSH=1.
    """
    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []
    effective_title = title or url
    body = ItemIn(kind="url", url=url, title=effective_title, tags=tag_list)
    return await create_item(body)


# ── Web UI (minimal) ─────────────────────────────────────────────────────────

@app.get("/ui", response_class=HTMLResponse)
async def web_ui():
    return """<!DOCTYPE html>
<html><head><meta charset=UTF-8><title>HookVault</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font:14px/1.5 'JetBrains Mono',monospace;background:#0d1117;color:#e6edf3}
header{padding:1rem 2rem;background:#161b22;border-bottom:1px solid #30363d}
header h1{color:#58a6ff;font-size:1.1rem}
.wrap{padding:2rem;max-width:900px}
input,textarea{width:100%;background:#161b22;color:#e6edf3;border:1px solid #30363d;
  padding:.5rem;border-radius:4px;font-family:monospace}
input:focus,textarea:focus{outline:none;border-color:#58a6ff}
button{background:#238636;color:#fff;border:none;padding:.5rem 1.2rem;
  border-radius:4px;cursor:pointer;margin-top:.5rem}
button:hover{background:#2ea043}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-top:1rem}
.card{background:#161b22;border:1px solid #30363d;border-radius:6px;padding:1rem}
.tag{display:inline-block;background:#1a4429;color:#3fb950;
  border-radius:10px;padding:.1rem .5rem;font-size:.75rem;margin:.1rem}
.hook-id{color:#8b949e;font-size:.75rem;font-family:monospace}
.link-arrow{color:#e3b341}
h3{font-size:.9rem;color:#58a6ff;margin-bottom:.5rem}
.row{display:flex;gap:.5rem;align-items:center;margin-bottom:.5rem}
label{color:#8b949e;font-size:.8rem;min-width:80px}
</style></head><body>
<header><h1>⛓ HookVault</h1></header>
<div class=wrap>
  <div class=grid>
    <div class=card>
      <h3>Register Item</h3>
      <div class=row><label>Kind</label>
        <select id=kind style="background:#161b22;color:#e6edf3;border:1px solid #30363d;padding:.4rem;border-radius:4px">
          <option>file</option><option>url</option><option>note</option><option>email</option>
        </select></div>
      <div class=row><label>Title</label><input id=title placeholder="Title"></div>
      <div class=row><label>Path/URL</label><input id=path placeholder="/data/... or https://..."></div>
      <div class=row><label>Tags</label><input id=tags placeholder="tag1,tag2"></div>
      <button onclick=addItem()>Register</button>
    </div>
    <div class=card>
      <h3>Search</h3>
      <input id=q placeholder="Search title, path, URL...">
      <input id=stag placeholder="Filter by tag" style="margin-top:.5rem">
      <button onclick=search()>Search</button>
    </div>
  </div>
  <div id=results style="margin-top:1.5rem"></div>
</div>
<script>
async function addItem(){
  const kind=document.getElementById('kind').value;
  const title=document.getElementById('title').value;
  const pv=document.getElementById('path').value;
  const tags=document.getElementById('tags').value.split(',').map(t=>t.trim()).filter(Boolean);
  const body={kind,title,tags};
  if(kind==='file') body.path=pv; else body.url=pv;
  const r=await fetch('/items',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
  const d=await r.json();
  alert('Registered: '+d.hook_id);
  search();
}
async function search(){
  const q=document.getElementById('q').value;
  const tag=document.getElementById('stag').value;
  let url='/items?limit=50';
  if(q) url+='&q='+encodeURIComponent(q);
  if(tag) url+='&tag='+encodeURIComponent(tag);
  const r=await fetch(url);
  const items=await r.json();
  const div=document.getElementById('results');
  div.innerHTML=items.map(i=>`
    <div class=card style="margin-bottom:.5rem">
      <div style="display:flex;justify-content:space-between">
        <strong>${esc(i.title)}</strong>
        <span class=hook-id>${esc(i.hook_id)}</span>
      </div>
      <div style="color:#8b949e;font-size:.8rem">${esc(i.path||i.url||'')}</div>
      <div>${(i.tags||[]).map(t=>'<span class=tag>'+esc(t)+'</span>').join('')}</div>
      <button onclick="showLinks('${i.hook_id}')" style="margin-top:.3rem;background:#21262d;font-size:.75rem">Links</button>
    </div>`).join('');
}
async function showLinks(hookId){
  const r=await fetch('/links/'+hookId);
  const d=await r.json();
  const all=[...d.outgoing,...d.incoming];
  alert(all.length ? all.map(l=>l.title+' ('+l.kind+')').join('\n') : 'No links yet');
}
function esc(s){return (s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;')}
search();
</script></body></html>"""


# ─── CLI (click) ──────────────────────────────────────────────────────────────

@click.group()
def cli():
    """HookVault CLI — manage hooks from the command line"""
    init_db()


@cli.command("add-file")
@click.argument("path")
@click.option("--title", default=None)
@click.option("--tags",  default="", help="Comma-separated tags")
def add_file(path, title, tags):
    """Register a file and get its hook ID."""
    p     = Path(path).resolve()
    title = title or p.name
    tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    hook_id = make_hook_id(str(p))
    now = datetime.utcnow().isoformat()
    with db() as conn:
        existing = conn.execute("SELECT hook_id FROM items WHERE hook_id=?", (hook_id,)).fetchone()
        if existing:
            click.echo(f"Already registered: {hook_id}")
            return
        conn.execute("""
            INSERT INTO items (id, hook_id, kind, path, url, title, content_hash, tags, meta, created_at, updated_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """, (str(uuid.uuid4()), hook_id, "file", str(p), None, title,
              file_hash(p), json.dumps(tag_list), "{}", now, now))
    click.echo(f"Registered: {hook_id}  ({title})")


@cli.command("add-url")
@click.argument("url")
@click.option("--title", required=True)
@click.option("--tags",  default="")
def add_url(url, title, tags):
    """Register a URL."""
    tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    hook_id = make_hook_id(url)
    now = datetime.utcnow().isoformat()
    with db() as conn:
        existing = conn.execute("SELECT hook_id FROM items WHERE hook_id=?", (hook_id,)).fetchone()
        if existing:
            click.echo(f"Already registered: {hook_id}"); return
        conn.execute("""
            INSERT INTO items (id, hook_id, kind, path, url, title, content_hash, tags, meta, created_at, updated_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """, (str(uuid.uuid4()), hook_id, "url", None, url, title,
              None, json.dumps(tag_list), "{}", now, now))
    click.echo(f"Registered: {hook_id}  ({title})")


@cli.command("link")
@click.argument("src_hook")
@click.argument("dst_hook")
@click.option("--note", default=None)
@click.option("--kind", default="reference")
def link(src_hook, dst_hook, note, kind):
    """Create a bidirectional link between two hook IDs."""
    now = datetime.utcnow().isoformat()
    link_id = str(uuid.uuid4())
    with db() as conn:
        for h in (src_hook, dst_hook):
            if not conn.execute("SELECT 1 FROM items WHERE hook_id=?", (h,)).fetchone():
                click.echo(f"ERROR: not found: {h}"); return
        try:
            conn.execute("""
                INSERT INTO links (id, src_hook, dst_hook, kind, note, created_at)
                VALUES (?,?,?,?,?,?)
            """, (link_id, src_hook, dst_hook, kind, note, now))
            conn.execute("""
                INSERT OR IGNORE INTO links (id, src_hook, dst_hook, kind, note, created_at)
                VALUES (?,?,?,?,?,?)
            """, (str(uuid.uuid4()), dst_hook, src_hook, kind, f"↩ {note or ''}", now))
        except sqlite3.IntegrityError:
            click.echo("Link already exists"); return
    click.echo(f"Linked: {src_hook} ↔ {dst_hook}")


@cli.command("show")
@click.argument("hook_id")
def show(hook_id):
    """Show an item and its links."""
    with db() as conn:
        row = conn.execute("SELECT * FROM items WHERE hook_id=?", (hook_id,)).fetchone()
        if not row:
            click.echo("Not found"); return
        item = row_to_dict(row)
        item = enrich(item)
    click.echo(f"\n{item['title']}")
    click.echo(f"  hook_id : {item['hook_id']}")
    click.echo(f"  kind    : {item['kind']}")
    click.echo(f"  path    : {item.get('path') or '—'}")
    click.echo(f"  url     : {item.get('url') or '—'}")
    click.echo(f"  tags    : {', '.join(item.get('tags') or []) or '—'}")
    click.echo(f"  created : {item['created_at']}")
    if item["links_out"]:
        click.echo("\n  Links →")
        for l in item["links_out"]:
            click.echo(f"    {l['dst_hook']}  {l['title']}  [{l['kind']}]")
    if item["links_in"]:
        click.echo("\n  ← Linked from")
        for l in item["links_in"]:
            click.echo(f"    {l['src_hook']}  {l['title']}  [{l['kind']}]")


@cli.command("search")
@click.option("--q",   default=None)
@click.option("--tag", default=None)
@click.option("--kind", default=None)
def search(q, tag, kind):
    """Search items."""
    sql, params = "SELECT * FROM items WHERE 1=1", []
    if q:
        sql += " AND (title LIKE ? OR path LIKE ? OR url LIKE ?)"
        params.extend([f"%{q}%", f"%{q}%", f"%{q}%"])
    if tag:
        sql += ' AND tags LIKE ?'; params.append(f'%"{tag}"%')
    if kind:
        sql += ' AND kind = ?'; params.append(kind)
    sql += " ORDER BY created_at DESC LIMIT 50"
    with db() as conn:
        rows = conn.execute(sql, params).fetchall()
    for r in rows:
        item = row_to_dict(r)
        tags_str = ",".join(item.get("tags") or [])
        click.echo(f"{item['hook_id']}  {item['title']:<50}  [{item['kind']}]  {tags_str}")


@cli.command("raindrop-import")
@click.option("--collection-id", "-c", default=0, type=int,
              help="Raindrop collection ID (0=Unsorted, -1=All)")
@click.option("--tag", "-t", multiple=True, help="Filter by tag(s)")
@click.option("--overwrite", is_flag=True, help="Update existing items")
def raindrop_import_cmd(collection_id, tag, overwrite):
    """Import bookmarks from Raindrop.io into HookVault."""
    if not RAINDROP_TOKEN:
        click.echo("ERROR: RAINDROP_TOKEN not set"); return
    try:
        raindrops = raindrop_search(collection_id=collection_id,
                                   tags=list(tag) or None)
    except Exception as e:
        click.echo(f"Raindrop API error: {e}"); return

    now = datetime.utcnow().isoformat()
    created = skipped = 0
    init_db()
    for rd in raindrops:
        url   = rd.get("link", "")
        title = rd.get("title", url)
        tags  = rd.get("tags", [])
        rd_id = rd.get("_id")
        if not url:
            continue
        hook_id = make_hook_id(url)
        meta_s = json.dumps({"raindrop_id": rd_id, "excerpt": rd.get("excerpt", ""),
                              "domain": rd.get("domain", "")})
        with db() as conn:
            existing = conn.execute(
                "SELECT hook_id FROM items WHERE hook_id=?", (hook_id,)
            ).fetchone()
            if existing and not overwrite:
                skipped += 1
                continue
            if existing:
                conn.execute(
                    "UPDATE items SET title=?,tags=?,meta=?,updated_at=? WHERE hook_id=?",
                    (title, json.dumps(tags), meta_s, now, hook_id),
                )
            else:
                conn.execute("""
                    INSERT INTO items
                      (id,hook_id,kind,path,url,title,content_hash,tags,meta,created_at,updated_at)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?)
                """, (str(uuid.uuid4()), hook_id, "url", None, url,
                      title, None, json.dumps(tags), meta_s, now, now))
            created += 1
    click.echo(f"Imported {created}, skipped {skipped}")


@cli.command("serve")
@click.option("--host", default="0.0.0.0")
@click.option("--port", default=PORT, type=int)
def serve(host, port):
    """Start the HookVault API server."""
    uvicorn.run("hookvault:app", host=host, port=port, reload=False)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] not in ("serve",):
        cli()
    else:
        uvicorn.run(app, host="0.0.0.0", port=PORT)
