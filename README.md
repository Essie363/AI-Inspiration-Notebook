# AI Inspiration Notebook

每两天一期的小型 AI 产品研究笔记。从 GitHub / YouTube / BuilderPulse 中筛选值得关注的 AI 产品，用产品经理视角写分析。

## 内容

- **AI 灵感簿** — 产品卡片（痛点 / 为什么 AI / 产品洞见 / 可迁移思路）
- **Builder Digest** — 26 位一线 AI builder 的推文时间线
- **Opportunities** — BuilderPulse 每日行业信号简报

## 如何使用

直接打开 `index.html` 即可，无需服务器。也可托管到 GitHub Pages。

## 部署到 GitHub Pages

1. 创建 GitHub 仓库（建议 Private + GitHub Pages）
2. 上传以下文件（保持目录结构）：

```
├── index.html
├── assets/
│   ├── style.css
│   └── script.js
└── data/
    ├── projects.json
    └── raw/
        └── YYYY-MM-DD/
            └── x.json
```

3. Settings → Pages → Source: Deploy from a branch → 选择分支 → Save

## 更新方式

本项目由 Codex Agent 协作生成。新内容通过 `node scripts/generate_page.js` 编译为 `index.html` 后上传。

## 设计

Designed by Essie Zhang
