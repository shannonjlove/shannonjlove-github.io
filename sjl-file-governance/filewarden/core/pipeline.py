"""
FileWarden v2 — Core Transaction Pipeline
SJL Sovereign Cloud | 07100_FILEWARDEN

Canonical pipeline:
  discover -> stabilize -> identify -> analyze -> version -> diff
           -> rename -> sidecar -> hook -> mirror -> register -> publish

Each stage is a named function. Skills (plugins) register as hooks at any stage.
A transaction is a dict carried through the pipeline; any stage may abort by
setting transaction["abort"] = True with a reason in transaction["abort_reason"].
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import shutil
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

log = logging.getLogger("filewarden.pipeline")

# ─────────────────────────────────────────────
# TRANSACTION DATA STRUCTURE
# ─────────────────────────────────────────────

@dataclass
class Transaction:
    """Single file governance transaction."""
    original_path: Path
    event_type: str = "created"         # created | modified | moved | deleted
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    # Populated during pipeline stages
    stable: bool = False
    sha256: Optional[str] = None
    sha8: Optional[str] = None
    docid: Optional[str] = None
    para: Optional[str] = None
    semantic_title: Optional[str] = None
    version: Optional[str] = None
    prior_version: Optional[str] = None
    prior_sha256: Optional[str] = None
    canonical_name: Optional[str] = None
    canonical_path: Optional[Path] = None
    sidecar_path: Optional[Path] = None
    mirror_verified: bool = False
    registry_id: Optional[str] = None
    hook_id: Optional[str] = None
    bookstack_url: Optional[str] = None
    paperparrot_id: Optional[str] = None
    ocr_state: str = "pending"
    vision_state: str = "pending"
    metadata: Dict[str, Any] = field(default_factory=dict)
    history: List[str] = field(default_factory=list)

    # Control
    abort: bool = False
    abort_reason: Optional[str] = None
    quarantine_code: Optional[str] = None
    skill_outputs: Dict[str, Any] = field(default_factory=dict)

    def log_stage(self, stage: str, msg: str) -> None:
        entry = f"{datetime.now(timezone.utc).isoformat()} [{stage}] {msg}"
        self.history.append(entry)
        log.info("%s | %s | %s", self.original_path.name, stage, msg)

    def abort_with(self, reason: str, quarantine: Optional[str] = None) -> None:
        self.abort = True
        self.abort_reason = reason
        self.quarantine_code = quarantine or "09300_METADATA-CONFLICT"
        log.warning("ABORT %s: %s", self.original_path.name, reason)


# ─────────────────────────────────────────────
# PIPELINE ENGINE
# ─────────────────────────────────────────────

class Pipeline:
    """
    Runs a transaction through the governance pipeline.
    Skills register pre/post hooks at named stages.
    """

    STAGES = [
        "stabilize",
        "identify",      # DOCID assignment/recovery
        "analyze",       # OCR, vision, metadata extraction
        "version",       # version increment, diff
        "rename",        # canonical filename
        "sidecar",       # write sidecar JSON + SHA256 file
        "hook",          # register hook
        "mirror",        # rclone mirror + checksum verify
        "register",      # update central registry
        "publish",       # BookStack + PaperParrot
    ]

    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config
        self._pre_hooks: Dict[str, List[Callable]] = {s: [] for s in self.STAGES}
        self._post_hooks: Dict[str, List[Callable]] = {s: [] for s in self.STAGES}
        self._stage_funcs: Dict[str, Callable] = {}

        # Register built-in stage implementations
        from filewarden.core import stages
        for stage in self.STAGES:
            fn = getattr(stages, stage, None)
            if fn:
                self._stage_funcs[stage] = fn

    def register_skill(
        self,
        stage: str,
        hook: Callable,
        when: str = "post",
    ) -> None:
        """Register a skill hook at a pipeline stage. when='pre' or 'post'."""
        if stage not in self.STAGES:
            raise ValueError(f"Unknown stage: {stage}")
        if when == "pre":
            self._pre_hooks[stage].append(hook)
        else:
            self._post_hooks[stage].append(hook)

    def run(self, tx: Transaction) -> Transaction:
        """Execute all pipeline stages for a transaction."""
        for stage in self.STAGES:
            if tx.abort:
                break
            self._run_stage(stage, tx)

        if tx.abort:
            self._quarantine(tx)

        return tx

    def _run_stage(self, stage: str, tx: Transaction) -> None:
        tx.log_stage(stage, "start")

        # Pre-hooks
        for hook in self._pre_hooks[stage]:
            try:
                hook(tx, self.config)
            except Exception as e:
                log.error("Pre-hook %s.%s failed: %s", stage, hook.__name__, e)

        if tx.abort:
            return

        # Built-in stage function
        fn = self._stage_funcs.get(stage)
        if fn:
            try:
                fn(tx, self.config)
            except Exception as e:
                tx.abort_with(f"Stage {stage} raised: {e}", "09300_METADATA-CONFLICT")
                return

        if tx.abort:
            return

        # Post-hooks
        for hook in self._post_hooks[stage]:
            try:
                hook(tx, self.config)
            except Exception as e:
                log.error("Post-hook %s.%s failed: %s", stage, hook.__name__, e)

        tx.log_stage(stage, "done")

    def _quarantine(self, tx: Transaction) -> None:
        """Move file to appropriate quarantine subdirectory."""
        q_code = tx.quarantine_code or "09300_METADATA-CONFLICT"
        q_root = Path(self.config.get("quarantine_root", "/srv/sjl/09000_QUARANTINE"))
        q_dir = q_root / q_code
        q_dir.mkdir(parents=True, exist_ok=True)

        dest = q_dir / tx.original_path.name
        try:
            shutil.move(str(tx.original_path), str(dest))
            log.warning("QUARANTINE %s -> %s", tx.original_path.name, q_code)
        except Exception as e:
            log.error("Could not quarantine %s: %s", tx.original_path, e)


# ─────────────────────────────────────────────
# SKILL REGISTRY (module-level singleton)
# ─────────────────────────────────────────────

_SKILL_REGISTRY: List[Dict[str, Any]] = []
_skill_registry = _SKILL_REGISTRY  # alias for internal use


def skill(stage: str, when: str = "post", name: Optional[str] = None):
    """Decorator to register a function as a FileWarden skill."""
    def decorator(fn: Callable) -> Callable:
        _skill_registry.append({
            "stage": stage,
            "when": when,
            "name": name or fn.__name__,
            "fn": fn,
        })
        return fn
    return decorator


def load_skills(pipeline: Pipeline) -> None:
    """Load all registered skills into the pipeline."""
    for entry in _skill_registry:
        pipeline.register_skill(entry["stage"], entry["fn"], entry["when"])
        log.info("Loaded skill: %s at %s/%s", entry["name"], entry["stage"], entry["when"])
