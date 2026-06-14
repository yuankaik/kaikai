# GitHub 热门仓库排名速查 (2026-06-14)

## 已确认可迁移的技能

| 排名 | 仓库 | ⭐ | Hermes 技能名 | 状态 |
|------|------|-----|-------------|------|
| 25 | NousResearch/hermes-agent | 193K | hermes-agent | 正在用 |
| 36 | avelino/awesome-go | 175K | awesome-go-reference | ✅ |
| 37 | multica-ai/andrej-karpathy-skills | 175K | karpathy-coding-guidelines | ✅ |
| 44 | f/prompts.chat | 164K | awesome-chatgpt-prompts | ✅ |
| 46 | jlevy/the-art-of-command-line | 161K | command-line-art | ✅ |
| 50 | anthropics/skills | 150K | anthropics-skills-catalog + mcp-builder | ✅ |
| 51 | langflow-ai/langflow | 150K | — | ❌ 依赖太多 |
| 57 | x1xhlol/system-prompts-and-models | 140K | — | ⏳ 待网络 |
| 64 | firecrawl/firecrawl | 132K | firecrawl-web-scraping | ✅ |
| 82 | Shubhamsaboo/awesome-llm-apps | 114K | awesome-llm-apps | ✅ |
| 87 | msitarzewski/agency-agents | 113K | agency-agents | ✅ |
| 91 | garrytan/gstack | 110K | gstack + 55 gstack-* | ✅ |
| 113 | farion1231/cc-switch | 100K | — | ⏳ 跨平台助手 |
| 116 | browser-use/browser-use | 99K | — | ⏳ |
| 132 | nextlevelbuilder/ui-ux-pro-max | 91K | — | ❌ Claude专属 |
| 139 | punkpeye/awesome-mcp-servers | 89K | awesome-mcp-servers | ✅ |
| 149 | harry0703/MoneyPrinterTurbo | 87K | — | ❌ 独立应用 |
| 153 | karpathy/autoresearch | 87K | autoresearch | ✅ |
| 170 | thedotmack/claude-mem | 82K | claude-mem | ✅ |
| 250 | unclecode/crawl4ai | 68K | crawl4ai | ✅ (lxml失败) |
| 278 | ComposioHQ/awesome-claude-skills | 64K | — | ⏳ |
| 342 | mem0ai/mem0 | 59K | mem0 | ✅ |

## 翻页进度

已翻完：1-810 名（逐页手动）+ API 全部 1000 条（100/页批量扫）
覆盖范围：⭐ 515K → 32K
当前 Hermes 技能总数：351

## 网络/安装失败记录

| 项目 | 失败原因 |
|------|----------|
| langflow | pip 依赖爆炸，需 Docker |
| crawl4ai | lxml 编译失败（Python 3.14） |
| MediaCrawler | git clone 超时 |
| claude-mem | npx 下载代理问题 |
| gitnexus | npm 代理连接被拒 |

## GitHub API 关键发现

- Search API 最多返回 1000 条结果（10 页 × 100 条）
- `stars:>40000` 约 800 个仓库，全在可翻范围内
- 100/页模式比 10/页快 10 倍，适合批量扫描
