#!/usr/bin/env bash
# =============================================================================
# GOURCE INSTALLER — shannonjlove.cloud
# Builds Gource from shannonjlove/Gource (acaudwell/Gource fork).
# Gource visualizes git repository history as an animated tree.
#
# Usage: sudo bash scripts/install/install-gource.sh
# After install: gource /path/to/git/repo
# =============================================================================

set -euo pipefail

GOURCE_REPO="https://github.com/shannonjlove/Gource.git"
INSTALL_DIR="/opt/gource-src"

log()  { echo "[$(date '+%H:%M:%S')] $*"; }
die()  { echo "ERROR: $*" >&2; exit 1; }

# ---- Check if already installed --------------------------------------------
if command -v gource &>/dev/null; then
    CURRENT=$(gource --version 2>/dev/null || echo "unknown")
    log "gource already installed: $CURRENT"
    read -rp "Reinstall/upgrade? [y/N] " yn
    [[ "${yn,,}" == "y" ]] || exit 0
fi

# ---- Build dependencies (Debian/Ubuntu) ------------------------------------
if command -v apt-get &>/dev/null; then
    log "Installing build dependencies..."
    apt-get update -qq
    apt-get install -y \
        build-essential automake autoconf \
        libsdl2-dev \
        libgraphicsmagick++1-dev \
        libfreetype-dev \
        libpcre2-dev \
        libpng-dev \
        libglm-dev \
        libboost-dev \
        libboost-filesystem-dev \
        git 2>/dev/null | tail -5

    # ftgl may be packaged differently
    apt-get install -y libftgl-dev 2>/dev/null \
        || apt-get install -y libglew-dev 2>/dev/null \
        || log "WARN: libftgl-dev/libglew-dev not found — build may fail"
fi

# ---- Clone or update source ------------------------------------------------
if [[ -d "$INSTALL_DIR/.git" ]]; then
    log "Updating existing source at $INSTALL_DIR..."
    git -C "$INSTALL_DIR" pull --ff-only origin master 2>/dev/null \
        || git -C "$INSTALL_DIR" pull --ff-only origin main 2>/dev/null \
        || log "WARN: could not pull — using existing source"
else
    log "Cloning $GOURCE_REPO → $INSTALL_DIR..."
    git clone --depth=1 "$GOURCE_REPO" "$INSTALL_DIR"
fi

cd "$INSTALL_DIR"

# ---- Build -----------------------------------------------------------------
log "Running autogen.sh..."
./autogen.sh

log "Running configure..."
./configure --prefix=/usr/local

log "Building (this takes 1–3 minutes)..."
make -j"$(nproc)"

log "Installing..."
make install

gource --version && log "gource installed: $(gource --version)"

# ---- Quick usage tip -------------------------------------------------------
echo ""
echo "================================================================"
echo "Gource is installed. Usage examples:"
echo ""
echo "  # Visualize current git repo (opens window)"
echo "  gource"
echo ""
echo "  # Render to MP4 (requires ffmpeg)"
echo "  gource -1280x720 -o - | ffmpeg -y -r 60 -f image2pipe \\"
echo "    -vcodec ppm -i - -vcodec libx264 -preset fast \\"
echo "    -pix_fmt yuv420p -crf 18 gource.mp4"
echo ""
echo "  # Generate git log for a specific repo"
echo "  gource --output-custom-log gource.log /path/to/repo"
echo "================================================================"
