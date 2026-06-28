"""
FileWarden v2 — SJL Sovereign Cloud File Governance Daemon

Entry point. Loads config, wires watchdog inotify observer, and drives
the governance pipeline for every stable file dropped into a watched path.

Usage:
    python -m filewarden.filewarden --config /opt/sjl/filewarden.yaml
    # or as a systemd Quadlet (see 07000_SYSTEM-AUTOMATION/)
"""

from __future__ import annotations

import argparse
import logging
import logging.handlers
import os
import signal
import sys
import time
from pathlib import Path
from typing import Any, Dict

import yaml

from filewarden.core.pipeline import Pipeline, load_skills
from filewarden.core.registry import load as load_registry


log = logging.getLogger("filewarden")


# ─── Config Loading ───────────────────────────────────────────────────────────

def load_config(path: str) -> Dict[str, Any]:
    with open(path, "r") as fh:
        return yaml.safe_load(fh) or {}


def _apply_env_secrets(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    For any config key ending in '_env', resolve the named environment variable
    and store the value under the key without the '_env' suffix.
    Secrets are never written to disk or echoed to logs.
    """
    resolved: Dict[str, Any] = {}
    for k, v in config.items():
        if k.endswith("_env") and isinstance(v, str):
            env_val = os.environ.get(v)
            if env_val:
                resolved[k[:-4]] = env_val  # strip '_env' suffix
        else:
            resolved[k] = v
    return resolved


# ─── Logging Setup ────────────────────────────────────────────────────────────

def setup_logging(config: Dict[str, Any]) -> None:
    level = getattr(logging, config.get("log_level", "INFO").upper(), logging.INFO)
    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stdout)]

    log_file = config.get("log_file")
    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        handlers.append(
            logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=config.get("log_max_bytes", 10 * 1024 * 1024),
                backupCount=config.get("log_backup_count", 5),
            )
        )

    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
        handlers=handlers,
    )


# ─── Pipeline Factory ─────────────────────────────────────────────────────────

def build_pipeline(config: Dict[str, Any]) -> Pipeline:
    pipeline = Pipeline(config)
    load_skills(pipeline)
    return pipeline


# ─── File Event Handler ───────────────────────────────────────────────────────

def _process_file(path: Path, pipeline: Pipeline, config: Dict[str, Any]) -> None:
    """Run the governance pipeline on a single file."""
    from filewarden.core.pipeline import Transaction

    if not path.is_file():
        return

    name = path.name
    # Skip hidden/system files and sidecar artifacts
    if (
        name.startswith(".")
        or name.endswith(".sjl.json")
        or name.endswith(".sha256")
        or name == "filewarden.db"
        or name == "filewarden.db-wal"
        or name == "filewarden.db-shm"
    ):
        return

    skip_folders = set(config.get("subfolder_skip_files", []))
    if name in skip_folders:
        return

    log.info("Processing: %s", path)
    tx = Transaction(original_path=path)
    pipeline.run(tx)


# ─── Watchdog Observer ────────────────────────────────────────────────────────

def _start_watchdog(watch_paths: list[str], pipeline: Pipeline, config: Dict[str, Any]) -> Any:
    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler, FileCreatedEvent, FileModifiedEvent

        class _Handler(FileSystemEventHandler):
            def on_created(self, event: FileCreatedEvent) -> None:  # type: ignore[override]
                if not event.is_directory:
                    _process_file(Path(event.src_path), pipeline, config)

            def on_moved(self, event: Any) -> None:
                if not event.is_directory:
                    _process_file(Path(event.dest_path), pipeline, config)

        observer = Observer()
        for wp in watch_paths:
            p = Path(wp)
            p.mkdir(parents=True, exist_ok=True)
            observer.schedule(_Handler(), str(p), recursive=True)
            log.info("Watching: %s", p)

        observer.start()
        return observer

    except ImportError:
        log.error(
            "watchdog is not installed. Install it with: pip install watchdog\n"
            "Alternatively, run filewarden in one-shot mode: "
            "python -m filewarden.filewarden --config ... --file <path>"
        )
        sys.exit(1)


# ─── Batch Scan (one-shot) ────────────────────────────────────────────────────

def run_batch_scan(watch_paths: list[str], pipeline: Pipeline, config: Dict[str, Any]) -> None:
    """Walk all watch paths and process every eligible file."""
    for wp in watch_paths:
        root = Path(wp)
        if not root.exists():
            log.warning("Watch path does not exist: %s", wp)
            continue
        for path in sorted(root.rglob("*")):
            _process_file(path, pipeline, config)


# ─── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="FileWarden v2 — SJL Sovereign Cloud File Governance Daemon"
    )
    parser.add_argument("--config", default="/opt/sjl/filewarden.yaml", help="Path to YAML config")
    parser.add_argument("--file", help="Govern a single file and exit (one-shot mode)")
    parser.add_argument("--scan", action="store_true", help="Batch-scan watch paths and exit")
    args = parser.parse_args()

    config = load_config(args.config)
    config = _apply_env_secrets(config)
    setup_logging(config)

    log.info("FileWarden v2 starting (config: %s)", args.config)

    registry = load_registry(config)
    config["_registry"] = registry

    # Pipeline auto-loads stage functions from filewarden.core.stages in __init__
    pipeline = build_pipeline(config)

    # ── One-shot: single file ──────────────────────────────────────────────────
    if args.file:
        _process_file(Path(args.file), pipeline, config)
        return

    # ── One-shot: batch scan ───────────────────────────────────────────────────
    if args.scan:
        run_batch_scan(config.get("watch_paths", []), pipeline, config)
        return

    # ── Daemon mode ───────────────────────────────────────────────────────────
    watch_paths = config.get("watch_paths", [])
    if not watch_paths:
        log.error("No watch_paths configured. Nothing to watch.")
        sys.exit(1)

    observer = _start_watchdog(watch_paths, pipeline, config)

    def _shutdown(signum: int, frame: Any) -> None:
        log.info("Signal %d received; stopping observer.", signum)
        observer.stop()

    signal.signal(signal.SIGTERM, _shutdown)
    signal.signal(signal.SIGINT, _shutdown)

    log.info("FileWarden v2 daemon running. SIGTERM or Ctrl-C to stop.")
    try:
        while observer.is_alive():
            time.sleep(1)
    finally:
        observer.join()
        log.info("FileWarden v2 stopped.")


if __name__ == "__main__":
    main()
