#!/usr/bin/env python3
"""
BookStack Sync — push Markdown files to BookStack pages via REST API.
Designed to keep CLAUDE.md (and other docs) live-synced with a BookStack instance.

Usage:
    # Push a single file:
    python bookstack_sync.py push CLAUDE.md

    # Watch a file and push on every save:
    python bookstack_sync.py watch CLAUDE.md

    # Pull a page from BookStack and save locally:
    python bookstack_sync.py pull --page-id 42 --output CLAUDE.md

    # List all pages in a book:
    python bookstack_sync.py list-pages --book-id 1

Environment variables (required):
    BS_URL              BookStack base URL, e.g. https://docs.shannonjlove.cloud
    BS_TOKEN_ID         API token ID from your BookStack profile
    BS_TOKEN_SECRET     API token secret from your BookStack profile

Environment variables (optional):
    BS_PAGE_ID          Default page ID to push to (can override per-file via --page-id)
    BS_BOOK_ID          Default book ID (used when creating a new page)
    BS_CHAPTER_ID       Default chapter ID (alternative to book_id for page creation)
    FW_LOG              Log file path (default: /var/log/filewarden/bookstack_sync.log)
"""

from __future__ import annotations

import logging
import os
import sys
import time
from pathlib import Path
from typing import Optional

import click
import requests
import yaml  # pyyaml

# ─── Config ──────────────────────────────────────────────────────────────────

BS_URL      = os.environ.get("BS_URL", "").rstrip("/")
TOKEN_ID    = os.environ.get("BS_TOKEN_ID", "")
TOKEN_SEC   = os.environ.get("BS_TOKEN_SECRET", "")
PAGE_ID_ENV = os.environ.get("BS_PAGE_ID")
BOOK_ID_ENV = os.environ.get("BS_BOOK_ID")
CHAP_ID_ENV = os.environ.get("BS_CHAPTER_ID")

LOG_FILE = Path(os.environ.get("FW_LOG", "/var/log/filewarden/bookstack_sync.log"))

# ─── Logging ─────────────────────────────────────────────────────────────────

def setup_logging(verbose: bool = False):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    level = logging.DEBUG if verbose else logging.INFO
    handlers: list[logging.Handler] = [logging.StreamHandler()]
    try:
        handlers.append(logging.FileHandler(LOG_FILE))
    except OSError:
        pass
    logging.basicConfig(
        level=level,
        format="%(asctime)s  %(levelname)-7s  %(message)s",
        handlers=handlers,
    )

log = logging.getLogger("bookstack_sync")


# ─── BookStack client ─────────────────────────────────────────────────────────

class BookStackClient:
    def __init__(self, base_url: str, token_id: str, token_secret: str):
        if not base_url:
            raise ValueError("BS_URL is not set")
        if not token_id or not token_secret:
            raise ValueError("BS_TOKEN_ID and BS_TOKEN_SECRET must be set")
        self.base = base_url
        self.headers = {
            "Authorization": f"Token {token_id}:{token_secret}",
            "Content-Type": "application/json",
        }

    def _url(self, path: str) -> str:
        return f"{self.base}/api/{path.lstrip('/')}"

    def get_page(self, page_id: int) -> dict:
        r = requests.get(self._url(f"pages/{page_id}"), headers=self.headers, timeout=15)
        r.raise_for_status()
        return r.json()

    def update_page(self, page_id: int, name: str, markdown: str,
                    tags: Optional[list] = None) -> dict:
        payload: dict = {"name": name, "markdown": markdown}
        if tags:
            payload["tags"] = tags
        r = requests.put(
            self._url(f"pages/{page_id}"),
            headers=self.headers,
            json=payload,
            timeout=30,
        )
        r.raise_for_status()
        return r.json()

    def create_page(self, name: str, markdown: str,
                    book_id: Optional[int] = None,
                    chapter_id: Optional[int] = None,
                    tags: Optional[list] = None) -> dict:
        payload: dict = {"name": name, "markdown": markdown}
        if chapter_id:
            payload["chapter_id"] = chapter_id
        elif book_id:
            payload["book_id"] = book_id
        else:
            raise ValueError("Either book_id or chapter_id is required to create a page")
        if tags:
            payload["tags"] = tags
        r = requests.post(
            self._url("pages"),
            headers=self.headers,
            json=payload,
            timeout=30,
        )
        r.raise_for_status()
        return r.json()

    def list_pages(self, book_id: Optional[int] = None) -> list:
        params = {"count": 500}
        if book_id:
            params["filter[book_id]"] = book_id
        r = requests.get(self._url("pages"), headers=self.headers,
                         params=params, timeout=15)
        r.raise_for_status()
        return r.json().get("data", [])

    def export_markdown(self, page_id: int) -> str:
        r = requests.get(self._url(f"pages/{page_id}/export/markdown"),
                         headers=self.headers, timeout=15)
        r.raise_for_status()
        return r.text


# ─── Frontmatter helpers ──────────────────────────────────────────────────────

def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Split YAML frontmatter from Markdown body. Returns (meta, body)."""
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            try:
                meta = yaml.safe_load(parts[1]) or {}
                return meta, parts[2].lstrip("\n")
            except yaml.YAMLError:
                pass
    return {}, text


def inject_page_id(filepath: Path, page_id: int):
    """Write bookstack_page_id into the file's YAML frontmatter."""
    text = filepath.read_text()
    meta, body = parse_frontmatter(text)
    meta["bookstack_page_id"] = page_id
    fm = yaml.dump(meta, default_flow_style=False).strip()
    filepath.write_text(f"---\n{fm}\n---\n\n{body}")
    log.info("Wrote bookstack_page_id: %d into %s", page_id, filepath.name)


