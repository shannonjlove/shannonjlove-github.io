# WebTop Deployment

## Quick Install (paste in WebTop terminal)

```bash
curl -fsSL https://raw.githubusercontent.com/shannonjlove/shannonjlove-github.io/claude/idrives3-storage-org-zo63il/scripts/deploy/webtop-bootstrap.sh | bash
```

Or if cloning the repo first:

```bash
git clone https://github.com/shannonjlove/shannonjlove-github.io.git /tmp/sjl-repo && \
  bash /tmp/sjl-repo/scripts/deploy/webtop-bootstrap.sh
```

## What the bootstrap does

1. **Installs rclone** (apt-get or curl installer)
2. **Configures iDrive E2** with credentials (no OAuth needed)
3. **Opens Dropbox OAuth** × 2 accounts (FCPXServerSJL + shannonjlove) — browser opens in WebTop
4. **Opens pCloud OAuth** — browser opens in WebTop
5. **Deploys scripts** to `/opt/sjl-scripts/inbox-routing/`
6. **Installs systemd timer** for 15-minute automated sync
7. **Runs first sync** on confirmation

## After deployment

| Command | Purpose |
|---------|---------|
| `inbox-sync.sh` | Manual sync all sources → S3 inbox |
| `systemctl status sjl-inbox-sync.timer` | Timer status |
| `journalctl -u sjl-inbox-sync -f` | Live logs |
| `rclone ls idrive-primary:inbox-idrive-e2/01001-uploads/` | Check inbox |

## MediaFire

Edit `/etc/sjl-inbox-sync.env` and add your MediaFire password:
```
MEDIAFIRE_PASSWORD=YourPassword
```
Then the Python script handles sync automatically on each run.
