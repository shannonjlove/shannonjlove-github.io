#!/usr/bin/env bash
# tag-and-analyze.sh — exhaustive metadata extraction, AI tagging, and write-back
#
# Called by FileWarden on every file that enters the PARA inbox.
# Run BEFORE sjl_rename so raw filenames are still available for heuristics.
#
# What it does (gracefully skips any tool not installed):
#   ALL files   : ExifTool full dump → <file>.meta.json
#   Images      : FFprobe dims + ExifTool XMP write-back (pipeline stamp, color space)
#   Video       : FFprobe streams → <file>.ffprobe.json + thumbnail extraction
#   Audio       : FFprobe tech data + fpcalc AcoustID fingerprint + MusicBrainz lookup
#                 + mutagen write-back of enriched ID3/FLAC/MP4 tags
#   Documents   : pdfinfo + pdftotext → <file>.ocr.txt + Tesseract for scanned PDFs
#
# Output per file:
#   <file>.meta.json      — full ExifTool dump (all tags, all groups)
#   <file>.ffprobe.json   — FFprobe technical streams (video/audio only)
#   <file>.acoustid.json  — AcoustID fingerprint (audio only)
#   <file>.ocr.txt        — extracted text (documents/OCR only)
#   FileWarden log entry  — one-line summary per file
#
# Install deps:  bash /opt/filewarden/scripts/install-tagging-deps.sh
set -euo pipefail

FILE="${1:?file path required}"
LOG="/var/log/filewarden/tagging.log"
STAMP="$(date '+%Y-%m-%d %H:%M:%S')"

log()  { echo "[$STAMP] [tag] $*" | tee -a "$LOG"; }
have() { command -v "$1" >/dev/null 2>&1; }

[ ! -f "$FILE" ] && { log "ERROR not found: $FILE"; exit 1; }

EXT="${FILE##*.}"; EXT="${EXT,,}"
BASE="${FILE%.*}"
SIDECAR="${BASE}.meta.json"

log "START $FILE"

# ── ExifTool — runs on EVERY file ─────────────────────────────────────────────
if have exiftool; then
  exiftool -j -G -q -a -u "$FILE" 2>/dev/null > "$SIDECAR" \
    || echo '[]' > "$SIDECAR"
  log "exiftool: wrote $SIDECAR"
else
  echo '[]' > "$SIDECAR"
  log "WARN: exiftool not installed"
fi

# ── File type dispatch ─────────────────────────────────────────────────────────
case "$EXT" in

# ── Images ────────────────────────────────────────────────────────────────────
jpg|jpeg|png|gif|webp|heic|heif|tiff|bmp|raw|cr2|nef|arw|dng|orf|rw2|srw)
  log "type: image"

  # FFprobe for dimensions and color space
  if have ffprobe; then
    ffprobe -v quiet -print_format json -show_streams "$FILE" \
      2>/dev/null > "${BASE}.ffprobe.json" || true
  fi

  # Stamp XMP metadata — marks file as processed by SJL pipeline
  if have exiftool; then
    exiftool -overwrite_original -q \
      -XMP-xmp:ProcessingSoftware="SJL-FileWarden" \
      -XMP-xmp:MetadataDate="$(date '+%Y:%m:%d %H:%M:%S')" \
      -XMP-xmpMM:InstanceID="uuid:$(cat /proc/sys/kernel/random/uuid 2>/dev/null || uuidgen)" \
      "$FILE" 2>/dev/null || true
    log "exiftool: XMP pipeline stamp written"
  fi

  # Tesseract OCR for images that may contain text (screenshots, scans)
  if have tesseract && [[ "$EXT" =~ ^(jpg|jpeg|png|tiff|bmp)$ ]]; then
    tesseract "$FILE" "${BASE}.ocr" -l eng quiet 2>/dev/null \
      && mv "${BASE}.ocr.txt" "${BASE}.ocr.txt" 2>/dev/null \
      && log "tesseract: OCR complete" || true
  fi
  ;;

