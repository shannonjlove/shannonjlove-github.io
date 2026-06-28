/**
 * mcp-tools-config.js — MCP tool endpoints for sjl-mcp-gateway
 *
 * Drop this file into /opt/sjl-mcp-gateway/ then restart the gateway container.
 * Exposes real tools so Claude Desktop / claude.ai can control SJL Sovereign Cloud.
 *
 * Transport: HTTP (MCP over HTTP, JSON-RPC 2.0)
 * Endpoint:  https://mcp.shannonjlove.cloud/mcp
 *
 * Claude Desktop config (~/.claude/claude_desktop_config.json):
 * {
 *   "mcpServers": {
 *     "sjl-cloud": {
 *       "url": "https://mcp.shannonjlove.cloud/mcp",
 *       "transport": "http"
 *     }
 *   }
 * }
 */

'use strict';

const { execFile } = require('child_process');
const { promisify } = require('util');
const execFileAsync = promisify(execFile);
const fetch = require('node-fetch').default || require('node-fetch');

const N8N_URL = process.env.N8N_URL || 'http://n8n:5678';
const N8N_API_KEY = process.env.N8N_API_KEY || '';
const FILE_API_URL = process.env.FILE_API_URL || 'http://sjl-file-api:8090';
const RCLONE_CONF = process.env.RCLONE_CONFIG || '/root/.config/rclone/rclone.conf';
const INBOX_REMOTE = 'idrive-primary:inbox-idrive-e2/01001-uploads';
const INBOX_SYNC_SCRIPT = '/opt/sjl-scripts/inbox-routing/inbox-sync.sh';

// ─────────────────────────────────────────────────────────────────────────────
// Tool definitions (MCP tools/list response)
// ─────────────────────────────────────────────────────────────────────────────

const TOOLS = [
  {
    name: 'system_status',
    description: 'Returns the live health status of all SJL Sovereign Cloud services.',
    inputSchema: {
      type: 'object',
      properties: {},
      required: [],
    },
  },
  {
    name: 'storage_inbox_status',
    description: 'Lists the inbox bucket contents and file counts per source folder (dropbox-fcpx, dropbox-sjl, pcloud, mediafire, api).',
    inputSchema: {
      type: 'object',
      properties: {
        prefix: {
          type: 'string',
          description: 'Optional subfolder prefix to inspect (default: root of 01001-uploads/)',
        },
      },
      required: [],
    },
  },
  {
    name: 'storage_list',
    description: 'Lists files in any iDrive E2 bucket or prefix.',
    inputSchema: {
      type: 'object',
      properties: {
        path: {
          type: 'string',
          description: 'Path in format bucket/prefix or idrive-primary:bucket/prefix',
        },
        max_items: {
          type: 'number',
          description: 'Maximum number of items to return (default: 50)',
        },
      },
      required: ['path'],
    },
  },
  {
    name: 'rclone_list_remotes',
    description: 'Lists all configured rclone remotes and checks which ones are reachable.',
    inputSchema: {
      type: 'object',
      properties: {},
      required: [],
    },
  },
  {
    name: 'rclone_sync_inbox',
    description: 'Triggers an immediate inbox sync — pulls files from all configured cloud sources (Dropbox, pCloud, MediaFire) into iDrive E2 inbox/01001-uploads/.',
    inputSchema: {
      type: 'object',
      properties: {},
      required: [],
    },
  },
  {
    name: 'n8n_list_workflows',
    description: 'Lists all n8n workflows with their IDs, names, and active status.',
    inputSchema: {
      type: 'object',
      properties: {},
      required: [],
    },
  },
  {
    name: 'n8n_trigger_workflow',
    description: 'Triggers an n8n workflow via its webhook URL.',
    inputSchema: {
      type: 'object',
      properties: {
        webhook_path: {
          type: 'string',
          description: 'The webhook path (e.g. "inbox-sync" → POST to /webhook/inbox-sync)',
        },
        payload: {
          type: 'object',
          description: 'Optional JSON payload to send to the webhook',
        },
      },
      required: ['webhook_path'],
    },
  },
  {
    name: 'files_list_inbox',
    description: 'Lists recent files uploaded through sjl-file-api.',
    inputSchema: {
      type: 'object',
      properties: {
        limit: {
          type: 'number',
          description: 'Number of items to return (default: 20)',
        },
      },
      required: [],
    },
  },
];

