// generate_page.js - AI Inspiration Notebook v2.1 (UTF-8 safe)
// Usage: node scripts/generate_page.js

const fs = require("fs");
const path = require("path");
const { execSync } = require("child_process");
const ROOT = path.resolve(__dirname, "..");

const projects = JSON.parse(fs.readFileSync(ROOT + "/data/projects.json", "utf-8"));
const TODAY = (() => { const n = new Date(); const pad = x => String(x).padStart(2, "0"); return n.getFullYear() + "-" + pad(n.getMonth() + 1) + "-" + pad(n.getDate()); })();
const YESTERDAY = (() => { const n = new Date(); n.setDate(n.getDate() - 1); const pad = x => String(x).padStart(2, "0"); return n.getFullYear() + "-" + pad(n.getMonth() + 1) + "-" + pad(n.getDate()); })();
const todayProjects = projects.filter(p => p.date === TODAY);
const catCount = (arr, cat) => {
  if (cat === "extension") return arr.filter(p => (p.category || "").toLowerCase() === "chrome-extension" || (p.category || "").toLowerCase() === "extensions").length;
  if (cat === "creative") return arr.filter(p => (p.category || "").toLowerCase() === "creative" || (p.category || "").toLowerCase() === "creative tools").length;
  if (cat === "workflow") return arr.filter(p => (p.category || "").toLowerCase() === "workflow").length;
  return arr.length;
};
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
// ==================== Opportunities: BuilderPulse ====================
const BP_DIR = "D:\\codex_workspace\\BuilderPulse-main\\BuilderPulse-main\\zh\\2026";
let oppHtml = "<div class=\"opp-empty\">No BuilderPulse reports available for the past two days.</div>";

