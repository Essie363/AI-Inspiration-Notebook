"""AI Inspiration Notebook - X/Twitter AI Project Collector (X API v2, PRD 2.4)"""
import requests, json, sys, os, re, glob
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(ROOT, "data", "raw")
TODAY = datetime.now().strftime("%Y-%m-%d")
CONFIG_PATH = os.path.join(ROOT, "config.json")
SINCE_ID_FILE = os.path.join(RAW_DIR, ".twitter_since_id")

# PRD 2.4: 3-query search strategy
QUERIES = [
    '"AI product launch" OR "new AI tool" -is:retweet',
    '"just shipped" OR "just launched" AI -is:retweet',
    '"built this" OR "made this" AI -is:retweet',
]

NON_AI_PATTERNS = [
    r"music video", r"trailer", r"movie", r"gameplay",
    r"concert", r"sport", r"crypto", r"nft", r"token",
    r"giveaway", r"airdrop", r"follow me",
]

X_API_BASE = "https://api.twitter.com/2"


def load_bearer_token():
    if not os.path.exists(CONFIG_PATH):
        return None
    with open(CONFIG_PATH, "r", encoding="utf-8-sig") as f:
        return json.load(f).get("twitter_bearer_token", "")


def load_since_id():
    """Load last seen tweet_id for incremental pull (PRD 2.4)."""
    if os.path.exists(SINCE_ID_FILE):
        with open(SINCE_ID_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    return None


def save_since_id(tweets):
    """Save max tweet_id so next run only fetches newer tweets."""
    if not tweets:
        return
    try:
        max_id = max(int(t["tweet_id"]) for t in tweets)
        os.makedirs(os.path.dirname(SINCE_ID_FILE), exist_ok=True)
        with open(SINCE_ID_FILE, "w", encoding="utf-8") as f:
            f.write(str(max_id))
    except Exception:
        pass


def search_tweets(bearer_token, query, max_results=10, since_id=None):
    """Search recent tweets using X API v2. Supports since_id for incremental pull."""
    url = f"{X_API_BASE}/tweets/search/recent"
    headers = {"Authorization": f"Bearer {bearer_token}"}
    params = {
        "query": query,
        "max_results": max_results,
        "tweet.fields": "created_at,public_metrics,author_id",
        "user.fields": "name,username",
        "expansions": "author_id",
    }
    if since_id:
        params["since_id"] = since_id
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=15)
        data = resp.json()
        if "errors" in data:
            print(f"  API Error: {data['errors'][0].get('detail', data['errors'])}")
            return []
        users = {}
        for u in data.get("includes", {}).get("users", []):
            users[u["id"]] = u
        results = []
        for tweet in data.get("data", []):
            author = users.get(tweet.get("author_id", ""), {})
            metrics = tweet.get("public_metrics", {})
            u = author.get("username", "")
            results.append({
                "tweet_id": tweet["id"],
                "text": tweet.get("text", ""),
                "author_name": author.get("name", ""),
                "author_username": u,
                "created_at": tweet.get("created_at", ""),
                "likes": metrics.get("like_count", 0),
                "retweets": metrics.get("retweet_count", 0),
                "url": f"https://twitter.com/{u}/status/{tweet['id']}",
            })
        return results
    except Exception as e:
        print(f"  Request failed: {e}")
        return []


def is_ai_related(text):
    text_lower = text.lower()
    for pattern in NON_AI_PATTERNS:
        if re.search(pattern, text_lower):
            return False
    ai_kws = ["ai", "llm", "gpt", "agent", "copilot", "assistant", "automation",
              "model", "openai", "claude", "gemini", "workflow", "prompt",
              "rag", "mcp", "open source", "langchain", "chatbot", "diffusion",
              "stable diffusion", "machine learning"]
    return any(kw in text_lower for kw in ai_kws)


def load_previous_tweet_ids():
    """Cross-day dedup: load all tweet_ids from previous raw data (PRD 2.4)."""
    seen = set()
    raw_glob = os.path.join(RAW_DIR, "*/x.json")
    for fpath in sorted(glob.glob(raw_glob), reverse=True):
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                for item in json.load(f):
                    tid = item.get("tweet_id", "")
                    if tid:
                        seen.add(tid)
        except Exception:
            continue
    return seen


