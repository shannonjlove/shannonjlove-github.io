#!/usr/bin/env bash
# Deploy cloud import pipeline on the VPS.
# Prerequisites: rclone configured with dropbox, pcloud, idrive remotes.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FW_SCRIPTS="/opt/filewarden/scripts"
FW_CONFIG="/etc/filewarden/config.yaml"

echo "==> Creating directories..."
mkdir -p /data/staging/dropbox /data/staging/pcloud
mkdir -p /data/archive/dropbox /data/archive/pcloud
mkdir -p /var/log/filewarden
mkdir -p "$FW_SCRIPTS"

echo "==> Installing scripts..."
install -m 755 "$REPO_DIR/scripts/sync-cloud-sources.sh"    "$FW_SCRIPTS/sync-cloud-sources.sh"
install -m 755 "$REPO_DIR/scripts/upload-to-idrive-s3.sh"   "$FW_SCRIPTS/upload-to-idrive-s3.sh"

echo "==> Appending FileWarden rules..."
if [ ! -f "$FW_CONFIG" ]; then
  echo "ERROR: $FW_CONFIG not found. Is FileWarden installed?"
  exit 1
fi

MARKER="# --- cloud-import-rules ---"
if grep -q "$MARKER" "$FW_CONFIG"; then
  echo "    Rules already present, skipping."
else
  echo "" >> "$FW_CONFIG"
  echo "$MARKER" >> "$FW_CONFIG"
  cat "$REPO_DIR/cloud-import-rules.yaml" >> "$FW_CONFIG"
  echo "    Rules appended to $FW_CONFIG"
fi

echo "==> Verifying rclone remotes..."
for REMOTE in dropbox pcloud idrive; do
  if rclone listremotes 2>/dev/null | grep -q "^${REMOTE}:"; then
    echo "    $REMOTE: OK"
  else
    echo "    WARNING: '$REMOTE' remote not found in rclone config"
    echo "             Run: rclone config  (to add it)"
  fi
done

echo "==> Installing systemd units..."
install -m 644 "$REPO_DIR/cloud-import.service" /etc/systemd/system/cloud-import.service
install -m 644 "$REPO_DIR/cloud-import.timer"   /etc/systemd/system/cloud-import.timer
systemctl daemon-reload
systemctl enable --now cloud-import.timer

echo ""
echo "Done! Cloud import pipeline active."
echo "  Runs     : every 15 min via cloud-import.timer"
echo "  Logs     : /var/log/filewarden/cloud-sync.log"
echo "  Status   : systemctl status cloud-import.timer"
echo "  Manual   : systemctl start cloud-import.service"
echo ""
echo "Buckets used (create in iDrive e2 dashboard):"
echo "  sjl-media    — images, video, audio"
echo "  sjl-docs     — documents, PDFs, spreadsheets"
echo "  sjl-archive  — everything else"
