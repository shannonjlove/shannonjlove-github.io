"""
Tests for the FileWarden core pipeline.
Run with: pytest sjl-file-governance/filewarden/tests/
"""

import hashlib
import json
import tempfile
from pathlib import Path

import pytest

from filewarden.core.pipeline import Transaction, Pipeline, skill, _SKILL_REGISTRY


# ─── Transaction ──────────────────────────────────────────────────────────────

def test_transaction_defaults(tmp_path: Path) -> None:
    f = tmp_path / "test.txt"
    f.write_text("hello")
    tx = Transaction(original_path=f)
    assert tx.original_path == f
    assert tx.version is None       # set by version stage, not at construction
    assert tx.abort is False
    assert tx.skill_outputs == {}


def test_transaction_abort(tmp_path: Path) -> None:
    f = tmp_path / "test.txt"
    f.write_text("hello")
    tx = Transaction(original_path=f)
    tx.abort_with("test abort reason")
    assert tx.abort is True
    assert "test abort reason" in tx.abort_reason


# ─── Skill Decorator ──────────────────────────────────────────────────────────

def test_skill_registration() -> None:
    @skill(stage="analyze", when="post", name="_test_skill_reg")
    def _my_skill(tx: Transaction, config: dict) -> None:
        tx.skill_outputs["_test_skill_reg"] = True

    assert any(
        entry["name"] == "_test_skill_reg"
        for entry in _SKILL_REGISTRY
    )


def test_skill_runs_in_pipeline(tmp_path: Path) -> None:
    f = tmp_path / "sample.txt"
    f.write_text("data")

    ran: list[bool] = []

    @skill(stage="analyze", when="post", name="_test_pipeline_skill")
    def _hook(tx: Transaction, config: dict) -> None:
        ran.append(True)

    pipeline = Pipeline(config={})

    # Minimal stage stubs so the pipeline can complete
    def _noop(tx: Transaction, config: dict) -> None:
        pass

    for stage in ["stabilize", "identify", "analyze", "version",
                  "rename", "sidecar", "hook", "mirror", "register", "publish"]:
        pipeline.register_stage(stage, _noop)

    from filewarden.core.pipeline import load_skills
    load_skills(pipeline)

    tx = Transaction(original_path=f)
    pipeline.run(tx)

    assert ran, "Post-analyze skill hook did not fire"


# ─── Registry ─────────────────────────────────────────────────────────────────

def test_registry_upsert_and_lookup(tmp_path: Path) -> None:
    from filewarden.core.registry import load as load_registry, Registry

    config = {"registry_path": str(tmp_path / "test.db")}
    reg: Registry = load_registry(config)

    docid = "SJL-CLOUD-TEST-0001"
    reg.upsert(
        docid=docid,
        canonical_filename="02000_2026-06-28__SJL-CLOUD-TEST-0001__test-doc__v1-0__abc12345.txt",
        canonical_path=str(tmp_path / "02000_2026-06-28__SJL-CLOUD-TEST-0001__test-doc__v1-0__abc12345.txt"),
        version="1-0",
        sha256_full="a" * 64,
        para="02000",
        mirror_state="verified",
        hook_id=None,
        ocr_state=None,
    )

    row = reg.find_by_docid(docid)
    assert row is not None
    assert row["docid"] == docid
    assert row["version"] == "1-0"


# ─── Naming Convention ────────────────────────────────────────────────────────

def test_canonical_name_format() -> None:
    """Verify the canonical filename pattern from §4 of the doctrine."""
    import re
    pattern = re.compile(
        r"^\d{5}_\d{4}-\d{2}-\d{2}__[A-Z0-9\-]+__[a-z0-9\-]+__v\d+-\d+__[0-9a-f]{8}\.\w+$"
    )
    valid = "02000_2026-06-28__SJL-CLOUD-0017__persistent-metadata-manual__v7-2__843dc901.pdf"
    assert pattern.match(valid), f"Canonical name did not match pattern: {valid}"


# ─── Skill: Screenshot Sort ───────────────────────────────────────────────────

def test_screenshot_device_identification() -> None:
    from filewarden.skills.skill_screenshot_sort import _identify_device
    assert _identify_device((390, 844)) == "iphone-14"
    assert _identify_device((844, 390)) == "iphone-14"   # landscape
    assert _identify_device((9999, 5000)) == "desktop-unknown"
    assert _identify_device((100, 9999)) == "mobile-unknown"


# ─── Skill: Video Sort ────────────────────────────────────────────────────────

def test_tv_episode_detection() -> None:
    from filewarden.skills.skill_video_sort import TV_PATTERN, MOVIE_PATTERN
    assert TV_PATTERN.search("Breaking.Bad.S03E07.1080p.mkv")
    assert TV_PATTERN.search("Show Name - s01e12.mp4")
    assert not TV_PATTERN.search("Inception.2010.mkv")


def test_movie_year_detection() -> None:
    from filewarden.skills.skill_video_sort import MOVIE_PATTERN
    m = MOVIE_PATTERN.search("Inception (2010).mkv")
    assert m and m.group(2) == "2010"

    m2 = MOVIE_PATTERN.search("The.Matrix.1999.BluRay.mkv")
    assert m2 and m2.group(2) == "1999"


# ─── Skill: Stabilize Timing ─────────────────────────────────────────────────

def test_lock_detection() -> None:
    from filewarden.skills.skill_stabilize_timing import _is_locked
    from pathlib import PurePosixPath

    class _FakePath:
        def __init__(self, name: str):
            self.name = name
            self.parent = Path("/tmp")
        def __truediv__(self, other: str) -> "_FakePath":
            return _FakePath(self.name + other)
        def exists(self) -> bool:
            return False

    assert _is_locked(_FakePath("video.mkv.part"))      # type: ignore[arg-type]
    assert _is_locked(_FakePath(".~lock.doc.tmp"))      # type: ignore[arg-type]
    assert not _is_locked(_FakePath("normalfile.pdf"))  # type: ignore[arg-type]


