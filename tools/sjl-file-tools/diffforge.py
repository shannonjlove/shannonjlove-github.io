#!/usr/bin/env python3
"""
DiffForge — server-side DeltaWalker replacement
Web-based file & directory comparison with side-by-side diff, char-level highlighting,
file upload, server-path access, and directory tree compare.

Usage:
    python diffforge.py [--port 8082] [--host 0.0.0.0]
    uvicorn diffforge:app --host 0.0.0.0 --port 8082
"""

from __future__ import annotations

import difflib
import hashlib
import os
import sys
from pathlib import Path
from typing import List, Optional

import uvicorn
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

# ─── Config ──────────────────────────────────────────────────────────────────

PORT        = int(os.environ.get("DF_PORT", "8082"))
ALLOW_PATHS = os.environ.get("DF_ALLOW_PATHS", "/data")   # comma-separated roots

def allowed_path(p: str) -> bool:
    roots = [r.strip() for r in ALLOW_PATHS.split(",")]
    return any(Path(p).resolve().is_relative_to(r) for r in roots)


# ─── FastAPI ─────────────────────────────────────────────────────────────────

app = FastAPI(title="DiffForge", version="1.0.0",
              description="File & directory comparison — server-side DeltaWalker")


# ─── Diff Engine ─────────────────────────────────────────────────────────────

def compute_diff(left_lines: List[str], right_lines: List[str], context: int = 3) -> dict:
    sm = difflib.SequenceMatcher(None, left_lines, right_lines, autojunk=False)
    ratio = round(sm.ratio(), 4)

    hunks = []
    additions = deletions = 0

    for group in sm.get_grouped_opcodes(context):
        hunk_lines = []
        i1 = group[0][1]; i2 = group[-1][2]
        j1 = group[0][3]; j2 = group[-1][4]
        header = f"-{i1+1},{i2-i1} +{j1+1},{j2-j1}"

        for tag, a1, a2, b1, b2 in group:
            if tag == "equal":
                for line in left_lines[a1:a2]:
                    hunk_lines.append({"type": "context",
                                       "left": line.rstrip("\n"),
                                       "right": line.rstrip("\n")})

            elif tag == "delete":
                for line in left_lines[a1:a2]:
                    hunk_lines.append({"type": "removed",
                                       "left": line.rstrip("\n"), "right": ""})
                    deletions += 1

            elif tag == "insert":
                for line in right_lines[b1:b2]:
                    hunk_lines.append({"type": "added",
                                       "left": "", "right": line.rstrip("\n")})
                    additions += 1

            elif tag == "replace":
                lc = [l.rstrip("\n") for l in left_lines[a1:a2]]
                rc = [r.rstrip("\n") for r in right_lines[b1:b2]]
                for k in range(max(len(lc), len(rc))):
                    l = lc[k] if k < len(lc) else ""
                    r = rc[k] if k < len(rc) else ""
                    if l and r:
                        hunk_lines.append({"type": "changed", "left": l, "right": r})
                        additions += 1; deletions += 1
                    elif l:
                        hunk_lines.append({"type": "removed", "left": l, "right": ""})
                        deletions += 1
                    else:
                        hunk_lines.append({"type": "added", "left": "", "right": r})
                        additions += 1

        hunks.append({"header": header, "lines": hunk_lines})

    return {"ratio": ratio, "additions": additions,
            "deletions": deletions, "hunks": hunks}


# ─── Request models ──────────────────────────────────────────────────────────

class TextDiff(BaseModel):
    left: str;  right: str
    context: int = 3

class PathDiff(BaseModel):
    left_path:  str;  right_path: str
    context:    int = 3

class DirDiff(BaseModel):
    left_dir:  str;  right_dir: str


# ─── Routes ──────────────────────────────────────────────────────────────────

@app.post("/diff/text")
async def diff_text(req: TextDiff):
    return compute_diff(req.left.splitlines(True), req.right.splitlines(True), req.context)


@app.post("/diff/files")
async def diff_files(
    left:    UploadFile = File(...),
    right:   UploadFile = File(...),
    context: int = 3,
):
    lc = (await left.read()).decode("utf-8", errors="replace")
    rc = (await right.read()).decode("utf-8", errors="replace")
    return compute_diff(lc.splitlines(True), rc.splitlines(True), context)


@app.post("/diff/paths")
async def diff_paths(req: PathDiff):
    for p in (req.left_path, req.right_path):
        if not allowed_path(p):
            raise HTTPException(403, f"Path not allowed: {p}")
    lp, rp = Path(req.left_path), Path(req.right_path)
    if not lp.exists(): return {"error": f"Not found: {req.left_path}"}
    if not rp.exists(): return {"error": f"Not found: {req.right_path}"}
    try:
        lc = lp.read_text(errors="replace")
        rc = rp.read_text(errors="replace")
    except Exception as e:
        return {"error": str(e)}
    return compute_diff(lc.splitlines(True), rc.splitlines(True), req.context)


