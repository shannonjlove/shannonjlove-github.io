#!/usr/bin/env bash
set -euo pipefail

# JDownloader 2 install script for shannonjlove.cloud WebTop
# Run as root or with sudo on the VPS

INSTALL_DIR="/opt/jdownloader"
COMPOSE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "==> Creating data directories..."
mkdir -p "$INSTALL_DIR/config" "$INSTALL_DIR/downloads"
chown -R 1000:1000 "$INSTALL_DIR"

echo "==> Ensuring Docker & Compose plugin are installed..."
if ! command -v docker &>/dev/null; then
    apt-get update -y
    apt-get install -y ca-certificates curl gnupg lsb-release
    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
        gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
      https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | \
      tee /etc/apt/sources.list.d/docker.list > /dev/null
    apt-get update -y
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    systemctl enable --now docker
fi

if [ ! -f "$COMPOSE_DIR/.env" ]; then
    echo ""
    echo "  No .env file found. Creating one from .env.example..."
    cp "$COMPOSE_DIR/.env.example" "$COMPOSE_DIR/.env"
    echo ""
    echo "  !! Edit $COMPOSE_DIR/.env with your MyJDownloader credentials, then re-run this script."
    echo ""
    exit 1
fi

echo "==> Pulling latest JDownloader 2 image..."
docker compose -f "$COMPOSE_DIR/docker-compose.yml" --env-file "$COMPOSE_DIR/.env" pull

echo "==> Starting JDownloader 2..."
docker compose -f "$COMPOSE_DIR/docker-compose.yml" --env-file "$COMPOSE_DIR/.env" up -d

echo ""
echo "Done! JDownloader 2 is running."
echo "  Web UI : http://$(hostname -I | awk '{print $1}'):5800"
echo "  MyJDownloader will appear in your mobile app within ~30 seconds."