// ─────────────────────────────────────────────────────────────────────────────
// Tool handlers
// ─────────────────────────────────────────────────────────────────────────────

async function handleSystemStatus() {
  const services = [
    { name: 'n8n', url: 'http://n8n:5678/healthz' },
    { name: 'bookstack', url: 'http://bookstack:6875' },
    { name: 'paperless', url: 'http://paperless:8000' },
    { name: 'sjl-file-api', url: `${FILE_API_URL}/health` },
    { name: 'rclone-gui', url: 'http://rclone-gui:5572' },
    { name: 'rclone-mcp', url: 'http://rclone-mcp:8026/health' },
    { name: 'stash', url: 'http://stash:9999' },
    { name: 'kuma', url: 'http://kuma:3001' },
  ];

  const results = await Promise.allSettled(
    services.map(async (svc) => {
      try {
        const res = await fetch(svc.url, { timeout: 3000 });
        return { name: svc.name, status: 'up', code: res.status };
      } catch (e) {
        return { name: svc.name, status: 'down', error: e.message.slice(0, 80) };
      }
    })
  );

  const statusRows = results.map((r) => r.value || { name: '?', status: 'error' });
  const lines = statusRows.map((s) =>
    s.status === 'up'
      ? `✅ ${s.name} (HTTP ${s.code})`
      : `❌ ${s.name} — ${s.error || 'unreachable'}`
  );

  return {
    content: [{ type: 'text', text: `SJL Service Status (${new Date().toISOString()}):\n\n${lines.join('\n')}` }],
  };
}

async function handleStorageInboxStatus(args) {
  const prefix = args.prefix ? args.prefix : '';
  const remote = `${INBOX_REMOTE}/${prefix}`;

  try {
    const { stdout } = await execFileAsync('rclone', [
      'lsd', remote,
      '--config', RCLONE_CONF,
      '--max-depth', '1',
    ], { timeout: 15000 });

    const folders = stdout.trim().split('\n').filter(Boolean);
    const lines = ['Inbox folders at ' + remote + ':\n'];

    for (const folder of folders) {
      const parts = folder.trim().split(/\s+/);
      const name = parts[parts.length - 1];
      try {
        const { stdout: sizeOut } = await execFileAsync('rclone', [
          'size', `${remote}/${name}`,
          '--config', RCLONE_CONF,
          '--json',
        ], { timeout: 10000 });
        const info = JSON.parse(sizeOut);
        lines.push(`  ${name}/  — ${info.count} files, ${(info.bytes / 1048576).toFixed(1)} MB`);
      } catch {
        lines.push(`  ${name}/`);
      }
    }

    if (folders.length === 0) lines.push('  (empty)');
    return { content: [{ type: 'text', text: lines.join('\n') }] };
  } catch (e) {
    return { content: [{ type: 'text', text: `Error listing inbox: ${e.message}` }], isError: true };
  }
}

async function handleStorageList(args) {
  const max = args.max_items || 50;
  const path = args.path.startsWith('idrive-primary:') ? args.path : `idrive-primary:${args.path}`;

  try {
    const { stdout } = await execFileAsync('rclone', [
      'ls', path,
      '--config', RCLONE_CONF,
      '--max-depth', '2',
    ], { timeout: 20000 });

    const lines = stdout.trim().split('\n').filter(Boolean).slice(0, max);
    const text = lines.length > 0
      ? `Files in ${path}:\n\n${lines.join('\n')}${lines.length === max ? `\n\n(showing first ${max} items)` : ''}`
      : `(empty — no files found in ${path})`;

    return { content: [{ type: 'text', text }] };
  } catch (e) {
    return { content: [{ type: 'text', text: `Error listing ${path}: ${e.message}` }], isError: true };
  }
}

