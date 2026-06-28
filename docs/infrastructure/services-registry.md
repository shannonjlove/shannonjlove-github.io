# SJL Sovereign Cloud — Services Registry

**Last updated:** 2026-06-28  
**Authority:** GOVERNANCE-NORMATIVE — this document is the single source of truth for all service ports, subdomains, container names, and storage assignments.

---

## Infrastructure Overview

| Node | Role | Public IP | Tailscale IP |
|------|------|-----------|--------------|
| Hostinger VPS | Primary (containers live here) | `72.61.74.250` | `100.115.66.75` |
| Oracle Cloud VPS | Secondary / relay | — | `100.67.229.94` |

**Reverse proxy:** Nginx Proxy Manager (NPM) running on Hostinger, exposed on 80/443.  
**Network:** All containers on `sjl_net` bridge; NPM routes subdomains → container:port.  
**Tailscale:** Admin-only services (Portainer, monitor) reachable only via Tailscale.

---

## Service Registry (Authoritative Port Table)

| Service | Container Name | Internal Port | Subdomain | S3 Bucket (PARA) | Status |
|---------|---------------|--------------|-----------|-------------------|--------|
| Hub / Homepage | `hub` | 80 | `hub.shannonjlove.cloud` | `assets-e2` (07020) | needs NPM route |
| n8n Automation | `n8n` | 5678 | `n8n.shannonjlove.cloud` | `n8n-backups-e2` (08010) | ✅ Live |
| BookStack Wiki | `bookstack` | 6875 | `bookstack.shannonjlove.cloud` | `bookstack-data-e2` (08020) | ✅ Live |
| Paperless-NGX | `paperless` | 8000 | `docs.shannonjlove.cloud` | `paperless-docs-e2` (08030) | ✅ Live |
| WebTop Browser | `webtop` | 3000 | `webtop.shannonjlove.cloud` | — | ✅ Live |
| MCP Gateway | `sjl-mcp-gateway` | **7300** | `mcp.shannonjlove.cloud` | `agent-data-e2` (07010) | ✅ Live (status only) |
| SJL MCP Server | `sjl-mcp` | **8789** | *(merged into mcp.shannonjlove.cloud)* | — | ⚠️ verify running |
| SJL File API | `sjl-file-api` | **8090** | `api.shannonjlove.cloud` | `inbox-idrive-e2` (01001) | needs NPM route |
| Rclone Web GUI | `rclone-gui` | **5572** | `files.shannonjlove.cloud` | all remotes | ❌ needs start |
| Rclone MCP | `rclone-mcp` | **8026** | `rclone-mcp.shannonjlove.cloud` | all remotes | ❌ needs start |
| Stash (media) | `stash` | **9999** | `private.shannonjlove.cloud` | `private-idrive-e2` (06000) | ❌ needs start |
| Uptime Kuma | `kuma` | **3001** | `status.shannonjlove.cloud` | — | needs NPM route |
| Tailscale MCP | `tailnet` | **8788** | Tailscale only | — | internal only |
| SJL Monitor | `sjl-monitor` | **8790** | Tailscale only | — | internal only |
| Portainer | `portainer` | 9000 / 9443 | Tailscale only | — | internal only |

### Port Quick Reference

```
3000  webtop
3001  kuma (status)
5572  rclone-gui / rclone-mcp (shared base — differentiate by container)
5678  n8n
6875  bookstack
7300  sjl-mcp-gateway
8000  paperless
8026  rclone-mcp (MCP protocol port)
8090  sjl-file-api  ← CORRECT PORT (not 8086)
8789  sjl-mcp
8790  sjl-monitor
9000  portainer
9999  stash
```

---

## NPM Proxy Host Configuration (Required Routes)

Configure these in Nginx Proxy Manager → Proxy Hosts:

| Subdomain | Forward Hostname | Forward Port | SSL | Notes |
|-----------|-----------------|-------------|-----|-------|
| `hub.shannonjlove.cloud` | `hub` | `80` | ✅ | Homepage / landing |
| `n8n.shannonjlove.cloud` | `n8n` | `5678` | ✅ | Already configured |
| `mcp.shannonjlove.cloud` | `sjl-mcp-gateway` | `7300` | ✅ | Already configured |
| `api.shannonjlove.cloud` | `sjl-file-api` | `8090` | ✅ | Add this route |
| `files.shannonjlove.cloud` | `rclone-gui` | `5572` | ✅ | Add + auth protect |
| `rclone-mcp.shannonjlove.cloud` | `rclone-mcp` | `8026` | ✅ | Add this route |
| `private.shannonjlove.cloud` | `stash` | `9999` | ✅ | Add this route |
| `status.shannonjlove.cloud` | `kuma` | `3001` | ✅ | Add this route |
| `bookstack.shannonjlove.cloud` | `bookstack` | `6875` | ✅ | Already configured |
| `docs.shannonjlove.cloud` | `paperless` | `8000` | ✅ | Already configured |
| `webtop.shannonjlove.cloud` | `webtop` | `3000` | ✅ | Already configured |

