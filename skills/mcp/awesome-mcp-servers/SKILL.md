---
name: awesome-mcp-servers
description: MCP 服务器黄页——2,627 个服务器，51 个分类。来自 punkpeye/awesome-mcp-servers (89K⭐)。搜索 MCP 工具时不靠猜，从社区维护的权威列表查找。
source: https://github.com/punkpeye/awesome-mcp-servers
---

# Awesome MCP Servers

2,627 个 MCP (Model Context Protocol) 服务器，51 个分类。找到合适的 MCP 工具来拓展 Hermes 的能力边界。

## 使用方式

```
https://github.com/punkpeye/awesome-mcp-servers
```

浏览分类，Ctrl+F 搜索关键词。

## 重点分类速查

### 🌐 浏览器自动化 (61)
- `microsoft/playwright-mcp` — 微软官方 Playwright MCP
- `browserbase/mcp-server-browserbase` — 云端浏览器
- `browsermcp/mcp` — 控制本地 Chrome

### 🔍 代码搜索与理解
- `st3v3nmw/sourcerer-mcp` — 语义代码搜索，减少 token 浪费
- `SimplyLiz/CodeMCP` — 80+ 工具：语义搜索、调用图、影响分析
- `admica/FileScopeMCP` — 代码库依赖关系分析

### 🖥️ 代码执行 (17)
- `pydantic/pydantic-ai/mcp-run-python` — Python 沙箱
- `yepcode/mcp-server-js` — JS/Python 沙箱

### 📁 文件系统 (29)
- `modelcontextprotocol/server-filesystem` — 直接文件系统访问
- `microsoft/markitdown` — 任意格式转 Markdown

### 🐙 Git (20)
- `idosal/git-mcp` — 远程操作 GitHub 仓库
- `narumiruna/gitingest-mcp` — 仓库→文本摘要

### 🧠 知识记忆 (202)
- 记忆持久化、RAG 连接器、项目上下文管理

### 🗄️ 数据库 (110)
- PostgreSQL、MySQL、SQLite、Redis 等 MCP 连接器

### 🔒 安全 (151)
- 漏洞扫描、渗透测试工具

### 📊 监控 (60)
- Prometheus、Grafana、日志分析

### ☁️ 云平台 (85)
- AWS、GCP、Azure、Vercel、Cloudflare

### 💬 通讯 (97)
- Slack、Discord、Telegram、邮件

### 🏢 办公效率 (74)
- Notion、Google Workspace、Airtable、Jira

## 安装 MCP 服务器

Hemes 支持通过 `native-mcp` 技能连接 MCP 服务器：

```bash
# 示例：安装 Playwright MCP
npx @anthropic/mcp-server-playwright

# Python MCP
pip install mcp-server-xxx
```

## 技巧

1. **语义搜索优先** — `sourcerer-mcp` 能理解代码含义，比 grep 强
2. **用沙箱跑代码** — 不要直接在 Hermes 环境执行
3. **浏览器自动化** — Playwright MCP 比内置 browser 工具更强
4. **按需加载** — 不要同时连太多 MCP，选 3-5 个最需要的
