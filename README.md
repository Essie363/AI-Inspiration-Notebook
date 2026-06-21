# AI 灵感簿 🎯

每日精选 3 个近 1 年内活跃的 AI 小项目，用产品思维框架拆解它们的创意切入点。

## 一句话

**从发现项目 → 拆解思维 → 积累直觉。** 帮你建立「X 问题能不能用 AI 解」的创意手感。

## 使用方式

1. 打开 `index.html` 查看每日简报
2. 用分类标签筛选项目（Extensions / Creative / Workflow）
3. 点击「View Original」去 GitHub 查看项目详情
4. 读到好项目？把链接丢给我，我来加进来

## 数据来源

| 来源 | 方式 | 状态 |
|------|------|------|
| GitHub | Python 自动采集，Search API 搜索热门 AI 项目 | ✅ 已上线 |
| X/Twitter | 待配置 API Key | ⏳ Phase 2 |
| YouTube | 待配置 API Key | ⏳ Phase 2 |
| 小红书 | 你手动丢链接，我来提取分析 | 🔗 随时可用 |

## 技术栈

- Python 3.12（采集 + 页面生成）
- 静态 HTML/CSS/JS（纯前端，无需服务器）
- Codex 自动任务（每日调度 + LLM 分析）

## 项目结构

```
ai-inspiration-notebook/
├── index.html              # 主页面（自动生成）
├── data/
│   ├── projects.json       # 所有项目归档
│   └── raw/                # 原始采集数据
├── scripts/
│   ├── config.py           # 公用配置
│   ├── fetch_github.py     # GitHub 热门 AI 项目采集
│   └── generate_page.py    # 页面生成器
├── assets/
│   ├── style.css
│   └── script.js
└── README.md
```

## 项目筛选标准

1. **近 1 年内活跃** — 创建或更新在近 1 年内的项目
2. **AI 前沿相关** — LLM、Agent、多模态、RAG、AI 工作流等方向
3. **有产品思维** — 解决真实痛点，切入点有启发

## 每个项目的分析框架

1. Pain Point — 它解决了什么痛点？
2. Why AI — 为什么用 AI 做？为什么是现在？
3. Product Insight — 产品思维拆解（核心）
4. Transfer — 由此及彼：这个思维还能用在别处吗？