**Do NOT expose publicly (Tailscale only):**
- Portainer (9000/9443)
- sjl-monitor (8790)
- tailnet (8788)
- Any admin/management interfaces

---

## iDrive E2 Storage Assignments

| Subdomain / Service | Bucket | PARA Code | Prefix |
|--------------------|--------|-----------|--------|
| FileWarden intake | `inbox-idrive-e2` | 01001 | `01001-uploads/` |
| Dropbox FCPXServerSJL | `inbox-idrive-e2` | 01001 | `01001-uploads/dropbox-fcpx/` |
| Dropbox shannonjlove | `inbox-idrive-e2` | 01001 | `01001-uploads/dropbox-sjl/` |
| pCloud | `inbox-idrive-e2` | 01001 | `01001-uploads/pcloud/` |
| MediaFire | `inbox-idrive-e2` | 01001 | `01001-uploads/mediafire/` |
| sjl-file-api uploads | `inbox-idrive-e2` | 01001 | `01001-uploads/api/` |
| Active projects | `projects-idrive-e2` | 02000 | per project subfolder |
| Infrastructure configs | `stacks-backups-e2` | 07030 | `07030-compose-files/` |
| Agent / AI context | `agent-data-e2` | 07010 | `07010-context/` |
| n8n backups | `n8n-backups-e2` | 08010 | `08010-workflows/` |
| BookStack backups | `bookstack-data-e2` | 08020 | `08020-database-backups/` |
| Paperless backups | `paperless-docs-e2` | 08030 | `08030-database-backups/` |
| Photos | `shannon-photos-e2` | 06010 | `06010-ios-photos/` |
| Video media | `video-media-e2` | 06020 | per subfolder |
| Graphics | `graphics-media-e2` | 06030 | `06030-brand-assets/` |
| Quarantine / errors | `quarantine-e2` | 09001 | per category |

---

## AI / Claude Desktop MCP Endpoints

After `mcp-tools-config.js` is deployed to `sjl-mcp-gateway`:

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

### Available MCP Tools (post-deploy)

| Tool | Description |
|------|-------------|
| `storage_inbox_status` | List inbox bucket contents and counts |
| `storage_list` | List any iDrive E2 bucket/prefix |
| `rclone_sync_inbox` | Trigger immediate inbox sync from cloud sources |
| `rclone_list_remotes` | List all configured rclone remotes and their status |
| `n8n_trigger_workflow` | Trigger an n8n workflow by webhook ID |
| `n8n_list_workflows` | List all active n8n workflows |
| `files_upload` | Upload a file to the inbox via sjl-file-api |
| `system_status` | Return live container health for all services |

---

## Known Issues / Mismatches (as of 2026-06-28)

| Issue | Impact | Fix |
|-------|--------|-----|
| `agent.shannonjlove.cloud` returns 502 | AI agent subdomain broken | Start/fix `hub` or dedicated agent container; update NPM route |
| `rclone-gui` / `rclone-mcp` containers not running | `files.shannonjlove.cloud` and `rclone-mcp.shannonjlove.cloud` dead | Run `fix-routing.sh` on VPS |
| `stash` container not running | `private.shannonjlove.cloud` dead | Run `fix-routing.sh` on VPS |
| `kuma` missing NPM route | `status.shannonjlove.cloud` timeout | Add NPM proxy host kuma:3001 |
| `sjl-file-api` port was documented as 8086 | Wrong port in some scripts/docs | Correct port is **8090** everywhere |
| MCP gateway has no real tools | Claude Desktop can't use cloud services via MCP | Deploy `mcp-tools-config.js` |
| Dropbox/pCloud OAuth incomplete | Inbox sync doesn't run for those sources | Complete OAuth in WebTop browser |
| `mediafire-sjl` rclone remote type `mediafire` invalid | rclone errors on startup | Remove from rclone.conf; Python script handles MediaFire instead |
