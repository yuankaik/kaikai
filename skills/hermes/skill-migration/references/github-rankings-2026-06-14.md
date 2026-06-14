# GitHub 排名扫描与技能评估实录

日期：2026-06-14 | 扫描范围：⭐515K → 32K（~1,000 个仓库）

## 批量并行分析模式

对于一次发现多个候选仓库，用 `delegate_task` 并行分析：

```python
delegate_task(tasks=[
    {"goal": "分析 repo A，判断可迁移性", "context": "...", "toolsets": ["browser"]},
    {"goal": "分析 repo B，判断可迁移性", "context": "...", "toolsets": ["browser"]},
    {"goal": "分析 repo C，判断可迁移性", "context": "...", "toolsets": ["browser"]},
])
```

每个子 Agent 返回：repo 内容摘要 + 可迁移性判断 + 草稿 SKILL.md。

## 本次评估结果速查

| 排名 | 仓库 | ⭐ | 迁移结果 |
|------|------|-----|----------|
| 34 | DigitalPlatDev/FreeDomain | 178K | ❌ 文档站，无技能价值 |
| 36 | avelino/awesome-go | 175K | ✅ awesome-go-reference |
| 37 | multica-ai/andrej-karpathy-skills | 175K | ✅ karpathy-coding-guidelines |
| 44 | f/prompts.chat | 164K | ✅ awesome-chatgpt-prompts |
| 46 | jlevy/the-art-of-command-line | 161K | ✅ command-line-art |
| 50 | anthropics/skills | 150K | ✅ anthropics-skills-catalog + mcp-builder |
| 51 | langflow-ai/langflow | 150K | ❌ 依赖爆炸，待 Docker |
| 64 | firecrawl/firecrawl | 132K | ✅ firecrawl-web-scraping |
| 67 | mattpocock/skills | 128K | 📋 待评估 |
| 82 | Shubhamsaboo/awesome-llm-apps | 114K | ✅ awesome-llm-apps |
| 87 | msitarzewski/agency-agents | 113K | ✅ agency-agents |
| 91 | garrytan/gstack | 110K | ✅ gstack (55技能) |
| 113 | farion1231/cc-switch | 100K | 📋 待评估 |
| 116 | browser-use/browser-use | 99K | 📋 待评估 |
| 132 | ui-ux-pro-max-skill | 91K | ❌ Claude专属，需转换 |
| 139 | punkpeye/awesome-mcp-servers | 89K | ✅ awesome-mcp-servers |
| 149 | MoneyPrinterTurbo | 87K | ❌ 独立应用，已有替代 |
| 153 | karpathy/autoresearch | 87K | ✅ autoresearch |
| 170 | thedotmack/claude-mem | 82K | ⏳ 代理问题，待安装 |
| 250 | unclecode/crawl4ai | 68K | ❌ lxml编译失败 |
| 278 | awesome-claude-skills | 64K | 📋 待评估 |
| 296 | scrapy/scrapy | 62K | ❌ 太重，已有替代 |
| 325 | karpathy/nanoGPT | 60K | ❌ 教学项目 |
| 342 | mem0ai/mem0 | 59K | ✅ 已安装 |
| 348 | zylon-ai/private-gpt | 57K | ❌ 功能重叠 |
| 357 | worldmonitor | 56K | ❌ RSS阅读器 |
| 415 | MediaCrawler | 51K | ⏳ 克隆超时 |
| 593 | danielmiessler/Fabric | 42K | ❌ 独立CLI工具 |
| 597 | GitNexus | 42K | ⏳ npm代理问题 |
| 598 | system_prompts_leaks | 42K | ✅ 已克隆 |

## 失败模式速查

| 失败类型 | 表现 | 原因 |
|----------|------|------|
| 依赖爆炸 | pip 解析超时 | langflow 几百个依赖 |
| 编译失败 | lxml gcc 错误 | Python 3.14 兼容性 |
| 代理超时 | curl/wget/npm 卡住 | 代理只通 git |
| npm ECONNREFUSED | proxy 127.0.0.1:56666 | 代理服务不稳定 |

## 用户偏好（kai哥）

- 每批 30-100 个快速浏览，挑亮点
- 先评估再安装，不盲目全装
- 特别关注：办公软件（Excel/PPT/PDF）、Agent 技能、爬虫工具
- 网络代理限制下，git 可用但 curl/npm 不稳定
