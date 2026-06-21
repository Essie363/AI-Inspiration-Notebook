"""AI Inspiration Notebook - X/Twitter AI Project Collector (X API v2)"""
import requests, json, sys, os, re
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(ROOT, "data", "raw")
TODAY = datetime.now().strftime("%Y-%m-%d")
CONFIG_PATH = os.path.join(ROOT, "config.json")

# Search queries for AI project/product tweets
# Search queries from PRD Section 2.4
QUERIES = [
    '"AI product launch" OR "new AI tool" -is:retweet',
    '"just shipped" OR "just launched" AI -is:retweet',
    '"built this" OR "made this" AI -is:retweet',
]

# Non-AI content patterns to exclude
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

def search_tweets(bearer_token, query, max_results=10):
    url = f"{X_API_BASE}/tweets/search/recent"
    headers = {"Authorization": f"Bearer {bearer_token}"}
    params = {
        "query": query,
        "max_results": max_results,
        "tweet.fields": "created_at,public_metrics,author_id",
        "user.fields": "name,username",
        "expansions": "author_id",
    }
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
                "url": f"https://twitter.com/{u}/status/{tweet["id"]}",
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

def save_results(tweets):
    os.makedirs(os.path.join(RAW_DIR, TODAY), exist_ok=True)
    path = os.path.join(RAW_DIR, TODAY, "twitter.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(tweets, f, ensure_ascii=False, indent=2)
    print(f"  Saved: {path}")
    return path

def run():
    print("=" * 50)
    print("X/Twitter AI Project Collector")
    print("=" * 50)

    bearer_token = load_bearer_token()
    if not bearer_token:
        print("  [ERROR] No Bearer Token in config.json")
        return

    all_tweets = []
    seen_ids = set()

    for q in QUERIES:
        print(f"  Searching: {q[:60]}...")
        tweets = search_tweets(bearer_token, q)
        print(f"    -> Found {len(tweets)} tweets")
        for t in tweets:
            if t["tweet_id"] not in seen_ids:
                seen_ids.add(t["tweet_id"])
                all_tweets.append(t)

    if not all_tweets:
        print("  No results found")
        return

    ai_tweets = [t for t in all_tweets if is_ai_related(t["text"])]
    print(f"\n  Total collected: {len(all_tweets)}")
    print(f"  AI-related: {len(ai_tweets)}")

    save_results(ai_tweets)

    print(f"\nTop tweets by likes:")
    ai_tweets.sort(key=lambda x: x["likes"], reverse=True)
    for i, t in enumerate(ai_tweets[:10], 1):
        print(f"\n  {i}. @{t['author_username']} ({t['author_name']})")
        print(f"      Likes: {t['likes']:,}")
        pub = t.get("created_at", "")[:10]
        print(f"      Posted: {pub}")
        text_preview = t["text"][:120].replace("\n", " ")
        print(f"      {text_preview}")
        print(f"      {t['url']}")


if __name__ == "__main__":
    run()