def get_page_id_from_file(filepath: Path) -> Optional[int]:
    """Read bookstack_page_id from YAML frontmatter if present."""
    text = filepath.read_text()
    meta, _ = parse_frontmatter(text)
    pid = meta.get("bookstack_page_id")
    return int(pid) if pid else None


# ─── Push logic ──────────────────────────────────────────────────────────────

def push_file(client: BookStackClient, filepath: Path,
              page_id: Optional[int], book_id: Optional[int],
              chapter_id: Optional[int], dry_run: bool) -> int:
    text = filepath.read_text()
    meta, body = parse_frontmatter(text)

    effective_page_id = page_id or get_page_id_from_file(filepath) or (
        int(PAGE_ID_ENV) if PAGE_ID_ENV else None
    )
    title = meta.get("title") or filepath.stem.replace("-", " ").replace("_", " ").title()
    tags = [{"name": k, "value": str(v)} for k, v in meta.items()
            if k not in ("title", "bookstack_page_id")]

    if dry_run:
        log.info("[dry-run] Would push '%s' → page_id=%s", title, effective_page_id or "NEW")
        return effective_page_id or 0

    if effective_page_id:
        result = client.update_page(effective_page_id, title, body, tags=tags or None)
        pid = result["id"]
        log.info("Updated BookStack page %d: '%s'  slug=%s", pid, title, result.get("slug"))
    else:
        eff_book = book_id or (int(BOOK_ID_ENV) if BOOK_ID_ENV else None)
        eff_chap = chapter_id or (int(CHAP_ID_ENV) if CHAP_ID_ENV else None)
        result = client.create_page(title, body, book_id=eff_book,
                                    chapter_id=eff_chap, tags=tags or None)
        pid = result["id"]
        log.info("Created BookStack page %d: '%s'  slug=%s", pid, title, result.get("slug"))
        inject_page_id(filepath, pid)

    return pid


# ─── CLI ─────────────────────────────────────────────────────────────────────

@click.group()
@click.option("--verbose", "-v", is_flag=True)
@click.pass_context
def cli(ctx, verbose):
    setup_logging(verbose)
    ctx.ensure_object(dict)
    try:
        ctx.obj["client"] = BookStackClient(BS_URL, TOKEN_ID, TOKEN_SEC)
    except ValueError as e:
        log.error("%s", e)
        sys.exit(1)


@cli.command()
@click.argument("filepath", type=click.Path(exists=True, path_type=Path))
@click.option("--page-id",    "-p", type=int, default=None)
@click.option("--book-id",    "-b", type=int, default=None)
@click.option("--chapter-id", "-c", type=int, default=None)
@click.option("--dry-run",    "-n", is_flag=True)
@click.pass_context
def push(ctx, filepath, page_id, book_id, chapter_id, dry_run):
    """Push a Markdown file to BookStack."""
    client = ctx.obj["client"]
    pid = push_file(client, filepath, page_id, book_id, chapter_id, dry_run)
    click.echo(f"Done — page_id: {pid}")


@cli.command()
@click.argument("filepath", type=click.Path(exists=True, path_type=Path))
@click.option("--page-id",    "-p", type=int, default=None)
@click.option("--book-id",    "-b", type=int, default=None)
@click.option("--chapter-id", "-c", type=int, default=None)
@click.option("--interval",   "-i", type=int, default=5,
              help="Seconds between modification checks")
@click.pass_context
def watch(ctx, filepath, page_id, book_id, chapter_id, interval):
    """Watch a file and push to BookStack on every save."""
    client = ctx.obj["client"]
    log.info("Watching %s (every %ds)", filepath, interval)
    last_mtime = filepath.stat().st_mtime
    while True:
        time.sleep(interval)
        try:
            mtime = filepath.stat().st_mtime
            if mtime != last_mtime:
                last_mtime = mtime
                log.info("Change detected — pushing %s", filepath.name)
                push_file(client, filepath, page_id, book_id, chapter_id, dry_run=False)
        except Exception as exc:
            log.error("Watch error: %s", exc)


@cli.command()
@click.option("--page-id", "-p", type=int, required=True)
@click.option("--output",  "-o", type=click.Path(path_type=Path), default=None)
@click.pass_context
def pull(ctx, page_id, output):
    """Pull a BookStack page and save as Markdown."""
    client = ctx.obj["client"]
    md = client.export_markdown(page_id)
    meta_info = client.get_page(page_id)
    name = meta_info.get("name", f"page-{page_id}")
    if output:
        target = Path(output)
    else:
        slug = meta_info.get("slug", f"page-{page_id}")
        target = Path(f"{slug}.md")
    target.write_text(md)
    click.echo(f"Saved '{name}' → {target}")


@cli.command("list-pages")
@click.option("--book-id", "-b", type=int, default=None)
@click.pass_context
def list_pages(ctx, book_id):
    """List pages in BookStack (optionally filtered by book)."""
    client = ctx.obj["client"]
    pages = client.list_pages(book_id)
    for p in pages:
        click.echo(f"  {p['id']:5d}  {p['book_id']:4d}/{p.get('chapter_id') or '    '}  {p['name']}")


if __name__ == "__main__":
    cli()
