#!/usr/bin/env bash
# =============================================================================
# SJL FILE PROCESSOR — Hazel "Run Shell Script" action
# Shannon J. Love | shannonjlove.cloud
#
# Triggered by Hazel when a file lands in any @INBOX_[cloud] folder.
# Performs: IDENTIFY → RENAME (SJL) → EXIF WRITE → XMP SIDECAR →
#           HOOKMARK BOOKMARK → RAINDROP ENTRY
#
# Usage: Called by Hazel with $1 = full POSIX path to the file.
#        Store at: ~/Library/Application Scripts/Hazel/sjl-process.sh
#        chmod +x ~/Library/Application\ Scripts/Hazel/sjl-process.sh
#
# Dependencies: exiftool, python3, curl, jq, osascript (Hookmark)
# =============================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# CONFIGURATION — edit these
# ---------------------------------------------------------------------------
RAINDROP_TOKEN="YOUR_RAINDROP_API_TOKEN"   # Raindrop.io API token
INBOX_COLLECTION_ID="0"                    # Raindrop @INBOX collection numeric ID
SJL_OWNER="Shannon J. Love"
SJL_EMAIL="sjlove@shannonjeffreylove.com"
LOG_FILE="$HOME/Library/Logs/sjl-hazel.log"

# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------
log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"; }

die() { log "ERROR: $*"; exit 1; }

# Detect cloud from parent folder path
detect_cloud() {
    local path="$1"
    case "$path" in
        *iCloud*)                cloud="icloud"  ;;
        *Dropbox/Business*|*dropbox-biz*) cloud="dropbox-biz" ;;
        *Dropbox*)               cloud="dropbox" ;;
        *Google\ Drive*)         cloud="gdrive"  ;;
        *pCloud*)                cloud="pcloud"  ;;
        *MEGA*)                  cloud="mega"    ;;
        *MediaFire*)             cloud="mediafire" ;;
        *shannonjlove.cloud*)    cloud="sjlcloud" ;;
        *)                       cloud="icloud"  ;;  # default: iCloud
    esac
    echo "$cloud"
}

# Detect PARA bucket from parent folder path
detect_para() {
    local path="$1"
    case "$path" in
        *@PROJECTS*) echo "projects"  ;;
        *@AREAS*)    echo "areas"     ;;
        *@RESOURCES*)echo "resources" ;;
        *@ARCHIVES*) echo "archives"  ;;
        *)           echo "inbox"     ;;
    esac
}

# Map file extension to SJL category + subcategory
detect_category() {
    local ext="${1,,}"   # lowercase
    case "$ext" in
        jpg|jpeg|heic|heif|webp|tif|tiff|png|gif|bmp|avif)
            echo "media image" ;;
        mp4|mov|m4v|mkv|avi|wmv|webm|mts|m2ts)
            echo "media video" ;;
        mp3|aac|m4a|wav|flac|ogg|opus|aiff)
            echo "media audio" ;;
        cr2|cr3|arw|nef|dng|raf|rw2|orf|pef|srw)
            echo "media raw" ;;
        pdf)
            echo "document pdf" ;;
        doc|docx|rtf|odt)
            echo "document text" ;;
        xls|xlsx|csv|ods)
            echo "document spreadsheet" ;;
        ppt|pptx|key|odp)
            echo "document presentation" ;;
        txt|md|markdown)
            echo "document text" ;;
        sh|py|js|ts|rb|go|rs|swift|pl|php|html|css|json|yaml|yml|toml)
            echo "code script" ;;
        zip|tar|gz|bz2|7z|rar)
            echo "archive backup" ;;
        *)
            echo "general file" ;;
    esac
}

# Build a clean description from the original filename (strip ext, spaces → hyphens, lowercase, max 40 chars)
filename_to_desc() {
    local base="$1"
    base="${base%.*}"                          # strip extension
    base="${base// /-}"                        # spaces to hyphens
    base="${base//_/-}"                        # underscores to hyphens
    base=$(echo "$base" | tr '[:upper:]' '[:lower:]')   # lowercase
    base=$(echo "$base" | sed 's/[^a-z0-9-]//g')        # strip non-alphanumeric except hyphen
    base=$(echo "$base" | sed 's/--*/-/g')               # collapse multiple hyphens
    base="${base:0:40}"                        # max 40 chars
    base="${base%-}"                           # strip trailing hyphen
    echo "$base"
}

# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
FILE="${1:?No file argument passed by Hazel}"
[[ -f "$FILE" ]] || die "File not found: $FILE"

DIR="$(dirname "$FILE")"
BASENAME="$(basename "$FILE")"
EXT="${BASENAME##*.}"
EXT_LOWER="${EXT,,}"

log "=== Processing: $BASENAME ==="

# Step 1 — IDENTIFY
CLOUD=$(detect_cloud "$DIR")
PARA=$(detect_para "$DIR")
read -r CATEGORY SUBCATEGORY <<< "$(detect_category "$EXT_LOWER")"

log "Cloud: $CLOUD | PARA: $PARA | Cat: $CATEGORY-$SUBCATEGORY"

# Step 2 — DATE (use EXIF DateTimeOriginal, fallback to file birth date)
EXIF_DATE=$(exiftool -d '%Y-%m-%d_%H-%M' -DateTimeOriginal -s3 "$FILE" 2>/dev/null || true)
if [[ -z "$EXIF_DATE" || "$EXIF_DATE" == "-" ]]; then
    # macOS: use file birth date
    BIRTH=$(GetFileInfo -d "$FILE" 2>/dev/null | awk '{print $1, $2}' || true)
    if [[ -n "$BIRTH" ]]; then
        EXIF_DATE=$(date -jf "%m/%d/%Y %H:%M:%S" "$BIRTH" '+%Y-%m-%d_%H-%M' 2>/dev/null || date '+%Y-%m-%d_%H-%M')
    else
        EXIF_DATE=$(date '+%Y-%m-%d_%H-%M')
    fi
fi
DATE_SEGMENT="$EXIF_DATE"

# Step 3 — UUID24
UUID24=$(python3 -c "import uuid; print(uuid.uuid4().hex[:24])")
log "UUID24: $UUID24"

# Step 4 — DESCRIPTION (from original filename; TagBot enriches later)
DESC=$(filename_to_desc "$BASENAME")
[[ -z "$DESC" || "$DESC" == "-" ]] && DESC="file"

# Step 5 — BUILD SJL FILENAME
SJL_NAME="${DATE_SEGMENT}_${CATEGORY}-${SUBCATEGORY}_${DESC}_${UUID24}.${EXT_LOWER}"
SJL_PATH="${DIR}/${SJL_NAME}"

log "New name: $SJL_NAME"

# Step 6 — WRITE SJL XMP FIELDS into the file before rename
PROCESSED_UTC=$(date -u '+%Y-%m-%dT%H:%M:%SZ')

exiftool -overwrite_original -q \
    -XMP-xmp:Identifier="$UUID24" \
    -XMP:SJLuuid24="$UUID24" \
    -XMP:SJLparabucket="$PARA" \
    -XMP:SJLcloud="$CLOUD" \
    -XMP:SJLprocessed="$PROCESSED_UTC" \
    -XMP:SJLowner="$SJL_OWNER" \
    -IPTC:Keywords+="sjl" \
    -IPTC:Keywords+="$CLOUD" \
    -IPTC:Keywords+="$CATEGORY" \
    -IPTC:Keywords+="$SUBCATEGORY" \
    -IPTC:Keywords+="$PARA" \
    "$FILE" 2>/dev/null || log "WARN: ExifTool write skipped (may be unsupported type)"

# Step 7 — RENAME
mv "$FILE" "$SJL_PATH"
log "Renamed → $SJL_NAME"

# Step 8 — CREATE XMP SIDECAR (alongside renamed file)
XMP_SIDECAR="${DIR}/${SJL_NAME%.*}.xmp"
exiftool -overwrite_original -q \
    -o "$XMP_SIDECAR" \
    -tagsfromfile "$SJL_PATH" \
    -all:all \
    "$SJL_PATH" 2>/dev/null || true
[[ -f "$XMP_SIDECAR" ]] && log "XMP sidecar: ${SJL_NAME%.*}.xmp"

