# SJL Sovereign Cloud — Claude Code Operating Context

> Source: SJL_Sovereign_Cloud___Claude_Code_Operating_Context_Nexus.txt (76000_2026-06-21 v1-0)
> Always-loaded context for Claude Code sessions on this project.
> Contains NO secret values — secrets referenced by path/env-var name only.

## Identity & Host

- **Nexus host**: shannonjlove (Hostinger VPS) · 72.61.74.250 · Ubuntu 24.04.4 LTS
- **Service account**: `sjl` (UID/GID 1001:1001) — all apps run as sjl, never root
- **Companion node**: Oracle Cloud ARM `oracle-sos` · Tailscale 100.67.229.94 (compute worker only)
- **Tailscale account**: shannonjlove@mac.com
- Rootless Podman only. No Docker, no docker-compose.

## MCP Connector — EXISTING, DO NOT DUPLICATE

| Field | Value |
|---|---|
| Name | SJL Unified Cloud MCP V2 |
| systemd unit | `/home/sjl/.config/systemd/user/sjl-cloud-access-mcp.service` |
| App dir | `/srv/sjl/70000_SYSTEM-AUTOMATION/76000_mcp-cloud-access/app` |
| Entry | `app/server.py` · OCI provider: `app/oracle_tools.py` |
| venv | `app/.venv` |
| Local endpoint | `http://127.0.0.1:8797/mcp` (bind 0.0.0.0:8797) |
| Remote endpoint | `https://mcp.shannonjlove.cloud/mcp` |
| Runtime mode | `readonly=true` — **CONFIRM before any mutation call** |

> **Port note**: Password manager shows 8798; operating context doc says 8797. Treat 8797 as authoritative until Shannon confirms otherwise.

Preferred `.mcp.json` registration (local execution on Nexus):
```json
{
  "mcpServers": {
    "sjl-unified-cloud-mcp-v2": {
      "type": "http",
      "url": "http://127.0.0.1:8797/mcp"
    }
  }
}
```
Use `https://mcp.shannonjlove.cloud/mcp` only when NOT executing on Nexus.

## Secret References — PATHS AND NAMES ONLY, NEVER VALUES

| Purpose | Path | Mode |
|---|---|---|
| Canonical OCI config | `/opt/secrets/oci-config` | 0600 |
| Source OCI config (verify vs canonical — do not assume sync) | `/opt/secrets/oci/config` | 0600 |
| OCI private signing key | `/opt/secrets/oci/oci_api_key.pem` | 0600 |
| OCI public key | `/opt/secrets/oci/oci_api_key_public.pem` | 0644 |
| Cloud integrations env | `/opt/secrets/sjl-cloud-integrations.env` | sjl:sjl |
| OCI SDK dir (if present) | `/home/sjl/.oci/` | sjl:sjl |

Expected env vars in `sjl-cloud-integrations.env` (verify presence, never print values):
`BOOKSTACK_URL`, `BOOKSTACK_TOKEN_ID`, `BOOKSTACK_TOKEN_SECRET`, `BOOKSTACK_BOOK_ID` (optional)

Expected OCI config block structure (`oci-config`, actual values already in file — do not regenerate):
```
[DEFAULT]
user=<OCID>
fingerprint=<value>
tenancy=<OCID>
region=us-ashburn-1
key_file=/opt/secrets/oci/oci_api_key.pem
```

## Hard Rules

1. **Never** echo, print, log, commit, or write secret VALUES anywhere.
2. **Never** recursively chown/chmod across `/srv/sjl`.
3. Read-only inventory calls before any mutation call, every session.
4. Snapshot before editing `server.py`, `oracle_tools.py`, the unit file, proxy config, or secret references — timestamped copies + SHA-256 manifest, before and after.
5. `py_compile` any Python change before restarting the service. If it fails: do not restart — restore snapshot and report.
6. Restart only the specific affected unit: `systemctl --user restart sjl-cloud-access-mcp.service`, then check status + recent journal.
7. Do not create a second/parallel MCP connector, OCI user, API key, or secret store. Use what exists.
8. Capture OCI `opc-request-id` on any error. Use SDK pagination + retry-strategy helpers for list/read calls.
9. Update BookStack page 479 (SJL Sovereign Cloud Access Registry) in place — do not create a duplicate page.
10. All multi-step terminal work must be combined into a single base64-encoded one-liner (NeoServer/iOS SSH paste-limit constraint). Fallback: `echo [BASE64] > /tmp/x.b64 && base64 -d /tmp/x.b64 | bash`

