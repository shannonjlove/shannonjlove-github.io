#!/usr/bin/env bash
# JDownloader 2 — native Java install for shannonjlove.cloud VPS
# Bypasses container registries; runs as a systemd service under root.
# Usage: bash install-native.sh [--email EMAIL --password PASS --device NAME]
set -euo pipefail

INSTALL_DIR="/opt/jdownloader"
SERVICE_SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/jdownloader-native.service"
SERVICE_DEST="/etc/systemd/system/jdownloader.service"

# ── Parse optional CLI args ───────────────────────────────────────────────────
MJD_EMAIL=""
MJD_PASSWORD=""
MJD_DEVICE="SJL-VPS"

while [[ $# -gt 0 ]]; do
  case $1 in
    --email)    MJD_EMAIL="$2";    shift 2 ;;
    --password) MJD_PASSWORD="$2"; shift 2 ;;
    --device)   MJD_DEVICE="$2";   shift 2 ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

# ── 1. Java ───────────────────────────────────────────────────────────────────
if ! command -v java &>/dev/null; then
  echo "==> Installing Java..."
  apt-get update -y
  apt-get install -y default-jre
fi
echo "==> Java: $(java -version 2>&1 | head -1)"

# ── 2. wget ───────────────────────────────────────────────────────────────────
if ! command -v wget &>/dev/null; then
  apt-get install -y wget
fi

# ── 3. Directories ────────────────────────────────────────────────────────────
mkdir -p "$INSTALL_DIR"

# ── 4. Download installer ─────────────────────────────────────────────────────
JAR="$INSTALL_DIR/JDownloader.jar"
if [ ! -f "$JAR" ]; then
  echo "==> Downloading JDownloader installer..."
  wget -q --show-progress \
    -O "$JAR" \
    "https://installer.jdownloader.org/JDownloader.jar"
fi

# ── 5. Run installer (headless) ───────────────────────────────────────────────
# JDownloader.jar is both installer and launcher on Linux.
# On first run it self-updates and downloads Core.jar + plugins.
# JDownloader2.jar is NOT created on Linux — JDownloader.jar is always used.
APP_JAR="$INSTALL_DIR/Core.jar"
if [ ! -f "$APP_JAR" ]; then
  echo "==> Running JDownloader installer (headless — this may take 1-2 min)..."
  java -Djava.awt.headless=true \
       -jar "$JAR" \
       -norestart \
       -noexternalreset \
       2>&1 | tee /tmp/jd-install.log || true
  # Installer exits non-zero even on success; check for Core.jar
  if [ ! -f "$APP_JAR" ]; then
    echo ""
    echo "ERROR: Core.jar not found after install."
    echo "       Install log: /tmp/jd-install.log"
    exit 1
  fi
  echo "==> Installer complete."
fi

# ── 6. MyJDownloader credentials ─────────────────────────────────────────────
CFG_DIR="$INSTALL_DIR/cfg"
mkdir -p "$CFG_DIR"
MJD_CFG="$CFG_DIR/org.jdownloader.api.myjdownloader.MyJDownloaderSettings.json"

if [ ! -f "$MJD_CFG" ] || [ -n "$MJD_EMAIL" ]; then
  if [ -z "$MJD_EMAIL" ]; then
    echo ""
    read -rp "  MyJDownloader email    : " MJD_EMAIL
    read -rp "  MyJDownloader password : " MJD_PASSWORD
    read -rp "  Device name [$MJD_DEVICE]: " _dev
    MJD_DEVICE="${_dev:-$MJD_DEVICE}"
  fi
  cat > "$MJD_CFG" <<JSON
{
  "email"      : "${MJD_EMAIL}",
  "password"   : "${MJD_PASSWORD}",
  "devicename" : "${MJD_DEVICE}",
  "autoconnect": true
}
JSON
  chmod 600 "$MJD_CFG"
  echo "==> MyJDownloader credentials written."
fi

# ── 7. Install systemd service ────────────────────────────────────────────────
echo "==> Installing systemd service..."
if [ -f "$SERVICE_SRC" ]; then
  install -m 644 "$SERVICE_SRC" "$SERVICE_DEST"
else
  # Write inline if repo file isn't present
  cat > "$SERVICE_DEST" <<'UNIT'
[Unit]
Description=JDownloader 2
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
ExecStart=/usr/bin/java -Djava.awt.headless=true -jar /opt/jdownloader/JDownloader.jar -norestart
WorkingDirectory=/opt/jdownloader
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
UNIT
fi

systemctl daemon-reload
systemctl enable jdownloader.service
systemctl restart jdownloader.service

echo ""
echo "Done! JDownloader 2 is running."
echo "  Status : systemctl status jdownloader.service"
echo "  Logs   : journalctl -u jdownloader.service -f"
echo "  MyJDownloader will appear in the mobile app within ~30 seconds."