# ── Video ─────────────────────────────────────────────────────────────────────
mp4|mov|avi|mkv|webm|m4v|mts|m2ts|wmv|flv|vob|ogv)
  log "type: video"

  if have ffprobe; then
    ffprobe -v quiet -print_format json -show_format -show_streams "$FILE" \
      2>/dev/null > "${BASE}.ffprobe.json"
    DURATION=$(python3 -c "
import json,sys
d=json.load(open('${BASE}.ffprobe.json'))
fmt=d.get('format',{})
print(fmt.get('duration','?')+'s  '+fmt.get('size','?')+'B  '+fmt.get('bit_rate','?')+'bps')
" 2>/dev/null || echo "?")
    log "ffprobe: $DURATION"
  fi

  # Stamp video metadata via ExifTool
  if have exiftool; then
    exiftool -overwrite_original -q \
      -XMP-xmp:ProcessingSoftware="SJL-FileWarden" \
      -XMP-xmp:MetadataDate="$(date '+%Y:%m:%d %H:%M:%S')" \
      "$FILE" 2>/dev/null || true
  fi

  # Extract poster thumbnail at 10% mark
  if have ffmpeg; then
    ffmpeg -v quiet -ss 0 -i "$FILE" -vframes 1 -q:v 2 \
      "${BASE}.thumb.jpg" 2>/dev/null \
      && log "ffmpeg: thumbnail extracted" || true
  fi
  ;;

# ── Audio ─────────────────────────────────────────────────────────────────────
mp3|aac|flac|wav|m4a|ogg|opus|wma|aiff|alac)
  log "type: audio"

  if have ffprobe; then
    ffprobe -v quiet -print_format json -show_format -show_streams "$FILE" \
      2>/dev/null > "${BASE}.ffprobe.json"
    AUDIO_INFO=$(python3 -c "
import json,sys
d=json.load(open('${BASE}.ffprobe.json'))
fmt=d.get('format',{})
tags=fmt.get('tags',{})
s=d.get('streams',[{}])[0]
print('|'.join(filter(None,[
  tags.get('title',''),tags.get('artist',''),tags.get('album',''),
  str(round(float(fmt.get('duration',0))))+'s',
  s.get('codec_name',''),str(s.get('sample_rate',''))+'Hz'
])))
" 2>/dev/null || echo "?")
    log "ffprobe: $AUDIO_INFO"
  fi

  # AcoustID fingerprint for music identification
  if have fpcalc; then
    fpcalc -json "$FILE" 2>/dev/null > "${BASE}.acoustid.json" \
      && log "fpcalc: fingerprint generated" || true
  fi

  # Beets import (non-destructive lookup + tag write)
  if have beet; then
    beet import -q "$FILE" 2>>"$LOG" \
      && log "beets: tags updated via MusicBrainz" || true
  fi

  # mutagen fallback — ensure basic tags exist
  if have python3; then
    python3 - "$FILE" << 'PYEOF' 2>/dev/null || true
import sys, os
try:
    import mutagen
    f = mutagen.File(sys.argv[1], easy=True)
    if f is None: sys.exit(0)
    if 'encodedby' not in (f.tags or {}):
        f['encodedby'] = ['SJL-FileWarden']
    if 'comment' not in (f.tags or {}):
        f['comment'] = [f'Tagged: {__import__("datetime").datetime.now().isoformat()}']
    f.save()
except Exception as e:
    print(f'mutagen: {e}', file=sys.stderr)
PYEOF
    log "mutagen: pipeline tag written"
  fi
  ;;

# ── PDF Documents ──────────────────────────────────────────────────────────────
pdf)
  log "type: pdf"

  if have pdfinfo; then
    pdfinfo "$FILE" 2>/dev/null > "${BASE}.pdfinfo.txt" \
      && log "pdfinfo: metadata extracted" || true
  fi

  # pdftotext — embedded text first (fast, accurate)
  if have pdftotext; then
    pdftotext -layout "$FILE" "${BASE}.ocr.txt" 2>/dev/null \
      && log "pdftotext: text extracted" \
      || true
  fi

  # Tesseract OCR fallback for scanned PDFs
  if have tesseract && [ -f "${BASE}.ocr.txt" ]; then
    WORDS=$(wc -w < "${BASE}.ocr.txt" 2>/dev/null || echo 0)
    if [ "$WORDS" -lt 50 ]; then
      log "pdftotext: sparse ($WORDS words) — running Tesseract OCR"
      if have pdftoppm; then
        pdftoppm -r 150 -l 5 "$FILE" "/tmp/fw_ocr_$$" 2>/dev/null || true
        for img in /tmp/fw_ocr_$$-*.ppm; do
          [ -f "$img" ] && tesseract "$img" "${img%.ppm}" quiet 2>/dev/null || true
        done
        cat /tmp/fw_ocr_$$-*.txt >> "${BASE}.ocr.txt" 2>/dev/null || true
        rm -f /tmp/fw_ocr_$$* 2>/dev/null || true
        log "tesseract: scanned PDF OCR complete"
      fi
    fi
  fi

  # ExifTool PDF metadata stamp
  if have exiftool; then
    exiftool -overwrite_original -q \
      -PDF:Producer="SJL-FileWarden" \
      "$FILE" 2>/dev/null || true
  fi
  ;;

