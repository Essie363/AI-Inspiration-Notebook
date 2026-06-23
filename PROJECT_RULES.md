
## 数据写入禁令（2026-06-23 起）

PM 绝对禁止直接修改：data/projects.json、index.html。
原因：PM 侧写入曾导致中文编码丢失。

正确流程：
1. PM 审批候选项目后 → 通知研发加入 projects.json
2. 研发用 generate_page.js（UTF-8安全）写入数据 + 生成页面
3. 每次写入后自动备份 projects_backup.json

中文乱码排查：先查 projects.json → 坏了从 backup 恢复；没坏则 generate_page.js 有问题。