@app.post("/diff/dirs")
async def diff_dirs(req: DirDiff):
    for d in (req.left_dir, req.right_dir):
        if not allowed_path(d):
            raise HTTPException(403, f"Path not allowed: {d}")
    ld, rd = Path(req.left_dir), Path(req.right_dir)
    if not ld.is_dir(): raise HTTPException(400, f"Not a dir: {req.left_dir}")
    if not rd.is_dir(): raise HTTPException(400, f"Not a dir: {req.right_dir}")

    def walk(base: Path):
        return {f.relative_to(base) for f in base.rglob("*") if f.is_file()}

    lf = walk(ld); rf = walk(rd)
    only_left  = sorted(str(f) for f in lf - rf)
    only_right = sorted(str(f) for f in rf - lf)
    modified   = []
    same       = []

    for f in lf & rf:
        lh = hashlib.md5((ld / f).read_bytes()).hexdigest()
        rh = hashlib.md5((rd / f).read_bytes()).hexdigest()
        (modified if lh != rh else same).append(str(f))

    return {
        "only_left":  only_left,
        "only_right": only_right,
        "modified":   sorted(modified),
        "same":       sorted(same),
        "stats": {
            "only_left":  len(only_left),
            "only_right": len(only_right),
            "modified":   len(modified),
            "same":       len(same),
        },
    }


# ─── Web UI ──────────────────────────────────────────────────────────────────

UI = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>DiffForge</title>
<style>
:root {
  --bg:      #0d1117;
  --surface: #161b22;
  --border:  #30363d;
  --text:    #e6edf3;
  --muted:   #8b949e;
  --blue:    #58a6ff;
  --green:   #3fb950;
  --red:     #f85149;
  --yellow:  #e3b341;
  --add-bg:  rgba(35,134,54,.15);
  --rem-bg:  rgba(248,81,73,.15);
  --add-ln:  rgba(35,134,54,.28);
  --rem-ln:  rgba(248,81,73,.28);
  --add-hl:  rgba(35,134,54,.45);
  --rem-hl:  rgba(248,81,73,.45);
}
*{box-sizing:border-box;margin:0;padding:0}
body{font:13px/1.5 'JetBrains Mono','Fira Code','Courier New',monospace;
     background:var(--bg);color:var(--text)}
header{display:flex;align-items:center;gap:.75rem;padding:.75rem 1.5rem;
       background:var(--surface);border-bottom:1px solid var(--border)}
header h1{font-size:1rem;color:var(--blue)}
.badge{font-size:.65rem;padding:.15rem .5rem;border-radius:8px;
       background:#1c2e4a;color:var(--blue)}
.wrap{padding:1.5rem;max-width:1800px;margin:0 auto}
.tabs{display:flex;border-bottom:1px solid var(--border);margin-bottom:1rem;gap:0}
.tab{padding:.5rem 1.1rem;cursor:pointer;border-bottom:2px solid transparent;
     color:var(--muted);font-size:.85rem;transition:color .15s}
.tab.active,.tab:hover{color:var(--blue);border-bottom-color:var(--blue)}
.panel{display:none}.panel.active{display:block}
.two{display:grid;grid-template-columns:1fr 1fr;gap:.75rem;margin-bottom:.75rem}
.lbl{font-size:.72rem;color:var(--muted);margin-bottom:.3rem}
textarea{width:100%;height:280px;background:var(--surface);color:var(--text);
  border:1px solid var(--border);padding:.75rem;font:13px/1.5 monospace;
  resize:vertical;border-radius:5px}
textarea:focus{outline:none;border-color:var(--blue)}
input[type=text],input[type=file]{width:100%;background:var(--surface);
  color:var(--text);border:1px solid var(--border);padding:.5rem .75rem;
  border-radius:5px;font:13px monospace}
input[type=text]:focus{outline:none;border-color:var(--blue)}
.toolbar{display:flex;gap:.5rem;align-items:center;flex-wrap:wrap;margin-bottom:.75rem}
button{background:#238636;color:#fff;border:none;padding:.45rem 1rem;
  border-radius:5px;cursor:pointer;font:13px monospace}
button:hover{background:#2ea043}
button.sec{background:var(--surface);border:1px solid var(--border);color:var(--text)}
button.sec:hover{background:var(--border)}
select{background:var(--surface);color:var(--text);border:1px solid var(--border);
  padding:.45rem .6rem;border-radius:5px;font:13px monospace}
.stats{display:flex;gap:1rem;margin-bottom:.5rem;font-size:.8rem;
  padding:.4rem .6rem;background:var(--surface);border-radius:5px;flex-wrap:wrap}
.stat-add{color:var(--green)} .stat-rem{color:var(--red)} .stat-sim{color:var(--blue)}
#diff-out{background:var(--surface);border:1px solid var(--border);
  border-radius:5px;overflow:auto;max-height:72vh}
.dt{width:100%;border-collapse:collapse;font:12.5px/1.5 monospace;white-space:pre}
.dt td{padding:0 .6rem;vertical-align:top}
.dt .ln{color:var(--muted);width:36px;text-align:right;user-select:none;
  border-right:1px solid var(--border);padding:0 .4rem}
.add{background:var(--add-bg)} .add .ln{background:var(--add-ln)}
.rem{background:var(--rem-bg)} .rem .ln{background:var(--rem-ln)}
.hdr{background:rgba(88,166,255,.09);color:var(--blue);
  font-size:.72rem;padding:.25rem .7rem;font-family:monospace}
.ch-add{background:var(--add-hl);border-radius:2px}
.ch-rem{background:var(--rem-hl);border-radius:2px;text-decoration:line-through}
.sep{width:22px;text-align:center;color:var(--muted)}
.dir-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:.4rem;margin-top:1rem}
.df{padding:.4rem .8rem;border-radius:4px;border:1px solid var(--border);
  font-size:.8rem;cursor:pointer;background:var(--surface)}
