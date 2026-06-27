#!/bin/bash
# inbox-sync.sh — Route all cloud storage files to inbox-idrive-e2/01001-uploads/
# Part of SJL Sovereign Cloud inbox-first routing architecture
# Run via: systemd timer (sjl-inbox-sync.timer) or n8n cron every 15 minutes
#
# REQUIRES: rclone configured with:
#   [idrive-primary] — iDrive E2 primary account
#   [dropbox-fcpx]   — Dropbox FCPXServerSJL@gmail.com
#   [dropbox-sjl]    — Dropbox shannonjlove@mac.com
#   [pcloud-sjl]     — pCloud SJL account
# See: docs/infrastructure/inbox-first-routing.md

set -euo pipefail

INBOX="idrive-primary:inbox-idrive-e2/01001-uploads"
LOG_DIR="/var/log/sjl-inbox-sync"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
LOG_FILE="${LOG_DIR}/sync-${TIMESTAMP}.log"
RCLONE_FLAGS="--no-update-modtime --log-level INFO --stats-one-line --transfers 4"
ERRORS=0

mkdir -p "$LOG_DIR"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

sync_source() {
    local name="$1"
    local remote="$2"
    local dest="${INBOX}/${name}/"

    log "SYNC START: ${name} → ${dest}"

    if rclone copy "${remote}" "${dest}" ${RCLONE_FLAGS} 2>>"$LOG_FILE"; then
        local count
        count=$(rclone size "${dest}" --json 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('count',0))" 2>/dev/null || echo "?")
        log "SYNC OK: ${name} — inbox now has ${count} objects"
    else
        log "SYNC ERROR: ${name} — exit code $?"
        ERRORS=$((ERRORS + 1))
    fi
}

log "=== SJL Inbox Sync Starting ==="

# Dropbox FCPXServerSJL (primary production account)
if rclone listremotes | grep -q "^dropbox-fcpx:"; then
    sync_source "dropbox-fcpx" "dropbox-fcpx:"
else
    log "SKIP: dropbox-fcpx not configured (run: rclone config)"
fi

# Dropbox shannonjlove personal account
if rclone listremotes | grep -q "^dropbox-sjl:"; then
    sync_source "dropbox-sjl" "dropbox-sjl:"
else
    log "SKIP: dropbox-sjl not configured"
fi

# pCloud
if rclone listremotes | grep -q "^pcloud-sjl:"; then
    sync_source "pcloud" "pcloud-sjl:"
else
    log "SKIP: pcloud-sjl not configured"
fi

# MediaFire (handled by separate Python script)
if command -v python3 >/dev/null && [[ -f "$(dirname "$0")/mediafire-inbox-sync.py" ]]; then
    log "SYNC START: mediafire → ${INBOX}/mediafire/"
    if python3 "$(dirname "$0")/mediafire-inbox-sync.py" 2>>"$LOG_FILE"; then
        log "SYNC OK: mediafire"
    else
        log "SYNC ERROR: mediafire — exit code $?"
        ERRORS=$((ERRORS + 1))
    fi
else
    log "SKIP: mediafire-inbox-sync.py not found or python3 unavailable"
fi

log "=== SJL Inbox Sync Complete (errors: ${ERRORS}) ==="

# Rotate logs older than 14 days
find "$LOG_DIR" -name "sync-*.log" -mtime +14 -delete 2>/dev/null || true

exit $ERRORS
