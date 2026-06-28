#!/usr/bin/env bash
# PhotoPrism native install — AI photo/video tagging for SJL media pipeline
#
# PhotoPrism watches /data/resources/ and /data/projects/ and applies:
#   - Object + scene + activity AI labels (TensorFlow Lite)
#   - Face detection and clustering
#   - GPS / map integration
#   - Color analysis
#   - XMP sidecar write-back (tags persist with files)
#
# This installs the native binary (no Docker) since container registries may be blocked.
# After install, PhotoPrism is available at: https://pics.shannonjlove.cloud
#
# Requires: NPM proxy entry for port 2342 → pics.shannonjlove.cloud
set -euo pipefail

PP_VERSION="${1:-latest}"
PP_DIR="/opt/photoprism"
PP_DATA="/data/photoprism"
PP_ORIGINALS="/data/resources"
PP_IMPORT="/data/inbox"
PP_USER="photoprism"

echo "==> Installing PhotoPrism (native binary)..."

# Create user
useradd -r -s /bin/false -d "$PP_DATA" "$PP_USER" 2>/dev/null || true

# Create directories
mkdir -p "$PP_DIR" "$PP_DATA/storage" "$PP_DATA/cache" "$PP_DATA/sidecar"
chown -R "$PP_USER:$PP_USER" "$PP_DATA"

# Install system dependencies
apt-get install -y ffmpeg libvips libvips-tools exiftool darktable 2>/dev/null || \
apt-get install -y ffmpeg libvips-tools exiftool 2>/dev/null || true

# Download latest release binary via GitHub API
echo "==> Fetching latest PhotoPrism release..."
RELEASE_URL=$(curl -sf https://api.github.com/repos/photoprism/photoprism/releases/latest \
  | python3 -c "
import json,sys
data = json.load(sys.stdin)
for a in data.get('assets',[]):
    if 'linux-amd64' in a['name'] and a['name'].endswith('.tar.gz'):
        print(a['browser_download_url'])
        break
" 2>/dev/null || echo "")

if [ -z "$RELEASE_URL" ]; then
  echo "ERROR: Could not fetch release URL. Download manually from:"
  echo "  https://github.com/photoprism/photoprism/releases"
  echo "  Extract to $PP_DIR and re-run systemctl enable --now photoprism"
  exit 1
fi

echo "==> Downloading $RELEASE_URL"
curl -L "$RELEASE_URL" -o /tmp/photoprism.tar.gz
tar -xzf /tmp/photoprism.tar.gz -C "$PP_DIR" --strip-components=1
rm /tmp/photoprism.tar.gz
chown -R "$PP_USER:$PP_USER" "$PP_DIR"

# Write environment config
cat > /etc/photoprism/options.env << EOF
PHOTOPRISM_ADMIN_USER=admin
PHOTOPRISM_ADMIN_PASSWORD=SJL-PhotoPrism-2025
PHOTOPRISM_AUTH_MODE=password
PHOTOPRISM_SITE_URL=https://pics.shannonjlove.cloud/
PHOTOPRISM_ORIGINALS_PATH=$PP_ORIGINALS
PHOTOPRISM_IMPORT_PATH=$PP_IMPORT
PHOTOPRISM_STORAGE_PATH=$PP_DATA/storage
PHOTOPRISM_SIDECAR_PATH=$PP_DATA/sidecar
PHOTOPRISM_CACHE_PATH=$PP_DATA/cache
PHOTOPRISM_BACKUP_PATH=$PP_DATA/backup
PHOTOPRISM_HTTP_HOST=127.0.0.1
PHOTOPRISM_HTTP_PORT=2342
PHOTOPRISM_DISABLE_TLS=true
PHOTOPRISM_DEFAULT_TLS=false
PHOTOPRISM_JPEG_QUALITY=92
PHOTOPRISM_DETECT_NSFW=false
PHOTOPRISM_UPLOAD_NSFW=true
PHOTOPRISM_DATABASE_DRIVER=sqlite
PHOTOPRISM_DATABASE_DSN=$PP_DATA/storage/index.db
PHOTOPRISM_WORKERS=2
PHOTOPRISM_WAKEUP_INTERVAL=900
PHOTOPRISM_AUTO_INDEX=300
PHOTOPRISM_AUTO_IMPORT=300
PHOTOPRISM_EXIF_BRUTEFORCE=true
PHOTOPRISM_FACE_SIZE=50
PHOTOPRISM_FACE_SCORE=9
PHOTOPRISM_FACE_OVERLAP=42
PHOTOPRISM_FACE_CLUSTER_SIZE=80
PHOTOPRISM_FACE_CLUSTER_SCORE=15
EOF
chmod 640 /etc/photoprism/options.env
mkdir -p /etc/photoprism

echo "==> Installing systemd service..."
cp "$(dirname "${BASH_SOURCE[0]}")/photoprism.service" /etc/systemd/system/photoprism.service
systemctl daemon-reload
systemctl enable --now photoprism

echo "==> Running initial index..."
sudo -u "$PP_USER" "$PP_DIR/photoprism" index --cleanup 2>&1 | tail -5 || true

echo ""
echo "Done! PhotoPrism is running."
echo "  Web UI  : https://pics.shannonjlove.cloud  (or http://127.0.0.1:2342)"
echo "  Login   : admin / SJL-PhotoPrism-2025  (change after first login)"
echo "  Watching: $PP_ORIGINALS"
echo "  Sidecars: $PP_DATA/sidecar  (XMP tags written here)"
echo ""
echo "Add to NPM: forward pics.shannonjlove.cloud → 127.0.0.1:2342"
echo "CHANGE THE DEFAULT PASSWORD immediately after first login."
