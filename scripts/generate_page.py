"""AI 灵感簿 - 页面生成器 v5（含收藏功能）"""
import json as j2
import random
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import ROOT_DIR, DATA_FILE, INDEX_HTML, RAW_DIR

if sys.stdout.encoding != "utf-8":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")


def load_projects():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return j2.load(f)
    return []


def load_builder_tweets():
    """Load tweets from today's x.json raw data (follow-builders feed)."""
    today = datetime.now().strftime("%Y-%m-%d")
    x_path = os.path.join(RAW_DIR, today, "x.json")
    if os.path.exists(x_path):
        with open(x_path, "r", encoding="utf-8") as f:
            return j2.load(f)
    # Try yesterday as fallback
    from datetime import timedelta
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    x_path_y = os.path.join(RAW_DIR, yesterday, "x.json")
    if os.path.exists(x_path_y):
        with open(x_path_y, "r", encoding="utf-8") as f:
            return j2.load(f)
    return []


def generate_timeline(tweets):
    """Generate Builder Digest timeline HTML per PRD 4.7."""
    if not tweets:
        return '<div class="empty-state"><p>No builder updates yet.</p></div>'
    lines = []
    lines.append('<div class="timeline-feed">')
    # Group by builder
    builders = {}
    for t in tweets:
        name = t.get("author_name", "Unknown")
        if name not in builders:
            builders[name] = []
        builders[name].append(t)
    # Sort builders by max likes
    builder_order = sorted(builders.keys(), key=lambda n: max(t["likes"] for t in builders[n]), reverse=True)
    for name in builder_order:
        btweets = builders[name]
        username = btweets[0].get("author_username", "")
        lines.append('<div class="timeline-builder">')
        lines.append('  <div class="timeline-builder-header">')
        lines.append('    <span class="timeline-avatar"></span>')
        lines.append('    <span class="timeline-builder-name">' + escape(name) + '</span>')
        lines.append('    <span class="timeline-builder-handle">@' + escape(username) + '</span>')
        lines.append('  </div>')
        for t in btweets:
            tid = t.get("tweet_id", "")
            text = t.get("text", "")
            url = t.get("url", "#")
            likes = t.get("likes", 0)
            created = t.get("created_at", "")[:10]
            lines.append('  <div class="timeline-item">')
            lines.append('    <p class="timeline-text">' + escape(text) + '</p>')
            lines.append('    <div class="timeline-meta">')
            lines.append('      <span class="timeline-date">' + escape(created) + '</span>')
            lines.append('      <span class="timeline-likes">&#9825; ' + str(likes) + '</span>')
            lines.append('      <a href="' + escape(url) + '" target="_blank" class="timeline-link">View on X &#8599;</a>')
            lines.append('    </div>')
            lines.append('  </div>')
        lines.append('</div>')
    lines.append('</div>')
    return '\n'.join(lines)



def escape(s):
    if not s: return ""
    s = str(s)
    s = s.replace("%%", "")
    s = s.replace("<mark>", "[[[M]]]").replace("</mark>", "[[[/M]]]")
    s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").replace("'", "&#39;")
    s = s.replace("[[[M]]]", "<mark>").replace("[[[/M]]]", "</mark>")
    return s


