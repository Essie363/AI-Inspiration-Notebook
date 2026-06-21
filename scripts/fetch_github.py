"""AI Inspiration Notebook - GitHub AI project collector (Search API v3)"""
import requests, json, os, sys, glob
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import ROOT_DIR, RAW_DIR, TODAY

HEADERS = {"User-Agent": "AI-Inspiration/2.0"}

# PRD 2.2: 6-query strategy with sliding time windows and mixed sorting
SEARCH_QUERIES = [
    {"q": "ai agent stars:>10",           "sort": "stars",   "days_back": 7,   "desc": "Agent paradigm"},
    {"q": "\"AI for\" stars:>10",          "sort": "stars",   "days_back": 30,  "desc": "Vertical apps"},
    {"q": "ai stars:>500",                 "sort": "stars",   "days_back": 365, "desc": "Proven high-star"},
    {"q": "\"AI assistant\" OR \"AI copilot\" stars:>10", "sort": "updated", "days_back": 30, "desc": "Copilot/assistant"},
    {"q": "\"indie hacker\" OR \"AI side project\" stars:>5", "sort": "stars", "days_back": 90, "desc": "Indie makers"},
    {"q": "\"AI chrome extension\" OR \"AI plugin\" stars:>5", "sort": "stars", "days_back": 90, "desc": "Extensions/plugins"},
]


def compute_pushed_after(days_back):
    """Compute pushed:>YYYY-MM-DD for dynamic time window."""
    return (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")


def search_repos(query, sort, per_page=10):
    """Search GitHub repos with query and sort order."""
    url = f"https://api.github.com/search/repositories?q={query}&sort={sort}&order=desc&per_page={per_page}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code == 200:
            return resp.json().get("items", [])
        print(f"  API returned status: {resp.status_code}")
        return []
    except Exception as e:
        print(f"  Request failed: {e}")
        return []


def is_ai_related(repo):
    """Check if repo is AI-related by title/description/topics."""
    text = f"{repo.get('name','')} {repo.get('description','')} {' '.join(repo.get('topics',[]))}"
    text = text.lower()
    keywords = [
        "ai", "llm", "gpt", "agent", "chatgpt", "openai", "claude", "gemini",
        "rag", "embedding", "vector", "copilot", "assistant", "workflow",
        "automation", "prompt", "langchain", "llama", "mistral",
        "diffusion", "stable diffusion", "machine learning", "deep learning",
        "nlp", "multimodal", "whisper", "translation", "voice", "speech",
        "vision", "image generation", "chatbot", "ai-powered",
    ]
    return any(kw in text for kw in keywords)


def load_previous_full_names():
    """Load full_name set from last collection for cross-day dedup (PRD 2.2)."""
    seen = set()
    raw_glob = os.path.join(RAW_DIR, "*/github.json")
    for path in sorted(glob.glob(raw_glob), reverse=True):
        try:
            with open(path, "r", encoding="utf-8") as f:
                for item in json.load(f):
                    fn = item.get("full_name", "")
                    if fn:
                        seen.add(fn)
        except Exception:
            continue
    return seen


def fetch_all():
    """Collect from 6 dimensions, dedup, filter, and return."""
    seen_names = set()  # current run dedup
    previous_names = load_previous_full_names()  # cross-day dedup
    results = []

    for sq in SEARCH_QUERIES:
        pushed_after = compute_pushed_after(sq["days_back"])
        full_q = f'{sq["q"]} pushed:>{pushed_after}'
        print(f"  [{sq['desc']}] {sq['q'][:50]}... (window: {sq['days_back']}d, sort: {sq['sort']})")
        repos = search_repos(full_q, sq["sort"])
        print(f"    -> Found {len(repos)} repos")
        for repo in repos:
            full_name = repo["full_name"]
            if full_name in seen_names or full_name in previous_names:
                continue  # skip duplicates (same-run + cross-day)
            if not is_ai_related(repo):
                continue
            seen_names.add(full_name)
            pushed = repo.get("pushed_at", "")
            results.append({
                "full_name": full_name,
                "url": repo.get("html_url", f"https://github.com/{full_name}"),
                "description": repo.get("description", "") or "",
                "language": repo.get("language", "") or "",
                "stars": repo.get("stargazers_count", 0),
                "forks": repo.get("forks_count", 0),
                "open_issues": repo.get("open_issues_count", 0),
                "created_at": repo.get("created_at", ""),
                "pushed_at": pushed,
                "topics": repo.get("topics", []),
                "license": repo.get("license", {}).get("spdx_id", "") if repo.get("license") else "",
            })

    results.sort(key=lambda x: x["stars"], reverse=True)
    print(f"  [Dedup] Cross-day excluded: {len(previous_names & seen_names)}")
    return results


def save_raw(projects):
    """Save raw data to data/raw/YYYY-MM-DD/github.json."""
    os.makedirs(os.path.join(RAW_DIR, TODAY), exist_ok=True)
    path = os.path.join(RAW_DIR, TODAY, "github.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(projects, f, ensure_ascii=False, indent=2)
    print(f"  Saved: {path}")
    return path


def run():
    print("=" * 50)
    print("GitHub AI Project Collector (PRD 2.2)")
    print("=" * 50)

    projects = fetch_all()

    if not projects:
        print("  !! No matching projects found")
        return []

    save_raw(projects)
    print(f"\n  Total unique: {len(projects)}")
    for i, p in enumerate(projects[:15], 1):
        desc = (p["description"][:80] + "...") if len(p["description"]) > 80 else p["description"]
        print(f"  {i}. {p['full_name']}  (Stars: {p['stars']}, Updated: {p.get('pushed_at','')[:10]})")
        print(f"      {desc}")

    return projects


if __name__ == "__main__":
    run()