.df:hover{border-color:var(--blue)} .only-l{color:var(--red)} .only-r{color:var(--green)}
.mod{color:var(--yellow)} .same{color:var(--muted)}
.dir-stats{display:flex;gap:1rem;margin-top:.5rem;font-size:.8rem}
.error{color:var(--red);padding:.75rem}
</style>
</head>
<body>
<header>
  <h1>⚡ DiffForge</h1>
  <span class=badge>v1.0</span>
  <span style="color:var(--muted);font-size:.8rem;margin-left:.5rem">File Comparison &amp; Merge</span>
</header>

<div class=wrap>
  <div class=tabs>
    <div class="tab active" onclick="tab('text')">Text</div>
    <div class=tab onclick="tab('files')">Upload Files</div>
    <div class=tab onclick="tab('paths')">Server Paths</div>
    <div class=tab onclick="tab('dirs')">Directories</div>
  </div>

  <!-- Text -->
  <div class="panel active" id=p-text>
    <div class=two>
      <div><div class=lbl>Left / Original</div>
        <textarea id=lt placeholder="Paste original content…"></textarea></div>
      <div><div class=lbl>Right / Modified</div>
        <textarea id=rt placeholder="Paste modified content…"></textarea></div>
    </div>
    <div class=toolbar>
      <button onclick="diffText()">Compare</button>
      <button class=sec onclick="clearAll()">Clear</button>
      <select id=ctx>
        <option value=3>3 context lines</option>
        <option value=5>5</option><option value=10>10</option><option value=0>0</option>
      </select>
    </div>
  </div>

  <!-- Files -->
  <div class=panel id=p-files>
    <div class=two>
      <div><div class=lbl>Left File</div><input type=file id=lf></div>
      <div><div class=lbl>Right File</div><input type=file id=rf></div>
    </div>
    <div class=toolbar><button onclick="diffFiles()">Compare Files</button></div>
  </div>

  <!-- Paths -->
  <div class=panel id=p-paths>
    <div class=two>
      <div><div class=lbl>Left Path (server)</div>
        <input type=text id=lp placeholder="/data/..."></div>
      <div><div class=lbl>Right Path (server)</div>
        <input type=text id=rp placeholder="/data/..."></div>
    </div>
    <div class=toolbar><button onclick="diffPaths()">Compare Paths</button></div>
  </div>

  <!-- Dirs -->
  <div class=panel id=p-dirs>
    <div class=two>
      <div><div class=lbl>Left Directory</div>
        <input type=text id=ld placeholder="/data/folder-a"></div>
      <div><div class=lbl>Right Directory</div>
        <input type=text id=rd placeholder="/data/folder-b"></div>
    </div>
    <div class=toolbar><button onclick="diffDirs()">Compare Directories</button></div>
    <div id=dir-out></div>
  </div>

  <div id=stats class=stats style=display:none></div>
  <div id=diff-out></div>
</div>

<script>
function tab(name){
  document.querySelectorAll('.tab').forEach((t,i)=>{
    t.classList.toggle('active',['text','files','paths','dirs'][i]===name)
  });
  ['text','files','paths','dirs'].forEach(n=>{
    document.getElementById('p-'+n).classList.toggle('active',n===name)
  });
}

async function diffText(){
  const ctx=+document.getElementById('ctx').value;
  render(await post('/diff/text',{
    left:document.getElementById('lt').value,
    right:document.getElementById('rt').value,context:ctx}));
}

