#!/usr/bin/env bash
# =============================================================================
# GVM INSTALLER — shannonjlove.cloud
# Installs Go Version Manager from shannonjlove/gvm (moovweb/gvm fork)
# then bootstraps Go (binary 1.4 → latest).
#
# Run as the user who will own the Go installations (not root).
# Usage: bash scripts/install/install-gvm.sh [go-version]
#        Default go-version: go1.23.0
# =============================================================================

set -euo pipefail

GO_VERSION="${1:-go1.23.0}"
GVM_REPO="https://github.com/shannonjlove/gvm.git"

log() { echo "[$(date '+%H:%M:%S')] $*"; }
die() { echo "ERROR: $*" >&2; exit 1; }

# ---- Dependencies ----------------------------------------------------------
if command -v apt-get &>/dev/null; then
    log "Installing gvm dependencies..."
    sudo apt-get update -qq
    sudo apt-get install -y bison binutils gcc make curl git mercurial \
        build-essential 2>/dev/null | tail -3
fi

# ---- Install gvm -----------------------------------------------------------
GVM_DIR="${GVM_DIR:-$HOME/.gvm}"

if [[ -d "$GVM_DIR" ]]; then
    log "gvm already installed at $GVM_DIR — upgrading source..."
    cd "$GVM_DIR" && git pull --ff-only origin master 2>/dev/null || true
    log "gvm source updated"
else
    log "Cloning gvm from $GVM_REPO..."
    git clone --depth=1 "$GVM_REPO" /tmp/gvm-src
    GVM_INSTALLER=/tmp/gvm-src/binscripts/gvm-installer
    chmod +x "$GVM_INSTALLER"
    # gvm-installer reads GVM_NO_UPDATE_PROFILE to avoid shell profile edits
    GVM_NO_UPDATE_PROFILE=1 bash "$GVM_INSTALLER" "$GVM_DIR" 2>&1 | tail -10
    rm -rf /tmp/gvm-src
    log "gvm installed to $GVM_DIR"
fi

# ---- Source gvm ------------------------------------------------------------
# shellcheck disable=SC1090
[[ -s "$GVM_DIR/scripts/gvm" ]] && source "$GVM_DIR/scripts/gvm" \
    || die "gvm script not found at $GVM_DIR/scripts/gvm"

# ---- Bootstrap Go 1.4 (needed to compile Go 1.5+) -------------------------
if ! gvm list 2>/dev/null | grep -q "go1.4"; then
    log "Installing Go 1.4 (bootstrap binary)..."
    gvm install go1.4 -B
fi
gvm use go1.4
export GOROOT_BOOTSTRAP="$GOROOT"
log "Bootstrap: Go 1.4 set as GOROOT_BOOTSTRAP"

# ---- Install requested Go version -----------------------------------------
if gvm list 2>/dev/null | grep -q "$GO_VERSION"; then
    log "$GO_VERSION already installed"
else
    log "Installing $GO_VERSION..."
    gvm install "$GO_VERSION"
fi

gvm use "$GO_VERSION" --default
log "Active Go: $(go version)"

# ---- Shell profile snippet (print; user appends manually if needed) --------
PROFILE_SNIPPET=$(cat <<'SNIP'
# gvm — Go Version Manager
[[ -s "$HOME/.gvm/scripts/gvm" ]] && source "$HOME/.gvm/scripts/gvm"
SNIP
)

echo ""
echo "================================================================"
echo "gvm + Go installed successfully."
echo ""
echo "Add this to your ~/.bashrc or ~/.zshrc if not already present:"
echo ""
echo "$PROFILE_SNIPPET"
echo "================================================================"