def save_results(tweets):
    os.makedirs(os.path.join(RAW_DIR, TODAY), exist_ok=True)
    path = os.path.join(RAW_DIR, TODAY, "x.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(tweets, f, ensure_ascii=False, indent=2)
    print(f"  Saved: {path}")
    return path


def collect_with_since_id(bearer_token, since_id):
    """Run all 3 queries with since_id, return AI-filtered unique results."""
    all_tweets = []
    seen_ids = set()
    for q in QUERIES:
        print(f"  Searching (since_id): {q[:60]}...")
        tweets = search_tweets(bearer_token, q, since_id=since_id)
        print(f"    -> Found {len(tweets)} tweets")
        for t in tweets:
            if t["tweet_id"] not in seen_ids:
                seen_ids.add(t["tweet_id"])
                all_tweets.append(t)
    return [t for t in all_tweets if is_ai_related(t["text"])]


def collect_full_window(bearer_token, previous_ids):
    """Run all 3 queries without since_id, dedup against cross-day history."""
    all_tweets = []
    seen_ids = set()
    for q in QUERIES:
        print(f"  Searching (full window): {q[:60]}...")
        tweets = search_tweets(bearer_token, q)
        print(f"    -> Found {len(tweets)} tweets")
        for t in tweets:
            tid = t["tweet_id"]
            if tid not in seen_ids and tid not in previous_ids:
                seen_ids.add(tid)
                all_tweets.append(t)
    return [t for t in all_tweets if is_ai_related(t["text"])]


def run():
    print("=" * 50)
    print("X/Twitter AI Project Collector (PRD 2.4)")
    print("=" * 50)

    bearer_token = load_bearer_token()
    if not bearer_token:
        print("  [ERROR] No Bearer Token in config.json")
        return

    # Load incremental state
    since_id = load_since_id()
    previous_ids = load_previous_tweet_ids()
    mode = "incremental" if since_id else "initial"

    if since_id:
        print(f"  [Mode] Incremental (since_id: {since_id[:8]}...)")
    else:
        print("  [Mode] Initial (no since_id, full 7-day window)")

    # First pass: incremental pull
    ai_tweets = collect_with_since_id(bearer_token, since_id)
    count = len(ai_tweets)
    print(f"\n  Incremental results: {count} AI-related tweets")

    # Adaptive fallback: if < 5, retry with full window (PRD 2.4)
    MIN_THRESHOLD = 5
    if count < MIN_THRESHOLD and since_id:
        print(f"  [Fallback] < {MIN_THRESHOLD} results, retrying with full 7-day window...")
        fallback_tweets = collect_full_window(bearer_token, previous_ids)
        fb_count = len(fallback_tweets)
        print(f"  [Fallback] Found {fb_count} AI-related tweets")
        if fb_count >= count:
            ai_tweets = fallback_tweets
            print(f"  Using fallback results ({len(ai_tweets)} total)")
        else:
            print(f"  Keeping incremental results ({len(ai_tweets)} total)")

    if not ai_tweets:
        print("  No new results found")
        return

    # Save and display
    save_results(ai_tweets)
    save_since_id(ai_tweets)  # update since_id state
    print(f"  [Dedup] Cross-day excluded: {len(previous_ids & set(t['tweet_id'] for t in ai_tweets))}")

    print(f"\nTop tweets by likes:")
    ai_tweets.sort(key=lambda x: x["likes"], reverse=True)
    for i, t in enumerate(ai_tweets[:10], 1):
        print(f"\n  {i}. @{t['author_username']} ({t['author_name']})")
        print(f"      Likes: {t['likes']:,}")
        print(f"      Posted: {t.get('created_at', '')[:10]}")
        text_preview = t["text"][:120].replace("\n", " ")
        print(f"      {text_preview}")
        print(f"      {t['url']}")


if __name__ == "__main__":
    run()