def generate_card(p, delay=0):
    pid = p.get("id", "")
    icon = {"GitHub": "&#128187;", "YouTube": "&#9654;"}.get(p.get("source", ""), "&#128279;")
    cat_labels = {"chrome-extension": "Extension", "creative": "Creative", "workflow": "Workflow"}
    tags_h = "".join('<span class="tag">' + escape(t) + "</span>" for t in p.get("tags", []))

    a = p.get("analysis", {})
    insight_raw = a.get("insight", "")
    preview = ""
    if insight_raw:
        pt = insight_raw.replace("<mark>", "").replace("</mark>", "")
        pt = pt.split("%%")[0].strip()
        pt = pt.rstrip("，；：、—…;:-")
        if len(pt) > 80:
            pt = pt[:77].rstrip("，；：、—…;:-") + "..."
        preview = pt
    card = []
    style_attr = ' style="animation: cardEnter 0.45s ease-out both; animation-delay: ' + str(delay) + 's"' if delay > 0 else ""
    card.append('<div class="card" data-category="' + escape(p.get("category", "")) + '" data-pid="' + escape(pid) + '"' + style_attr + '>')
    card.append('  <div class="card-header">')
    card.append('    <span class="source-badge">' + icon + " " + escape(p.get("source", "")) + "</span>")
    cat_data = p.get("category", "")
    card.append('    <span class="card-cat-badge" data-cat="' + cat_data.replace("chrome-extension", "extension") + '">' + cat_labels.get(cat_data, "") + "</span>")
    card.append('    <span class="card-date">' + escape(p.get("date", "")) + "</span>")
    card.append('    <span class="fav-btn">&#9829;</span>')
    card.append("  </div>")
    card.append('  <h2 class="card-title">' + escape(p.get("title", "")) + "</h2>")
    card.append('  <p class="card-desc">' + escape(p.get("description", "")) + "</p>")

    if preview:
        card.append('  <div class="key-insight">')
        card.append('    <span class="key-insight-label">KEY INSIGHT</span>')
        card.append("    " + escape(preview))
        card.append("  </div>")
    card.append('  <div class="expand-hint">click to expand</div>')

    full_parts = ""
    blocks = [
        ("Pain Point", escape(a.get("pain_point", ""))),
        ("Why AI", escape(a.get("why_ai", ""))),
        ("Product Insight", escape(a.get("insight", ""))),
        ("Transfer", escape(a.get("transfer", ""))),
    ]
    for label, val in blocks:
        if not val: continue
        full_parts += '<div class="analysis-block">\n'
        full_parts += '  <span class="analysis-label">' + label + "</span>\n"
        full_parts += "  <p>" + val + "</p>\n"
        full_parts += "</div>\n"

    card.append('  <div class="card-full">')
    card.append('    <div class="card-full-tags">' + tags_h + "</div>")
    card.append('    <div class="card-full-grid">')
    card.append("      " + full_parts)
    card.append("    </div>")
    card.append('    <div style="display:flex;gap:14px;align-items:center;margin-top:18px;">')
    card.append('      <a href="' + escape(p.get("url", "#")) + '" target="_blank" class="ext-link">&#128279; View Original</a>')
    card.append('      <button class="close-btn">&#10005; Collapse</button>')
    card.append("    </div>")
    card.append("  </div>")
    card.append("</div>")
    return "\n".join(card)


