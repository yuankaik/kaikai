# GitHub 技能发现与迁移模式

本会话中建立的从 GitHub 热门仓库发现和迁移技能的流程。

## 排名浏览

```bash
# 每页 10 个，从第 N 页开始
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
3. **创建** → `skill_manage(action='create', ...)` 写入 ~/.hermes/skills/
4. **备份** → 推送到 GitHub 仓库作为持久备份

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
