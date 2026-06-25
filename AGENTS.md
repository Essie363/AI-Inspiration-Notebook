# AGENTS.md — AI-Inspiration-Notebook

## 协作规则（所有 Agent 必须遵守）

1. 先读 `_系统/通信录.md`，确认协作方线程 ID
2. 跨 Agent 消息用 `send_message_to_thread` 工具发送，不在对话里打字
3. 每条消息带 `REQ-YYYYMMDD-NNN`（派发方生成，回报方引用，序号每日从 001 重置）
4. 消息格式：📋 派发 / ✅ 完成 / ⚠️ 退回 / 🎉 验收通过，均标注「记录于: _系统/工作日志/YYYY-MM-DD_角色.md」
5. 每轮协作后在 `_系统/工作日志/` 追加 `[HH:MM] [动作] REQ-ID — 内容 — 结果`
6. 完整指令见各角色 `.agents/` 目录

## 角色分工

| 角色 | 线程 | 核心职责 |
|------|------|---------|
| 产品经理 | `019eea61` | 审批→分析→维护PRD→派发→验收 |
| 产品研发 | `019eea72` | 读PRD→实现→commit→回报 |
| 采集Agent | `019ef08b` | fetch_all→初筛→候选清单→通知PM |

## 项目文档索引

- PRD（核心规约）：`_system/planning/PRD.md`
- 实现细节：`_system/docs/specs.md`
- 函数索引：`_system/docs/implementation.md`
- 项目复盘：`LESSONS.md`
- 内容过滤规则：`_system/content-filter-rules.md`

## 关键约束

- PM 不写代码，研发不审批，采集不分析
- 验收只看浏览器实际效果，不认「代码已改」
- config.json 永不上传，API Key 不泄露
- 语言风格：平实直白讲因果，禁止 PPT 黑话