def generate_html(projects, builder_tweets=None):
    total = len(projects)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")

    cats = {
        "chrome-extension": {"label": "Extensions", "icon": "&#128230;", "projects": []},
        "creative": {"label": "Creative Tools", "icon": "&#127912;", "projects": []},
        "workflow": {"label": "Workflow", "icon": "&#9881;&#65039;", "projects": []},
    }
    for p in projects:
        cat = p.get("category", "creative")
        if cat in cats:
            cats[cat]["projects"].append(p)

    tab_order = ["chrome-extension", "creative", "workflow"]
    tab_labels = {
        "chrome-extension": "Extensions (" + str(len(cats["chrome-extension"]["projects"])) + ")",
        "creative": "Creative (" + str(len(cats["creative"]["projects"])) + ")",
        "workflow": "Workflow (" + str(len(cats["workflow"]["projects"])) + ")",
    }

    tabs_html = ""
    tabs_html += '<button class="tab active" onclick="filterCategory(this, \'all\')">All (' + str(total) + ")</button>\n"
    for cat_key in tab_order:
        tabs_html += '<button class="tab" onclick="filterCategory(this, \'' + cat_key + '\')">' + tab_labels[cat_key] + "</button>\n"

    # Builder Digest tab (PRD 4.7)
    digest_count = len(builder_tweets) if builder_tweets else 0
    tabs_html += '<button class="tab" onclick="switchToTimeline(this)">Builder Digest (' + str(digest_count) + ')</button>\n'


    grids_html = '<div class="card-grid">\n'
    all_projects = []
    for cat_key in tab_order:
        all_projects.extend(cats[cat_key]["projects"])
    random.seed(datetime.now().strftime("%Y-%m-%d"))
    random.shuffle(all_projects)
    for idx, p in enumerate(all_projects):
        d = round(0.06 + idx * 0.08, 2) if idx < 10 else 0
        grids_html += generate_card(p, d) + "\n"
    grids_html += "</div>\n"

    # Read assets
    assets_dir = os.path.join(ROOT_DIR, "assets")
    css_content = ""
    css_path = os.path.join(assets_dir, "style.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            css_content = f.read()
    js_content = ""
    js_path = os.path.join(assets_dir, "script.js")
    if os.path.exists(js_path):
        with open(js_path, "r", encoding="utf-8") as f:
            js_content = f.read()

    lines = []
    lines.append("<!DOCTYPE html>")
    lines.append('<html lang="en">')
    lines.append("<head>")
    lines.append('<meta charset="UTF-8">')
    lines.append('<meta name="viewport" content="width=device-width, initial-scale=1.0">')
    lines.append("<title>AI Inspiration Notebook</title>")
    lines.append("<style>" + css_content + "</style>")
    lines.append("</head>")
    lines.append("<body>")
    lines.append('<div class="container">')

    lines.append('  <header class="header">')
    lines.append('    <div class="header-top">')
    lines.append("      <h1>AI Inspiration Notebook</h1>")
    lines.append('      <div class="header-meta">')
    lines.append("        <span>" + now_str + "</span>")
    lines.append('        <span class="dot">&middot;</span>')
    lines.append("        <span>" + str(total) + " projects</span>")
    lines.append("      </div>")
    lines.append('      <div class="header-right">')
    lines.append('        <button class="fav-header-btn" onclick="openFavModal()" title="Your favorites">&#9825;</button>')
    lines.append('        <button id="themeBtn" class="theme-btn" onclick="toggleTheme()">&#127769;</button>')
    lines.append("      </div>")
    lines.append("    </div>")
    lines.append("  </header>")

    lines.append('  <div class="tabs">' + tabs_html + "</div>")
    lines.append("  <main>")
    if grids_html:
        lines.append(grids_html)
    else:
        lines.append('    <div class="empty-state"><p>No projects yet.</p></div>')
    lines.append("  </main>")

    # Builder Digest timeline (hidden by default, shown via JS)
    lines.append('  <div id="digestSection" class="digest-section" style="display:none">')
    timeline_html = generate_timeline(builder_tweets) if builder_tweets else ''
    lines.append(timeline_html)
    lines.append('  </div>')

    lines.append('  <footer class="footer">')
    lines.append("    <p>AI Inspiration Notebook &mdash; small AI product case studies, daily</p>")
    lines.append('    <p style="margin-top:8px;font-size:11px;">Designed by Essie Zhang</p>')
    lines.append("  </footer>")
    lines.append("</div>")

    # Toast
    lines.append('<div id="toast" class="toast"></div>')

    # Favorites Modal
    lines.append('<div id="favModal" class="fav-modal" style="display:none">')
    lines.append('  <div class="fav-modal-bg" onclick="closeFavModal()"></div>')
    lines.append('  <div class="fav-modal-panel">')
    lines.append('    <div class="fav-modal-header">')
    lines.append('      <h2 class="fav-modal-title">Favorites</h2>')
    lines.append('      <button class="fav-modal-close" onclick="closeFavModal()">&times;</button>')
    lines.append('    </div>')
    lines.append('    <div id="favModalBody" class="fav-modal-body">')
    lines.append('      <div class="fav-empty">No favorites yet.</div>')
    lines.append('    </div>')
    lines.append('  </div>')
    lines.append('</div>')

    lines.append("<script>" + js_content + "</script>")
    lines.append("</body>")
    lines.append("</html>")

    html = "\n".join(lines)
    with open(INDEX_HTML, "w", encoding="utf-8") as f:
        f.write(html)
    print("[OK] " + INDEX_HTML)


def run():
    print("=" * 50)
    print("AI Inspiration Notebook - v5 (favorites)")
    print("=" * 50)
    projects = load_projects()
    if not projects:
        print("  [WARN] empty")
        generate_html([])
        return
    print("  -> " + str(len(projects)) + " projects")
    builder_tweets = load_builder_tweets()
    print("  -> " + str(len(builder_tweets)) + " builder tweets")
    generate_html(projects, builder_tweets)
    # JS 语法检查：防止 script.js 带语法错误生成坏页面
    if not check_js_syntax(INDEX_HTML):
        restore_last_backup()
        print("  [ERR] JS syntax error detected, rolled back to last backup")
        sys.exit(1)
    save_backup()
    cleanup_old_backups()
    print("  [OK] Done!")



import shutil
from datetime import datetime, timedelta

BACKUP_DIR = os.path.join(ROOT_DIR, "data", "backups")


def save_backup():
    """Save a timestamped backup of the generated page."""
    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_path = os.path.join(BACKUP_DIR, timestamp + "_index.html")
    try:
        shutil.copy2(INDEX_HTML, backup_path)
        print(f"  [Backup] Saved: {backup_path}")
    except Exception as e:
        print(f"  [Backup] Failed: {e}")


def check_js_syntax(html_path):
    """生成后校验 JS 语法，防止引入语法错误导致页面不响应"""
    import re, subprocess, tempfile, os
    try:
        with open(html_path, "r", encoding="utf-8") as f:
            html = f.read()
        m = re.search(r"<script>([\s\S]*?)</script>", html)
        if not m:
            print("  [WARN] No <script> found in generated page")
            return True
        js_code = m.group(1)
        tmp = os.path.join(tempfile.gettempdir(), "_ai_inspiration_check.js")
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(js_code)
        r = subprocess.run(["node", "--check", tmp], capture_output=True, text=True)
        os.remove(tmp)
        if r.returncode != 0:
            print("  [JS ERROR] " + r.stderr.strip())
            return False
        return True
    except FileNotFoundError:
        print("  [WARN] node not found, skipping JS check")
        return True
    except Exception as e:
        print("  [WARN] JS check failed: " + str(e))
        return True


def restore_last_backup():
    """从最近的备份恢复 index.html"""
    import glob
    backup_dir = os.path.join(ROOT_DIR, "data", "backups")
    if not os.path.exists(backup_dir):
        print("  [ERR] No backup directory")
        return
    backups = sorted(glob.glob(os.path.join(backup_dir, "*_index.html")))
    if not backups:
        print("  [ERR] No backup found")
        return
    latest = backups[-1]
    shutil.copy2(latest, INDEX_HTML)
    print("  [Rollback] Restored from: " + latest)


def cleanup_old_backups(days=7):
    """Remove backups older than the specified number of days."""
    if not os.path.exists(BACKUP_DIR):
        return
    cutoff = datetime.now() - timedelta(days=days)
    count = 0
    for fname in os.listdir(BACKUP_DIR):
        fpath = os.path.join(BACKUP_DIR, fname)
        if not os.path.isfile(fpath):
            continue
        mtime = datetime.fromtimestamp(os.path.getmtime(fpath))
        if mtime < cutoff:
            os.remove(fpath)
            count += 1
    if count > 0:
        print(f"  [Backup] Cleaned {count} old backup(s)")

if __name__ == "__main__":
    run()
