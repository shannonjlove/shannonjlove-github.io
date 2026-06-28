#!/usr/bin/env bash
# One-shot script: creates "SJL Infrastructure" collection in Raindrop
# and bulk-adds all shannonjlove.cloud subdomains as bookmarks.
set -euo pipefail

API="https://api.raindrop.io/rest/v1"
TOKEN="${RAINDROP_TOKEN:?RAINDROP_TOKEN env var is required}"
AUTH="Authorization: Bearer ${TOKEN}"

echo "==> Creating SJL Infrastructure collection..."
COLLECTION=$(curl -sf -X POST "$API/collection" \
  -H "$AUTH" -H "Content-Type: application/json" \
  -d '{"title":"SJL Infrastructure","view":"list","sort":-1,"public":false}')
COLLECTION_ID=$(echo "$COLLECTION" | jq -r '.item._id')
echo "    Collection ID: $COLLECTION_ID"

echo "==> Bulk adding subdomains..."
PAYLOAD=$(python3 - "$COLLECTION_ID" <<'PYEOF'
import json, sys
cid = int(sys.argv[1])
col = {"$id": cid}
items = [
  {"link":"https://shannonjlove.cloud",           "title":"SJL - Main Site",           "tags":["sjl","root"],                "collection":col},
  {"link":"https://webtop.shannonjlove.cloud",    "title":"WebTop - Browser Desktop",  "tags":["sjl","container","webtop"],  "collection":col},
  {"link":"https://bookstack.shannonjlove.cloud", "title":"BookStack - Knowledge Base","tags":["sjl","docs","bookstack"],    "collection":col},
  {"link":"https://n8n.shannonjlove.cloud",       "title":"n8n - Automation",          "tags":["sjl","automation","n8n"],    "collection":col},
  {"link":"https://dashboard.shannonjlove.cloud", "title":"Dashboard",                 "tags":["sjl","dashboard"],           "collection":col},
  {"link":"https://admin.shannonjlove.cloud",     "title":"Admin Panel",               "tags":["sjl","admin"],               "collection":col},
  {"link":"https://agent.shannonjlove.cloud",     "title":"Agent",                     "tags":["sjl","ai","agent"],          "collection":col},
  {"link":"https://api.shannonjlove.cloud",       "title":"API",                       "tags":["sjl","api"],                 "collection":col},
  {"link":"https://status.shannonjlove.cloud",    "title":"Status Page",               "tags":["sjl","status"],              "collection":col},
  {"link":"https://stacks.shannonjlove.cloud",    "title":"Stacks",                    "tags":["sjl","stacks"],              "collection":col},
  {"link":"https://docs.shannonjlove.cloud",      "title":"Docs",                      "tags":["sjl","docs"],                "collection":col},
  {"link":"https://pages.shannonjlove.cloud",     "title":"Pages",                     "tags":["sjl","pages"],               "collection":col},
  {"link":"https://pics.shannonjlove.cloud",      "title":"Pics",                      "tags":["sjl","media","pics"],        "collection":col},
  {"link":"https://media.shannonjlove.cloud",     "title":"Media",                     "tags":["sjl","media"],               "collection":col},
  {"link":"https://assets.shannonjlove.cloud",    "title":"Assets",                    "tags":["sjl","assets"],              "collection":col},
  {"link":"https://private.shannonjlove.cloud",   "title":"Private",                   "tags":["sjl","private"],             "collection":col},
  {"link":"https://rclone-mcp.shannonjlove.cloud","title":"Rclone MCP",               "tags":["sjl","rclone","mcp"],        "collection":col},
]
print(json.dumps({"items": items}))
PYEOF
)

RESULT=$(curl -sf -X POST "$API/raindrops" \
  -H "$AUTH" -H "Content-Type: application/json" \
  -d "$PAYLOAD")

echo "$RESULT" | jq -r 'if .result == true then "    Success: \(.items | length) bookmarks added." else "    Error: \(.)" end'
echo ""
echo "Done! Open https://app.raindrop.io to see your SJL Infrastructure collection."
