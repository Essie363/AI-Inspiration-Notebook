"""AI Inspiration Notebook - Tweet translation via Codex conversation (PRD 2.4)

This script does NOT call any external API.
It reads x.json, prints tweets needing translation,
and accepts translated output back via a JSON file.

Usage:
  python scripts/translate_tweets.py prepare    # prints tweets to translate
  python scripts/translate_tweets.py apply      # reads translations.json and updates x.json
"""

import json, os, sys

# Fix Windows console encoding for emoji output
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(ROOT, "data", "raw")
TODAY = datetime.now().strftime("%Y-%m-%d")
X_PATH = os.path.join(RAW_DIR, TODAY, "x.json")
TRANS_PATH = os.path.join(RAW_DIR, TODAY, "_translations.json")


def prepare():
    """Print tweets that need translation as numbered list for Codex to translate."""
    x_path = X_PATH
    if not os.path.exists(x_path):
        yesterday = (datetime.now() - __import__('datetime').timedelta(days=1)).strftime("%Y-%m-%d")
        x_path_y = os.path.join(RAW_DIR, yesterday, "x.json")
        if os.path.exists(x_path_y):
            x_path = x_path_y
        else:
            print("No x.json found for today or yesterday.")
            return

    with open(x_path, "r", encoding="utf-8") as f:
        tweets = json.load(f)

    pending = []
    for i, t in enumerate(tweets):
        text = t.get("text", "")
        if not text or len(text) < 15:
            continue
        pending.append({
            "index": i,
            "text": text,
            "author": t.get("author_name", ""),
            "username": t.get("author_username", ""),
            "text_zh": t.get("text_zh", ""),
        })

    untranslated = [p for p in pending if not p["text_zh"]]

    if not untranslated:
        print(f"All {len(pending)} tweets already translated.")
        return

    print(f"# Translation needed: {len(untranslated)}/{len(pending)} tweets")
    print(f"# Source: {x_path}")
    print(f"# Please translate each tweet to natural Simplified Chinese.")
    print(f"# Keep proper nouns (product names, people, tech terms) unchanged.")
    print(f"# Do NOT add explanations. Keep emojis.")
    print()
    for item in untranslated:
        print(f"[{item['index']}] @{item['username']} ({item['author']})")
        print(f"    {item['text']}")
        print()

    # Also save a structured file for apply step
    save_data = [{"index": item["index"], "text": item["text"]} for item in untranslated]
    with open(TRANS_PATH, "w", encoding="utf-8") as f:
        json.dump(save_data, f, ensure_ascii=False, indent=2)
    print(f"---")
    print(f"Index file saved: {TRANS_PATH}")
    print(f"When translations are ready, run: python scripts/translate_tweets.py apply")


def apply():
    """Read translations from stdin (JSON array of {index, text_zh}) and update x.json."""
    if not os.path.exists(TRANS_PATH):
        print(f"No pending translations file: {TRANS_PATH}")
        print("Run 'prepare' first.")
        return

    if not os.path.exists(X_PATH):
        print(f"No x.json: {X_PATH}")
        return

    # Read translations from stdin
    raw = sys.stdin.read()
    try:
        translations = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON input: {e}")
        return

    if not isinstance(translations, list):
        print("Expected a JSON array of {index, text_zh}")
        return

    # Build lookup
    trans_map = {}
    for item in translations:
        idx = item.get("index")
        if idx is not None:
            trans_map[idx] = item.get("text_zh", "")

    # Update x.json
    with open(x_path, "r", encoding="utf-8") as f:
        tweets = json.load(f)

    updated = 0
    for i, t in enumerate(tweets):
        if i in trans_map and trans_map[i]:
            t["text_zh"] = trans_map[i]
            updated += 1

    with open(X_PATH, "w", encoding="utf-8") as f:
        json.dump(tweets, f, ensure_ascii=False, indent=2)

    print(f"Updated {updated} tweets in {X_PATH}")
    print(f"Run generate_page.py to see translations on page.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/translate_tweets.py [prepare|apply]")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "prepare":
        prepare()
    elif cmd == "apply":
        apply()
    else:
        print(f"Unknown command: {cmd}")