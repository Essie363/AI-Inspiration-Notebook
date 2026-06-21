"""AI 灵感簿 - 公用配置"""

import os
from datetime import datetime

# 项目根目录
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 数据文件路径
DATA_FILE = os.path.join(ROOT_DIR, "data", "projects.json")
RAW_DIR = os.path.join(ROOT_DIR, "data", "raw")

# 网页输出路径
INDEX_HTML = os.path.join(ROOT_DIR, "index.html")

# GitHub Trend 采集配置
GITHUB_TREND_URL = "https://github.com/trending?since=daily"

# AI 关键词（用于过滤 GitHub 项目）
AI_KEYWORDS = [
    "ai", "llm", "gpt", "agent", "chatgpt", "openai", "claude", "gemini",
    "rag", "embedding", "vector", "copilot", "assistant", "workflow",
    "automation", "prompt", "langchain", "llama", "mistral", "transformer",
    "diffusion", "stable diffusion", "midjourney", "machine learning",
    "deep learning", "nlp", "computer vision", "multimodal", "vision",
    "voice", "speech", "tts", "stt", "whisper", "translation",
]

# 项目标签体系
TAGS = {
    "form": ["Chrome 插件", "AI Agent", "开源工具", "SaaS", "桌面应用", "CLI 工具", "API 工具"],
    "scene": ["To C", "To B", "To C & To B"],
    "tech": ["LLM", "多模态", "RAG", "语音", "图像", "视频", "代码", "搜索", "工作流"],
}

# 今天的日期
TODAY = datetime.now().strftime("%Y-%m-%d")