# ── Office Documents ──────────────────────────────────────────────────────────
doc|docx|xls|xlsx|ppt|pptx|odt|ods|odp)
  log "type: office"

  if have python3; then
    python3 - "$FILE" "$BASE" << 'PYEOF' 2>/dev/null || true
import sys, json
path, base = sys.argv[1], sys.argv[2]
ext = path.rsplit('.', 1)[-1].lower()
meta = {}
try:
    if ext == 'docx':
        from docx import Document
        doc = Document(path)
        meta = {'paragraphs': len(doc.paragraphs),
                'words': sum(len(p.text.split()) for p in doc.paragraphs),
                'core_props': {k: str(getattr(doc.core_properties, k, ''))
                               for k in ['author','title','subject','keywords','modified']}}
    elif ext in ('xlsx','xls'):
        import openpyxl
        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
        meta = {'sheets': wb.sheetnames, 'sheet_count': len(wb.sheetnames)}
except ImportError as e:
    meta = {'error': f'missing library: {e}'}
except Exception as e:
    meta = {'error': str(e)}

with open(base + '.docmeta.json', 'w') as f:
    json.dump(meta, f, indent=2, default=str)
PYEOF
    log "docmeta: extracted"
  fi
  ;;

*)
  log "type: other ($EXT) — exiftool metadata only"
  ;;
esac


# ── HookVault — register file with all extracted tags ─────────────────────────
# Gives every processed file a persistent hook:// ID, links it bidirectionally
# to its S3 destination URL, and stores all metadata as searchable tags.
HV_URL="${HOOKVAULT_URL:-http://localhost:8086}"

if curl -sf "$HV_URL/stats" >/dev/null 2>&1; then
  # Build tag list from sidecar metadata
  TAGS=$(python3 - "$SIDECAR" "$EXT" "$FILE" << 'PYEOF' 2>/dev/null || echo '"sjl-pipeline"')
import json, sys, os

sidecar_path, ext, filepath = sys.argv[1], sys.argv[2], sys.argv[3]
tags = ["sjl-pipeline", f"ext:{ext}", f"type:{ext}"]

try:
    data = json.load(open(sidecar_path))
    if isinstance(data, list) and data:
        exif = data[0]
        for key in ["File:MIMEType","EXIF:Make","EXIF:Model","EXIF:GPSLatitude",
                    "QuickTime:MajorBrand","ID3:Artist","ID3:Album","ID3:Genre",
                    "XMP:Label","IPTC:Keywords"]:
            val = exif.get(key)
            if val and isinstance(val, str) and len(val) < 80:
                clean = val.strip().lower().replace(' ', '-')
                tags.append(f"{key.split(':')[1].lower()}:{clean}")
