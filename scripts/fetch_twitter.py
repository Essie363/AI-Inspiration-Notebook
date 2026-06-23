"""AI Inspiration Notebook - X/Twitter builder tweet extractor (follow-builders feed, PRD 2.4)"""
import json, os, sys
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(ROOT, "data", "raw")
TODAY = datetime.now().strftime("%Y-%m-%d")

# Path to follow-builders feed (installed skill in Codex)
USER_HOME = os.path.expanduser("~")
FEED_PATH = os.path.join(USER_HOME, ".codex", "skills", "follow-builders", "feed-x.json")


def load_feed():
    if not os.path.exists(FEED_PATH):
        print(f"  [ERROR] Feed not found: {FEED_PATH}")
        return {}
    with open(FEED_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_tweets(feed_data, limit_per_builder=5):
    """Extract tweets from feed, skip seen ones, limit per builder."""
    seen = set()
    x_items = feed_data.get("x", [])
    all_tweets = []

    for builder in x_items:
        name = builder.get("name", "Unknown")
        handle = builder.get("handle", "")
        tweets = builder.get("tweets", [])
        selected = []
        for t in tweets:
            tid = t.get("id", "")
            if tid in seen:
                continue
            seen.add(tid)
            text = t.get("text", "")
            # Strip trailing t.co short links (X appends these, no value to readers)
            import re
            text = re.sub(r'\s*https?://t\.co/\S+\s*$', '', text).strip()
            # Skip overly short tweets (no real content)
            if len(text) < 40:
                continue
            selected.append({
                "tweet_id": tid,
                "text": text,
                "author_name": name,
                "author_username": handle,
                "created_at": t.get("createdAt", ""),
                "likes": t.get("likes", 0),
                "retweets": t.get("retweets", 0),
                "url": t.get("url", ""),
                "is_quote": t.get("isQuote", False),
            })
            if len(selected) >= limit_per_builder:
                break
        all_tweets.extend(selected)

    all_tweets.sort(key=lambda x: x["likes"], reverse=True)
    return all_tweets



def save_results(tweets):
    os.makedirs(os.path.join(RAW_DIR, TODAY), exist_ok=True)
    path = os.path.join(RAW_DIR, TODAY, "x.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(tweets, f, ensure_ascii=False, indent=2)
    print(f"  Saved: {path}")
    return path


def run():
    print("=" * 50)
    print("X/Twitter Builder Feed Extractor (PRD 2.4)")
    print("=" * 50)

    feed = load_feed()
    if not feed:
        return

    builderc_count = len(feed.get("x", []))
    print(f"  Feed: {FEED_PATH}")
    print(f"  Builders in feed: {builderc_count}")
    print(f"  seenTweets: {len(feed.get('seenTweets', {}))} tracked")

    tweets = extract_tweets(feed)
    save_results(tweets)

    print(f"\n  Extracted: {len(tweets)} tweets (limit 5 per builder)")
    for i, t in enumerate(tweets[:10], 1):
        text_preview = t["text"][:100].replace("\n", " ")
        print(f"\n  {i}. @{t['author_username']} ({t['author_name']})")
        print(f"      Likes: {t['likes']:,}  |  {t.get('created_at','')[:10]}")
        print(f"      {text_preview}")


if __name__ == "__main__":
    run()