#!/usr/bin/env bash
# =============================================================================
# ARTIVC INSTALLER — shannonjlove.cloud
# Installs ArtiVC (Artifact Version Control) for large-file versioning.
# ArtiVC/ArtiVC (https://github.com/shannonjlove/ArtiVC)
#
# ArtiVC provides git-style versioning for large binary files (ML models,
# 3DGS scene files, datasets) stored on cloud backends.
#
# SUPPORTED BACKENDS (SJL-relevant):
#   - AWS S3 / iDrive E2 / any S3-compatible endpoint
#   - Google Cloud Storage
#   - Azure Blob Storage
#   - SSH/SFTP (shannonjlove.cloud direct)
#   - Local filesystem
#   - 40+ via rclone (pCloud, MEGA, Dropbox, MediaFire, etc.)
#
# REQUIREMENTS:
#   - Go 1.17+ (for build from source)
#     OR: pre-built binary download (fallback if Go not found)
#
# SJL USE CASES:
#   - Version 3DGS scene files from LichtFeld Studio (.ply, .splat exports)
#   - Version TagBot ML models (CLIP, BLIP, YOLOv8 weights)
#   - Version large media libraries before migration between clouds
#   - Track dataset versions for AI training runs
#
# INSTALLATION:
#   Source: github.com/shannonjlove/ArtiVC
#   Binary: /usr/local/bin/avc
#   Source dir: /opt/artivc
#
# Usage: bash scripts/install/install-artivc.sh
#
# After install:
#   # Initialize a versioned artifact repository:
#   avc init s3://my-bucket/my-artifact-repo
#
#   # Push current directory's files as a new version:
#   avc push -m "initial 3DGS scene export"
#
#   # Pull the latest version:
#   avc pull
#
#   # List version history:
#   avc log
#
#   # Tag a version:
#   avc tag v1.0
#
#   # Diff between versions:
#   avc diff HEAD~1
#
# SJL S3-compatible (iDrive E2) example:
#   export AWS_ACCESS_KEY_ID=...
#   export AWS_SECRET_ACCESS_KEY=...
#   export AWS_ENDPOINT_URL=https://s3.us-east-1.idrivecloud.io
#   avc init s3://sjlcloud-3dgs/my-scene
#   avc push -m "lichtfeld studio export 32K"
#
# SJL rclone backend example (pCloud, MEGA, Dropbox):
#   avc init rclone://pcloud:@RESOURCES_pcloud/3dgs-scenes
#   avc push
#
# SJL SSH backend example (shannonjlove.cloud):
#   avc init ssh://shannonjlove.cloud/data/artivc/3dgs-scenes
#   avc push
# =============================================================================

set -euo pipefail

REPO="https://github.com/shannonjlove/ArtiVC.git"
INSTALL_DIR="/opt/artivc"
BINARY_NAME="avc"
BINARY_PATH="$INSTALL_DIR/bin/$BINARY_NAME"
LINK_PATH="/usr/local/bin/$BINARY_NAME"

# Fallback: upstream release download if Go is not available
UPSTREAM_RELEASE_URL="https://github.com/InfuseAI/ArtiVC/releases/latest/download"

log() { echo "[$(date '+%H:%M:%S')] $*"; }
die() { echo "ERROR: $*" >&2; exit 1; }

# ---- Go check --------------------------------------------------------------
GO_FOUND=false
GO_CMD=""
if command -v go &>/dev/null; then
    GO_VER=$(go version | awk '{print $3}' | tr -d 'go')
    GO_MAJ=$(echo "$GO_VER" | cut -d. -f1)
    GO_MIN=$(echo "$GO_VER" | cut -d. -f2)
    if [[ "$GO_MAJ" -gt 1 ]] || [[ "$GO_MAJ" -eq 1 && "$GO_MIN" -ge 17 ]]; then
        GO_FOUND=true
        GO_CMD="go"
        log "Go: $(go version | awk '{print $3,$4}')"
    else
        log "WARN: Go $GO_VER found but need >= 1.17 — will try release binary fallback"
    fi
else
    log "WARN: Go not found — will try release binary fallback"
fi

# ---- Clone or update source ------------------------------------------------
if [[ -d "$INSTALL_DIR/.git" ]]; then
    log "Updating existing ArtiVC source at $INSTALL_DIR..."
    git -C "$INSTALL_DIR" fetch origin main 2>/dev/null \
        && git -C "$INSTALL_DIR" merge --ff-only origin/main 2>/dev/null \
        || log "WARN: could not pull — using existing source"
else
    log "Cloning ArtiVC → $INSTALL_DIR..."
    git clone --depth=1 "$REPO" "$INSTALL_DIR"
fi

# ---- Build or download binary ----------------------------------------------
mkdir -p "$INSTALL_DIR/bin"

