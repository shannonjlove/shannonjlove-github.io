#!/usr/bin/env python3
"""
FileWarden — Hazel-style file automation daemon
Watches directories and applies YAML-configured rules to incoming files.
Actions: sjl_rename, mkdir_move, move, log, run_script.

Usage:
    python filewarden.py --config /etc/filewarden/config.yaml
    python filewarden.py --config /etc/filewarden/config.yaml --dry-run
"""

from __future__ import annotations

import logging
import os
import re
import shutil
import subprocess
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import click
import yaml
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

# ─── Logging ─────────────────────────────────────────────────────────────────

LOG_FILE = Path(os.environ.get("FW_LOG", "/var/log/filewarden/filewarden.log"))

def setup_logging(verbose: bool = False):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    level = logging.DEBUG if verbose else logging.INFO
    fmt = "%(asctime)s  %(levelname)-7s  %(message)s"
    handlers: list[logging.Handler] = [logging.StreamHandler()]
    try:
        handlers.append(logging.FileHandler(LOG_FILE))
    except OSError:
        pass
    logging.basicConfig(level=level, format=fmt, handlers=handlers)

log = logging.getLogger("filewarden")


# ─── SJL rename ──────────────────────────────────────────────────────────────

def _uuid24() -> str:
    """Generate a 24-character lowercase UUID (hex, no dashes)."""
    return uuid.uuid4().hex[:24]


def sjl_rename(path: Path, category: str, subcategory: str) -> Path:
    """
    SJL naming convention:
        YYYY-MM-DD_HH-MM_category-subcategory_description_UUID24.ext

    Example:
        2026-06-26_14-30_resources-automation_invoice_a3f9b2c1d4e5f6a7b8c9d0e1.pdf
    """
    now       = datetime.now()
    dt_str    = now.strftime("%Y-%m-%d_%H-%M")
    slug      = re.sub(r"[^a-z0-9]+", "-", path.stem.lower()).strip("-")
    uid       = _uuid24()
    ext       = path.suffix.lstrip(".")
    new_name  = f"{dt_str}_{category}-{subcategory}_{slug}_{uid}.{ext}"
    new_path  = path.parent / new_name
    return new_path


# ─── Condition evaluation ─────────────────────────────────────────────────────

def get_attribute(path: Path, attribute: str) -> Any:
    if attribute == "extension":
        return path.suffix.lstrip(".").lower()
    if attribute == "size_mb":
        try:
            return round(path.stat().st_size / (1024 * 1024), 2)
        except OSError:
            return 0
    if attribute == "name":
        return path.name
    if attribute == "stem":
        return path.stem
    return None


def evaluate_condition(path: Path, cond: dict) -> bool:
    attr  = get_attribute(path, cond["attribute"])
    op    = cond["operator"]
    value = cond["value"]

    if op == "is":
        return str(attr).lower() == str(value).lower()
    if op == "is_not":
        return str(attr).lower() != str(value).lower()
    if op == "contains":
        return str(value).lower() in str(attr).lower()
    if op == "greater_than":
        try:
            return float(attr) > float(value)
        except (TypeError, ValueError):
            return False
    if op == "less_than":
        try:
            return float(attr) < float(value)
        except (TypeError, ValueError):
            return False
    if op == "matches_regex":
        return bool(re.search(value, str(attr)))
    return False


def rule_matches(path: Path, rule: dict) -> bool:
    conditions: list = rule.get("conditions", [])
    if not conditions:
        return True
    match_mode = rule.get("match", "all")
    results = [evaluate_condition(path, c) for c in conditions]
    return all(results) if match_mode == "all" else any(results)


# ─── Action execution ─────────────────────────────────────────────────────────

def expand_vars(template: str, path: Path) -> str:
    """Replace {year}, {month}, {day}, {full_name}, {name}, {ext}, {size_mb}."""
    now = datetime.now()
    try:
        size_mb = str(round(path.stat().st_size / (1024 * 1024), 2))
    except OSError:
        size_mb = "0"
    return (
        template
        .replace("{year}",      now.strftime("%Y"))
        .replace("{month}",     now.strftime("%m"))
        .replace("{day}",       now.strftime("%d"))
        .replace("{full_name}", path.name)
        .replace("{name}",      path.stem)
        .replace("{ext}",       path.suffix.lstrip("."))
        .replace("{size_mb}",   size_mb)
    )


