# AI 灵感簿 — 产品需求文档（PRD）v2.0

> 项目版本：v2.0  
> 最后更新：2026-06-21（重构版）  
> 设计师：Essie Zhang

---

## 1. 产品概述

隔天从 GitHub、YouTube、X 等平台自动采集近一年内活跃的 AI 小项目，AI 自动筛选排优先级；小红书等平台由你手动链接触发。用产品思维框架拆解创意切入点，生成静态网页供随时翻阅学习。


### 1.2 目标用户

- **你 / Essie Zhang**：2 年视频流媒体商业化 PM 经验，正在向 AI 产品经理转型
- 核心需求：建立「某个问题能不能用 AI 解」的创意直觉
- 身份定位：非专业软件工程师，追求简单、实用、易维护的方案

### 1.3 核心理念

不关注技术实现，只关注**产品思维与用户洞察**。每个入选项目的核心价值是——

- 创造者发现了什么人类痛点？
- 为什么用 AI 的方式去解？
- 切入视角有什么独特之处？

### 1.4 当前状态（截至 2026-06-21）

- 项目总数：**10 个**（7 个 GitHub 来源 + 3 个 YouTube 来源）
- 核心采集管道：GitHub + YouTube 双源并行，已全部上线
- 页面迭代版本：v5（含收藏系统、备份回滚）；X/Twitter 数据源已切换为 follow-builders feed

---

## 2. 数据管线

### 2.1 数据源一览

| 来源 | 筛选方式 | 采集方式 | 状态 |
|------|---------|---------|------|
| GitHub | 🤖 AI 自动筛选 + 排优先级 | Python 自动采集（Search API v3 + 6 维度关键词搜索） | ✅ 已上线 |
| YouTube | 🤖 AI 自动筛选 + 排优先级 | Python 自动采集（YouTube Data API v3） | ✅ 已上线 |
| X/Twitter | 🤖 AI 自动筛选 + 排优先级 | 接入 follow-builders skill 的中央 feed（无需 API Key） | ✅ 已上线 |
| 小红书 | 👤 你手动丢链接 | content-extractor skill 提取内容 | 🔗 随时可用 |
| B 站 / 其他 | 👤 你手动丢链接 | content-extractor skill 提取内容 | 🔗 随时可用 |

### 2.2 GitHub 采集（scripts/fetch_github.py）

- **接口**：GitHub Search API `/search/repositories`（免费，无需 Key）
- **搜索策略**（6 条 query，混合排序 + 滑动时间窗口）：
  | # | Query | 排序 | 时间窗口 | 定位 |
  |---|-------|------|---------|------|
  | 1 | `ai agent stars:>10 pushed:>{7天}` | stars | 7 天 | Agent 是当下核心范式，好项目多从此来 |
  | 2 | `"AI for" stars:>10 pushed:>{1月}` | stars | 1 月 | 「AI for X」垂直应用，定义了用户和场景 |
  | 3 | `ai stars:>500 pushed:>2025-06-01` | stars | 1 年 | 补课：经过市场验证的高星项目 |
  | 4 | `"AI assistant" OR "AI copilot" stars:>10 pushed:>{1月}` | updated | 1 月 | 助手/副驾驶 = 嵌入现有流程的产品思维 |
  | 5 | `"indie hacker" OR "AI side project" stars:>5 pushed:>{3月}` | stars | 3 月 | 独立开发者创意产品，窄切口有叙事 |
  | 6 | `"AI chrome extension" OR "AI plugin" stars:>5 pushed:>{3月}` | stars | 3 月 | 扩展/插件 = 最产品化的形态 |
- **过滤规则**：标题/描述/topics 命中 AI 关键词 + pushed_at 在对应时间窗口内
- **防重复**：对比上一次采集的 `data/raw/` 数据，剔除重复 `full_name`
- **输出**：`data/raw/YYYY-MM-DD/github.json`
- **限制**：未认证 API 60 次/小时，当前足够；认证后可提升至 5000 次/小时
### 2.3 YouTube 采集（scripts/fetch_youtube.py）

- **接口**：YouTube Data API v3
- **认证**：通过 `config.json` 中的 `youtube_api_key` 字段（已配置）
- **搜索策略**（6 组 query，混合排序 + 滑动时间窗口）：
  | # | Query | 排序 | 时间窗口 | 定位 |
  |---|-------|------|---------|------|
  | 1 | `AI agent demo` | date | 7 天 | Agent 实操演示 |
  | 2 | `best AI products` | relevance | 不限 | 产品盘点（Fireship 风格，我们最好的来源之一） |
  | 3 | `AI product review` | relevance | 不限 | 补课：单品深度评测，产品视角 |
  | 4 | `how I built AI` | date | 7 天 | Maker 讲述自己的产品故事 |
  | 5 | `new AI tool launch` | date | 7 天 | 新品发布 |
  | 6 | `AI startup product` | date | 7 天 | 创业公司产品 |