if [[ "$GO_FOUND" == true ]]; then
    log "Building ArtiVC from source (go build)..."
    cd "$INSTALL_DIR"

    GIT_COMMIT=$(git rev-parse HEAD 2>/dev/null || echo "unknown")
    GIT_TAG=$(git describe --tags --abbrev=0 --exact-match 2>/dev/null || echo "")
    GIT_DIRTY=$(test -n "$(git status --porcelain 2>/dev/null)" && echo "dirty" || echo "clean")
    VERSION="${GIT_TAG:-dev}"

    LDFLAGS="-X github.com/infuseai/artivc/cmd.tagVersion=${VERSION}"
    LDFLAGS+=" -X github.com/infuseai/artivc/cmd.gitCommit=${GIT_COMMIT}"
    LDFLAGS+=" -X github.com/infuseai/artivc/cmd.gitTreeState=${GIT_DIRTY}"
    LDFLAGS+=" -s -w"

    "$GO_CMD" build -o "$BINARY_PATH" -ldflags "$LDFLAGS" main.go
    log "Build complete: $BINARY_PATH"
else
    # Fallback: download pre-built release binary from upstream InfuseAI releases
    log "Downloading pre-built ArtiVC binary from upstream releases..."

    OS="$(uname -s | tr '[:upper:]' '[:lower:]')"
    ARCH="$(uname -m)"
    case "$ARCH" in
        x86_64) ARCH="amd64" ;;
        aarch64|arm64) ARCH="arm64" ;;
        *) die "Unsupported architecture: $ARCH — install Go 1.17+ and re-run" ;;
    esac

    ASSET_NAME="artivc_${OS}_${ARCH}.tar.gz"
    DOWNLOAD_URL="${UPSTREAM_RELEASE_URL}/${ASSET_NAME}"
    TMP_DIR=$(mktemp -d)

    log "Downloading: $DOWNLOAD_URL"
    curl -fsSL "$DOWNLOAD_URL" -o "$TMP_DIR/$ASSET_NAME" \
        || die "Download failed — install Go 1.17+ and re-run for source build"

    tar -xzf "$TMP_DIR/$ASSET_NAME" -C "$TMP_DIR"
    mv "$TMP_DIR/$BINARY_NAME" "$BINARY_PATH" 2>/dev/null \
        || mv "$TMP_DIR/avc" "$BINARY_PATH" 2>/dev/null \
        || die "Could not find 'avc' binary in release archive"

    rm -rf "$TMP_DIR"
    log "Downloaded binary: $BINARY_PATH"
fi

chmod +x "$BINARY_PATH"

# ---- Symlink to /usr/local/bin ---------------------------------------------
ln -sf "$BINARY_PATH" "$LINK_PATH" 2>/dev/null \
    || log "WARN: could not symlink to $LINK_PATH (need root?)"

# ---- Verify installation ---------------------------------------------------
if command -v "$BINARY_NAME" &>/dev/null; then
    AVC_VER=$("$BINARY_NAME" version 2>/dev/null || echo "installed")
    log "ArtiVC installed: $AVC_VER"
else
    log "WARN: $BINARY_NAME not found in PATH — add $INSTALL_DIR/bin to PATH manually"
fi

# ---- rclone check (needed for 40+ extra backends) -------------------------
if ! command -v rclone &>/dev/null; then
    log "NOTE: rclone not found — install it for pCloud/MEGA/Dropbox/MediaFire backends:"
    log "      curl https://rclone.org/install.sh | sudo bash"
    log "      Then: rclone config (add pcloud, mega, dropbox, etc.)"
fi

# ---- Usage summary ---------------------------------------------------------
echo ""
echo "================================================================"
echo "ArtiVC installed at: $BINARY_PATH"
echo "Binary: avc (symlinked to $LINK_PATH)"
echo ""
echo "Artifact version control for large files."
echo "Use for 3DGS scenes, ML models, media libraries."
echo ""
echo "-- QUICK START --"
echo ""
echo "Initialize a repository on a backend:"
echo "  # S3 / iDrive E2:"
echo "  avc init s3://sjlcloud-3dgs/my-scene-repo"
echo ""
echo "  # SSH (shannonjlove.cloud):"
echo "  avc init ssh://shannonjlove.cloud/data/artivc/3dgs"
echo ""
echo "  # rclone (pCloud, MEGA, Dropbox):"
echo "  avc init rclone://pcloud:@RESOURCES_pcloud/3dgs-scenes"
echo "  avc init rclone://mega:@RESOURCES_mega/ml-models"
echo ""
echo "  # Local filesystem:"
echo "  avc init /data/artivc/tagbot-models"
echo ""
echo "Workflow:"
echo "  avc push -m 'lichtfeld studio 32K export'  # snapshot current dir"
echo "  avc log                                     # show version history"
echo "  avc pull                                    # get latest version"
echo "  avc pull HEAD~1                             # get previous version"
echo "  avc tag v1.0                                # tag a version"
echo "  avc diff HEAD~1                             # diff two versions"
echo "  avc status                                  # show changed files"
echo ""
echo "iDrive E2 (S3-compatible) setup:"
echo "  export AWS_ACCESS_KEY_ID=..."
echo "  export AWS_SECRET_ACCESS_KEY=..."
echo "  export AWS_ENDPOINT_URL=https://s3.us-east-1.idrivecloud.io"
echo "  avc init s3://sjlcloud-3dgs/scene-name"
echo ""
echo "rclone setup (pCloud, MEGA, Dropbox, MediaFire):"
echo "  rclone config  # add pcloud, mega, dropbox, etc."
echo "  avc init rclone://pcloud:@RESOURCES_pcloud/3dgs-scenes"
echo ""
echo "Source: $INSTALL_DIR"
echo "================================================================"
