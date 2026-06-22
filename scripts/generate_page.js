// generate_page.js - AI Inspiration Notebook v2.1 (UTF-8 safe)
// Usage: node scripts/generate_page.js

const fs = require("fs");
const path = require("path");
const { execSync } = require("child_process");
const ROOT = path.resolve(__dirname, "..");

const projects = JSON.parse(fs.readFileSync(ROOT + "/data/projects.json", "utf-8"));
let tweets = [];
try {
  const dirs = fs.readdirSync(ROOT + "/data/raw").filter(d => /^\d{4}-\d{2}-\d{2}$/.test(d)).sort().reverse();
  for (const d of dirs) {
    const xp = ROOT + "/data/raw/" + d + "/x.json";
    if (fs.existsSync(xp)) { tweets = JSON.parse(fs.readFileSync(xp, "utf-8")); break; }
  }
} catch(e) {}

const now = new Date().toISOString().replace("T", " ").slice(0, 16);

const esc = s => { if(!s)return""; return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;").replace(/'/g,"&#39;"); };
const aColor = n => { const c=["#a4c0b4","#a8c4c0","#d4b8a8","#c8a8b8","#b8c4a8","#a8b4c4","#c4a8b0","#a8b8c4","#b4a8c4","#a8c4b8","#c4b8a8","#b8a8c4","#c0a8b4","#a8c0c4","#c4a4a8","#a8c4ac"]; let h=0; for(let i=0;i<n.length;i++)h=n.charCodeAt(i)+((h<<5)-h); return c[Math.abs(h)%c.length]; };
const sIcons = {"GitHub":"&#128187;","YouTube":"&#9654;"};
const catLabel = {"chrome-extension":"Extension","creative":"Creative Tools","workflow":"Workflow"};

// --- Bug 4 fix: staggered card animation ---
function card(p, idx) {
  const icon=sIcons[p.source]||"&#128279;", cL=catLabel[p.category]||"Creative", cK=p.category==="chrome-extension"?"extension":p.category;
  const tags=(p.tags||[]).map(t=>`<span class="tag">${esc(t)}</span>`).join(""), a=p.analysis||{};
  // Staggered animation delay (Bug 4)
  const delay = Math.round((0.06 + idx * 0.08) * 100) / 100;
  const animStyle = idx < 10 ? ` style="animation: cardEnter 0.45s ease-out both; animation-delay: ${delay}s"` : "";
  let h=`<div class="card" data-category="${cK}" data-pid="${esc(p.id)}"${animStyle}>
  <div class="card-header">
    <span class="source-badge">${icon} ${esc(p.source)}</span>
    <span class="card-cat-badge" data-cat="${cK}">${cL}</span>
    <span class="card-date">${esc(p.date)}</span>
    <span class="fav-btn">&#9829;</span>
  </div>
  <h2 class="card-title">${esc(p.title)}</h2>
  <p class="card-desc">${esc(p.description)}</p>
`;
  let pv=""; if(a.insight){pv=a.insight.replace(/<mark>/g,"").replace(/<\/mark>/g,"").split("%%")[0].trim();if(pv.length>80)pv=pv.substring(0,77)+"...";h+=`  <div class="key-insight">
    <span class="key-insight-label">KEY INSIGHT</span>
    ${esc(pv)}
  </div>
`;}
  h+=`  <div class="expand-hint">click to expand</div>
  <div class="card-full">
    <div class="card-full-tags">${tags}</div>
    <div class="card-full-grid">
`;
  for(const[lb,vl]of[["Pain Point",a.pain_point],["Why AI",a.why_ai],["Product Insight",a.insight],["Transfer",a.transfer]]){
    if(!vl)continue;
    h+=`<div class="analysis-block">
  <span class="analysis-label">${lb}</span>
  <p>${vl}</p>
</div>
`;
  }
  h+=`    </div>
    <div style="display:flex;gap:14px;align-items:center;margin-top:18px;">
      <a href="${esc(p.url)}" target="_blank" class="ext-link">&#128279; View Original</a>
      <button class="close-btn">&#10005; Collapse</button>
    </div>
  </div>
</div>
`;
  return h;
}

// Builder timeline
let nav="", tl=`<div class="timeline-feed">
<h2 style="font-family:var(--font-serif);font-size:24px;margin-bottom:20px;">Builder Digest</h2>
`;
if(tweets.length>0){
  const bd={}; for(const t of tweets){const n=t.author_name||"Unknown";if(!bd[n])bd[n]=[];bd[n].push(t);}
  const bo=Object.keys(bd).sort((a,b)=>Math.max(...bd[b].map(t=>t.likes||0))-Math.max(...bd[a].map(t=>t.likes||0)));
  nav=`<nav class="timeline-sidebar">
  <div class="timeline-sidebar-title">Builders</div>
`;
  for(const n of bo){const u=bd[n][0].author_username||"";nav+=`    <a href="#builder-${u}" class="timeline-nav-item" data-builder="builder-${u}">${esc(n)}</a>
`;}
  nav+="</nav>\n";
  for(const n of bo){
    const bt=bd[n],u=bt[0].author_username||"";
    tl+=`<div class="timeline-builder" id="builder-${u}">
  <div class="timeline-builder-header">
    <span class="timeline-avatar" style="background:${aColor(n)}"></span>
    <span class="timeline-builder-name">${esc(n)}</span>
    <span class="timeline-builder-handle">@${esc(u)}</span>
  </div>
`;
    for(const t of bt){
      const zh=t.text_zh||"",en=t.text||"",url=t.url||"#";
      tl+=`  <div class="timeline-item">
`;
      if(zh){tl+=`    <p class="timeline-text timeline-text-zh">${esc(zh)}</p>
    <p class="timeline-text timeline-text-en">${esc(en)}</p>
`;}
      else{tl+=`    <p class="timeline-text">${esc(en)}</p>
`;}
      tl+=`    <div class="timeline-meta">
      <span class="timeline-date">${(t.created_at||"").slice(0,10)}</span>
      <span class="timeline-likes">&#9825; ${t.likes||0}</span>
      <a href="${esc(url)}" target="_blank" class="timeline-link">View on X &#8599;</a>
    </div>
  </div>
`;
    }
    tl+="</div>\n";
  }
}
tl+="</div>\n";

let e=0,c=0,w=0; for(const p of projects){if(p.category==="chrome-extension")e++;else if(p.category==="creative")c++;else w++;}

// --- Bug 7: daily random shuffle ---
function seedRandom(seed) {
  let s = seed;
  return function() { s = (s * 1664525 + 1013904223) & 0xFFFFFFFF; return (s >>> 0) / 0xFFFFFFFF; };
}
function shuffle(arr, seed) {
  const rng = seedRandom(seed);
  const a = arr.slice();
  for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(rng() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; }
  return a;
}
const todaySeed = new Date().toISOString().slice(0, 10).replace(/-/g, "");
const shuffledProjects = shuffle(projects, parseInt(todaySeed, 10));

const css = fs.readFileSync(ROOT+"/assets/style.css","utf-8");
const js = fs.readFileSync(ROOT+"/assets/script.js","utf-8");

// --- Bug 1: add header-meta with date and count ---
// --- Bug 3: add theme toggle button ---
const html = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI Inspiration Notebook</title>
<style>${css}</style>
</head>
<body>
<div class="container">
  <header class="header">
    <div class="header-top">
      <h1>AI Inspiration Notebook</h1>
      <div class="header-meta">
        <span>${now}</span>
        <span class="dot">&middot;</span>
        <span>${projects.length} projects</span>
      </div>
      <div class="header-right">
        <button class="fav-header-btn" onclick="openFavModal()" title="Your favorites">&#9825;</button>
        <button id="themeBtn" class="theme-btn" onclick="toggleTheme()">&#127769;</button>
      </div>
    </div>
  </header>

  <div class="channel-bar">
    <button class="channel-btn active" onclick="switchChannel(this, 'inspiration')">AI Projects</button>
    <button class="channel-btn" onclick="switchChannel(this, 'builder')">Builder Digest</button>
  </div>

  <div id="channel-inspiration" class="channel-content active">
    <div class="tabs" id="categoryTabs">
      <button class="tab active" onclick="filterCategory(this, 'all')">All (${projects.length})</button>
      <button class="tab" onclick="filterCategory(this, 'extension')">Extensions (${e})</button>
      <button class="tab" onclick="filterCategory(this, 'creative')">Creative (${c})</button>
      <button class="tab" onclick="filterCategory(this, 'workflow')">Workflow (${w})</button>
    </div>
    <div class="card-grid">
${shuffledProjects.map((p, i) => card(p, i)).join("")}    </div>
  </div>

  <div id="channel-builder" class="channel-content" style="display:none">
    <div class="timeline-layout">
${nav}      <div class="timeline-content">
${tl}      </div>
    </div>
  </div>

  <footer class="footer">
    <p>AI Inspiration Notebook \u2014 small AI product studies, every other day</p>
    <p style="margin-top:8px;font-size:11px;">Designed by Essie Zhang</p>
  </footer>
</div>

<div id="toast" class="toast"></div>
<div id="favModal" class="fav-modal" style="display:none">
  <div class="fav-modal-bg" onclick="closeFavModal()"></div>
  <div class="fav-modal-panel">
    <div class="fav-modal-header"><h2 class="fav-modal-title">Favorites</h2><button class="fav-modal-close" onclick="closeFavModal()">&times;</button></div>
    <div id="favModalBody" class="fav-modal-body"><div class="fav-empty">No favorites yet.</div></div>
  </div>
</div>

<script>${js}</script>
</body>
</html>`;

const buf = Buffer.from(html, "utf-8");
const outputPath = ROOT + "/index.html";
fs.writeFileSync(outputPath, buf);
console.log("[generate_page.js] Generated. Projects: " + projects.length + ", Tweets: " + tweets.length);

// --- Feat 5: Auto backup ---
const BACKUP_DIR = ROOT + "/data/backups";
fs.mkdirSync(BACKUP_DIR, { recursive: true });
const ts = new Date().toISOString().replace(/:/g, "-").replace(/T/, "_").slice(0, 19);
const backupPath = BACKUP_DIR + "/" + ts + "_index.html";
fs.copyFileSync(outputPath, backupPath);
console.log("  [Backup] " + backupPath);

// --- Feat 5 (cont): Cleanup backups older than 7 days ---
const cutoff = Date.now() - 7 * 24 * 60 * 60 * 1000;
let cleaned = 0;
for (const fname of fs.readdirSync(BACKUP_DIR)) {
  const fpath = BACKUP_DIR + "/" + fname;
  if (!fs.statSync(fpath).isFile()) continue;
  if (fs.statSync(fpath).mtimeMs < cutoff) { fs.unlinkSync(fpath); cleaned++; }
}
if (cleaned > 0) console.log("  [Backup] Cleaned " + cleaned + " old backup(s)");

// --- Feat 6: JS syntax check + rollback ---
try {
  const m = html.match(/<script>([\s\S]*?)<\/script>/);
  if (m) {
    const tmp = ROOT + "/data/_tmp_js_check.js";
    fs.writeFileSync(tmp, m[1], "utf-8");
    execSync("\"" + process.execPath + "\" --check \"" + tmp + "\"", { stdio: "pipe" });
    fs.unlinkSync(tmp);
  }
} catch(e) {
  // Rollback to last backup
  const backups = fs.readdirSync(BACKUP_DIR).filter(f => f.endsWith("_index.html")).sort();
  if (backups.length > 0) {
    const lastGood = BACKUP_DIR + "/" + backups[backups.length - 1];
    fs.copyFileSync(lastGood, outputPath);
    console.error("[rollback] JS syntax error, restored: " + lastGood);
    process.exit(1);
  }
}

console.log("  [OK] Done!");