## Bootstrap Discovery Sequence (read-only, run first, every session on Nexus)

```bash
# 1. Identity
id && whoami

# 2. Service status
loginctl show-user sjl && systemctl --user status sjl-cloud-access-mcp.service

# 3. Read unit file (do not edit)
cat /home/sjl/.config/systemd/user/sjl-cloud-access-mcp.service

# 4. Port check
ss -lntp | grep ':8797 '

# 5. MCP discovery
curl -s http://127.0.0.1:8797/mcp

# 6. OCI config diff (flag if different, do not silently prefer one)
diff /opt/secrets/oci-config /opt/secrets/oci/config

# 7. BookStack vars presence (not values)
grep -qE 'BOOKSTACK_(URL|TOKEN_ID|TOKEN_SECRET)' /opt/secrets/sjl-cloud-integrations.env && echo "BOOKSTACK vars present" || echo "BOOKSTACK vars MISSING"

# 8. OCI identity verification (non-destructive)
/srv/sjl/70000_SYSTEM-AUTOMATION/76000_mcp-cloud-access/app/.venv/bin/python - <<'EOF'
import oci
config = oci.config.from_file("/opt/secrets/oci-config", "DEFAULT")
oci.config.validate_config(config)
identity = oci.identity.IdentityClient(config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY)
tenancy = identity.get_tenancy(config["tenancy"]).data
user = identity.get_user(config["user"]).data
print(f"tenancy={tenancy.name} user={user.name} region={config['region']}")
EOF
```

Expected: `tenancy.name == "lovecloud"`, `user.name == "shannonjlove@mac.com"`, `region == "us-ashburn-1"`

## Success Criteria (all must pass before claiming session healthy)

- [ ] MCP server discoverable at local or remote endpoint
- [ ] `cloud_access_health` succeeds
- [ ] `oracle_config_status` succeeds
- [ ] `oracle_identity_test` succeeds
- [ ] `oracle_resources_summary` succeeds
- [ ] OCI inventory matches (or intentionally diverges from, with explanation) the 20260621T210512Z baseline
- [ ] `sjl-cloud-access-mcp.service` is active
- [ ] Port 8797 listening
- [ ] No raw credential values in any log, journal excerpt, or generated doc
- [ ] BookStack page 479 updated with status + paths (not values)

## Known Open Questions (resolve before mutating anything)

1. **Port conflict**: Password manager shows 8798; context doc says 8797. Which is current? Ask Shannon.
2. **Canonical vs source OCI config**: if `/opt/secrets/oci-config` and `/opt/secrets/oci/config` differ, which wins? Ask Shannon, don't guess.
3. **Connector readonly=true**: confirm whether read-write is in scope for the current session.
4. **py_compile failure path**: restore-snapshot-and-report, not retry-and-restart.
5. **BookStack creds**: verify presence before assuming write access to page 479.

## DeltaWalker — Config Diff & Merge Skill

DeltaWalker (Deltopia Inc., deltawalker.com) is the designated tool for resolving configuration discrepancies on Nexus — including the open questions around dual OCI configs and the port conflict. Docs last updated April 29, 2026.

### Core concepts

| Term | Meaning |
|---|---|
| Reference | First/left content area — all differences defined relative to this |
| Modified | Second/right content area |
| Two-way | Reference vs Modified |
| Three-way | Common ancestor (center) vs Reference vs Modified — shows conflicts |
| Deletion | Block in Reference missing from Modified (orange) |
| Addition | Block in Modified absent from Reference (blue) |
| Change | Block present in both but altered (green) |
| Conflict | Both Modified sides differ from ancestor (red — three-way only) |
| Bird's-Eye View | Scaled color strip on the right — instant overview of all difference locations |

