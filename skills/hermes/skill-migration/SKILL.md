---
name: skill-migration
description: 从 GitHub 仓库、本地 Agent 目录、或外部技能库发现并迁移技能到 Hermes。涵盖批量迁移、单个分析导入、备份到 GitHub 的完整工作流。
---

# Skill Migration — 技能迁移工作流

从任意来源发现、分析、迁移技能到 Hermes，并备份到 GitHub。

## 触发条件

- 用户说"搜技能"、"迁移技能"、"安装这个仓库的技能"
- 浏览 GitHub 热门项目时发现可用的技能
- 系统重装后从 GitHub 恢复技能

---

## 工作流一：从 GitHub 热门仓库迁移

### Step 0: 批量并行分析（推荐）

同时发现多个候选仓库时，用 `delegate_task` 并行分析，效率提升 3-5 倍：

```python
delegate_task(tasks=[
    {"goal": "分析 repo A 并判断可迁移性", "context": "...", "toolsets": ["browser"]},
    {"goal": "分析 repo B 并判断可迁移性", "context": "...", "toolsets": ["browser"]},
    {"goal": "分析 repo C 并判断可迁移性", "context": "...", "toolsets": ["browser"]},
])
```

每个子 Agent 返回：仓库摘要 + 可迁移性判断 + 草稿 SKILL.md。

详细评估记录见 `references/github-rankings-2026-06-14.md`。

### Step 1: 排名发现

```bash
# GitHub API 搜索按星标排序
curl -s "https://api.github.com/search/repositories?q=stars:%3E1&sort=stars&order=desc&per_page=10&page=N"
```

判断一个仓库是否值得做成技能：
- ✅ 有可复用的知识/代码/模式
- ✅ 仓库内容可以被 Agent 直接使用
- ❌ 纯文档站/营销页
- ❌ 纯粹的工具/框架源码（用户已有对应技能除外）
- ❌ 你已有类似技能的

### Step 2: 仓库分析

用 `delegate_task` 派子 Agent 分析，任务模板：

```
Navigate to <repo_url> and analyze:
1. Read README, file structure
2. Extract key content (skills, tools, patterns)
3. Draft complete Hermes SKILL.md with YAML frontmatter
4. Return the SKILL.md content ready to create
```

如果网络不稳（代理超时），降级方案：
- 直接用 `browser_navigate` 打开 raw.githubusercontent.com URL
- 用 `browser_console(expression="document.body.innerText")` 提取
- 基于已知信息 + GitHub API 摘要创建轻量级 SKILL.md

### Step 3: 创建技能

```python
skill_manage(action="create", category="<匹配分类>", name="<技能名>", content="<SKILL.md>")
```

分类映射：
| 仓库类型 | Hermes 分类 |
|----------|------------|
| AI Agent 相关 | autonomous-ai-agents |
| 开发工具 | software-development |
| DevOps/CLI | devops |
| 设计/创意 | creative |
| 效率/办公 | productivity |
| 数据/ML | mlops / data-science |

### Step 4: 实际安装（如果是可安装工具）

```bash
# Python 包
pip install --break-system-packages <package>

# npm 包（带代理）
npm install -g <package> --proxy http://127.0.0.1:56666

# Git 仓库 + setup
git clone --depth 1 <repo> <dest>
cd <dest> && ./setup --host hermes
```

---

## 工作流二：本地全盘批量迁移

### Step 1: 全盘搜索

```bash
# 搜索所有 SKILL.md
find /mnt/c/Users/admin -name "SKILL.md" 2>/dev/null
find /home/adminkaikai -name "SKILL.md" 2>/dev/null

# 搜索 Agent 配置目录
find /mnt/c/Users/admin -maxdepth 3 -name ".agents" -o -name ".claude" -o -name ".codex" -type d
```

### Step 2: 批量复制

已有脚本：`hermes-messaging-setup/scripts/batch_migrate.py`

