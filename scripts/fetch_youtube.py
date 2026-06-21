"""AI 灵感簿 - YouTube 采集（YouTube Data API v3）"""
import requests, json, sys, os, re
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(ROOT, "data", "raw")
TODAY = datetime.now().strftime("%Y-%m-%d")
CONFIG_PATH = os.path.join(ROOT, "config.json")

# AI 项目关键词
QUERIES = [
    "AI project demo",
    "new AI tool launch",
    "AI product showcase",
    "build with AI agent",
    "AI app demo",
    "AI startup product",
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


def search_videos(api_key, query, max_results=10):
    """Search YouTube videos using Data API v3."""
    url = f"{YOUTUBE_API_BASE}/search"
    params = {
        "part": "snippet",
        "q": query,
        "maxResults": max_results,
        "type": "video",
        "order": "viewCount",
        "publishedAfter": "2025-06-01T00:00:00Z",
        "regionCode": "US",
        "key": api_key,
    }
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


def save_results(videos):
    os.makedirs(os.path.join(RAW_DIR, TODAY), exist_ok=True)
    path = os.path.join(RAW_DIR, TODAY, "youtube.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(videos, f, ensure_ascii=False, indent=2)
    print(f"  Saved: {path}")
    return path


def run():
    print("=" * 50)
    print("YouTube AI 项目采集")
    print("=" * 50)

    api_key = load_api_key()
    if not api_key:
        print("  [ERROR] No API key found in config.json")
        print("  Add your key: echo '{\"youtube_api_key\":\"YOUR_KEY\"}' > config.json")
        return

    all_videos = []
    seen_ids = set()

    for q in QUERIES:
        print(f"  Searching: {q}")
        videos = search_videos(api_key, q)
        for v in videos:
            if v["video_id"] not in seen_ids:
                seen_ids.add(v["video_id"])
                all_videos.append(v)

    if not all_videos:
        print("  No results found")
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

    print(f"\n  Total found: {len(all_videos)}")
    print(f"  AI-related: {len(final)}")
    print(f"\nTop videos by views:")
    final.sort(key=lambda x: x["views"], reverse=True)
    for i, v in enumerate(final[:10], 1):
        print(f"\n  {i}. {v['title']}")
        print(f"      Channel: {v['channel']}")
        print(f"      Views: {v['views']:,}")
        pub = v.get("published_at", "")[:10]
        print(f"      Published: {pub}")
        print(f"      https://www.youtube.com/watch?v={v['video_id']}")
        desc = v.get("description", "")[:100]
        if desc:
            print(f"      {desc}")


if __name__ == "__main__":
    run()
