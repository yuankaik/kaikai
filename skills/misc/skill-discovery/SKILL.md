---
name: skill-discovery
description: 从外部来源发现和迁移技能——GitHub 星标排名搜索、浏览器 SPA 内容提取、批量跨生态迁移（Claude/Codex/Superpowers/Agents）。
---

# 技能发现与迁移

从 GitHub、其他 Agent 生态、文档站点中发现有价值的技能并迁移到 Hermes。

## 触发条件

- 用户问"有没有什么好技能"、"GitHub 上热门的是什么"
- 需要从 Claude/Codex/Superpowers/Agents 等生态迁移技能
- 需要批量搜索和评估外部资源

## 1. GitHub 星标排名搜索

### 快速翻页模式（推荐）

用户通常想看大量排名（30-50 个）快速扫货。用批量翻页：

```bash
# 一次翻 3-4 页，简洁格式
for p in 1 2 3; do
  curl -s "https://api.github.com/search/repositories?q=stars:%3E1&sort=stars&order=desc&per_page=10&page=$p" \
    | python3 -c "
import json,sys
start = 1 + ($p-1)*10
data=json.load(sys.stdin)
for i,r in enumerate(data.get('items',[]), start):
    s=r['stargazers_count']; n=r['full_name']
    d=(r.get('description') or 'N/A')[:100]
    print(f'{i:3}. {r[\"stargazers_count\"]:>6,}  {r[\"full_name\"]}')
    print(f'     {d}'); print()
"
done
```

### 逐页翻（用户看一页评一页）

```bash
curl -s "https://api.github.com/search/repositories?q=stars:%3E1&sort=stars&order=desc&per_page=10&page=N" \
  | python3 -c "import json,sys; ..."
```

- 每页 10 个，不需要 GitHub token
- 可加 `+language:python` 筛选语言

### 向用户展示时的标注

| 标记 | 含义 |
|------|------|
| 🔥 / 📦 | 值得安装 |
| ✅ | 已有技能，直接跳过 |
| ⚡ | 可做技能但需适配 |
| ❌ | 不适合做成技能（纯文档/闭源/商业服务） |
| 默认无标记 | 工具/框架/不相关 |

### 翻页节奏

- 前 100 名：逐页翻，每页重点标记
- 100-300 名：每 2-3 页合并展示
- 300+：一次 30-40 个批量翻，只标亮点
- 用户说"继续"就翻，说"这个不错"就停下来分析
- **GitHub Search API 限制 1000 条**，约覆盖 ⭐32K 以上。更深需用特定关键词搜索
- **100/页模式**：用户赶时间时用 `per_page=100`，一次翻 300-400 个，只输出名字+星标

### 快速姓名模式（用户赶时间时）

```bash
for p in N M; do
  curl -s "https://api.github.com/search/repositories?q=stars:%3E1&sort=stars&order=desc&per_page=100&page=$p" \
    | python3 -c "
import json,sys
for r in json.load(sys.stdin).get('items',[]):
    print(f'{r[\"stargazers_count\"]:>7,}  {r[\"full_name\"]}')
"
done
```

### API 限制

- `total_count` 显示总数，但最多只返回 1000 条
- `stars:>40000` 约 800 个，全在可翻范围
- 翻到底部后用 `total_count` 确认是否还有剩余
- 如需更深搜索，用特定关键词：`agent+skill`、`claude+code+skill` 等

### 评估可迁移性

对每个候选仓库判断：

| 可迁移 | 不可迁移 |
|--------|----------|
| SKILL.md 文件（格式相似可转换） | 纯文档/落地页（无程序化内容） |
| Python/CLI 工具可安装使用 | 闭源后端/只有前端 UI |
| 参考知识库（Awesome 列表） | 需要专属硬件/账号才能用 |
| 系统提示词/行为准则 | 纯商业服务 |

## 2. SPA 文档提取

很多现代文档站点是 SPA（React/Next.js），curl 返回 404。用浏览器工具：

```javascript
// 提取完整文章内容
document.querySelector('article').innerText

// 提取特定区域
document.querySelector('.markdown-body').innerText
```

Hermes 工具链：`browser_navigate(url)` → `browser_console(expression="...")`

## 3. 批量跨生态迁移

### 源目录结构

常见其他 Agent 的技能目录：

