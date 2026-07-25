# SJL Hub — Gaussian Splatting Imaging + 3D Filesystem Visualization
# Lovable Build Prompt — Sprint 2 Addition

## Context

Extends the SJL Hub dashboard (built in Sprint 1 with React 18 + TypeScript + Tailwind
+ shadcn/ui) with two new screens:

1. **3DGS Scene Manager** — configure and monitor 3D Gaussian Splatting imaging pipeline
   connecting to LichtFeld Studio's MCP bridge at `127.0.0.1:45677`
2. **3D Filesystem Visualizer** — Three.js-powered 3D treemap of the PARA file structure
   across all 8 cloud services

---

## Lovable Prompt

```
Add two screens to the SJL Hub React app (React 18, TypeScript, Tailwind CSS, shadcn/ui,
React Router v6). The app already has a Dashboard, Project Hub View, Project Detail,
File Detail, and Universal Link Resolver at /open?id=[UUID24].

---

SCREEN 6: 3DGS SCENE MANAGER
Route: /scenes

A panel for managing 3D Gaussian Splatting scenes via LichtFeld Studio.

LichtFeld Studio exposes an MCP bridge at http://127.0.0.1:45677/mcp
(HTTP POST with standard MCP tool_call JSON body).

Available MCP tools (call via POST to /mcp):
  - get_scene_info       → { name, status, gaussian_count, training_step, fps }
  - list_export_presets  → array of { id, name, resolution, format }
  - trigger_export       → { preset_id, output_path } → { job_id }
  - get_export_status    → { job_id } → { status, progress, output_path }
  - get_viewport_stats   → { vram_mb, render_fps, gaussian_visible }

Layout:
- LEFT PANEL (30%):
  - Connection status badge (connected/disconnected to port 45677)
  - Current scene card: name, gaussian count, training step, live FPS
  - VRAM usage bar (show percentage and MB)
  - "Refresh" button (poll /mcp every 5s when connected)

- RIGHT PANEL (70%):
  - "Export Configuration" section
  - Resolution grid: Viewport / 1080p / 4K / 8K / 12K / 16K / 20K / 24K / 28K / 32K
    - Each tile shows resolution, VRAM estimate (from viewport-export-lichtfeld plugin specs)
    - VRAM estimates: 1080p=25MB, 4K=100MB, 8K=400MB, 12K=900MB, 16K=1.6GB, 20K=2.5GB,
      24K=3.6GB, 28K=4.9GB, 32K=6.4GB
    - Tile color: green if VRAM available, amber if close to limit, red if over
    - Selected tile highlights with accent border
  - Format selector: JPG (quality slider 60–100) | PNG (compression 0–9)
  - Transparency toggle (PNG only): "RGBA via BW2A alpha extraction"
  - Output path input (default: ~/Desktop/[scene-name]-[resolution].[ext])
  - Export button → calls trigger_export → shows progress bar with cancel
  - Export history: last 5 exports with filename, resolution, timestamp, open-in-finder link

- SJL INTEGRATION:
  - "Save to PARA" toggle: when enabled, after export:
    1. Renames exported file to SJL convention:
       YYYY-MM-DD_HH-MM_media-image_[scene-name]-[resolution]_UUID24.[ext]
    2. Routes to @RESOURCES_sjlcloud/3dgs-exports/
    3. Fires HookVault webhook (POST to /api/hook) with the file's full metadata payload
  - UUID24 generated client-side (uuid4().hex.slice(0,24) equivalent in JS)

---

SCREEN 7: 3D FILESYSTEM VISUALIZER
Route: /fs3d

An interactive Three.js 3D visualization of the SJL PARA file system across all 8 clouds.

Tech: use @react-three/fiber and @react-three/drei (already in React ecosystem).
Do NOT use an external CDN. Import from the npm packages.

VISUALIZATION CONCEPT:
- 3D force-directed graph OR 3D treemap, user can toggle between views
- Force-directed: nodes float in 3D space; edges connect files to their project hub
- Treemap: stacked 3D boxes (XY footprint = file count, Z height = file age)

DATA MODEL (from HookVault REST API — mock for Lovable build):
  clouds: ["gdrive", "mediafire", "pcloud", "dropbox", "dropbox-biz", "mega", "icloud", "sjlcloud"]
  para: ["projects", "areas", "resources", "archives", "inbox"]
  Each cloud×para bucket has: { file_count, total_size_mb, last_modified, project_hubs[] }
  Each project hub has: { name, slug, file_count, files: [{ uuid24, name, category, size_mb }] }

NODE TYPES AND SIZES:
  - Cloud root node: large sphere, cloud's primary color
    (gdrive=blue, pcloud=cyan, dropbox=navy, mega=red, icloud=silver, sjlcloud=purple)
  - PARA bucket node: medium cube
    (projects=green, areas=teal, resources=amber, archives=gray, inbox=orange)
  - Project hub node: rounded box, size = sqrt(file_count)
  - File node: small point/dot, color = category
    (media=magenta, document=white, code=green, finance=yellow, legal=red, creative=pink)

CONTROLS:
  - Orbit controls (drag to rotate, scroll to zoom, right-drag to pan)
  - Filter panel (right sidebar):
    - Toggle clouds on/off (checkbox grid, cloud color coding)
    - Toggle PARA buckets on/off
    - Category filter (multi-select chips)
    - Search: highlights matching nodes, dims others
  - Click a project hub node → opens Project Detail panel (from SJL Hub Screen 3) as a drawer
  - Click a file node → opens File Detail panel (Screen 4) as a drawer
  - Hover tooltip: shows name, cloud, PARA bucket, file count/size

PERFORMANCE:
  - Render at most 2000 nodes at once — use LOD (level of detail) for large datasets
  - Files beyond the 2000 limit aggregate into their parent hub node
  - Use instancedMesh for file dots (all share one geometry)
  - 60 FPS target on a modern laptop; degrade gracefully by hiding file-level nodes first

TOOLBAR (top of screen):
  - View toggle: Force-directed | Treemap
  - Reset camera button
  - Screenshot button: exports current view as PNG
  - "Focus on [cloud]" quick-jump dropdown

THEME:
  - Dark background only (#0a0a0f) — the 3D space is always dark
  - Ambient light (dim) + point light from above + subtle fog at distance
  - Node labels (drei Text component) visible at medium zoom, hidden when zoomed out far

---

ROUTING ADDITION:
Add to the existing nav sidebar:
  - "3DGS Scenes" item with a cube icon → /scenes
  - "3D File View" item with a network icon → /fs3d

Both screens should respect the existing dark/light theme toggle for their UI chrome
(sidebars, drawers, filter panels) — only the Three.js canvas itself stays dark.

Use mock data for all API calls. Structure the data fetching as hooks
(useLichtFeldMCP, useFileSystem3D) with a config flag to swap mock → live.

Tech additions needed (add to package.json):
  "@react-three/fiber": "^8",
  "@react-three/drei": "^9",
  "three": "^0.170"
```

