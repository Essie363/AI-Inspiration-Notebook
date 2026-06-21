"""AI Inspiration Notebook - YouTube AI project video collector (Data API v3)"""
import requests, json, sys, os, re, glob
from datetime import datetime, timedelta

sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(ROOT, "data", "raw")
TODAY = datetime.now().strftime("%Y-%m-%d")
CONFIG_PATH = os.path.join(ROOT, "config.json")

# PRD 2.3: 6-query strategy with mixed sorting and sliding time windows
QUERIES = [
    {"q": "AI agent demo",        "order": "date",      "days_back": 7,   "desc": "Agent live demos"},
    {"q": "best AI products",     "order": "relevance", "days_back": None,"desc": "Product roundups"},
    {"q": "AI product review",    "order": "relevance", "days_back": None,"desc": "In-depth reviews"},
    {"q": "how I built AI",       "order": "date",      "days_back": 7,   "desc": "Maker build stories"},
    {"q": "new AI tool launch",   "order": "date",      "days_back": 7,   "desc": "New tool launches"},
    {"q": "AI startup product",   "order": "date",      "days_back": 7,   "desc": "Startup products"},
]

NON_AI_KEYWORDS = [
    "music video", "trailer", "movie", "gameplay", "android app", "hello world",
    "nvidia tech demo", "evolution of", "wwdc", "concert", "sport",
]

YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"


def load_api_key():
    if not os.path.exists(CONFIG_PATH):
        return None
    with open(CONFIG_PATH, "r", encoding="utf-8-sig") as f:
        return json.load(f).get("youtube_api_key", "")


def search_videos(api_key, query, order, max_results=10, days_back=None):
    """Search YouTube videos with dynamic time window per PRD 2.3."""
    url = f"{YOUTUBE_API_BASE}/search"
    params = {
        "part": "snippet",
        "q": query,
        "maxResults": max_results,
        "type": "video",
        "order": order,
        "regionCode": "US",
        "key": api_key,
    }
    if days_back:
        pub_after = (datetime.utcnow() - timedelta(days=days_back)).strftime("%Y-%m-%dT00:00:00Z")
        params["publishedAfter"] = pub_after
    try:
        resp = requests.get(url, params=params, timeout=15)
        data = resp.json()
        if "error" in data:
            print(f"  API Error: {data['error']['message']}")
            return []
        items = data.get("items", [])
        results = []
        for item in items:
            snippet = item.get("snippet", {})
            results.append({
                "video_id": item["id"]["videoId"],
                "title": snippet.get("title", ""),
                "description": snippet.get("description", "")[:300],
                "channel": snippet.get("channelTitle", ""),
                "published_at": snippet.get("publishedAt", ""),
            })
        return results
    except Exception as e:
        print(f"  Request failed: {e}")
        return []


def get_video_stats(api_key, video_ids):
    """Get view/like counts for videos."""
    if not video_ids:
        return {}
    url = f"{YOUTUBE_API_BASE}/videos"
    params = {
        "part": "statistics",
        "id": ",".join(video_ids),
        "key": api_key,
    }
    try:
        resp = requests.get(url, params=params, timeout=15)
        data = resp.json()
        stats_map = {}
        for item in data.get("items", []):
            s = item.get("statistics", {})
            stats_map[item["id"]] = {
                "views": int(s.get("viewCount", 0)),
                "likes": int(s.get("likeCount", 0)),
            }
        return stats_map
    except Exception:
        return {}


def is_ai_related(title, desc):
    text = (title + " " + desc).lower()
    if any(kw in text for kw in NON_AI_KEYWORDS):
        return False
    ai_kws = ["ai", "llm", "gpt", "agent", "copilot", "assistant", "automation",
              "model", "neural", "machine learning", "deep learning", "chatgpt",
              "openai", "claude", "gemini", "workflow", "prompt", "rag", "mcp"]
    return any(kw in text for kw in ai_kws)


def load_previous_video_ids():
    """Load video_id set from previous collections for cross-day dedup (PRD 2.3)."""
    seen = set()
    raw_glob = os.path.join(RAW_DIR, "*/youtube.json")
    for path in sorted(glob.glob(raw_glob), reverse=True):
        try:
            with open(path, "r", encoding="utf-8") as f:
                for item in json.load(f):
                    vid = item.get("video_id", "")
                    if vid:
                        seen.add(vid)
        except Exception:
            continue
    return seen


def save_results(videos):
    os.makedirs(os.path.join(RAW_DIR, TODAY), exist_ok=True)
    path = os.path.join(RAW_DIR, TODAY, "youtube.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(videos, f, ensure_ascii=False, indent=2)
    print(f"  Saved: {path}")
    return path


def run():
    print("=" * 50)
    print("YouTube AI Project Collector (PRD 2.3)")
    print("=" * 50)

    api_key = load_api_key()
    if not api_key:
        print("  [ERROR] No API key found in config.json")
        return

    all_videos = []
    seen_ids = set()
    previous_ids = load_previous_video_ids()

    for q in QUERIES:
        window_label = f"{q['days_back']}d" if q["days_back"] else "unlimited"
        print(f"  [{q['desc']}] {q['q']} (order: {q['order']}, window: {window_label})")
        videos = search_videos(api_key, q["q"], q["order"], days_back=q["days_back"])
        print(f"    -> Found {len(videos)} videos")
        for v in videos:
            vid = v["video_id"]
            if vid not in seen_ids and vid not in previous_ids:
                seen_ids.add(vid)
                all_videos.append(v)

    if not all_videos:
        print("  No new results found")
        return

    # Fetch statistics
    print(f"\n  Fetching statistics for {len(all_videos)} videos...")
    video_ids = [v["video_id"] for v in all_videos]
    stats_map = get_video_stats(api_key, video_ids)

    # Combine data and filter
    final = []
    for v in all_videos:
        stats = stats_map.get(v["video_id"], {"views": 0, "likes": 0})
        v["views"] = stats["views"]
        v["likes"] = stats["likes"]
        desc = v.get("description", "")
        if is_ai_related(v["title"], desc):
            final.append(v)

    save_results(final)

    print(f"\n  Total new: {len(all_videos)}")
    print(f"  AI-related: {len(final)}")
    print(f"  [Dedup] Cross-day excluded: {len(previous_ids & seen_ids)}")

    final.sort(key=lambda x: x["views"], reverse=True)
    for i, v in enumerate(final[:10], 1):
        print(f"\n  {i}. {v['title']}")
        print(f"      Channel: {v['channel']}  |  Views: {v['views']:,}")
        pub = v.get("published_at", "")[:10]
        print(f"      Published: {pub}")
        print(f"      https://www.youtube.com/watch?v={v['video_id']}")


if __name__ == "__main__":
    run()