| 来源 | 路径 | 格式 |
|------|------|------|
| Hermes (主) | `~/.local/skills/<category>/<skill>/SKILL.md` | 标准 Hermes |
| Hermes (可选) | `~/.local/optional-skills/<category>/<skill>/SKILL.md` | 标准 Hermes |
| Claude | `/mnt/c/Users/<user>/.claude/skills/` (symlinks) | CLAUDE.md |
| Codex | `/mnt/c/Users/<user>/.codex/skills/.system/` | SKILL.md |
| Superpowers | `/mnt/c/Users/<user>/superpowers/skills/` | SKILL.md |
| Agents | `~/.agents/skills/` | SKILL.md + AGENTS.md |
| Anthropic | `anthropics/skills` GitHub | SKILL.md (兼容) |

### 批量迁移脚本模式

```python
import shutil
from pathlib import Path

SOURCES = [
    (Path.home() / ".local" / "skills", ""),
    (Path.home() / ".local" / "optional-skills", "opt-"),
    # ... more sources
]

for source_base, prefix in SOURCES:
    for skill_md in source_base.rglob("SKILL.md"):
        skill_dir = skill_md.parent
        parts = skill_dir.relative_to(source_base).parts
        category = parts[0] if len(parts) > 1 else "misc"
        skill_name = f"{prefix}{'-'.join(parts)}".replace("_", "-")
        
        dest = HERMES_SKILLS / category / skill_name / "SKILL.md"
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(skill_md, dest)
        
        # 同时复制 references/ scripts/ templates/ assets/
        for sub in ["references", "templates", "scripts", "assets"]:
            src_sub = skill_dir / sub
            if src_sub.is_dir() and not (dest.parent / sub).exists():
                shutil.copytree(src_sub, dest.parent / sub)
```

### 迁移后验证

```bash
hermes skills list        # 查看总数
find ~/.hermes/skills -name "SKILL.md" | wc -l  # 计数
```

## 4. 从单个 GitHub 仓库创建技能

### 直接转换（格式兼容时）

```bash
# 获取原始 SKILL.md
curl -sL "https://raw.githubusercontent.com/<org>/<repo>/main/SKILL.md"
```

### 需适配时（如 Claude → Hermes）

Claude 的 CLAUDE.md 格式与 Hermes SKILL.md 的区别：
- CLAUDE.md 无 YAML frontmatter — 需添加 `name` 和 `description`
- CLAUDE.md 放在项目根目录 — Hermes 放在 `skills/<category>/<name>/SKILL.md`
- 行为准则类内容 100% 通用，无需翻译

### 大型参考库（Awesome 列表）

对于 README 数百 KB 的参考库（如 awesome-go 252KB）：
- 不要嵌入全部内容 — 创建"使用指南"型技能
- 技能内容 = 分类速查 + 搜索方法
- 需要时克隆仓库搜索：`git clone --depth 1`

## 5. 网络问题处理

### Git/curl 代理超时

当系统配置了 HTTP 代理但不可用时：
```bash
# 绕过代理
GIT_SSL_NO_VERIFY=1 git -c http.proxy= -c https.proxy= clone ...
```

或使用浏览器工具直接获取原始文件：
```
browser_navigate("https://raw.githubusercontent.com/...")
browser_console(expression="document.body.innerText")
```

### pip 安装超时

使用国内镜像：
```bash
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple <package>
```

### npm 代理问题

当 git 代理 127.0.0.1:56666 但 npm 连接被拒时：
```bash
npm install -g <pkg> --proxy http://127.0.0.1:56666
```

## 6. GStack 安装模式

GStack（YC CEO Garry Tan 的虚拟工程团队）原生支持 Hermes：

```bash
git clone --depth 1 https://github.com/garrytan/gstack.git ~/.hermes/skills/gstack
cd ~/.hermes/skills/gstack && ./setup --host hermes
```

如果 setup 需要 bun 但系统没有：
```bash
npm install -g bun --proxy http://127.0.0.1:56666
cd ~/.hermes/skills/gstack && bun run gen:skill-docs --host hermes
```

生成 55 个 gstack-* 技能到 `~/.hermes/skills/`。

## 7. 安装 + 创建技能并行模式

用户选中的技能应同时进行：
- `pip install` 或 `git clone` 放后台 (`background=true`)
- 同时 `skill_manage create` 创建文档技能
- 不等安装完成就开始翻下一页

## 8. 技能备份到 GitHub

每次新增技能后同步：
```bash
cd ~/kaikai && rsync -aq --delete ~/.hermes/skills/ skills/
git add -A && git commit -m "📦 描述" && git push origin main
```

恢复用：
```bash
git clone https://github.com/yuankaik/kaikai.git
cp -r kaikai/skills/* ~/.hermes/skills/
```

## 参考脚本

迁移脚本保存在 `scripts/batch_migrate_skills.py` — 可从多个源目录批量复制 SKILL.md 到 `~/.hermes/skills/`。
