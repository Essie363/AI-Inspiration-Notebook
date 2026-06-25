# Implementation Reference

> 生成时间：2026-06-23
> 规则：后续任何代码改动，都需同步更新此文档。

---

## 数据采集脚本 (Python)

### `scripts/config.py`
**用途**：读取 `config.json` 中的 API Key 和配置参数。
- 无导出函数 — 全局变量：`CONFIG` 字典

### `scripts/fetch_all.py`
**用途**：总调度器，依次调用 GitHub / YouTube / X 三个采集脚本，运行全量采集并 save raw。
| 函数 | 行号 | 说明 |
|------|------|------|
| `run()` | L12 | 入口：依次执行三平台采集 |

### `scripts/fetch_github.py`
**用途**：调用 GitHub Search API，按 6 组 query 搜索 AI 相关仓库。
| 函数 | 行号 | 说明 |
|------|------|------|
| `compute_pushed_after(days_back)` | L21 | 计算时间窗口起始时间 |
| `search_repos(query, sort, per_page)` | L26 | 单次 GitHub Search API 调用 |
| `is_ai_related(repo)` | L40 | 判断仓库是否与 AI 相关（关键词匹配） |
| `load_previous_full_names()` | L55 | 读取上次采集结果，用于去重 |
| `fetch_all()` | L71 | 主逻辑：遍历 6 组 query，合并去重 |
| `save_raw(projects)` | L110 | 写 `data/raw/YYYY-MM-DD/github.json` |
| `run()` | L120 | 入口 |

### `scripts/fetch_twitter.py`
**用途**：从 follow-builders skill 的 `feed-x.json` 读取推文，支持增量拉取 + 翻译。
| 函数 | 行号 | 说明 |
|------|------|------|
| `load_feed()` | L16 | 读取 follow-builders 的 state-feed.json |
| `extract_tweets(feed_data, limit_per_builder)` | L24 | 提取推文，按 builder 分组，支持 since_id |
| `save_results(tweets)` | L67 | 写 `data/raw/YYYY-MM-DD/x.json` |
| `run()` | L76 | 入口 |

### `scripts/fetch_youtube.py`
**用途**：调用 YouTube Data API v3，按 6 组 query 搜索 AI 产品相关视频。
| 函数 | 行号 | 说明 |
|------|------|------|
| `load_api_key()` | L47 | 从 config.json 读取 API Key |
| `search_videos(api_key, query, order, max_results, days_back)` | L54 | 单次 YouTube API 搜索 |
| `get_video_stats(api_key, video_ids)` | L92 | 批量获取视频播放/点赞数据 |
| `is_ai_related(title, desc)` | L117 | 判断视频是否与 AI 相关 |
| `load_previous_video_ids()` | L127 | 读取上次采集结果去重 |
| `save_results(videos)` | L143 | 写 `data/raw/YYYY-MM-DD/youtube.json` |
| `run()` | L152 | 入口 |

### `scripts/fetch_youtube_test.py`
**用途**：无 API Key 的 YouTube 备用路线（网页抓取）。
| 函数 | 行号 | 说明 |
|------|------|------|
| `search_youtube(query, max_results)` | L16 | 抓取 YouTube 搜索结果页解析 |
| `run()` | L74 | 入口 |

### `scripts/search_small_projects.py`
**用途**：二次补充搜索小团队/独立开发者 AI 项目（辅助采集）。
- 无独立函数定义

### `scripts/translate_tweets.py`
**用途**：对 fetch_twitter 采集的推文生成简体中文翻译，写入 `text_zh` 字段。
| 函数 | 行号 | 说明 |
|------|------|------|
| `prepare()` | L26 | 读取最新 x.json，调用 LLM 翻译 |
| `apply()` | L80 | 回写 x.json |

### `scripts/fix_js.py` / `scripts/fix_tabs.py`
**用途**：一次性修复脚本（页面 JS 语法修复 / tab 栏修复），已不再使用。

---

## 页面生成脚本

### `scripts/generate_page.js` (主要)
**用途**：读取 `projects.json` + BuilderPulse 蒸馏版 → 生成自包含 `index.html`。
| 函数 | 行号 | 说明 |
|------|------|------|
| `card(p, idx)` | L36 | 生成单张产品卡片 HTML |
| `parseMdToHtml(md)` | L128 | Markdown 转 HTML（用于 Opportunities） |
| `seedRandom(seed)` | L251 | 确定性伪随机数生成器 |
| `shuffle(arr, seed)` | L255 | 基于种子的数组混排 |