# ─── Skill: PDF OCR Detect ────────────────────────────────────────────────────

def test_pdf_font_detection(tmp_path: Path) -> None:
    from filewarden.skills.skill_pdf_ocr_detect import _has_text_layer

    # Minimal "PDF" with a Font reference → has text layer
    pdf_with_font = tmp_path / "with_font.pdf"
    pdf_with_font.write_bytes(b"%PDF-1.4\n/Font\nsome content")
    assert _has_text_layer(pdf_with_font) is True

    # PDF without Font → no text layer
    pdf_no_font = tmp_path / "no_font.pdf"
    pdf_no_font.write_bytes(b"%PDF-1.4\nno text content here at all")
    assert _has_text_layer(pdf_no_font) is False


# ─── Skill: Extended Attribute Tagging ───────────────────────────────────────

def test_finder_tag_parse_plain() -> None:
    from filewarden.skills.skill_xattr_tag import _parse_finder_tags
    tags = _parse_finder_tags(["Work", "Home"])
    assert len(tags) == 2
    assert tags[0] == {"name": "Work", "color": 0}
    assert tags[1] == {"name": "Home", "color": 0}


def test_finder_tag_parse_color() -> None:
    from filewarden.skills.skill_xattr_tag import _parse_finder_tags
    tags = _parse_finder_tags(["Red\n5", "Work", "Blue\n4"])
    assert tags[0] == {"name": "Red",  "color": 5}
    assert tags[1] == {"name": "Work", "color": 0}
    assert tags[2] == {"name": "Blue", "color": 4}


def test_finder_tag_roundtrip() -> None:
    """Tags encode to the correct string format and decode back cleanly."""
    from filewarden.skills.skill_xattr_tag import (
        _parse_finder_tags, _build_finder_tag_strings
    )
    raw = ["Work", "Red\n5", "SJL-PROJECTS\n5", "Gray\n1"]
    parsed = _parse_finder_tags(raw)
    rebuilt = _build_finder_tag_strings(parsed)
    # Plain tags stay plain; color tags have the \nN suffix
    assert "Work" in rebuilt
    assert "Red\n5" in rebuilt
    assert "Gray\n1" in rebuilt


def test_merge_tags_deduplicates() -> None:
    from filewarden.skills.skill_xattr_tag import merge_tags
    existing = [{"name": "Work", "color": 0}, {"name": "Red", "color": 5}]
    additions = [{"name": "work", "color": 0}, {"name": "Blue", "color": 4}]
    merged = merge_tags(existing, additions)
    names_lower = [t["name"].lower() for t in merged]
    assert names_lower.count("work") == 1
    assert "blue" in names_lower
    assert len(merged) == 3


def test_merge_tags_addition_wins_on_color() -> None:
    """When same name exists, the addition's color should win."""
    from filewarden.skills.skill_xattr_tag import merge_tags
    existing  = [{"name": "Tag", "color": 0}]
    additions = [{"name": "Tag", "color": 5}]
    merged = merge_tags(existing, additions)
    assert len(merged) == 1
    assert merged[0]["color"] == 5


def test_para_color_map_complete() -> None:
    from filewarden.skills.skill_xattr_tag import PARA_COLOR_MAP, FINDER_COLORS
    for code, color_num in PARA_COLOR_MAP.items():
        assert code.isdigit() and len(code) == 5
        assert color_num in FINDER_COLORS


def test_quarantine_parse() -> None:
    from filewarden.skills.skill_xattr_tag import parse_quarantine_string
    q = "0083;5f123456;Safari;AAAA-BBBB"
    parsed = parse_quarantine_string(q)
    assert parsed["flags"] == "0083"
    assert parsed["source_app"] == "Safari"
    assert parsed["timestamp_hex"] == "5f123456"
    assert parsed["uuid"] == "AAAA-BBBB"


def test_xattr_write_read_roundtrip(tmp_path: Path) -> None:
    """Write tags as binary plist xattr, read back and verify (requires xattr module)."""
    pytest.importorskip("xattr")
    import plistlib
    from filewarden.skills.skill_xattr_tag import (
        write_finder_tags, read_finder_tags,
        write_spotlight_keywords, read_spotlight_keywords,
        write_spotlight_comment, read_spotlight_comment,
    )

    f = tmp_path / "test_tag.txt"
    f.write_text("hello")

    tags_in = [{"name": "Work", "color": 0}, {"name": "Red", "color": 5}]
    assert write_finder_tags(f, tags_in)

    tags_out = read_finder_tags(f)
    names_out = {t["name"] for t in tags_out}
    assert "Work" in names_out
    assert "Red" in names_out

    assert write_spotlight_keywords(f, ["sjl", "filewarden", "docid"])
    kw = read_spotlight_keywords(f)
    assert "sjl" in kw

    assert write_spotlight_comment(f, "DOCID:SJL-TEST-001 | PARA:02000 | v1-0 | abc12345")
    comment = read_spotlight_comment(f)
    assert comment and "SJL-TEST-001" in comment


def test_sjl_xattr_key_format() -> None:
    from filewarden.skills.skill_xattr_tag import _sjl_key
    key = _sjl_key("docid", syncable=True)
    assert key == "co.sjl.filewarden:docid#S"
    key_ns = _sjl_key("para", syncable=False)
    assert key_ns == "co.sjl.filewarden:para"
