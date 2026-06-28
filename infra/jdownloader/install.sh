#!/usr/bin/env bash
# NOTE: Container registries (docker.io, lscr.io, ghcr.io) return 403 from
# this VPS. Use install-native.sh instead for a working native Java install.
# This file is kept for reference only.
set -euo pipefail

# JDownloader 2 Podman Quadlet install script for shannonjlove.cloud WebTop
# Run as root or with sudo on the VPS

QUADLET_DIR="/etc/containers/systemd"
DATA_DIR="/opt/jdownloader"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "==> Ensuring Podman is installed..."
if ! command -v podman &>/dev/null; then
    apt-get update -y
    apt-get install -y podman
fi

echo "==> Creating data directories..."
mkdir -p "$DATA_DIR/config" "$DATA_DIR/downloads"
chown -R 1000:1000 "$DATA_DIR"

if [ ! -f "$DATA_DIR/.env" ]; then
    echo ""
    echo "  No .env file found at $DATA_DIR/.env"
    echo "  Copy and edit the example file, then re-run:"
    echo ""
    echo "    cp $SCRIPT_DIR/.env.example $DATA_DIR/.env"
    echo "    nano $DATA_DIR/.env"
    echo ""
    exit 1
fi
chmod 600 "$DATA_DIR/.env"

echo "==> Installing Quadlet unit..."
install -m 644 "$SCRIPT_DIR/jdownloader.container" "$QUADLET_DIR/jdownloader.container"

echo "==> Reloading systemd and starting service..."
systemctl daemon-reload
systemctl enable --now jdownloader.service

echo ""
echo "Done! JDownloader 2 is running via Podman Quadlet."
echo "  Status  : systemctl status jdownloader.service"
echo "  Logs    : journalctl -u jdownloader.service -f"
echo "  Web UI  : http://$(hostname -I | awk '{print $1}'):5800"
echo "  MyJDownloader will appear in your mobile app within ~30 seconds."
