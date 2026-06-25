# AI 灵感簿 — 实现规约（Specs）

> 最后更新：2026-06-23
> 配套 PRD：`_system/planning/PRD.md`

---

## 1. 数据管线详细参数

### 1.1 GitHub 搜索策略（scripts/fetch_github.py）

| # | Query | 排序 | 时间窗口 | 定位 |
|---|-------|------|---------|------|
| 1 | `ai agent stars:>10 pushed:>{7天}` | stars | 7 天 | Agent 是当下核心范式 |
| 2 | `"AI for" stars:>10 pushed:>{1月}` | stars | 1 月 | 垂直应用命名模式 |
| 3 | `ai stars:>500 pushed:>2025-06-01` | stars | 1 年 | 市场验证过的头部信号 |
| 4 | `"AI assistant" OR "AI copilot" stars:>10 pushed:>{1月}` | updated | 1 月 | 嵌入现有流程的产品思维 |
| 5 | `"AI for makers" OR "solo dev AI" stars:>5 pushed:>{3月}` | stars | 3 月 | Maker/indie AI projects |
| 6 | `"what new AI tool" OR "interesting AI project" stars:>5 pushed:>{3月}` | stars | 3 月 | 工具/项目发现 |

- **接口**：GitHub Search API `/search/repositories`（免费，无需 Key）
- **限制**：未认证 60 次/小时，足够日常使用
- **过滤**：标题/描述/topics 命中 AI 关键词 + pushed_at 在时间窗口内
- **去重**：对比上次采集 `data/raw/`，按 `full_name` 去重
- **输出**：`data/raw/YYYY-MM-DD/github.json`

### 1.2 YouTube 搜索策略（scripts/fetch_youtube.py）

| # | Query | 排序 | 时间窗口 | 定位 |
|---|-------|------|---------|------|
| 1 | `AI agent demo` | date | 7 天 | Agent 实操演示 |
| 2 | `best AI products` | relevance | 不限 | 产品盘点（Fireship 等优质来源） |
| 3 | `AI product review` | relevance | 不限 | 单品深度评测 |
| 4 | `how I built AI` | date | 7 天 | Maker 产品故事 |
| 5 | `new AI tool launch` | date | 7 天 | 新品发布 |
| 6 | `AI startup product` | date | 7 天 | 创业公司产品 |

- **接口**：YouTube Data API v3（API Key 配置在 config.json）
- **优质频道加权**：`TRUSTED_CHANNELS = ["Fireship", "IndieStudio"]`；白名单视频排序前置
- **信号门槛**：`MIN_VIEWS = 500`，零播放/零点赞/零评论视频不入库
- **去重**：对比上次采集 `data/raw/`，按 `video_id` 去重
- **备用方案**：`scripts/fetch_youtube_test.py` 无 API Key 网页抓取
- **输出**：`data/raw/YYYY-MM-DD/youtube.json`

### 1.3 X/Twitter 采集（follow-builders feed）

- **方案**：从 follow-builders skill 的 `feed-x.json` 读取推文
- **无需 API Key**
- **去重**：follow-builders 自带 seenTweets 机制
- **增量拉取**：since_id + 自适应回退（< 5 条时回退完整窗口）
- **翻译**：`translate_tweets.py` 在采集后调用 LLM 生成 `text_zh` 字段
- **输出**：`data/raw/YYYY-MM-DD/x.json`

---

## 2. 页面生成（scripts/generate_page.js）

**关键函数**（详见 `_system/docs/implementation.md`）：
- `card(p, idx)` — 生成单张产品卡片 HTML
- `parseMdToHtml(md)` — Markdown 转 HTML（Opportunities 用）
- `seedRandom(seed)` / `shuffle(arr, seed)` — 每日随机混排

**运行时行为**：
- 只渲染当天项目（`p.date === TODAY`）
- 自动备份到 `data/backups/`，保留 7 天
- 抽取 `<script>` 内容跑 `node --check`，出错自动回退最近备份

---

## 3. 前端交互（assets/script.js）

**关键函数**（详见 `_system/docs/implementation.md`）：
- `toggleTheme()` — 亮/暗切换
- `toggleFavorite()` / `restoreFavorites()` — 收藏系统
- `expandCard()` / `collapseCard()` — 卡片展开/收起
- `filterCategory()` — 分类筛选
- `switchChannel()` / `setChannel()` — 频道切换
- Builder Digest / Opportunities 左侧导航（IntersectionObserver + 平滑滚动）

---

## 4. 视觉规范实现

### 4.1 字体阶梯（assets/style.css）

