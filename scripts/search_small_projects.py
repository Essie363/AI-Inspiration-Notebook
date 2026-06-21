import requests, json, sys
sys.stdout.reconfigure(encoding="utf-8")
headers = {"User-Agent": "AI-Inspiration/1.0"}
queries = [
    "stars:50..3000 chrome extension ai pushed:>2025-01-01 sort:stars",
    "stars:50..3000 ai creative tool pushed:>2025-01-01 sort:stars",
    "stars:50..3000 ai productivity pushed:>2025-01-01 sort:stars",
    "stars:50..3000 personal ai project pushed:>2025-01-01 sort:stars",
    "stars:50..3000 ai agent extension pushed:>2025-01-01 sort:stars",
    "stars:50..3000 ai browser extension pushed:>2025-01-01 sort:stars",
]
seen = set()
for q in queries:
    url = "https://api.github.com/search/repositories?q=" + q + "&per_page=8"
    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code != 200:
            print("SKIP " + str(r.status_code) + ": " + q[:50])
            continue
        items = r.json().get("items", [])
        for item in items:
            fn = item["full_name"]
            if fn not in seen:
                seen.add(fn)
                desc = (item.get("description") or "")[:120]
                pushed = item.get("pushed_at","")[:10]
                lang = item.get("language") or "-"
                stars = item["stargazers_count"]
                print(fn)
                print("  stars:" + str(stars) + " pushed:" + pushed + " lang:" + lang)
                print("  " + desc)
                print("  topics:" + " ".join(item.get("topics", [])))
                print()
    except Exception as e:
        print("Error: " + str(e))
print("--- Total: " + str(len(seen)) + " unique projects ---")
