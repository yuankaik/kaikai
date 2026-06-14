---
name: claude-mem
description: 跨会话持久记忆系统 (82K⭐)——记录 Agent 每次操作，压缩存储，下次会话自动注入上下文。支持 Hermes (MCP)。搜索、时间线、观察者三层渐进式查询。
source: https://github.com/thedotmack/claude-mem
---

# Claude-Mem — 跨会话记忆

让你的 Hermes 拥有"长期记忆"。记录每次会话的所有操作，压缩存储，下次自动回忆。

## 安装

```bash
npx claude-mem install

# 如果 npx 超时（网络代理环境），加 proxy：
npm_config_proxy=http://127.0.0.1:56666 npx claude-mem install

curl http://localhost:37777/api/health  # 验证
```

Web 查看器: http://localhost:37777

## 在 Hermes 中使用

通过 MCP 连接 claude-mem 的搜索工具：

### 三层渐进式查询（省 token）

**Layer 1: 搜索**（~50-100 tokens）
```
search "authentication bug" → 匹配列表
```

**Layer 2: 时间线**（上下文）
```
timeline anchor=12345 → 前后各3条
```

**Layer 3: 详情**（~500-1000 tokens）
```
get_observations ids=[12345,12346]
```

### 会话生命周期

**开始时** — 自动提取最近上下文注入当前对话：
```
GET /api/context/recent?project=my-project
```

**结束时** — 记录重要发现：
```
POST /api/sessions/observations
{"note": "做了什么", "summary": "完成了什么"}
```

## 支持的工具

| Agent | 集成方式 |
|-------|---------|
| Claude Code | 完整 hooks + MCP |
| Codex | 原生 hooks |
| Gemini CLI | 完整 hooks |
| **Hermes** | **MCP 工具** |
| Cursor/Windsurf/Copilot | MCP/hooks |

## 存储架构

- SQLite: 会话、观察、摘要
- Chroma 向量库: 语义搜索
- FTS5: 全文搜索
- 混合搜索: 精准 + 语义

## 触发场景

- "我们之前怎么解决的？"
- "上次那个 bug 怎么修的？"
- "帮我查历史记录"
- 新会话开始时自动注入上下文
