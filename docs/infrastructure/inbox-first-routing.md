# Inbox-First Routing: All Files → S3 Inbox

**Authority:** SJL Sovereign Cloud Canonical Architecture v1.0 (GOVERNANCE-NORMATIVE)  
**Rule:** Every file from every service routes to `inbox-idrive-e2/01001-uploads/` FIRST.  
**No file may be placed directly into a PARA bucket without passing through inbox.**

---

## Architecture

```
Dropbox (FCPXServerSJL)  ──┐
Dropbox (shannonjlove)   ──┤
pCloud                   ──┼──► inbox-idrive-e2/01001-uploads/ ──► FileWarden ──► PARA bucket
MediaFire                ──┤
Any future service       ──┘
```

Sync frequency: **every 15 minutes** (via systemd timer or n8n cron)  
Conflict handling: files that already exist in inbox are skipped (`--no-update-modtime`)  
Post-sync: source files are NOT deleted — inbox keeps its own copy until FileWarden promotes it

---

## Step 1: Authenticate rclone on Your Local Machine (Mac/Linux)

OAuth flows require a browser. Run these on your **local Mac**, not the VPS.

### Install rclone (if not present)

```bash
brew install rclone       # Mac
# or
curl https://rclone.org/install.sh | sudo bash  # Linux
```

### Authenticate Dropbox – FCPXServerSJL account

```bash
rclone config
# Select: n (new remote)
# Name: dropbox-fcpx
# Type: dropbox
# client_id: (leave blank)
# client_secret: (leave blank)
# Auth: y (use browser)
# Browser opens → log in as FCPXServerSJL@gmail.com → Allow
# Confirm "y" when prompted
```

### Authenticate Dropbox – shannonjlove account

```bash
rclone config
# Name: dropbox-sjl
# Type: dropbox
# Auth: y (use browser)
# Log in as shannonjlove@mac.com → Allow
```

### Authenticate pCloud

```bash
rclone config
# Name: pcloud-sjl
# Type: pcloud
# Auth: y
# Log in with your pCloud credentials + 2FA code
```

### Export your rclone config

After all three authentications:

```bash
cat ~/.config/rclone/rclone.conf
```

Copy the `[dropbox-fcpx]`, `[dropbox-sjl]`, and `[pcloud-sjl]` sections.  
Paste them into `/etc/rclone/rclone.conf` on the VPS (or `~/.config/rclone/rclone.conf`).

---

## Step 2: Configure iDrive E2 in rclone

Add this to your rclone config on the VPS (already stored as environment in scripts below, but can also be a named remote):

```ini
[idrive-primary]
type = s3
provider = Other
env_auth = false
access_key_id = hNOOh0odHmPwKt9xDbll
secret_access_key = w8X3Ubjfp6rnGzjoFjBv1kwpdMpn9MxzbQcjozA6
endpoint = https://p3h2.va.idrivee2-48.com
region = us-east-1
```

---

## Step 3: MediaFire

rclone does not support MediaFire. Use the Python sync script instead:

```bash
# Install mediafire-dl or use the REST API script at:
# /opt/sjl-scripts/medifire-inbox-sync.py
# Requires: MEDIAFIRE_EMAIL and MEDIAFIRE_PASSWORD env vars
```

See: `scripts/mediafire-inbox-sync.py` in this repo.

---

## Step 4: Deploy the Inbox Routing Scripts

Copy `scripts/inbox-routing/` to the VPS at `/opt/sjl-scripts/inbox-routing/`:

```bash
scp -r scripts/inbox-routing/ vps:/opt/sjl-scripts/
chmod +x /opt/sjl-scripts/inbox-routing/*.sh
```

---

## Step 5: Enable systemd Timer

```bash
# Copy unit files
cp /opt/sjl-scripts/inbox-routing/sjl-inbox-sync.service /etc/systemd/system/
cp /opt/sjl-scripts/inbox-routing/sjl-inbox-sync.timer   /etc/systemd/system/

# Enable and start
systemctl daemon-reload
systemctl enable --now sjl-inbox-sync.timer

# Verify
systemctl status sjl-inbox-sync.timer
```

---

## Routing Rules (per FileWarden pipeline)

| Source | rclone Command | Notes |
|--------|---------------|-------|
| Dropbox FCPXServerSJL | `rclone copy dropbox-fcpx: idrive-primary:inbox-idrive-e2/01001-uploads/dropbox-fcpx/` | All files |
| Dropbox shannonjlove | `rclone copy dropbox-sjl: idrive-primary:inbox-idrive-e2/01001-uploads/dropbox-sjl/` | All files |
| pCloud | `rclone copy pcloud-sjl: idrive-primary:inbox-idrive-e2/01001-uploads/pcloud/` | All files |
| MediaFire | Python script | REST API |

Each source gets its own subdirectory under `01001-uploads/` so FileWarden can identify the source.

---

## n8n Automation (Alternative to systemd)

If you prefer n8n to handle scheduling (it's already running at `n8n.shannonjlove.cloud`):

1. Create a new workflow: **Inbox Sync - Every 15 Min**
2. Trigger: Schedule → every 15 minutes
3. Nodes:
   - `Execute Command`: `rclone copy dropbox-fcpx: idrive-primary:inbox-idrive-e2/01001-uploads/dropbox-fcpx/ --no-update-modtime --log-level INFO`
   - `Execute Command`: `rclone copy dropbox-sjl: idrive-primary:inbox-idrive-e2/01001-uploads/dropbox-sjl/ --no-update-modtime --log-level INFO`
   - `Execute Command`: `rclone copy pcloud-sjl: idrive-primary:inbox-idrive-e2/01001-uploads/pcloud/ --no-update-modtime --log-level INFO`
   - `Execute Command`: `python3 /opt/sjl-scripts/inbox-routing/mediafire-inbox-sync.py`
4. Error handling: Send notification on failure

---

## Verification

After first sync run:

```bash
# Check what arrived in inbox
rclone ls idrive-primary:inbox-idrive-e2/01001-uploads/ | head -20

# Count files by source
rclone ls idrive-primary:inbox-idrive-e2/01001-uploads/dropbox-fcpx/ | wc -l
rclone ls idrive-primary:inbox-idrive-e2/01001-uploads/pcloud/ | wc -l
```