except Exception:
    pass

# Add file size category
size = os.path.getsize(filepath)
if size < 1_000_000: tags.append("size:small")
elif size < 100_000_000: tags.append("size:medium")
else: tags.append("size:large")

print(json.dumps(tags))
PYEOF
  )

  HOOK_RESP=$(curl -sf -X POST "$HV_URL/items" \
    -H "Content-Type: application/json" \
    -d "{\"kind\":\"file\",\"path\":\"$FILE\",\"title\":\"$(basename "$FILE")\",\"tags\":$TAGS}" \
    2>/dev/null || echo '{}')

  HOOK_ID=$(python3 -c "import json,sys; print(json.loads(sys.argv[1]).get('hook_id',''))" \
    "$HOOK_RESP" 2>/dev/null || echo "")

  if [ -n "$HOOK_ID" ]; then
    # Write hook ID into the meta sidecar for downstream use
    python3 - "$SIDECAR" "$HOOK_ID" << 'PYEOF' 2>/dev/null || true
import json, sys
path, hook_id = sys.argv[1], sys.argv[2]
try:
    data = json.load(open(path)) if open(path).read(1) else []
except: data = []
if isinstance(data, list) and data:
    data[0]["SJL:HookVaultID"] = hook_id
elif isinstance(data, dict):
    data["SJL:HookVaultID"] = hook_id
with open(path, 'w') as f:
    json.dump(data, f, indent=2, default=str)
PYEOF
    log "hookvault: registered $HOOK_ID"
  fi
else
  log "hookvault: not reachable at $HV_URL — skipping registration"
fi

# ── DiffForge — verify file integrity vs existing S3 copy ─────────────────────
# For text/document files only: checks if this file differs from its last-known
# S3 version. Uses the .ocr.txt sidecar as the comparison corpus so binary diffs
# don't pollute the log. Skips if no prior version exists in HookVault.
DF_URL="${DIFFFORGE_URL:-https://diff.shannonjlove.cloud}"

if [[ "$EXT" =~ ^(pdf|txt|md|docx|doc|rtf|csv|json|yaml|yml|html|htm)$ ]]; then
  OCR_FILE="${BASE}.ocr.txt"
  if [ -f "$OCR_FILE" ] && curl -sf "$DF_URL/" >/dev/null 2>&1; then
    PRIOR_OCR="/tmp/fw_prior_$$_$(basename "$OCR_FILE")"
    # Attempt to fetch prior OCR from HookVault meta if hook ID known
    if [ -n "${HOOK_ID:-}" ]; then
      PRIOR_URL=$(curl -sf "$HV_URL/items/$HOOK_ID" 2>/dev/null \
        | python3 -c "import json,sys; d=json.load(sys.stdin); \
          print(d.get('meta',{}).get('last_ocr_s3_url',''))" 2>/dev/null || echo "")
      [ -n "$PRIOR_URL" ] && curl -sf "$PRIOR_URL" -o "$PRIOR_OCR" 2>/dev/null || true
    fi

    if [ -f "$PRIOR_OCR" ]; then
      DIFF_RESULT=$(curl -sf -X POST "$DF_URL/diff/files" \
        -F "left=@$PRIOR_OCR" -F "right=@$OCR_FILE" 2>/dev/null \
        | python3 -c "import json,sys; d=json.load(sys.stdin); \
          print(f\"ratio={d.get('ratio',0):.2f} +{d.get('additions',0)} -{d.get('deletions',0)}\")" \
        2>/dev/null || echo "?")
      log "diffforge: vs prior version — $DIFF_RESULT"
      rm -f "$PRIOR_OCR" 2>/dev/null || true
    else
      log "diffforge: no prior version found — first ingest"
    fi
  fi
fi

log "DONE $FILE"