async function diffFiles(){
  const fd=new FormData();
  fd.append('left',document.getElementById('lf').files[0]);
  fd.append('right',document.getElementById('rf').files[0]);
  render(await(await fetch('/diff/files',{method:'POST',body:fd})).json());
}

async function diffPaths(){
  render(await post('/diff/paths',{
    left_path:document.getElementById('lp').value,
    right_path:document.getElementById('rp').value}));
}

async function diffDirs(){
  const res=await post('/diff/dirs',{
    left_dir:document.getElementById('ld').value,
    right_dir:document.getElementById('rd').value});
  const d=document.getElementById('dir-out');
  if(res.error){d.innerHTML=`<div class=error>${res.error}</div>`;return}
  const s=res.stats;
  d.innerHTML=`<div class=dir-stats>
    <span class=only-l>← only left: ${s.only_left}</span>
    <span class=only-r>→ only right: ${s.only_right}</span>
    <span class=mod>~ modified: ${s.modified}</span>
    <span class=same>= same: ${s.same}</span>
  </div><div class=dir-grid>
    ${res.only_left.map(f=>`<div class="df only-l" title="Only in left">← ${esc(f)}</div>`).join('')}
    ${res.only_right.map(f=>`<div class="df only-r" title="Only in right">→ ${esc(f)}</div>`).join('')}
    ${res.modified.map(f=>`<div class="df mod" onclick="compareFile('${esc(document.getElementById('ld').value)}/${esc(f)}','${esc(document.getElementById('rd').value)}/${esc(f)}')">~ ${esc(f)}</div>`).join('')}
    ${res.same.map(f=>`<div class="df same">= ${esc(f)}</div>`).join('')}
  </div>`;
}

async function compareFile(l,r){
  document.getElementById('lp').value=l;
  document.getElementById('rp').value=r;
  tab('paths');await diffPaths();
}

async function post(url,body){
  const r=await fetch(url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
  return r.json();
}

function clearAll(){
  document.getElementById('lt').value='';
  document.getElementById('rt').value='';
  document.getElementById('diff-out').innerHTML='';
  document.getElementById('stats').style.display='none';
}

function render(data){
  const st=document.getElementById('stats');
  const out=document.getElementById('diff-out');
  if(data.error){out.innerHTML=`<div class=error>${esc(data.error)}</div>`;return}
  st.style.display='flex';
  st.innerHTML=`<span class=stat-sim>Similarity: <b>${(data.ratio*100).toFixed(1)}%</b></span>
    <span class=stat-add>+${data.additions} added</span>
    <span class=stat-rem>-${data.deletions} removed</span>
    <span style="color:var(--muted)">${data.additions+data.deletions} changed lines</span>`;

  let ll=1,rl=1,html='<table class=dt>';
  for(const hunk of data.hunks){
    html+=`<tr><td colspan=5 class=hdr>@@ ${esc(hunk.header)} @@</td></tr>`;
    for(const ln of hunk.lines){
      if(ln.type==='context'){
        html+=`<tr><td class=ln>${ll++}</td><td>${esc(ln.left)}</td>
          <td class=sep></td>
          <td class=ln>${rl++}</td><td>${esc(ln.right)}</td></tr>`;
      } else if(ln.type==='removed'){
        html+=`<tr class=rem><td class=ln>${ll++}</td>
          <td>${charDiff(ln.left,ln.right,'rem')}</td>
          <td class=sep style="color:var(--red)">-</td>
          <td class=ln></td><td></td></tr>`;
      } else if(ln.type==='added'){
        html+=`<tr class=add><td class=ln></td><td></td>
          <td class=sep style="color:var(--green)">+</td>
          <td class=ln>${rl++}</td>
          <td>${charDiff(ln.right,ln.left,'add')}</td></tr>`;
      } else if(ln.type==='changed'){
        html+=`<tr class=rem><td class=ln>${ll++}</td>
          <td>${charDiff(ln.left,ln.right,'rem')}</td>
          <td class=sep style="color:var(--yellow)">~</td>
          <td class=ln>${rl++}</td>
          <td>${charDiff(ln.right,ln.left,'add')}</td></tr>`;
      }
    }
  }
  html+='</table>';
  out.innerHTML=html;
}

function charDiff(a,b,side){
  // Word-level highlight
  const wa=a.split(/(\s+)/), wb=b.split(/(\s+)/);
  let result='',ai=0,bi=0;
  while(ai<wa.length){
    if(bi<wb.length && wa[ai]===wb[bi]){result+=esc(wa[ai]);ai++;bi++;}
    else{result+=`<span class=ch-${side}>${esc(wa[ai])}</span>`;ai++;}
  }
  return result;
}

function esc(s){return(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')}
</script>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
async def home():
    return UI


# ─── Entry point ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="DiffForge — server-side DeltaWalker")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=PORT)
    args = parser.parse_args()
    uvicorn.run(app, host=args.host, port=args.port)
