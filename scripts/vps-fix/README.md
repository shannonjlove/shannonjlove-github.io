# VPS Fix — System-Wide Routing and Service Repair

## Quick Run (on Hostinger VPS as root)

```bash
curl -fsSL https://raw.githubusercontent.com/shannonjlove/shannonjlove-github.io/claude/idrives3-storage-org-zo63il/scripts/vps-fix/fix-routing.sh | bash
```

## What fix-routing.sh Does

1. **Audits all containers** — checks running status against the services registry
2. **Starts stopped containers** — rclone-gui, rclone-mcp, stash, kuma, etc.
3. **Validates port bindings** — confirms container IPs on `sjl_net`
4. **Fixes rclone config** — removes invalid `[mediafire-sjl]` remote; adds `[idrive-primary]` if missing
5. **Fixes env file** — ensures `FILE_API_PORT=8090` in `/etc/sjl-inbox-sync.env` (fixes the 8086→8090 mismatch)
6. **Deploys MCP tools** — downloads `mcp-tools-config.js` to `/opt/sjl-mcp-gateway/` and restarts the gateway
7. **Reloads systemd** — ensures `sjl-inbox-sync.timer` is enabled

## NPM Routes to Add Manually

After running fix-routing.sh, log in to Nginx Proxy Manager and add:

| Subdomain | Forward Host | Port | Auth |
|-----------|-------------|------|------|
| `api.shannonjlove.cloud` | `sjl-file-api` | `8090` | none |
| `files.shannonjlove.cloud` | `rclone-gui` | `5572` | Basic auth (add in NPM) |
| `rclone-mcp.shannonjlove.cloud` | `rclone-mcp` | `8026` | none |
| `private.shannonjlove.cloud` | `stash` | `9999` | none (stash has its own auth) |
| `status.shannonjlove.cloud` | `kuma` | `3001` | none |
| `hub.shannonjlove.cloud` | `hub` | `80` | none |

## MCP Gateway (Claude Desktop / claude.ai)

After the fix, add to `~/.claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "sjl-cloud": {
      "url": "https://mcp.shannonjlove.cloud/mcp",
      "transport": "http"
    }
  }
}
```

Available tools after deploy:
- `system_status` — live container health
- `storage_inbox_status` — inbox bucket contents
- `storage_list` — list any S3 bucket/prefix
- `rclone_list_remotes` — configured remotes + reachability
- `rclone_sync_inbox` — trigger immediate inbox sync
- `n8n_list_workflows` — list n8n workflows
- `n8n_trigger_workflow` — fire a webhook
- `files_list_inbox` — recent uploads via file API

## Service Registry Reference

See: [`docs/infrastructure/services-registry.md`](../../docs/infrastructure/services-registry.md)

## Remaining Manual Steps

1. **Complete Dropbox OAuth** — open WebTop (`webtop.shannonjlove.cloud`) → terminal → run bootstrap:
   ```bash
   curl -fsSL https://raw.githubusercontent.com/shannonjlove/shannonjlove-github.io/claude/idrives3-storage-org-zo63il/scripts/deploy/webtop-bootstrap.sh | bash
   ```
   Log in with FCPXServerSJL@gmail.com and shannonjlove@mac.com when prompted.

2. **Complete pCloud OAuth** — same bootstrap script handles this (step 5).

3. **Add MediaFire password** — edit `/etc/sjl-inbox-sync.env`:
   ```
   MEDIAFIRE_PASSWORD=YourPassword
   ```

4. **Set n8n API key** — add `N8N_API_KEY=your-key` to the MCP gateway environment so `n8n_list_workflows` and `n8n_trigger_workflow` work.
