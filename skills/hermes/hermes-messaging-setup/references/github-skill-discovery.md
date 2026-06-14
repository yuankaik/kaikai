# GitHub 技能发现与迁移模式

本会话中建立的从 GitHub 热门仓库发现和迁移技能的流程。

## 排名浏览

### 快翻模式（kai哥偏好：一次 30 个）

```bash
# 快翻：一次 3 页，一行输出
for p in $PAGE $((PAGE+1)) $((PAGE+2)); do
  curl -s "https://api.github.com/search/repositories?q=stars:%3E1&sort=stars&order=desc&per_page=10&page=$p" \
    | python3 -c "
import json,sys
start = $START + ($p-$PAGE)*10
data=json.load(sys.stdin)
for i,r in enumerate(data.get('items',[]), start):
    s=r['stargazers_count']
    n=r['full_name']
    d=(r.get('description') or 'N/A')[:95]
    print(f'{s:>6,}  {n}     {d}')
"
done
```

### 精准模式（需要 description 时）

```bash
# 用 python3 -c 脚本完整输出
curl -s "https://api.github.com/search/repositories?q=stars:%3E1&sort=stars&order=desc&per_page=10&page=$PAGE" \
  | python3 -c "
import json, sys
data = json.load(sys.stdin)
for i, r in enumerate(data.get('items', []), start_num):
    print(f'{i:3}. ⭐ {r[\"stargazers_count\"]:>6,}  {r[\"full_name\"]}')
    print(f'     [{r.get(\"language\",\"\")}] {(r.get(\"description\") or \"N/A\")[:120]}')
    print()
"
```

## 分析仓库

当 curl 超时（proxy 限制），用浏览器兜底：

```python
# 导航到 raw README
browser_navigate("https://raw.githubusercontent.com/user/repo/main/README.md")
# 提取全文
content = browser_console(expression="document.body.innerText")
# 或导航到 GitHub 页面读取文件树
browser_navigate("https://github.com/user/repo/tree/main/skills")
```

## 有价值的技能信号

| 信号 | 示例 | 优先度 |
|------|------|--------|
| 原生 Hermes 支持 | `hosts/hermes.ts`, `--host hermes` | 🔥🔥🔥 |
| Agent 人格/提示词库 | anthropics/skills, agency-agents | 🔥🔥🔥 |
| 可运行 AI 应用 | awesome-llm-apps | 🔥🔥 |
| 系统提示词合集 | system-prompts-and-models | 🔥🔥 |
| Claude Code 工具 | gstack, mattpocock/skills | 🔥🔥 |
| 领域参考库 | awesome-go, the-art-of-command-line | 🔥 |
| 精选提示词 | prompts.chat | 🔥 |
| 通用工具/API | firecrawl | 🔥 |

## 迁移步骤

1. **分析** → 用 delegate_task 并行探索多个仓库
2. **提取** → 抓取 README、SKILL.md、关键代码
3. **判断** → 问三个问题：
   - 这是技能还是独立应用？（独立应用如 langflow 需要 Docker，不直接迁移）
   - 已有技能覆盖了吗？（如 crawl4ai vs firecrawl 功能重叠，但互补装）
   - 用户真有这需求吗？（如 scrapy 太重，跳过）
4. **创建** → `skill_manage(action='create', ...)` 写入 ~/.hermes/skills/
5. **备份** → `rsync + git push` 推送到 GitHub 仓库

## 拒绝模式（kai哥的决策习惯）

| 类型 | 示例 | 理由 |
|------|------|------|
| 学习项目 | nanoGPT | 教学用，不是日常技能 |
| 太重框架 | Scrapy | 工程级，AI Agent 有更轻替代 |
| 功能重叠 | crawl4ai vs firecrawl | 已有同类，除非互补 |
| 独立应用 | langflow, MoneyPrinterTurbo | 需 Docker/独立环境 |
| 纯文档 | HowToCook, free-programming-books | 无程序化价值 |
| 不是技能 | DigitalPlatDev/FreeDomain | 域名服务文档站 |

## 本会话已迁移的技能

| # | 仓库 | 技能名 |
|---|------|--------|
| 36 | avelino/awesome-go | awesome-go-reference |
| 37 | multica-ai/andrej-karpathy-skills | karpathy-coding-guidelines |
| 44 | f/prompts.chat | awesome-chatgpt-prompts |
| 46 | jlevy/the-art-of-command-line | command-line-art |
| 50 | anthropics/skills | anthropics-skills-catalog, mcp-builder |
| 64 | firecrawl/firecrawl | firecrawl-web-scraping |
| 82 | Shubhamsaboo/awesome-llm-apps | awesome-llm-apps |
| 87 | msitarzewski/agency-agents | agency-agents |
| 91 | garrytan/gstack | gstack (55 skills via setup) |
| 139 | punkpeye/awesome-mcp-servers | awesome-mcp-servers |
| 153 | karpathy/autoresearch | autoresearch |
| 170 | thedotmack/claude-mem | claude-mem |
| 250 | unclecode/crawl4ai | crawl4ai |
| 342 | mem0ai/mem0 | mem0 |
| 415 | NanmiCoder/MediaCrawler | mediacrawler |

## GStack 原生安装模式

GStack 是第一个支持 `--host hermes` 的原生安装工具。完整流程：

```bash
# 1. 安装 bun（npm 代理方式）
npm install -g bun --proxy http://127.0.0.1:56666

# 2. 克隆
git clone --depth 1 https://github.com/garrytan/gstack.git ~/.hermes/skills/gstack

# 3. 生成 Hermes 技能
cd ~/.hermes/skills/gstack && ./setup --host hermes
# 输出：GENERATED: .hermes/skills/gstack-*/SKILL.md (55 files)
```

**关键发现：**
- GStack 有自己的 `hosts/hermes.ts` 配置文件，自动处理工具名重写（Bash→terminal, Write→patch, Agent→delegate_task）
- 技能模板 `.tmpl` 编译为 `SKILL.md`，不要手动编辑生成的文件
- bun 是硬依赖，不能用 npm/npx 替代

## Claude-Mem 安装注意事项

- `npx claude-mem install` 首次下载大（可能超时），推荐用 npm 代理
- Hermes 只能通过 MCP 工具方式接入（没有 hook 系统）
- 安装后需手动配置 Hermes MCP 连接 claude-mem 的搜索服务器
