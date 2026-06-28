#!/usr/bin/env bash
# Install all tagging and analysis dependencies for the SJL pipeline.
# Run once on the VPS as root.
set -euo pipefail

echo "==> System packages..."
apt-get update -qq
apt-get install -y \
  libimage-exiftool-perl \
  ffmpeg \
  poppler-utils \
  tesseract-ocr \
  tesseract-ocr-eng \
  libchromaprint-tools \
  python3-pip \
  python3-mutagen \
  uuidgen

echo "==> Python libraries..."
pip3 install -q \
  mutagen \
  beets \
  python-docx \
  openpyxl \
  requests

echo "==> Beets config..."
BEETS_CFG="${HOME}/.config/beets/config.yaml"
mkdir -p "$(dirname "$BEETS_CFG")"
if [ ! -f "$BEETS_CFG" ]; then
  REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  # Look for beets config in repo
  BEETS_SRC="$(realpath "$REPO_DIR/../../../beets/config.yaml" 2>/dev/null || echo '')"
  if [ -f "$BEETS_SRC" ]; then
    cp "$BEETS_SRC" "$BEETS_CFG"
    echo "    Beets config installed from repo"
  else
    cat > "$BEETS_CFG" << 'BEETS'
directory: /data/resources/audio
library: /var/lib/beets/musiclibrary.db
import:
  move: no
  copy: no
  write: yes
  quiet: yes
  timid: no
plugins: fetchart acousticbrainz chroma lastgenre scrub
match:
  strong_rec_thresh: 0.10
  medium_rec_thresh: 0.25
acoustid:
  apikey: 8XaBELgH
BEETS
    echo "    Beets config written (default)"
  fi
fi

echo "==> Verifying tools..."
for CMD in exiftool ffprobe ffmpeg pdftotext tesseract fpcalc beet; do
  if command -v "$CMD" >/dev/null 2>&1; then
    echo "    $CMD: OK"
  else
    echo "    WARNING: $CMD not found"
  fi
done

echo ""
echo "Done! Tagging pipeline ready."
echo "  Test: bash /opt/filewarden/scripts/tag-and-analyze.sh /path/to/file"
echo "  Log:  /var/log/filewarden/tagging.log"