async function handleRcloneListRemotes() {
  try {
    const { stdout } = await execFileAsync('rclone', ['listremotes', '--config', RCLONE_CONF], { timeout: 5000 });
    const remotes = stdout.trim().split('\n').filter(Boolean);

    const checks = await Promise.allSettled(
      remotes.map(async (remote) => {
        try {
          await execFileAsync('rclone', ['lsd', remote, '--config', RCLONE_CONF, '--max-depth', '1'], { timeout: 8000 });
          return `✅ ${remote}`;
        } catch {
          return `❌ ${remote} (unreachable or auth needed)`;
        }
      })
    );

    const lines = checks.map((c) => c.value || '❓ unknown');
    return {
      content: [{
        type: 'text',
        text: `rclone remotes:\n\n${lines.join('\n')}\n\nNote: Dropbox/pCloud marked ❌ until OAuth is completed in WebTop.`,
      }],
    };
  } catch (e) {
    return { content: [{ type: 'text', text: `Error: ${e.message}` }], isError: true };
  }
}

async function handleRcloneSyncInbox() {
  try {
    const { stdout, stderr } = await execFileAsync('bash', [INBOX_SYNC_SCRIPT], {
      timeout: 300000, // 5 minutes
      env: { ...process.env, RCLONE_CONFIG: RCLONE_CONF },
    });
    const out = (stdout + stderr).trim();
    return {
      content: [{
        type: 'text',
        text: `Inbox sync triggered.\n\nOutput:\n${out.slice(0, 3000)}${out.length > 3000 ? '\n...(truncated)' : ''}`,
      }],
    };
  } catch (e) {
    const out = (e.stdout || '') + (e.stderr || '');
    return {
      content: [{
        type: 'text',
        text: `Sync completed with errors (exit ${e.code}):\n${out.slice(0, 2000)}`,
      }],
      isError: true,
    };
  }
}

async function handleN8nListWorkflows() {
  if (!N8N_API_KEY) {
    return { content: [{ type: 'text', text: 'N8N_API_KEY not set — set it in the gateway environment to enable n8n API access.' }] };
  }
  try {
    const res = await fetch(`${N8N_URL}/api/v1/workflows?limit=50`, {
      headers: { 'X-N8N-API-KEY': N8N_API_KEY },
      timeout: 10000,
    });
    const data = await res.json();
    if (!res.ok) return { content: [{ type: 'text', text: `n8n API error ${res.status}: ${JSON.stringify(data)}` }], isError: true };

    const workflows = data.data || [];
    const lines = workflows.map((w) => `${w.active ? '✅' : '⏸'} [${w.id}] ${w.name}`);
    return {
      content: [{
        type: 'text',
        text: workflows.length > 0
          ? `n8n Workflows (${workflows.length}):\n\n${lines.join('\n')}`
          : 'No workflows found.',
      }],
    };
  } catch (e) {
    return { content: [{ type: 'text', text: `Error: ${e.message}` }], isError: true };
  }
}