function parseMdToHtml(md) {
  let h = md;
  h = h.replace(/```(\w+)?\n([\s\S]*?)```/g, '<pre class="opp-code"><code>$2</code></pre>');
  h = h.replace(/`([^`]+)`/g, '<code class="opp-inline-code">$1</code>');
  h = h.replace(/^#### (.+)$/gm, '<h4 class="opp-h4">$1</h4>');
  h = h.replace(/^### (.+)$/gm, '<h3 class="opp-h3">$1</h3>');
  h = h.replace(/^## (.+)$/gm, '<h2 class="opp-h2">$1</h2>');
  h = h.replace(/^# (.+)$/gm, '<h2 class="opp-h1">$1</h2>');
  h = h.replace(/\*\*\*(.+?)\*\*\*/g, '<strong><em>$1</em></strong>');
  h = h.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  h = h.replace(/\*(.+?)\*/g, '<em>$1</em>');
  h = h.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" class="opp-link">$1</a>');
  h = h.replace(/^> (.+)$/gm, '<blockquote class="opp-blockquote">$1</blockquote>');
  h = h.replace(/^---$/gm, '<hr class="opp-hr">');
  let tblLines = h.split("\n");
  let inTable = false;
  let tblResult = [];
  for (let i = 0; i < tblLines.length; i++) {
    const line = tblLines[i];
    if (line.match(/^\|.+\|$/) && line.includes("|")) {
      if (!inTable) { inTable = true; tblResult.push('<table class="opp-table">'); }
      const cells = line.split("|").filter(c => c.trim() !== "");
      const isHeader = (i + 1 < tblLines.length && tblLines[i + 1] && tblLines[i + 1].match(/^\|[\s:|-]+\|$/));
      const tag = isHeader ? "th" : "td";
      tblResult.push("<tr>" + cells.map(c => "<" + tag + ">" + c.trim() + "</" + tag + ">").join("") + "</tr>");
      if (isHeader) { i++; }
    } else {
      if (inTable) { inTable = false; tblResult.push("</table>"); }
      tblResult.push(line);
    }
  }
  if (inTable) tblResult.push("</table>");
  h = tblResult.join("\n");
  h = h.split("\n").map(l => {
    const t = l.trim();
    if (!t) return "";
    if (t.startsWith("<")) return t;
    return '<p class="opp-p">' + t + "</p>";
  }).join("\n");
  return h;
}

try {
  // Find the most recent 2 available BuilderPulse files
  const bpDates = [];
  for (let offset = 0; offset < 14; offset++) {
    const d = new Date(); d.setDate(d.getDate() - offset);
    const ds = d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0");
    const fp = BP_DIR + "\\" + ds + ".md";
    if (fs.existsSync(fp)) { bpDates.push({ date: ds, path: fp }); }
    if (bpDates.length >= 2) break;
  }
    const OPP_DIR = ROOT + "/data/opportunities";
  if (bpDates.length > 0) {
    oppHtml = "";
    for (const f of bpDates) {
      // Prefer distilled version, fallback to raw BuilderPulse
      const distilledPath = OPP_DIR + "/" + f.date + "-distilled.md";
      const rawPath = f.path;
      const readPath = fs.existsSync(distilledPath) ? distilledPath : rawPath;
      const raw = fs.readFileSync(readPath, "utf-8");
      const parsed = parseMdToHtml(raw);
      oppHtml += '<div class="opp-day">';
      oppHtml += '<div class="opp-day-header">' + f.date + '</div>';
      oppHtml += '<div class="opp-day-content">' + parsed + '</div>';
      oppHtml += '</div>';
    }
  }
} catch(e) {
  oppHtml = "<div class=\"opp-empty\">Unable to load BuilderPulse data: " + esc(String(e)) + "</div>";
}


const formatDate = (ds) => {
  const parts = ds.split("-");
  if (parts.length === 3) return parseInt(parts[1]) + "月" + parseInt(parts[2]) + "日";
  return ds;
};
// Build Opportunities nav from H2 headings
let oppNav = "";
if (oppHtml.length > 0 && oppHtml.includes("opp-h2")) {
  oppNav = '<nav class="opp-sidebar" id="oppSidebar"><div class="opp-sidebar-title">On this page</div>';
  // Extract day blocks and their H2s
  const dayRe = /<div class="opp-day-header">([^<]+)<\/div>[\s\S]*?(?=<div class="opp-day-header">|$)/g;
  let dayMatch;
  let h2GlobalIdx = 0;
  const dayBlocks = [];
  while ((dayMatch = dayRe.exec(oppHtml)) !== null) {
    const dayDate = dayMatch[1];
    const dayContent = dayMatch[0];
    const dayH2s = [];
    const h2ReLocal = /<h2 class="opp-h2">([^<]+)<\/h2>/g;
    let h2m;
    while ((h2m = h2ReLocal.exec(dayContent)) !== null) {
      const title = h2m[1].replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&#39;/g, "'").replace(/&quot;/g, '"');
      const slug = "opp-" + h2GlobalIdx;
      h2GlobalIdx++;
      dayH2s.push({ title: title, slug: slug });
    }
    if (dayH2s.length > 0) dayBlocks.push({ date: dayDate, h2s: dayH2s });
  }
  // Build nav with date groups
  for (const block of dayBlocks) {
    oppNav += `<div class="opp-nav-date">${formatDate(block.date)}</div>`;
    for (const h of block.h2s) {
      oppNav += `<a href="#${h.slug}" class="opp-nav-item" data-opp="${h.slug}">${esc(h.title)}</a>`;
    }
  }
  oppNav += "</nav>";
  // Inject id anchors into oppHtml
  let h2Idx = 0;
  const allH2s = dayBlocks.flatMap(b => b.h2s);
  oppHtml = oppHtml.replace(/<h2 class="opp-h2">/g, function(m) {
    const id = allH2s[h2Idx] ? allH2s[h2Idx].slug : "";
    h2Idx++;
    return `<h2 class="opp-h2" id="${id}">`;
  });
}


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
const shuffledProjects = shuffle(todayProjects, parseInt(todaySeed, 10));

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
    <button class="channel-btn" onclick="switchChannel(this, 'inspiration')">AI Projects</button>
    <button class="channel-btn" onclick="switchChannel(this, 'builder')">Builder Digest</button>
    <button class="channel-btn" onclick="switchChannel(this, 'opportunities')">Opportunities</button>
  </div>

  <div id="channel-inspiration" class="channel-content" style="display:none">
    <div class="tabs" id="categoryTabs">
      <button class="tab active" onclick="filterCategory(this, 'all')">All (${todayProjects.length})</button>
      <button class="tab" onclick="filterCategory(this, 'extension')">Extensions (${catCount(todayProjects, "extension")})</button>
      <button class="tab" onclick="filterCategory(this, 'creative')">Creative (${catCount(todayProjects, "creative")})</button>
      <button class="tab" onclick="filterCategory(this, 'workflow')">Workflow (${catCount(todayProjects, "workflow")})</button>
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

  <div id="channel-opportunities" class="channel-content" style="display:none">
    <div class="timeline-layout opp-layout">
${oppNav}      <div class="timeline-content opp-content">
${oppHtml}      </div>
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