---

## Configuration Files

### LichtFeld MCP Client (TypeScript)

```typescript
// src/lib/lichtfeld-mcp.ts
// Thin wrapper around the LichtFeld Studio MCP bridge at port 45677

const LICHTFELD_MCP_URL = import.meta.env.VITE_LICHTFELD_MCP_URL || 'http://127.0.0.1:45677/mcp';

interface MCPToolCall {
  tool: string;
  arguments?: Record<string, unknown>;
}

interface MCPResponse<T = unknown> {
  result?: T;
  error?: { code: number; message: string };
}

export async function callLichtFeldMCP<T>(call: MCPToolCall): Promise<T> {
  const response = await fetch(LICHTFELD_MCP_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      jsonrpc: '2.0',
      id: Date.now(),
      method: 'tools/call',
      params: { name: call.tool, arguments: call.arguments ?? {} },
    }),
    signal: AbortSignal.timeout(5000),
  });

  if (!response.ok) throw new Error(`MCP HTTP ${response.status}`);
  const data: MCPResponse<T> = await response.json();
  if (data.error) throw new Error(`MCP error ${data.error.code}: ${data.error.message}`);
  return data.result as T;
}

export async function checkLichtFeldConnection(): Promise<boolean> {
  try {
    await callLichtFeldMCP({ tool: 'get_scene_info' });
    return true;
  } catch {
    return false;
  }
}
```

### HookVault Integration for SJL Export

