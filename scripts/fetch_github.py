"""AI 灵感簿 - GitHub 热门 AI 项目采集（使用 Search API）"""
import requests
import json
import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import ROOT_DIR, RAW_DIR, TODAY

HEADERS = {"User-Agent": "AI-Inspiration/1.0"}
ONE_YEAR_AGO = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")

# 多个搜索维度
SEARCH_QUERIES = [
    "ai app stars:>100 pushed:>2025-01-01",
    "ai agent stars:>100 pushed:>2025-01-01",
    "llm application stars:>50 pushed:>2025-06-01",
    "ai tool stars:>50 pushed:>2025-06-01",
    "gpt app stars:>50 pushed:>2025-06-01",
    "ai chrome extension stars:>20 pushed:>2025-01-01",
]


def search_repos(query, per_page=10):
    """搜索 GitHub 仓库"""
    url = f"https://api.github.com/search/repositories?q={query}&sort=stars&order=desc&per_page={per_page}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code == 200:
            return resp.json().get("items", [])
        print(f"  API 返回状态码: {resp.status_code}")
        return []
    except Exception as e:
        print(f"  请求失败: {e}")
        return []


def is_ai_related(repo):
    """判断仓库是否与 AI 相关"""
    text = f"{repo.get('name','')} {repo.get('description','')} {' '.join(repo.get('topics',[]))}"
    text = text.lower()
    keywords = [
        "ai", "llm", "gpt", "agent", "chatgpt", "openai", "claude", "gemini",
        "rag", "embedding", "vector", "copilot", "assistant", "workflow",
        "automation", "prompt", "langchain", "llama", "mistral",
        "diffusion", "stable diffusion", "machine learning", "deep learning",
        "nlp", "multimodal", "whisper", "translation", "voice", "speech",
        "vision", "image generation", "chatbot", "ai-powered",
    ]
    return any(kw in text for kw in keywords)


def fetch_all():
    """从多个维度搜索，去重后返回"""
    seen = set()
    results = []

    for query in SEARCH_QUERIES:
        print(f"  搜索: {query[:50]}...")
        repos = search_repos(query)
        print(f"    -> 找到 {len(repos)} 个")
        for repo in repos:
            full_name = repo["full_name"]
            if full_name not in seen and is_ai_related(repo):
                seen.add(full_name)
                pushed = repo.get("pushed_at", "")
                if pushed and pushed >= ONE_YEAR_AGO:
                    results.append({
                        "full_name": full_name,
                        "url": repo.get("html_url", f"https://github.com/{full_name}"),
                        "description": repo.get("description", "") or "",
                        "language": repo.get("language", "") or "",
                        "stars": repo.get("stargazers_count", 0),
                        "forks": repo.get("forks_count", 0),
                        "open_issues": repo.get("open_issues_count", 0),
                        "created_at": repo.get("created_at", ""),
                        "pushed_at": pushed,
                        "topics": repo.get("topics", []),
                        "license": repo.get("license", {}).get("spdx_id", "") if repo.get("license") else "",
                    })

    # 按 Star 排序
    results.sort(key=lambda x: x["stars"], reverse=True)
    return results


def save_raw(projects):
    """保存原始数据"""
    os.makedirs(os.path.join(RAW_DIR, TODAY), exist_ok=True)
    path = os.path.join(RAW_DIR, TODAY, "github.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(projects, f, ensure_ascii=False, indent=2)
    print(f"  -> 已保存: {path}")
    return path


def run():
    print("=" * 50)
    print("GitHub 热门 AI 项目采集")
    print("=" * 50)

    projects = fetch_all()

    if not projects:
        print("  !! 未找到符合条件的项目")
        return []

    save_raw(projects)

    print(f"\n{'='*50}")
    print(f"Top AI 项目（近 1 年活跃，按 Star 排序）")
    print(f"{'='*50}")
    for i, p in enumerate(projects[:15], 1):
        print(f"  {i}. {p['full_name']}")
        print(f"      Stars: {p['stars']}  |  Updated: {p.get('pushed_at','')[:10]}  |  Lang: {p.get('language','')}")
        desc = p["description"][:80] + "..." if len(p["description"]) > 80 else p["description"]
        print(f"      {desc}")
        print()

    return projects


if __name__ == "__main__":
    run()