def run_action(action: dict, current_path: Path, dry_run: bool) -> Path:
    """
    Execute one action. Returns the new path after renames/moves (or current_path
    if unchanged). Raises on errors so the rule loop can catch them.
    """
    atype  = action["type"]
    params = action.get("params", {})

    if atype == "sjl_rename":
        new_path = sjl_rename(
            current_path,
            params.get("category", "general"),
            params.get("subcategory", "file"),
        )
        log.info("sjl_rename  %s  →  %s", current_path.name, new_path.name)
        if not dry_run:
            current_path.rename(new_path)
        return new_path

    if atype == "mkdir_move":
        base    = Path(params["base"])
        pattern = params.get("subdir_pattern", "")
        subdir  = Path(expand_vars(pattern, current_path)) if pattern else Path()
        dest    = base / subdir
        log.info("mkdir_move  %s  →  %s/", current_path.name, dest)
        if not dry_run:
            dest.mkdir(parents=True, exist_ok=True)
            shutil.move(str(current_path), dest / current_path.name)
        return dest / current_path.name

    if atype == "move":
        dest = Path(expand_vars(params["destination"], current_path))
        log.info("move        %s  →  %s/", current_path.name, dest)
        if not dry_run:
            dest.mkdir(parents=True, exist_ok=True)
            shutil.move(str(current_path), dest / current_path.name)
        return dest / current_path.name

    if atype == "log":
        msg = expand_vars(params.get("message", "{full_name}"), current_path)
        log.info("LOG  %s", msg)
        return current_path

    if atype == "run_script":
        script = params.get("script", "")
        env = {
            **os.environ,
            "FW_FILE": str(current_path),
            "FW_NAME": current_path.stem,
            "FW_EXT":  current_path.suffix.lstrip("."),
        }
        log.info("run_script  for  %s", current_path.name)
        if not dry_run:
            result = subprocess.run(
                script, shell=True, env=env,
                capture_output=True, text=True, timeout=30,
            )
            if result.returncode != 0:
                log.warning("run_script exited %d: %s", result.returncode, result.stderr.strip())
        return current_path

    log.warning("Unknown action type: %s", atype)
    return current_path


# ─── Rule processor ───────────────────────────────────────────────────────────

def process_file(path: Path, rules: list, dry_run: bool):
    current = path
    for rule in rules:
        if not rule.get("enabled", True):
            continue
        if not rule_matches(current, rule):
            continue

        log.info("RULE  '%s'  matched  %s", rule["name"], current.name)
        for action in rule.get("actions", []):
            try:
                current = run_action(action, current, dry_run)
            except Exception as exc:
                log.error("Action %s failed: %s", action.get("type"), exc)
                break

        if rule.get("stop_processing", False):
            break


# ─── Watchdog handler ─────────────────────────────────────────────────────────

class FileWardenHandler(FileSystemEventHandler):
    def __init__(self, watch_cfg: dict, dry_run: bool):
        self.rules     = watch_cfg.get("rules", [])
        self.delay     = watch_cfg.get("delay_seconds", 0)
        self.dry_run   = dry_run

    def on_created(self, event: FileSystemEvent):
        if event.is_directory:
            return
        path = Path(event.src_path)
        if self.delay:
            time.sleep(self.delay)
        if not path.exists():
            return
        try:
            process_file(path, self.rules, self.dry_run)
        except Exception as exc:
            log.error("Unhandled error processing %s: %s", path, exc)

    def on_moved(self, event: FileSystemEvent):
        if event.is_directory:
            return
        path = Path(event.dest_path)
        if self.delay:
            time.sleep(self.delay)
        if not path.exists():
            return
        try:
            process_file(path, self.rules, self.dry_run)
        except Exception as exc:
            log.error("Unhandled error processing %s: %s", path, exc)


# ─── Main ─────────────────────────────────────────────────────────────────────

@click.command()
@click.option("--config",  "-c",
              default="/etc/filewarden/config.yaml",
              show_default=True,
              help="Path to config.yaml")
@click.option("--dry-run", "-n", is_flag=True,
              help="Log actions but do not move/rename files")
@click.option("--verbose", "-v", is_flag=True)
def main(config: str, dry_run: bool, verbose: bool):
    setup_logging(verbose)
    cfg_path = Path(config)
    if not cfg_path.exists():
        log.error("Config not found: %s", cfg_path)
        sys.exit(1)

    with cfg_path.open() as f:
        cfg = yaml.safe_load(f)

    watches: list = cfg.get("watches", [])
    if not watches:
        log.warning("No watches defined in config.")
        sys.exit(0)

    observer = Observer()
    for watch in watches:
        if not watch.get("enabled", True):
            continue
        watch_path = watch["path"]
        recursive  = watch.get("recursive", False)
        handler    = FileWardenHandler(watch, dry_run)
        observer.schedule(handler, watch_path, recursive=recursive)
        log.info("Watching  %s  (recursive=%s, %d rules)",
                 watch_path, recursive, len(watch.get("rules", [])))

    if dry_run:
        log.info("DRY-RUN mode — no files will be modified")

    observer.start()
    log.info("FileWarden started")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
    log.info("FileWarden stopped")


if __name__ == "__main__":
    main()
