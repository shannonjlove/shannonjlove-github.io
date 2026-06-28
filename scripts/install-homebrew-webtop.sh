#!/usr/bin/env bash
# Installs Homebrew in the Claude Code webtop environment (Ubuntu 24.04, non-root user).
# Run as root: bash scripts/install-homebrew-webtop.sh

set -e

CA_BUNDLE=/usr/local/share/ca-bundle.crt
PROXY=http://127.0.0.1:38485
INSTALL_USER=${SUDO_USER:-claude}

# Make proxy CA bundle accessible to non-root users
if [[ -f /root/.ccr/ca-bundle.crt ]]; then
  cp /root/.ccr/ca-bundle.crt "$CA_BUNDLE"
  chmod a+r "$CA_BUNDLE"
fi

# Install prerequisites
apt-get install -y build-essential curl file git bubblewrap 2>/dev/null

# Remove any partial install
rm -rf /home/linuxbrew

# Install Homebrew as the target user
NONINTERACTIVE=1 su -s /bin/bash "$INSTALL_USER" -c "
  export CURL_CA_BUNDLE=$CA_BUNDLE
  export GIT_SSL_CAINFO=$CA_BUNDLE
  export HTTPS_PROXY=$PROXY
  export https_proxy=$PROXY
  /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"
"

# Add brew to PATH for all users
cat > /etc/profile.d/brew.sh << 'EOF'
eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv bash)"
EOF
chmod +x /etc/profile.d/brew.sh

for BASHRC in /home/claude/.bashrc /home/ubuntu/.bashrc /root/.bashrc; do
  if [[ -f "$BASHRC" ]] && ! grep -q linuxbrew "$BASHRC"; then
    echo 'eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv bash)"' >> "$BASHRC"
  fi
done

echo ""
echo "Homebrew installed. Open a new shell or run:"
echo '  eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv bash)"'
