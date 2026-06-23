# AGENTS.md — AI-Inspiration-Notebook

## 协作协议（所有 Agent 必须遵守）

### 1. 先读通信录
每次开始工作前，先读 `_系统/通信录.md`，确认协作方的线程 ID。

### 2. 消息用工具发，不是打字
与其他 Agent 沟通时，**必须调用 `send_message_to_thread`** 工具发送消息。
❌ 在对话里打字说"我完成了" — 对方收不到
✅ 调用 `send_message_to_thread` 发送 — 对方线程会收到

### 3. Request ID 规则
每条跨 Agent 消息必须携带 `request_id`，格式：`REQ-YYYYMMDD-NNN`（如 `REQ-20260621-001`）。
派发方生成新 ID，回报方引用同一 ID。
序号从 001 开始，每个日历日重置。维护计数器文件 `_系统/.request_counter`（单行数字）。

### 4. SOP 消息格式

**派发任务：**
```
📋 REQ-YYYYMMDD-NNN
[简述内容]
→ 记录于: _系统/工作日志/YYYY-MM-DD_角色.md
```

**完成回报：**
```
✅ REQ-YYYYMMDD-NNN [动作]完成
[具体内容]
请验收。
→ 记录于: _系统/工作日志/YYYY-MM-DD_角色.md
```

**退回修改：**
```
⚠️ REQ-YYYYMMDD-NNN 验收未通过
问题：[具体列表]
请修复后重新回报。
```

**验收通过：**
```
🎉 REQ-YYYYMMDD-NNN 验收通过
本轮迭代完成。
```

### 5. 写工作日志
每轮协作后，在 `_系统/工作日志/` 下追加记录，行格式：
`[HH:MM] [动作] REQ-ID — 涉及内容 — 结果`

---

## 角色说明

### 产品经理（线程 `019eea61`）
完整指令见 `.agents/产品经理/AGENTS.md`
核心职责：审批候选 → 写分析 → 维护 PRD → 派发任务 → 验收

### 产品研发（线程 `019eea72`）
完整指令见 `.agents/产品研发/AGENTS.md`
核心职责：收到任务 → 读 PRD → 实现 → commit → **`send_message_to_thread` 回报**

### 采集Agent（线程待创建）
完整指令见 `.agents/采集Agent/AGENTS.md`
核心职责：运行 fetch_all.py → 接收手动链接 → 初筛排序 → 产出候选清单 → 通知 PM