# Step 9 — HOOKMARK BOOKMARK via AppleScript
# Creates a Hookmark bookmark for the file. To hook to a project hub,
# set PROJECT_HUB_PATH to the hub file/folder; leave empty to skip bidirectional hook.
PROJECT_HUB_PATH=""    # e.g. "/Users/shannon/iCloud Drive/@PROJECTS_icloud/Project-Name_PROJECTS_icloud"

HOOKMARK_RESULT=$(osascript <<APPLESCRIPT 2>/dev/null || true
tell application "Hook"
    -- Bookmark the new SJL file
    set sjlFile to POSIX file "$SJL_PATH" as alias
    set fileBM to bookmark from file sjlFile
    set fileName to name of fileBM
    set fileAddr to address of fileBM

    -- If a project hub is set, hook the file to the hub bidirectionally
    set hubPath to "$PROJECT_HUB_PATH"
    if hubPath is not "" then
        set hubFile to POSIX file hubPath as alias
        set hubBM to bookmark from file hubFile
        hook bookmark fileBM to bookmark hubBM
    end if

    return fileAddr & "|" & fileName
end tell
APPLESCRIPT
)

HOOKMARK_URL=""
if [[ -n "$HOOKMARK_RESULT" ]]; then
    HOOKMARK_URL=$(echo "$HOOKMARK_RESULT" | cut -d'|' -f1)
    log "Hookmark bookmark: $HOOKMARK_URL"
fi

# Step 10 — RAINDROP.IO ENTRY
if [[ "$RAINDROP_TOKEN" != "YOUR_RAINDROP_API_TOKEN" ]]; then
    # Determine Raindrop collection ID based on PARA bucket
    # Set your actual numeric Raindrop collection IDs here
    case "$PARA" in
        projects)  RD_COLLECTION_ID="INSERT_PROJECTS_ID"  ;;
        areas)     RD_COLLECTION_ID="INSERT_AREAS_ID"     ;;
        resources) RD_COLLECTION_ID="INSERT_RESOURCES_ID" ;;
        archives)  RD_COLLECTION_ID="INSERT_ARCHIVES_ID"  ;;
        *)         RD_COLLECTION_ID="$INBOX_COLLECTION_ID" ;;
    esac

    # Use Hookmark URL as the link if available, else file:// URI
    if [[ -n "$HOOKMARK_URL" ]]; then
        LINK_URL="$HOOKMARK_URL"
    else
        LINK_URL="file://$(python3 -c "import urllib.parse, sys; print(urllib.parse.quote('$SJL_PATH', safe='/:'))")"
    fi

    UNIVERSAL_LINK="https://hook.shannonjlove.cloud/open?id=${UUID24}"
    MARKDOWN_LINK="[${SJL_NAME}](${LINK_URL})"
    SEARCH_LINK="hook://search?q=${UUID24}"
    EXCERPT="Cloud: ${CLOUD} | PARA: ${PARA} | Cat: ${CATEGORY}-${SUBCATEGORY} | UUID: ${UUID24}"

    RD_PAYLOAD=$(python3 -c "
import json, sys
payload = {
    'link':      '$LINK_URL',
    'title':     '$SJL_NAME',
    'excerpt':   '$EXCERPT',
    'note':      'Universal: $UNIVERSAL_LINK\nMarkdown: $MARKDOWN_LINK\nSearch: $SEARCH_LINK',
    'tags':      ['sjl', '$CLOUD', '$CATEGORY', '$SUBCATEGORY', '$PARA'],
    'collection':{'\\$id': int('$RD_COLLECTION_ID')}
}
print(json.dumps(payload))
")

    RD_RESPONSE=$(curl -sf -X POST "https://api.raindrop.io/rest/v1/raindrop" \
        -H "Authorization: Bearer ${RAINDROP_TOKEN}" \
        -H "Content-Type: application/json" \
        -d "$RD_PAYLOAD" 2>/dev/null || true)

    RD_ID=$(echo "$RD_RESPONSE" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('item',{}).get('_id',''))" 2>/dev/null || true)
    [[ -n "$RD_ID" ]] && log "Raindrop entry: https://app.raindrop.io/my/$RD_ID"
fi

# ---------------------------------------------------------------------------
# DONE — output the new path for Hazel logging
# ---------------------------------------------------------------------------
log "=== Done: $SJL_PATH ==="
echo "$SJL_PATH"
