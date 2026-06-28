#!/usr/bin/env bash
# Pull files from Dropbox and pCloud into staging dirs via rclone.
# Run by cloud-import.timer every 15 minutes.
set -euo pipefail

LOG="/var/log/filewarden/cloud-sync.log"
STAMP="$(date '+%Y-%m-%d %H:%M:%S')"

log() { echo "[$STAMP] $*" | tee -a "$LOG"; }

mkdir -p /data/staging/dropbox /data/staging/pcloud "$(dirname "$LOG")"

RCLONE_OPTS=(
  --transfers 4
  --checkers 8
  --retries 3
  --low-level-retries 3
  --stats 0
  --log-level ERROR
  --log-file "$LOG"
)

log "==> Syncing Dropbox → /data/staging/dropbox/"
rclone sync dropbox: /data/staging/dropbox/ "${RCLONE_OPTS[@]}" \
  --exclude "**/.dropbox" \
  --exclude "**/.dropbox.cache/**" \
  && log "    Dropbox sync OK" \
  || log "    Dropbox sync FAILED (exit $?)"

log "==> Syncing pCloud → /data/staging/pcloud/"
rclone sync pcloud: /data/staging/pcloud/ "${RCLONE_OPTS[@]}" \
  && log "    pCloud sync OK" \
  || log "    pCloud sync FAILED (exit $?)"

log "==> Running FileWarden on staging dirs..."
python3 /opt/filewarden/filewarden.py \
  --once \
  --config /etc/filewarden/config.yaml \
  --watch /data/staging/dropbox \
  --watch /data/staging/pcloud \
  2>>"$LOG" \
  && log "    FileWarden pass OK" \
  || log "    FileWarden pass FAILED (exit $?)"

log "==> Done."