**自动备份 + JS 校验**（行号在文件末尾）：
- 每次生成后备份到 `data/backups/`
- 清理 7 天前的旧备份
- 抽取 `<script>` 内容跑 `node --check`，出错自动回退最近备份

### `scripts/generate_page.py` (已废弃)
**用途**：旧版 Python 页面生成器。已禁用——存在中文编码 bug，由 `generate_page.js` 替代。

---

## 前端交互脚本

### `assets/script.js`
**用途**：页面运行时交互逻辑。所有函数均为全局函数。
| 函数 | 行号 | 说明 |
|------|------|------|
| `toggleTheme()` | L9 | 亮/暗色主题切换 |
| `loadFavorites()` | L21 | 从 localStorage 读取收藏列表 |
| `saveFavorites(f)` | L26 | 保存收藏列表到 localStorage |
| `isFavorited(pid)` | L28 | 检查项目是否已收藏 |
| `toggleFavorite(btn)` | L36 | 点击收藏按钮，增/删收藏 |
| `updateCardUI(card, isFav)` | L51 | 更新卡片的收藏状态 UI |
| `restoreFavorites()` | L61 | 页面加载后恢复所有收藏状态 |
| `expandCard(card)` | L70 | 展开卡片详情 |
| `collapseCard(card)` | L75 | 收起卡片详情 |
| `filterCategory(btn, category)` | L85 | 按分类筛选卡片（All/Extensions/Creative/Workflow） |
| `openFavModal()` | L100 | 打开收藏弹窗 |
| `closeFavModal()` | L138 | 关闭收藏弹窗 |
| `unfavFromModal(pid)` | L143 | 从收藏弹窗中取消收藏 |
| `switchChannel(btn, channel)` | L207 | 频道切换入口 |
| `setChannel(channel, btn)` | L214 | 频道切换核心逻辑（显示/隐藏 + 滚动位置保存） |
| `switchToTimeline(btn)` | L250 | 旧版 Builder Digest 切换（已废弃） |

**初始化模块** (IIFE)：
| 模块 | 行号 | 说明 |
|------|------|------|
| 主题恢复 | L2 | 页面加载时从 localStorage 恢复主题 |
| 粘性 Tabs | ~L175 | IntersectionObserver 检测滚动，tabs 吸顶 + 阴影 |
| 频道恢复 | ~L285 | 页面加载时从 localStorage 恢复上次频道 |
| Builder Digest 导航 | ~L294 | IntersectionObserver + 点击平滑滚动 |
| Opportunities 导航 | ~L350 | IntersectionObserver + 点击平滑滚动 |

### `assets/style.css`
**用途**：全站视觉样式。按区域分块：

| 区块 | 行号 | 说明 |
|------|------|------|
| Variables | L1 | CSS 自定义属性（颜色、字体） |
| Header | L62 | 标题栏 + meta 信息 + 主题按钮 |
| Channel Switcher | L90 | 频道切换按钮栏 |
| Tabs | L126 | 分类标签栏（sticky + 阴影） |
| Timeline Layout | L146 | Builder/Opportunities 双栏布局 |
| Builder Digest Timeline | L220 | 时间线流 + 头像 + 推文项 |
| Card Grid | L336 | 卡片网格 |
| Card | L346 | 单张产品卡片 |
| Mark Highlight | L473 | `<mark>` 标签莫兰迪黄色高亮 |
| Full Analysis | L446 | 卡片展开分析区 |
| Favorites Modal | L535 | 收藏弹窗 |
| Opportunities Channel | L670 | Opportunities 内容区 |
| Opportunities Sidebar Nav | L807 | 左侧导航 + 日期分组 |

字体规范：全站统一六级阶梯 12/13/14/15/18/22px，Serif→标题+正文，Sans→UI+标签。

---

## 自动化部署

### `.github/workflows/deploy.yml`
**用途**：GitHub Actions 自动部署到 Pages。支持 `workflow_dispatch`（手动）+ `repository_dispatch`（采集 Agent API 触发）。流程 checkout → force-add 关键文件 → commit → push。