```python
# 核心逻辑
for source_base, prefix in SOURCES:
    for skill_md in source_base.rglob("SKILL.md"):
        # 检测分类，生成 Hermes 路径
        dest_dir = HERMES_SKILLS / category / skill_name
        shutil.copy2(skill_md, dest_dir / "SKILL.md")
        # 同时复制 references/, scripts/, templates/
```

源目录清单：
- `~/.local/skills/` — Hermes 兼容（直接复制）
- `~/.local/optional-skills/` — 加 `opt-` 前缀
- `/mnt/c/Users/admin/.agents/skills/` — 加 `agents-` 前缀
- `/mnt/c/Users/admin/superpowers/skills/` — 加 `super-` 前缀
- `/mnt/c/Users/admin/.codex/skills/.system/` — 加 `codex-` 前缀

---

## 工作流三：备份到 GitHub

### 首次备份

```bash
cd ~/kaikai
mkdir -p skills
rsync -av ~/.hermes/skills/ skills/
# 清理嵌套 git 仓库
find skills/ -name ".git" -type d -exec rm -rf {} +
git add skills/
git commit -m "📦 备份 Hermes 技能库"
git push origin main
```

### 增量同步

```bash
cd ~/kaikai
rsync -av --delete ~/.hermes/skills/ skills/
git add -A skills/
git commit -m "📦 同步技能库更新"
git push origin main
```

### 重装后恢复

```bash
git clone https://github.com/yuankaik/kaikai.git
cp -r kaikai/skills/* ~/.hermes/skills/
hermes gateway restart
```

---

## 工作流四：安装外部技能（如 gstack）

GStack 是特殊案例——它自带 `./setup --host hermes`，直接生成 SKILL.md。

```bash
git clone --depth 1 <repo> ~/.hermes/skills/<name>
cd ~/.hermes/skills/<name>
./setup --host hermes    # 或 bun run gen:skill-docs --host hermes
```

通用外部技能安装模式：
1. Clone 到 `~/.hermes/skills/` 下
2. 如果是裸 SKILL.md → 直接可用
3. 如果有 setup 脚本 → 运行它
4. 检查生成结果：`ls ~/.hermes/skills/`

---

## 网络代理注意事项

本环境 Git 走代理 `http://127.0.0.1:56666`，但 curl/wget/pip 不走。

| 操作 | 方法 |
|------|------|
| git clone | 直接用（代理自动生效） |
| npm install | `--proxy http://127.0.0.1:56666` |
| pip install | `-i https://pypi.tuna.tsinghua.edu.cn/simple` |
| curl/wget | 大概率超时，用浏览器代替 |
| GitHub API | curl 可能不稳定 |

降级策略：curl 失败 → 浏览器 navigate + console 提取 → delegate_task 分析

## 常见安装失败速查

| 失败 | 表现 | 处理 |
|------|------|------|
| 依赖爆炸 | pip resolution-too-deep | 换 Docker 或放弃（如 langflow） |
| lxml 编译 | gcc error with Python 3.14 | 等上游适配（如 crawl4ai） |
| npm 代理 | ECONNREFUSED 127.0.0.1:56666 | 代理不稳定，等恢复重试 |
| Git 超时 | Failed to connect to github.com:443 | 代理失效，放弃本次克隆 |
| bun 缺失 | bun is required but not installed | `npm install -g bun --proxy ...` |

---

## 判断标准：这个仓库值得迁移吗？

✅ 值得：
- 包含可复用的知识/代码模式（awesome-go-reference）
- 直接可用的 Agent 行为准则（karpathy-coding-guidelines）
- 技能库/SKILL.md 集合（anthropics/skills）
- 可直接安装的工具 + 使用指南（firecrawl）
- 有 setup 脚本的外部技能（gstack）

❌ 不值得：
- 纯文档/静态站点（DigitalPlatDev/FreeDomain）
- 你已有 3+ 个同类技能
- 纯源代码框架（K8s、Node.js 源码本身）
- 纯数据集合（iptv-org/iptv）
