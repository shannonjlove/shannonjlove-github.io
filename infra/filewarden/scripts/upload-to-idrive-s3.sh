#!/usr/bin/env bash
# Called by FileWarden run_script after sjl_rename.
# Uploads a single file to iDrive S3, routing to bucket by MIME type.
#
# Usage: upload-to-idrive-s3.sh <file_path> <source_label>
# Env:   IDRIVE_REMOTE (default: idrive)
#        IDRIVE_BUCKET_MEDIA, IDRIVE_BUCKET_DOCS, IDRIVE_BUCKET_ARCHIVE
set -euo pipefail

FILE="${1:?file path required}"
SOURCE="${2:-unknown}"
REMOTE="${IDRIVE_REMOTE:-idrive}"
LOG="/var/log/filewarden/cloud-sync.log"
STAMP="$(date '+%Y-%m-%d %H:%M:%S')"

log() { echo "[$STAMP] [upload] $*" >> "$LOG"; }

[ ! -f "$FILE" ] && { log "ERROR: $FILE not found"; exit 1; }

# Route to bucket by extension
EXT="${FILE##*.}"
EXT="${EXT,,}"   # lowercase

case "$EXT" in
  jpg|jpeg|png|gif|webp|heic|heif|tiff|bmp|svg|mp4|mov|avi|mkv|webm|m4v|mts|mp3|aac|flac|wav|m4a)
    BUCKET="${IDRIVE_BUCKET_MEDIA:-sjl-media}"
    ;;
  pdf|doc|docx|xls|xlsx|ppt|pptx|txt|md|rtf|pages|numbers|key|csv|json|yaml|yml|xml|html|htm)
    BUCKET="${IDRIVE_BUCKET_DOCS:-sjl-docs}"
    ;;
  *)
    BUCKET="${IDRIVE_BUCKET_ARCHIVE:-sjl-archive}"
    ;;
esac

# Preserve YYYY/MM subdirectory structure in S3
YEAR="$(date -r "$FILE" '+%Y' 2>/dev/null || date '+%Y')"
MONTH="$(date -r "$FILE" '+%m' 2>/dev/null || date '+%m')"
DEST="${REMOTE}:${BUCKET}/${YEAR}/${MONTH}/$(basename "$FILE")"

log "Uploading $FILE → $DEST (source: $SOURCE)"

rclone copyto "$FILE" "$DEST" \
  --s3-no-check-bucket \
  --retries 3 \
  --checksum \
  2>>"$LOG"

EXIT=$?
if [ $EXIT -eq 0 ]; then
  log "OK: $(basename "$FILE") → $DEST"
else
  log "FAILED (exit $EXIT): $FILE"
  exit $EXIT
fi
