"""AI Inspiration Notebook - BuilderPulse Opportunities fetcher (PRD 4.4)"""
import os, sys, shutil, subprocess

sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OPP_DIR = os.path.join(ROOT, "data", "opportunities")
BP_ROOT = r"D:\codex_workspace\BuilderPulse-main\BuilderPulse-main"
BP_ZH_DIR = os.path.join(BP_ROOT, "zh", "2026")


def git_pull():
    """Try git pull on BuilderPulse repo; skip if network unavailable."""
    if not os.path.isdir(os.path.join(BP_ROOT, ".git")):
        print("  [SKIP] BuilderPulse not a git repo, using local files")
        return False
    try:
        result = subprocess.run(
            ["git", "-C", BP_ROOT, "pull"],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            print(f"  [OK] git pull: {result.stdout.strip() or 'Already up to date.'}")
            return True
        else:
            print(f"  [WARN] git pull failed: {result.stderr.strip()[:100]}")
            return False
    except Exception as e:
        print(f"  [SKIP] git pull error: {e}")
        return False


def get_latest_files(n=2):
    """Get N most recent .md files from BuilderPulse zh/2026/."""
    if not os.path.isdir(BP_ZH_DIR):
        print(f"  [ERROR] BuilderPulse zh/2026/ not found: {BP_ZH_DIR}")
        return []
    files = sorted(
        [f for f in os.listdir(BP_ZH_DIR) if f.endswith(".md")],
        reverse=True
    )
    selected = files[:n]
    for f in selected:
        print(f"  Found: {f}")
    return selected


def copy_raw(filenames):
    """Copy raw .md files to data/opportunities/."""
    os.makedirs(OPP_DIR, exist_ok=True)
    copied = []
    for fname in filenames:
        src = os.path.join(BP_ZH_DIR, fname)
        dst = os.path.join(OPP_DIR, fname)
        shutil.copy2(src, dst)
        print(f"  Copied: {fname} -> data/opportunities/")
        copied.append(fname)
    return copied


def run():
    print("=" * 50)
    print("BuilderPulse Opportunities Fetcher (PRD 4.4)")
    print("=" * 50)

    # 1. git pull
    git_pull()

    # 2. get latest 2 days
    files = get_latest_files(2)
    if not files:
        print("  [ERROR] No files found. Abort.")
        return

    # 3. copy raw
    copied = copy_raw(files)
    print(f"\n  Total: {len(copied)} files copied to data/opportunities/")
    print("  Next step: AI distill raw -> -distilled.md (manual or automated)")


if __name__ == "__main__":
    run()