- **过滤规则**：
  - 排除非 AI 内容（音乐 MV、预告片、游戏、体育等）
  - 发布窗口按 query 分层：7 天（date 排序）；relevance 排序的不限窗口
- **防重复**：对比上一次采集的 `data/raw/` 数据，剔除重复 `video_id`
- **信号校验**：零播放/零点赞/零评论的新视频（信号全空）默认不入库——这些视频无法判断信息质量，降低入库门槛风险
- **输出**：`data/raw/YYYY-MM-DD/youtube.json`
- **备用方案**：`scripts/fetch_youtube_test.py` 提供无 API Key 的网页抓取路线
### 2.4 X/Twitter 采集（follow-builders feed）

- **方案**：使用已安装的 [follow-builders](https://github.com/zarazhangrui/follow-builders) skill
- **数据源**：26 位 AI builder 的推文，由 follow-builders 通过 GitHub Actions 定时拉取到中央 feed（`state-feed.json`），灵感簿采集 Agent 从本地读取
- **Builder 名单**：Andrej Karpathy、Swyx、Josh Woodward、Boris Cherny、Peter Yang、Nan Yu、Amanda Askell、Cat Wu、Amjad Masad、Guillermo Rauch、Alex Albert、Aaron Levie、Ryo Lu、Garry Tan、Matt Turck、Zara Zhang、Nikunj Kothari、Dan Shipper、Aditya Agarwal、Sam Altman、Claude (Official) 等共 26 人
- **优势**：无 API Key、无额度限制；名单由社区维护；已看推文自动去重（`seenTweets` 持久化）
- **输出**：`data/raw/YYYY-MM-DD/x.json`
  - 每条推文包含 `text`（原文）和 `text_zh`（AI 翻译的简体中文），页面优先显示 `text_zh`
- **扩展**：如需关注更多 builder，可提交 PR 到 follow-builders 的 `config/default-sources.json`

### 2.5 统一调度器（scripts/fetch_all.py）

- 按序执行 GitHub → YouTube 两个采集器
- 每个采集器独立运行，互不影响；即使一个失败，另一个仍然继续
- 采集后由 AI 自动筛选、排优先级，生成推荐清单推送给用户审阅；用户确认后编写分析入库

### 2.6 项目筛选标准（三条，缺一不可）

1. **近 1 年内活跃** — 创建或最近更新在近 1 年之内，不能是停更多年的老项目
2. **AI 前沿相关** — 涉及 LLM、Agent、多模态、RAG、AI 工作流、AI 原生应用等当前方向
3. **有产品思维** — 解决了一个真实痛点，切入点有启发。纯技术玩具但没有产品思考的不选


### 2.7 AI 自动筛选与优先级排序（适用于 GitHub / YouTube / X）

- AI 在原始采集结果中执行首轮筛选：
  1. 排除明显非 AI 项目（纯工具库、非 AI 技术栈等）
  2. 排除无产品叙事价值的项目（纯技术 Demo、无用户洞察）
  3. 识别有产品启发潜力的项目
- 对通过筛选的项目进行优先级排序
  - 考量维度：Stars / 播放量、近期趋势、产品创意新颖度、与你关注方向的匹配度
  - 输出：Top N 推荐清单 + 每条附一句话入选理由
- 用户审阅推荐清单，确认入选项目 → AI 编写分析文案 → 用户定稿 → 入库 `projects.json`

> 小红书 / B 站 / 其他平台不经过此流程——由你手动丢链接，AI 直接用 content-extractor 提取并分析。
---
- **数据源说明**：Builder Digest 内容更新依赖 follow-builders skill 的上游 eed-x.json 刷新频率（当前约每周 1-2 次），非实时推送。采集 Agent 每次运行时拉取最新 feed-x.json 并转存为 x.json；如上游无更新，x.json 内容保持上一次的数据。这是数据源固有特性，非 bug。


## 3. 分析框架

每个入选项目按以下 5 块框架编写分析文案：

| 模块 | 内容 |
|------|------|
| ① 一句话 | 这是什么产品 |
| ② Pain Point | 解决了什么痛点？新痛点还是老问题新解法？ |
| ③ Why AI | 为什么用 AI 做？为什么是现在？什么技术/成本/体验变化让这个产品可行？ |
| ④ Product Insight | 切入点怎么选的？核心洞察是什么？怎么冷启动？怎么变现？护城河在哪？ |
| ⑤ Transfer | 这个思维模型还能用在别处吗？用户是否可以联系自己的经验来理解？ |

### 3.1 分析文案风格要求

#### 基本准则

- 平白直实：每句话只讲一个事实或一个因果，不堆名词、不抖机灵
- 信息密度优先：一句「口播创作者反复手动剪口误——有特定、高频的痛点用户群」优于三段场景描写
- 答案前置：Key Insight 直接说出产品做了什么选择，不说「接住了用户的路径」这类虚指
- 讲 why 不讲 what：不是「AI 擅长模式识别」，而是「规则判断不了节奏感，因为节奏感因人而异」
- 删掉 PPT 黑话：不说寄生生态、自我进化闭环、产品壁垒越用越高

#### 禁止使用

- 设问句（「你有没有想过……」）、感叹句（「你猜怎么着！」）
- 夸张化命令式语气（「最聪明的不是功能」「这才是要害」）
- 花活比喻（「昨天剪掉的 17 个然后，今天一个都不会少」）
- 抽象名词堆叠（能力、闭环、范式、生态位）

#### 篇幅控制（适配网页卡片布局）

| 模块 | 上限 | 说明 |
|------|------|------|
| Key Insight | 1 句 | 直接说出核心选择或矛盾 |
| Pain Point | 2-3 句 | 谁在痛 + 为什么现有方案不解决 |
| Why AI | 3-4 句 | 规则方案为什么不够 + AI 改变了什么 |
| Product Insight | 4-5 句 | 产品形态选择的因果推演 |
| Transfer | 2-3 句 | 可迁移的方法论 / 三步法 |

每个项目的 Key Insight 用 `%%` 标记截断点，生成页面时只展示截断前的内容。

> 当前分析文案由 Codex LLM 编写，人工审查后保存到 `projects.json`

---

## 4. 网页功能与交互

### 4.1 页面布局

- **标题栏**：项目名称「AI Inspiration Notebook」+ 更新日期（`YYYY-MM-DD HH:MM`）+ 项目总数 + 收藏按钮（♥）+ 主题切换按钮（☀/🌙）
- **分类标签栏**：All / Extensions / Creative / Workflow / Builder Digest（各含项目计数或更新条数）
  - 前四个 tab 显示产品分析卡片，Builder Digest 显示 builder 推文时间线
  - 滚动时粘性固定在顶部（`position: sticky` + IntersectionObserver 检测 scroll sentinel）
  - 粘住后加上阴影下划线视觉提示
- **主内容区**：网格卡片布局，桌面 3 列 / 平板 2 列 / 手机 1 列
  - 视图策略：All 下所有卡片随机混排（`random.seed(当天日期)`），保证每日页面有新鲜感
- **页脚**：AI Inspiration Notebook + Designed by Essie Zhang

### 4.2 卡片交互

| 状态 | 显示内容 |
|------|---------|
| **紧凑状态**（默认） | 标题 · 一行描述 · 分类标签（带颜色框） · 来源标签 · 日期 · 心形收藏按钮 · Key Insight（2 行内，浅黄色背景高亮块） · 「click to expand」提示 |
| **展开状态**（点击卡片） | 卡片横向拉通铺满整行，其他卡片自动下移 + 标签列表（Chrome 插件 / To C 等） + Pain Point / Why AI / Product Insight / Transfer 四块分析（左右两列排列） + View Original 链接 + Collapse 按钮 |

### 4.3 收藏系统

- 每张卡片右上角有 ♡ 按钮：
  - 未收藏：镂空灰色心形（CSS 描边实现：`color: transparent; -webkit-text-stroke: 1.5px`）
  - 已收藏：红色实心心形（`color: var(--heart); #d4726a`）
- 数据存储在浏览器 `localStorage`，key 为 `ai-inspiration-favs`
  - 格式：`[{ id, addedAt }]`
  - 跨页面会话保留，**换设备或清缓存后丢失**（纯前端方案的设计代价）
- 已收藏的卡片左侧有红色边框标记（`card.classList.add("favorited")`）

### 4.4 收藏弹窗

- 点击右上角 ♥ 按钮打开
- 按收藏日期分组显示（最新在前）
- 每个项目显示：标题 + Open 链接 + ♥ 取消收藏按钮
- ♥ 按钮默认为红色实心（表示已收藏状态），点击即取消
- 按 Escape 或点击背景遮罩关闭弹窗

### 4.5 入场动效

- 页面加载时，卡片依次滑入（translateY: 20px → 0 + opacity: 0 → 1）
- 错位间隔 0.08s（卡 1: 0.06s → 卡 N: 0.06+N×0.08s）
- 动画时长 0.45s，ease-out

### 4.6 高亮标注

- 分析文本中的关键术语用 `<mark>` 标签包裹
- CSS 渲染为莫兰迪黄 `#f2ebd0` 背景色（无下划线）
- 暗色模式：`#4a3f28`

### 4.7 Builder Digest（Phase 2）

- 点击「Builder Digest」tab 时，主内容区从卡片网格切换为时间线流
- 每条显示：builder 名称 + 推文正文（简体中文翻译，AI 自动翻译）+ 原文链接
- 推文不超过 3 句话，不展开、不拆解——内容是信号，不是产品案例
- Builder Digest 更新频率跟随 follow-builders feed 节奏，非每日必新
- 英文推文在采集阶段由 AI 翻译为简体中文（`text_zh` 字段存入 `x.json`），页面优先显示中文
- 数据源同 PRD §2.4，从 follow-builders 的 `feed-x.json` 读取，隔天一批，翻译在采集阶段完成


### 4.8 Opportunities 频道（BuilderPulse 蒸馏版）

**数据来源**：BuilderPulse 中文版日报（`BuilderPulse/zh/2026/`），取最近 2 天

**筛选原则**：从 BuilderPulse 原文中只提取与「模型进展 / 产品发布 / 对日常有什么帮助」相关的内容，删掉纯技术工程话题（npm 后门、安全漏洞、容器配置、GPU 技术选型、"今日 2 小时构建"）。

**保留的板块结构**：

| 板块 | 内容 |
|------|------|
| 📝 核心观点 | 当日最重要的一个判断，一段话 |
| 📊 今日三大信号 | 当日最值得关注的 3 条动态，每条带「对你意味着什么」 |
| 📋 白话简报 | 表格形式：事件 + 讨论热度 + 对你意味着什么 |
| 🔍 发现机会 | 保留子板块：本地模型进展、模型路由、AI 工作伴侣、独立开发者产品思路 |
| 🔄 反直觉发现 | 当日跟表面头条不同的深层信号 |
| 📱 Product Hunt 热门 | 表格形式：产品 + 类型 + 一句话 |

**删除的板块**：今日 2 小时构建、技术选型·开发者工具、技术选型·大公司产品变动（如与普通用户无关）、HuggingFace 模型技术指标

**蒸馏语言规则**（与 PRD §3.1 一致）：
- 平白直实，每句只讲一个事实或一个因果
- 技术黑话转普通人语言（如「MCP 协议使 AI 连接外部工具」→「让 AI 能调用其他软件」）
- 每条控制在卡片可读长度，不超 5-6 句
- 聚焦「跟之前有什么不同 → 对普通用户意味着什么」，不讲跑分数字

**页面布局**：与 Builder Digest 一致的双栏布局（左侧 sticky 导航 + 右侧内容区），左侧目录自动提取 H2 标题，IntersectionObserver 滚动高亮

**更新频率**：跟 BuilderPulse 源同步，隔天取最新 2 天内容


---

## 5. 数据安全机制

### 5.1 自动备份

- 每次页面生成成功后，自动复制 `index.html` 到 `data/backups/YYYY-MM-DD_HH-MM-SS_index.html`
- 自动清理 7 天前的旧备份（按文件修改时间判断）

### 5.2 JS 语法校验 — 防止生成坏页面

- 页面生成后，抽取 `<script>` 内容写入临时 `.js` 文件
- 执行 `node --check` 做语法校验
- **如果 JS 语法出错**：自动从最近一次备份恢复 `index.html`，避免生成无法交互的坏页面
- 如果 `node` 不可用，跳过校验并 continue（不阻塞生成流程）


### 5.3 原始数据清理

- `data/raw/` 下的采集数据按日期分目录存储
- 每次页面生成时，自动删除 30 天前的日期目录（整目录递归删除）
- 保留窗口：30 天——够做月度趋势回顾，不无限堆积
- 每次采集约 340 KB，隔天运行 30 天约 15 次 ≈ 5 MB，磁盘压力可忽略
- 如果某天未执行 `generate_page.py`，清理也随之跳过（无独立 cron）
---

## 6. 视觉设计系统

### 6.1 亮色模式

| 用途 | 色值 |
|------|------|
| 背景 | `#f6f1ea` |
| 卡片表面 | `#fffcf7` |
| 正文 | `#3d2b1f`（深棕） |
| 次要文字 | `#7d6b5a` |
| 三级文字 | `#b0a090` |
| 边框 | `#e6ddd0` |
| 主色 | `#9a6b4d`（暖棕） |
| 标记高亮 | `#f2ebd0` |
| 心形色 | `#d4726a` |

### 6.2 暗色模式

| 用途 | 色值 |
|------|------|
| 背景 | `#1c1814` |
| 卡片表面 | `#27221c` |
| 正文 | `#e6ddd0` |
| 主色 | `#c49a6c` |
| 标记高亮 | `#4a3f28` |

### 6.3 字体

- 衬线体（标题 / Key Insight）：`"Noto Serif SC", "Source Han Serif SC", "STSong", Georgia, serif`
- 无衬线体（正文 / 标签 / 分析）：`"Noto Sans SC", -apple-system, BlinkMacSystemFont, sans-serif`

### 6.4 分类标签颜色

| 分类 | 亮色模式 | 暗色模式 |
|------|---------|---------|
| Extension | `#8ea9c6` 灰蓝 | `#6d8ba8` |
| Creative | `#c4a882` 暖沙 | `#a88d6a` |
| Workflow | `#92b8a8` 鼠尾草绿 | `#719a88` |

### 6.5 主题切换实现

- 使用 `data-theme="dark"` 属性附加到 `<html>` 元素
- CSS 变量覆盖模式：亮色变量在 `:root`，暗色变量在 `[data-theme="dark"]` 选择器下
- 用户偏好存储在 `localStorage` key `ai-inspiration-theme`
- 页面加载时立即读取 localStorage 恢复主题（避免闪烁）


### 6.6 字体规范阶梯

全站所有文字组件统一从以下六级字号中取值，不各自定义：

| 级别 | 字号 | 字重 | 字族 | 用途 |
|------|------|------|------|------|
| **H1** | 22px | 700 | Serif | 页面主标题 |
| **H2** | 18px | 700 | Serif | 板块标题（Opportunities 章节标题） |
| **Body-L** | 15px | 400 | Sans | 全局正文、卡片描述 |
| **Body-M** | 14px | 400 | Sans/Serif | 卡片分析正文（Serif）、Opportunities 正文（Serif） |
| **Body-S** | 13px | 400/500 | Sans | 卡片分析小字、导航项、标签、Builder Digest 推文 |
| **Caption** | 12px | 400/500 | Sans | 辅助文字、Key Insight 标签、tab 按钮 |

**字族分配**：
- Serif（`"Noto Serif SC", Georgia, serif`）：标题 H1/H2、卡片 Key Insight、Opportunities 正文段落
- Sans（`"Noto Sans SC", -apple-system, sans-serif`）：全局 UI、标签、按钮、导航、Builder Digest 全部内容

**色值统一**：
- 正文：`--text`（#3d2b1f 亮 / #e6ddd0 暗）
- 次要文字：`--text-secondary`（#7d6b5a 亮 / #b0a090 暗）
- 三级文字：`--text-tertiary`（#b0a090 亮 / #7d6b5a 暗）
- 主色强调：`--primary`（#9a6b4d 亮 / #c49a6c 暗）


---

## 7. 技术架构

### 7.1 技术栈

| 层 | 技术 |
|----|------|
| 数据采集 | Python 3.12（requests, json, re, datetime — 纯标准库 + requests） |
| 页面生成 | Python 脚本（字符串模板拼接，无模板引擎依赖） |
| 前端 | 纯静态 HTML / CSS / JavaScript（无框架、无依赖） |
| 数据存储 | localStorage（浏览器端），JSON（项目端） |
| 部署 | 本地 `file://` 直接打开，GitHub Pages（🔨 进行中） |

### 7.2 脚本清单

| 脚本 | 功能 | 调用方式 |
|------|------|----------|
| `fetch_all.py` | 统一采集调度器，依次调用 GitHub + YouTube 采集 | `python scripts/fetch_all.py` |
| `fetch_github.py` | GitHub Search API 6 维度搜索，过滤 AI 项目 | 被 fetch_all.py 调用 |
| `fetch_youtube.py` | YouTube Data API v3 搜索 AI 项目视频 | 被 fetch_all.py 调用 |
| `fetch_youtube_test.py` | YouTube 网页抓取备用方案（无需 API Key） | 独立运行，测试用 |
| `generate_page.py` | 读取 projects.json → 拼接 HTML/CSS/JS → 备份 + JS 校验 + 清理 | `node scripts/generate_page.js` |
| `search_small_projects.py` | 小星标专项搜索（早期探索，当前未集成管线） | 独立运行 |
| `config.py` | 公用路径、AI 关键词、标签体系配置 | 被其他脚本 import |

### 7.3 项目目录结构

```
ai-inspiration-notebook/
├── config.json              # API Key 配置（youtube_api_key）
├── index.html               # 主页面（自动生成，勿手动编辑）
├── README.md                # 项目说明
├── test.html                # 测试用页面
├── data/
│   ├── projects.json        # 所有项目归档（人工编写分析 + 原始信息）
│   ├── backups/             # 自动备份（YYYY-MM-DD_HH-MM-SS_index.html）
│   └── raw/                 # 原始采集数据（按日期分目录）
│       ├── YYYY-MM-DD/
│       │   ├── github.json  # GitHub 搜索结果原始数据
│       │   └── youtube.json # YouTube 搜索结果原始数据
├── scripts/
│   ├── config.py            # 公用配置（路径、AI 关键词、标签体系）
│   ├── fetch_all.py         # 统一采集调度器
│   ├── fetch_github.py      # GitHub 热门 AI 项目采集
│   ├── fetch_youtube.py     # YouTube AI 项目视频采集
│   ├── fetch_youtube_test.py # YouTube 网页抓取备用方案
│   ├── generate_page.py     # 页面生成器（含备份、JS 校验、7 天清理）
│   └── search_small_projects.py # 小项目专项搜索（探索性质）
├── assets/
│   ├── style.css            # 完整样式（亮/暗色模式 + 响应式 + 动效）
│   └── script.js            # 交互逻辑（主题/收藏/展开/筛选/弹窗/Toast）
└── _系统/                    # 项目管理文档
    ├── 规划文档/PRD.md
    ├── 设计文档/
    └── 参考资料/
```

---

## 8. 当前项目清单（10 个，截至 2026-06-21）

### 8.1 Chrome 插件类（3 个）

| # | 项目 | Stars | 一句话 Key Insight |
|---|------|-------|-------------------|
| 1 | **Writely** | 1.3k | Notion AI 只能在 Notion 里用。它可以去任何地方。就这么一个区别。 |
| 2 | **MouseTooltip Translator** | 1.2k | 选中→右键→翻译→等弹窗→关弹窗。你每天重复多少次？它砍成一步：悬停。 |
| 3 | **Claude Counter** | 1.9k | AI 不告诉你的事，就是你的机会。Claude 不显示 Token？那我来加几行字。 |

### 8.2 AI 创意工具类（3 个）

| # | 项目 | Stars | 一句话 Key Insight |
|---|------|-------|-------------------|
| 4 | **DashPlayer** | 4k | 你不是缺学习工具，你缺的是一个你本来就在用的东西，里面多了 AI。 |
| 5 | **Comic Translate** | 2.8k | 不做「AI 翻译」这个大而全的东西，只做「AI 翻译漫画」。定位越窄，用户越觉得这东西就是为我做的。 |
| 6 | **Writingway** | 170 | ChatGPT 写东西像助理，Writingway 更像一个也读过你草稿的编辑。区别就在这里。 |

### 8.3 AI 工作流类（1 个）

| # | 项目 | Stars | 一句话 Key Insight |
|---|------|-------|-------------------|
| 7 | **Quick Prompt** | 826 | AI 创造了一个新品类叫「Prompt 管理」——你是做品类第一，还是等别人做？ |

### 8.4 YouTube 来源（3 个）

| # | 项目 | 类型 | 一句话 |
|---|------|------|--------|
| 8 | **Paperclip** | 工作流 | 一个开源 Agent 编排平台。不是让你写 Agent，而是让你像招聘员工一样 hire Agent。 |
| 9 | **OpenClaw** | 工作流 | Fireship 讲述一个开源 AI 编码平台从个人项目到 23 万 Stars 的崛起故事。 |
| 10 | **7 New Open Source AI Tools** | 创意工具 | Fireship 盘点 7 个新开源 AI 工具，从代码助手到视频生成，每个几分钟就能上手。 |

---

## 9. 数据格式

### 9.1 projects.json 数据结构

> 注：`category` 决定分类归属（Extension / Creative / Workflow）。
> `tags` 为扁平数组，直接渲染在卡片上。`config.py` 中定义了三维标签体系（form/scene/tech），
> 但目前前端只用 tags 平铺展示，三维体系可用于未来分析维度扩展。

```json
{
  "id": "{project-slug}-{date}",
  "title": "项目名称",
  "url": "GitHub 或 YouTube 链接",
  "source": "GitHub | YouTube",
  "category": "chrome-extension | creative | workflow",
  "description": "一句话简介",
  "tags": ["Chrome 插件", "To C", "LLM", "..."],
  "date": "YYYY-MM-DD",
  "analysis": {
    "pain_point": "痛点描述（支持 <mark> 关键词高亮）",
    "why_ai": "为什么是 AI？为什么是现在？（支持 <mark>）",
    "insight": "产品思维拆解。第一句话用 %% 标记 Key Insight 截断点",
    "transfer": "由此及彼：这个思维还能用在别处吗？（支持 <mark>）"
  }
}
```

### 9.2 localStorage 数据结构

```json
// 收藏数据 — key: "ai-inspiration-favs"
[
  { "id": "writely-20260620", "addedAt": "2026-06-20" },
  { "id": "dashplayer-20260620", "addedAt": "2026-06-21" }
]

// 主题偏好 — key: "ai-inspiration-theme"
"dark" | "light"
```

### 9.3 config.json 结构

```json
{
  "youtube_api_key": "YOUR_YOUTUBE_DATA_API_V3_KEY"
}
```

> ⚠️ 此文件包含 API 密钥，切勿提交到公开仓库。

---

## 10. 后续规划（Phase 2+）

| 功能 | 优先级 | 说明 |
|------|--------|------|
| Builder Digest tab | 中 | 灵感簿页面新增「Builder Digest」tab，展示 follow-builders 26 位 builder 的推文摘要流 |
| GitHub Pages 公开发布 | 🔨 进行中 | 推送到 GitHub 仓库，开启 Pages；手机浏览器可直接访问 |
| 邮件 / 微信推送 | 低 | 通过 Resend 定期推送简报，或接入微信服务号 |
| 收藏夹分类筛选 | 低 | 收藏弹窗内增加分类选项卡（Extension / Creative / Workflow） |
| YouTube 网页抓取路线 | 低 | 优化 fetch_youtube_test.py，实现无 API Key 的高精度采集 |
| 三维标签前端 | 低 | 将 config.py 的 form/scene/tech 维度接入卡片 UI |
| follow-builders 名单扩展 | 低 | 按需提交 PR 到 follow-builders 仓库，增加关注的中国 AI builder |

---


---

## 11. 部署方案（GitHub Pages）

### 11.1 目标

通过 GitHub Pages 生成一个公有 URL，让自己在任何设备（手机/平板/电脑）的浏览器上直接访问灵感簿。

### 11.2 部署地址

`https://{GitHub用户名}.github.io/ai-inspiration-notebook/`

### 11.3 部署步骤

1. **创建 `.gitignore`** — 保护敏感文件
   - 排除：`config.json`（含 YouTube API Key）
   - 排除：`data/raw/`、`data/backups/`、`__pycache__/`、`*.pyc`、`scripts/__pycache__/`
   - 保留：`index.html`、`data/projects.json`、`assets/`、`scripts/`（可选）
2. **创建 GitHub 远程仓库** — 在 github.com 新建 repo（建议命名 `ai-inspiration-notebook`）
3. **关联远程并推送** — `git remote add origin {repo-url}` → `git push -u origin main`
4. **开启 GitHub Pages** — 仓库 Settings → Pages → Source: `main` 分支, `/ (root)` 目录 → Save
5. **等待 1-2 分钟** — GitHub 自动构建部署，完成后即可访问

### 11.4 安全红线

- ⚠️ **`config.json` 绝对不能推送** — 内含 YouTube API Key，必须在 `.gitignore` 第一行就排除
- 建议推送前执行 `git status` 二次确认 `config.json` 不在暂存区
- 如果 Key 曾经被推送到公开仓库：立即到 Google Cloud Console 吊销该 Key 并重新生成

### 11.5 推送内容决策

| 文件/目录 | 是否推送 | 原因 |
|-----------|---------|------|
| `index.html` | ✅ 推送 | 核心页面 |
| `data/projects.json` | ✅ 推送 | 项目归档数据 |
| `assets/` | ✅ 推送 | CSS + JS |
| `README.md` | ✅ 推送 | 项目说明 |
| `scripts/` | ⚠️ 可选 | 推送则别人可见搜索逻辑；不推送不影响页面运行 |
| `config.json` | ❌ 严禁 | YouTube API Key |
| `data/raw/` | ❌ 不推送 | 原始采集数据 |
| `data/backups/` | ❌ 不推送 | 页面备份 |
| `__pycache__/`、`*.pyc` | ❌ 不推送 | 编译缓存 |


### 11.6 GitHub Actions 自动部署

每次采集线程跑完 → 页面生成后，自动触发 GitHub Actions 将最新 `index.html` 和 `data/projects.json` 推送到仓库 → GitHub Pages 自动重新部署。

**触发条件**：采集 Agent 完成采集+分析+入库+页面生成后，触发部署 workflow

**workflow 流程**：
1. checkout 仓库
2. 复制最新 `index.html`、`data/projects.json`、`data/raw/` 当天目录到工作区
3. `git commit` + `git push`
4. GitHub Pages 检测到 main 分支更新 → 自动重新部署（1-2 分钟）

**用户侧效果**：用户打开同一个 URL，刷新即可看到当天最新内容。无需下载、无需安装、无需任何操作。

**安全红线**：
- `config.json` 已在 `.gitignore` 排除，不会被推送
- GitHub Pages 部署的是 `index.html` 静态文件，不含任何 API Key 或敏感数据
## 12. 已知技术决策、约束与环境信息

1. **Python 运行时**：3.12.13（通过 Codex 捆绑），无需额外安装
2. **Node.js 运行时**：v24.16.0（通过 Codex 捆绑）
3. **GitHub API 限制**：未认证时 60 次/小时，当前足够日常使用
4. **npm 不可用**：需通过 `pnpm.cmd` 安装 Node 包（当前无 Node 依赖需求）
5. **页面无服务器依赖**：纯静态 `file://` 直接打开，localStorage 在 `file://` 协议下正常
6. **收藏数据存储于浏览器**：换设备或清缓存后丢失（纯前端的固有限制）
7. **分析文案由 Codex LLM 辅助生成，人工审查定稿**：非全自动，保证分析质量
8. **自动化调度**：采集 Agent 已配置 48 小时定时触发；GitHub Actions 自动部署待实现
9. **数据管线**：GitHub / YouTube / X 由 AI 自动采集 + 筛选 + 排优先级；小红书 / B 站由用户手动丢链接触发
10. **YouTube 采集依赖 API Key**：已配置在 `config.json`，备用 `fetch_youtube_test.py` 提供无 Key 抓取路线；X/Twitter 通过 follow-builders feed 获取，无 API Key 依赖

---

### 12.1 当前实现与 PRD 的已知差距（待研发跟进）

| 差距 | 详情 | 影响 | 优先级 |
|------|------|------|--------|
| GitHub/YouTube 搜索策略未更新 | `fetch_github.py` 和 `fetch_youtube.py` 仍使用旧 query（如 `llm application`、`gpt app`），未同步 PRD 2.2 / 2.3 的新策略 | 采集质量低于 PRD 预期 | 🔴 高 |
| 三平台跨天去重缺失 | GitHub/YouTube 采集器均未对比上一次采集数据去重，隔天运行可能返回重复项目 | 推荐清单出现重复内容 | 🟡 中 |
| Builder Digest 中文翻译 | 推文需增加简体中文翻译（`text_zh` 字段），在 `fetch_twitter.py` 采集阶段由 AI 翻译 | Builder Digest 当前仅显示英文原文 | 🟡 中 |


## 13. 典型工作流

### 13.1 每日节奏

| 时间 | 动作 | 负责方 |
|------|------|--------|
| 08:30 | `fetch_all.py` 自动采集 GitHub + YouTube（或手动触发） | 系统 / 研发 |
| 08:35 | AI 自动筛选 + 排优先级，生成推荐清单 | 系统 |
| 08:40 | 产品经理审阅推荐清单，确认入选项目 | 产品经理 |
| 08:45 | AI 编写分析文案（按 PRD §3.1 语言标准），入库 `projects.json` | 系统 |
| 08:50 | `generate_page.py` 生成当天第一版 `index.html` | 系统 |
| 白天 | 产品经理随时甩小红书/B 站链接 → 提取 → 审批 → 追加入库 → 重新生成 | 产品经理 + 系统 |

### 13.2 自动采集日（隔天）

```
08:30  python scripts/fetch_all.py        # AI 自动采集 GitHub + YouTube
08:35  AI 自动筛选 + 排优先级 → 推荐清单    # AI 初筛，产品经理审阅确认
08:40  确认入选 → AI 编写分析 → 定稿入库     # 协作完成分析文案（PRD §3.1 标准）
08:50  node scripts/generate_page.js     # 生成页面 + 自动备份 + JS 校验
09:00  打开 index.html 查看效果             # 或刷新 GitHub Pages
```

### 13.3 手动链接追加（任意时间）

```
收到链接 → content-extractor 提取内容（按 content-filter-rules.md 判断）
         → 信息充分？→ 产品经理审批 → AI 编写分析文案 → 入库 projects.json
         → node scripts/generate_page.js → 重新生成页面
         → 信息不足？→ 直接告知产品经理「这条不行 + 原因」
```

> 手动链接追加不会覆盖当天自动采集已入库的项目。`projects.json` 是不断增长的列表，每次 `generate_page.py` 渲染全部项目。

---

## 14. 版本记录

| 版本 | 日期 | 核心变更 |
|------|------|----------|
| v1.0 | 2026-06-20 | 初版上线：10 个 GitHub 项目、基础卡片交互、3 分类 |
| v1.5 | 2026-06-21 凌晨 | 收藏系统、暗色模式、卡片展开/收起、入场动效、高亮标注 |
| v2.0 | 2026-06-21 | YouTube 源上线（3 个项目）、fetch_all 调度器、备份回滚机制、PRD 全面重构 |
