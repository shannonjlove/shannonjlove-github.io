#!/usr/bin/env bash
# Called by FileWarden after tag-and-analyze.sh, uploads file + sidecars to iDrive E2.
#
# Usage: upload-to-idrive-s3.sh <file_path> <para_category>
#   para_category: resources | areas | projects | archive
#
# Bucket map (matches existing iDrive E2 structure):
#   resources + photo ext  → shannon-photos-e2/06011-organized/YYYY/MM/
#   resources + video ext  → video-media-e2/06020-raw-footage/YYYY/MM/
#   resources + graphic    → graphics-media-e2/06030-brand-assets/YYYY/MM/
#   resources + document   → paperless-docs-e2/documents/YYYY/MM/
#   resources + audio/misc → resources-idrive-e2/YYYY/MM/
#   areas                  → areas-idrive-e2/YYYY/MM/
#   projects               → projects-idrive-e2/YYYY/MM/
#   archive                → archives-idrive-e2/YYYY/MM/
set -euo pipefail

FILE="${1:?file path required}"
PARA="${2:-resources}"
REMOTE="${IDRIVE_REMOTE:-idrive}"
LOG="/var/log/filewarden/cloud-sync.log"
STAMP="$(date '+%Y-%m-%d %H:%M:%S')"

log() { echo "[$STAMP] [upload] $*" >> "$LOG"; }

[ ! -f "$FILE" ] && { log "ERROR: $FILE not found"; exit 1; }

EXT="${FILE##*.}"
EXT="${EXT,,}"

# Determine bucket and subfolder by PARA category + file type
case "$PARA" in
  resources)
    case "$EXT" in
      jpg|jpeg|png|gif|webp|heic|heif|tiff|bmp|raw|cr2|nef|arw|dng|orf|rw2|srw)
        BUCKET="shannon-photos-e2"; SUBDIR="06011-organized" ;;
      mp4|mov|avi|mkv|webm|m4v|mts|m2ts|wmv|flv|vob|ogv)
        BUCKET="video-media-e2";    SUBDIR="06020-raw-footage" ;;
      ai|psd|indd|sketch|xd|afdesign|eps|svg|cdr|fig)
        BUCKET="graphics-media-e2"; SUBDIR="06030-brand-assets" ;;
      pdf|doc|docx|xls|xlsx|ppt|pptx|odt|ods|odp|pages|numbers|key|rtf)
        BUCKET="paperless-docs-e2"; SUBDIR="documents" ;;
      *)
        BUCKET="resources-idrive-e2"; SUBDIR="04001-reference-materials" ;;
    esac ;;
  areas)   BUCKET="areas-idrive-e2";    SUBDIR="03001-infrastructure-and-ops" ;;
  projects) BUCKET="projects-idrive-e2"; SUBDIR="02001-web-projects" ;;
  archive) BUCKET="archives-idrive-e2"; SUBDIR="05003-document-archives" ;;
  *)       BUCKET="resources-idrive-e2"; SUBDIR="04001-reference-materials" ;;
esac

YEAR="$(date -r "$FILE" '+%Y' 2>/dev/null || date '+%Y')"
MONTH="$(date -r "$FILE" '+%m' 2>/dev/null || date '+%m')"
BASE="$(basename "$FILE")"
PREFIX="${BUCKET}/${SUBDIR}/${YEAR}/${MONTH}"

upload_file() {
  local src="$1" dest="${REMOTE}:${PREFIX}/$(basename "$1")"
  [ -f "$src" ] || return 0
  log "→ $dest"
  rclone copyto "$src" "$dest" \
    --s3-no-check-bucket \
    --retries 3 \
    --checksum \
    2>>"$LOG"
}

log "Uploading [$PARA] $FILE → $BUCKET/$SUBDIR/$YEAR/$MONTH/"

upload_file "$FILE"

# Upload sidecars alongside the main file
for SIDECAR in \
    "${FILE%.*}.meta.json" \
    "${FILE%.*}.ffprobe.json" \
    "${FILE%.*}.acoustid.json" \
    "${FILE%.*}.ocr.txt"; do
  upload_file "$SIDECAR"
done

log "OK: $BASE → $BUCKET"
