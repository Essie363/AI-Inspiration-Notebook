"""AI 閻忓灚鍔呯花?- 缂佺喍绔撮柌鍥肠鐠嬪啫瀹?""
import sys, os
sys.stdout.reconfigure(encoding="utf-8")

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))

FETCHERS = [
    ("GitHub", os.path.join(SCRIPTS_DIR, "fetch_github.py")),
    ("YouTube", os.path.join(SCRIPTS_DIR, "fetch_youtube.py")),`n    ("Twitter", os.path.join(SCRIPTS_DIR, "fetch_twitter.py")),
]

def run():
    print("=" * 50)
    print("AI 閻忓灚鍔呯花?- 缂佺喍绔撮柌鍥肠")
    print(f"  閺冦儲婀? {__import__('datetime').datetime.now().strftime('%Y-%m-%d')}")
    print("=" * 50)
    for name, path in FETCHERS:
        if not os.path.exists(path):
            print(f"  [!] {name}: 缂傚搫鐨?)
            continue
        print(f"\n--- {name} ---")
        with open(path, 'r', encoding='utf-8-sig') as f:
            code = f.read()
        try:
            exec(code, {"__name__": "__main__", "__file__": path})
        except Exception as e:
            print(f"  [ERROR] {name}: {e}")

if __name__ == "__main__":
    run()