async function handleN8nTriggerWorkflow(args) {
  const webhookPath = args.webhook_path.replace(/^\//, '');
  const payload = args.payload || {};
  try {
    const res = await fetch(`${N8N_URL}/webhook/${webhookPath}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      timeout: 30000,
    });
    const text = await res.text();
    return {
      content: [{
        type: 'text',
        text: `Webhook POST to /webhook/${webhookPath}: HTTP ${res.status}\n\nResponse: ${text.slice(0, 1000)}`,
      }],
    };
  } catch (e) {
    return { content: [{ type: 'text', text: `Error triggering webhook: ${e.message}` }], isError: true };
  }
}

async function handleFilesListInbox(args) {
  const limit = args.limit || 20;
  try {
    const res = await fetch(`${FILE_API_URL}/items?limit=${limit}`, { timeout: 10000 });
    if (!res.ok) {
      return { content: [{ type: 'text', text: `sjl-file-api error ${res.status}` }], isError: true };
    }
    const data = await res.json();
    const items = Array.isArray(data) ? data : (data.items || []);
    if (items.length === 0) return { content: [{ type: 'text', text: 'No items in file API.' }] };
    const lines = items.map((item) => {
      const name = item.name || item.filename || item.key || JSON.stringify(item);
      const size = item.size ? ` (${(item.size / 1024).toFixed(1)} KB)` : '';
      return `  • ${name}${size}`;
    });
    return { content: [{ type: 'text', text: `Recent files (${items.length}):\n\n${lines.join('\n')}` }] };
  } catch (e) {
    return { content: [{ type: 'text', text: `Error: ${e.message}` }], isError: true };
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// MCP request dispatcher
// ─────────────────────────────────────────────────────────────────────────────

async function handleToolCall(name, args) {
  switch (name) {
    case 'system_status':       return handleSystemStatus();
    case 'storage_inbox_status': return handleStorageInboxStatus(args);
    case 'storage_list':         return handleStorageList(args);
    case 'rclone_list_remotes':  return handleRcloneListRemotes();
    case 'rclone_sync_inbox':    return handleRcloneSyncInbox();
    case 'n8n_list_workflows':   return handleN8nListWorkflows();
    case 'n8n_trigger_workflow': return handleN8nTriggerWorkflow(args);
    case 'files_list_inbox':     return handleFilesListInbox(args);
    default:
      return { content: [{ type: 'text', text: `Unknown tool: ${name}` }], isError: true };
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Express router (attach to existing sjl-mcp-gateway Express app)
// ─────────────────────────────────────────────────────────────────────────────

function attachToApp(app) {
  // MCP endpoint — handles JSON-RPC 2.0
  app.post('/mcp', async (req, res) => {
    const { jsonrpc, id, method, params } = req.body || {};

    if (jsonrpc !== '2.0') {
      return res.status(400).json({ error: 'Expected JSON-RPC 2.0' });
    }

    try {
      if (method === 'initialize') {
        return res.json({
          jsonrpc: '2.0', id,
          result: {
            protocolVersion: '2024-11-05',
            capabilities: { tools: {} },
            serverInfo: { name: 'sjl-cloud', version: '1.0.0' },
          },
        });
      }

      if (method === 'tools/list') {
        return res.json({ jsonrpc: '2.0', id, result: { tools: TOOLS } });
      }

      if (method === 'tools/call') {
        const { name, arguments: args = {} } = params || {};
        const result = await handleToolCall(name, args);
        return res.json({ jsonrpc: '2.0', id, result });
      }

      return res.json({
        jsonrpc: '2.0', id,
        error: { code: -32601, message: `Method not found: ${method}` },
      });
    } catch (e) {
      console.error('[MCP] Error handling', method, ':', e);
      return res.status(500).json({
        jsonrpc: '2.0', id,
        error: { code: -32603, message: e.message },
      });
    }
  });

  // Discovery endpoint
  app.get('/mcp', (req, res) => {
    res.json({
      name: 'sjl-cloud',
      version: '1.0.0',
      transport: 'http',
      endpoint: '/mcp',
      tools: TOOLS.map((t) => ({ name: t.name, description: t.description })),
    });
  });

  console.log('[MCP] Tools registered:', TOOLS.map((t) => t.name).join(', '));
}

// ─────────────────────────────────────────────────────────────────────────────
// Standalone mode (node mcp-tools-config.js)
// ─────────────────────────────────────────────────────────────────────────────

if (require.main === module) {
  const express = require('express');
  const app = express();
  app.use(express.json({ limit: '10mb' }));
  attachToApp(app);

  // Keep original status endpoint
  app.get('/status', (req, res) => {
    res.json({ status: 'ok', service: 'sjl-mcp-gateway', tools: TOOLS.length });
  });

  const PORT = process.env.PORT || 7300;
  app.listen(PORT, '0.0.0.0', () => {
    console.log(`[MCP] sjl-mcp-gateway running on port ${PORT}`);
    console.log(`[MCP] Endpoint: http://0.0.0.0:${PORT}/mcp`);
  });
}

module.exports = { attachToApp, TOOLS, handleToolCall };