| 层级 | 字号 | 字族 | 用途 |
|------|------|------|------|
| Caption | 12px | Sans | UI 标签、导航、日期 |
| Body-S | 13px | Sans/Serif | 正文、builder 名字 |
| Body-M | 14px | Serif | 正文次级 |
| Body-L | 15px | Serif | 卡片正文 |
| H2 | 18px | Serif | 板块标题 |
| H1 | 22px | Serif | 页面大标题 |

Serif = Georgia / Crimson Text；Sans = system-ui / Inter

### 4.2 CSS 区块索引（assets/style.css）

| 区块 | 用途 |
|------|------|
| Variables (L1) | CSS 自定义属性 |
| Header (L62) | 标题栏 |
| Channel Switcher (L90) | 频道切换按钮 |
| Tabs (L126) | 分类标签栏 sticky + 阴影 |
| Timeline Layout (L146) | Builder/Opportunities 双栏布局 |
| Card Grid (L336) | 卡片网格 |
| Card (L346) | 单张卡片 |
| Mark Highlight (L473) | <mark> 莫兰迪黄高亮 |
| Full Analysis (L446) | 卡片展开分析区 |
| Favorites Modal (L535) | 收藏弹窗 |
| Opportunities (L670) | Opportunities 内容区 |
| Opportunities Sidebar (L807) | 左侧导航 |

---

## 5. 自动化调度

### 5.1 采集 Agent

- **配置**：48 小时定时触发
- **流程**：fetch_all.py → 初筛 → 产出候选清单 → 通知 PM
- **线程 ID**：`019ef08b-0487-71f2-9d15-4d32d463a031`
- **手动链接处理**：PM 随时发链接 → 按 content-filter-rules.md 判断 → 入库或退回

### 5.2 GitHub Actions 自动部署（.github/workflows/deploy.yml）

- **触发**：workflow_dispatch（手动）+ repository_dispatch（采集 Agent API 触发）
- **流程**：checkout → force-add index.html + data/projects.json + data/raw/当天目录 + assets/ + README → commit → push
- **Google Pages**：检测 main 分支更新 → 自动重新部署（1-2 分钟）
- **安全**：config.json 在 .gitignore 中，永不上传
- **URL**：`https://essie363.github.io/AI-Inspiration-Notebook/`

---

## 6. 文件结构

```
├── index.html                    # 自包含静态页面
├── assets/
│   ├── style.css                 # 全站样式
│   └── script.js                 # 交互逻辑
├── data/
│   ├── projects.json             # 项目卡片数据
│   ├── projects_backup.json      # 项目数据备份
│   ├── backups/                  # 页面备份（保留 7 天）
│   └── raw/                      # 采集原始数据（保留 30 天）
│       └── YYYY-MM-DD/
│           ├── github.json
│           ├── youtube.json
│           └── x.json
├── data/opportunities/           # BuilderPulse 蒸馏版
├── scripts/                      # 采集 + 生成脚本
├── _system/                      # 项目文档
│   ├── planning/PRD.md           # 核心产品规约
│   ├── docs/
│   │   ├── implementation.md     # 函数名+行号索引
│   │   └── specs.md              # 本文件
│   ├── work-logs/                # 工作日志
│   ├── collections/              # 候选清单
│   ├── content-filter-rules.md   # 手动链接内容判定规则
│   └── 通信录.md                  # Agent 线程注册表
├── .github/workflows/deploy.yml  # Actions 部署
├── config.json                   # API Key（不提交）
└── README.md
```

---

## 7. 技术栈与环境

| 项目 | 值 |
|------|-----|
| Python | 3.12.13（Codex 捆绑） |
| Node.js | v24.16.0（Codex 捆绑） |
| GitHub API | 未认证 60 次/小时 |
| npm | 不可用，用 pnpm.cmd |
| 页面协议 | file:// 或 https:// GitHub Pages |
| localStorage | file:// 协议下正常 |

---

## 8. 版本记录

| 版本 | 日期 | 核心变更 |
|------|------|----------|
| v1.0 | 2026-06-20 | 初版：10 个 GitHub 项目、基础卡片、3 分类 |
| v1.5 | 2026-06-21 | 收藏系统、暗色模式、卡片展开、入场动效、高亮标注 |
| v2.0 | 2026-06-21 | YouTube 源上线、fetch_all 调度器、备份回滚、PRD 重构 |
| v2.1 | 2026-06-23 | Builder Digest 频道、Opportunities 频道、GitHub Actions 部署、内容过滤规则 |
| v3.0 | 2026-06-23 | PRD 分层：核心规约 + 实现细节分离 |
