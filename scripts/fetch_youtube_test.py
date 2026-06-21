"""AI 灵感簿 - YouTube 采集测试"""
import requests, json, re, sys, os
sys.stdout.reconfigure(encoding="utf-8")

YOUTUBE_SEARCH_URL = "https://www.youtube.com/results?search_query="
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

QUERIES = [
    "AI project demo 2026",
    "new AI tool launched",
    "AI product showcase",
    "built with AI agent",
]


def search_youtube(query, max_results=5):
    """Scrape YouTube search results (no API key needed)."""
    url = YOUTUBE_SEARCH_URL + requests.utils.quote(query) + "&sp=CAMSAhABEAI"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        print(f"  [ERROR] {e}")
        return []

    html = resp.text
    # Try to extract ytInitialData
    match = re.search(r"var ytInitialData = ({.*?});</script>", html, re.DOTALL)
    if not match:
        print("  [WARN] Could not find ytInitialData in HTML")
        return []

    try:
        data = json.loads(match.group(1))
    except json.JSONDecodeError:
        print("  [WARN] Could not parse ytInitialData")
        return []

    # Navigate to video list
    results = []
    try:
        contents = data["contents"]["twoColumnSearchResultsRenderer"]["primaryContents"][
            "sectionListRenderer"]["contents"]
        for section in contents:
            items = section.get("itemSectionRenderer", {}).get("contents", [])
            for item in items:
                vr = item.get("videoRenderer", {})
                if not vr:
                    continue
                video_id = vr.get("videoId", "")
                title_runs = vr.get("title", {}).get("runs", [])
                title = "".join(r.get("text", "") for r in title_runs)
                channel = vr.get("longBylineText", {}).get("runs", [{}])[0].get("text", "")
                views = vr.get("viewCountText", {}).get("simpleText", "")
                desc = vr.get("detailedMetadataSnippets", [{}])[0].get("snippetText", {}).get("runs", [{}])[0].get("text", "")

                results.append({
                    "title": title[:120],
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                    "channel": channel,
                    "views": views,
                    "description": desc[:200],
                })
                if len(results) >= max_results:
                    break
            if len(results) >= max_results:
                break
    except (KeyError, IndexError) as e:
        print(f"  [WARN] Parse error: {e}")

    return results


def run():
    print("=" * 50)
    print("YouTube AI 项目采集测试")
    print("=" * 50)

    all_results = []
    for q in QUERIES:
        print(f"\n  Searching: {q}")
        results = search_youtube(q, max_results=5)
        print(f"    -> Found {len(results)} videos")
        all_results.extend(results)

    if not all_results:
        print("\n  [FAIL] No results. YouTube search requires an API key.")
        print("  To set up: go to https://console.cloud.google.com")
        print("  Create a project -> Enable YouTube Data API v3 -> Create API Key")
        print("  Then save the key to config.json as youtube_api_key")
        return

    # Deduplicate by URL
    seen = set()
    unique = []
    for r in all_results:
        if r["url"] not in seen:
            seen.add(r["url"])
            unique.append(r)

    print(f"\n{'='*50}")
    print(f"Unique results: {len(unique)}")
    print(f"{'='*50}")
    for i, r in enumerate(unique[:10], 1):
        print(f"\n  {i}. {r['title']}")
        print(f"      Channel: {r['channel']}")
        print(f"      Views: {r['views']}")
        print(f"      {r['url']}")
        if r["description"]:
            print(f"      {r['description'][:100]}")


if __name__ == "__main__":
    run()