### Key DeltaWalker capabilities relevant to Nexus

**Remote comparison via SFTP** — DeltaWalker can open files directly from Nexus without copying them:
```
sftp://sjl@72.61.74.250/opt/secrets/oci-config
sftp://sjl@72.61.74.250/opt/secrets/oci/config
```
Credentials go in the Open Remote Resource dialog only — never in the path field.

**Three-way comparison** — the right mode for the OCI config question:
- Ancestor / Reference: the known-good baseline (e.g. the 20260621T210512Z snapshot)
- Left: `/opt/secrets/oci-config` (canonical)
- Right: `/opt/secrets/oci/config` (source)

This surfaces whether the two live configs agree with each other and with the baseline.

**Folder comparison** — start at the folder level to see structural drift, then drill into individual files. Relevant for comparing `/opt/secrets/` snapshots before/after edits (Hard Rule 4).

**Command line invocation** (macOS):
```bash
# Two-way file comparison
/Applications/DeltaWalker.app/Contents/MacOS/DeltaWalker \
  -pwd=/opt/secrets \
  oci-config oci/config

# Three-way (third path = ancestor/reference)
/Applications/DeltaWalker.app/Contents/MacOS/DeltaWalker \
  -pwd=/opt/secrets \
  oci-config oci/config baseline-oci-config

# Label the panels for clarity
/Applications/DeltaWalker.app/Contents/MacOS/DeltaWalker \
  -title1="canonical (oci-config)" \
  -title2="source (oci/config)" \
  /opt/secrets/oci-config /opt/secrets/oci/config
```

**Saving**: Cmd+S saves the focused file; Cmd+Shift+S saves all. HTTP/HTTPS are read-only; use WebDAV for remote saves. SFTP supports save.

### Applying DeltaWalker to open Nexus questions

| Open question | DeltaWalker approach |
|---|---|
| Port 8797 vs 8798 | Compare unit file vs password manager entry — two-way text compare |
| `oci-config` vs `oci/config` | Three-way compare with 20260621T210512Z baseline as ancestor |
| Pre/post snapshot verification (Hard Rule 4) | Folder compare: timestamped snapshot dir vs live `/srv/sjl/…/app` dir |
| Config drift over time | Folder compare: current `/opt/secrets/` vs known-good archived snapshot |

### DeltaWalker skill checklist (before resolving any config conflict)

1. Start with **folder comparison** to get the Bird's-Eye view of scope
2. Select only **changed** files (not additions/deletions unless expected)
3. Use **three-way** when a baseline exists — it distinguishes change from conflict
4. Check the **summary dialog** (counts of same/deleted/added/changed) before merging
5. Save to the **canonical** path after Shannon confirms which file wins
6. Never save values to a path that gets committed to git

## Remote Control Setup (iOS-only, headless VPS)

**Auth**: Must use `claude auth login` (subscription OAuth). API keys and `CLAUDE_CODE_OAUTH_TOKEN` are inference-only and cannot establish Remote Control sessions. `unset ANTHROPIC_API_KEY` before authenticating.

**Headless login on NeoServer**:
1. `unset ANTHROPIC_API_KEY && claude auth login`
2. Press `c` to copy the login URL → open in Safari on iPhone → sign into claude.ai
3. Copy the displayed code → paste back into NeoServer terminal

**Persistence**: Run inside tmux — Remote Control requires an attached TTY. `claude` process dying = session dying.
```bash
tmux new -s claude
cd /home/sjl/<project> && claude remote-control --sandbox
# detach: Ctrl-b d   |   reattach: tmux attach -t claude
```

For survive-reboot: wrap systemd `--user` service around tmux + `loginctl enable-linger sjl`.

**Version requirements**: Remote Control requires v2.1.51+; push notifications require v2.1.110+; headless paste fix in v2.1.108.

**Known fragility**: OAuth tokens fail to auto-refresh on headless Linux after ~6h (#50743). Re-run `claude auth login` if you hit 401s.