```typescript
// src/lib/hookvault.ts
// When a 3DGS export is saved to PARA, fire HookVault webhook

const HOOKVAULT_URL = import.meta.env.VITE_HOOKVAULT_URL || 'http://localhost:3033/api/hook';

function generateUUID24(): string {
  return Array.from(crypto.getRandomValues(new Uint8Array(12)))
    .map(b => b.toString(16).padStart(2, '0'))
    .join('');
}

function sjlFilename(opts: {
  date: Date; category: string; subcategory: string;
  description: string; uuid24: string; ext: string;
}): string {
  const d = opts.date;
  const pad = (n: number) => String(n).padStart(2, '0');
  const dateStr = `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}`;
  const timeStr = `${pad(d.getHours())}-${pad(d.getMinutes())}`;
  const desc = opts.description.toLowerCase().replace(/[^a-z0-9-]/g, '-').slice(0, 40);
  return `${dateStr}_${timeStr}_${opts.category}-${opts.subcategory}_${desc}_${opts.uuid24}.${opts.ext}`;
}

export async function hook3DGSExport(opts: {
  sceneName: string;
  resolution: string;
  format: 'jpg' | 'png';
  cloudPath: string;
}): Promise<{ uuid24: string; filename: string }> {
  const uuid24 = generateUUID24();
  const now = new Date();
  const filename = sjlFilename({
    date: now,
    category: 'media',
    subcategory: 'image',
    description: `${opts.sceneName}-${opts.resolution}-3dgs`,
    uuid24,
    ext: opts.format,
  });

  const payload = {
    title: filename,
    link: `file://${opts.cloudPath}/${filename}`,
    uuid24,
    cloud: 'sjlcloud',
    para_bucket: 'resources',
    tags: ['sjl', 'sjlcloud', 'media', 'image', '3dgs', opts.sceneName, opts.resolution],
    category: 'media',
    subcategory: 'image',
    excerpt: `3DGS export | Scene: ${opts.sceneName} | Res: ${opts.resolution} | ${opts.format.toUpperCase()}`,
    is_hub: false,
    canonical: true,
    processed_by: 'sjl-hub',
    created: now.toISOString(),
  };

  await fetch(HOOKVAULT_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  }).catch(console.warn);   // fire and forget

  return { uuid24, filename };
}
```

### Vite Environment Config

```bash
# .env.local (for local dev — not committed)
VITE_LICHTFELD_MCP_URL=http://127.0.0.1:45677/mcp
VITE_HOOKVAULT_URL=http://localhost:3033/api/hook
VITE_FILESYSTEM_API_URL=http://localhost:3033/api/filesystem

# .env.production
VITE_LICHTFELD_MCP_URL=http://127.0.0.1:45677/mcp
VITE_HOOKVAULT_URL=https://hub.shannonjlove.cloud/api/hook
VITE_FILESYSTEM_API_URL=https://hub.shannonjlove.cloud/api/filesystem
```

---

## VRAM Reference Table (from viewport-export-lichtfeld plugin)

| Resolution | Height | Approx VRAM |
|---|---|---|
| 1080p | 1080 | 25 MB |
| 4K | 2160 | 100 MB |
| 8K | 4320 | 400 MB |
| 12K | 6480 | 900 MB |
| 16K | 8640 | 1.6 GB |
| 20K | 10800 | 2.5 GB |
| 24K | 12960 | 3.6 GB |
| 28K | 15120 | 4.9 GB |
| 32K | 17280 | 6.4 GB |

---

## Package Dependencies to Add to SJL Hub

```json
{
  "@react-three/fiber": "^8",
  "@react-three/drei": "^9",
  "three": "^0.170"
}
```

---

## Files to Create in SJL Hub Repo

```
src/
  lib/
    lichtfeld-mcp.ts         ← MCP client for LichtFeld Studio
    hookvault.ts             ← HookVault webhook + SJL filename generation
  hooks/
    useLichtFeldMCP.ts       ← React hook: connection status + scene data polling
    useFileSystem3D.ts       ← React hook: PARA filesystem data for 3D render
  pages/
    SceneManager.tsx         ← Screen 6: 3DGS Scene Manager
    FileSystem3D.tsx         ← Screen 7: 3D Filesystem Visualizer
  components/3d/
    CloudNode.tsx            ← Three.js cloud root sphere
    ParaBucketNode.tsx       ← Three.js PARA bucket cube
    ProjectHubNode.tsx       ← Three.js project hub rounded box
    FileCloud.tsx            ← Three.js instanced file dot cloud
    ForceGraph3D.tsx         ← Force-directed layout orchestrator
    TreeMap3D.tsx            ← 3D treemap layout orchestrator
    SceneCanvas.tsx          ← @react-three/fiber Canvas wrapper
```
