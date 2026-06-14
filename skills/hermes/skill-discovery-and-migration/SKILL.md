---
name: skill-discovery-and-migration
description: 搜索和迁移 GitHub 高星技能到 Hermes 的完整工作流。覆盖 GitHub 排名扫描、技能分析评估、批量安装迁移、GitHub 备份同步。当用户说"找技能""搜技能""翻页""有没有好的仓库"时触发。
---

# 技能发现与迁移工作流

从 GitHub 全球高星仓库中发现并迁移技能到 Hermes 的完整流程。

## 用户偏好

- **自主执行**：用户说"不要轻易放弃和回来询问我"时，持续工作直到完成，中间不要停下来问
- **批量操作**：一次翻 30 个仓库，快速浏览，只对有实际价值的深入分析
- **决策权**：用户问"好不好"时，给分析+建议，最终由用户决定装不装

## 扫描流程

### 阶段一：GitHub 排名扫描

```bash
# 30个一批快翻
for p in 22 23 24; do
  curl -s "https://api.github.com/search/repositories?q=stars:%3E1&sort=stars&order=desc&per_page=10&page=$p" \
    | python3 -c "import json,sys; [print(f'{r[\"stargazers_count\"]:,} {r[\"full_name\"]} | {(r.get(\"description\")or\"\")[:80]}') for r in json.load(sys.stdin)['items']]"
done
```

### 阶段二：快速筛选

标注四类：
- ✅ 已有技能：跳过
- 🔥 直接可用：Agent 技能、MCP 工具、SKILL.md 格式
- 📚 参考价值：教程、知识库、精选列表
- ❌ 不适用：框架、工具、非技能类型

### 阶段三：并行分析安装

用 `delegate_task` 3 路并行：
1. 浏览器分析仓库结构
2. 提取 SKILL.md/README 内容
3. 判断 Hermes 兼容性
4. 创建技能 + 安装工具同步进行

### 阶段四：GitHub 备份

```bash
cd ~/kaikai
rsync -aq --delete ~/.hermes/skills/ skills/
git add -A && git commit -m "📦 同步技能" && git push origin main
```

## 网络环境

| 场景 | 方案 |
|------|------|
| Git 克隆 | `git clone --depth 1` 通过代理 127.0.0.1:56666 |
| npm 安装 | `npm install -g xxx --proxy http://127.0.0.1:56666` |
| pip 安装 | `pip install --break-system-packages -i https://pypi.tuna.tsinghua.edu.cn/simple xxx` |
| GitHub API | curl 直连通常可用 |
| 浏览器 | 备用方案，raw.githubusercontent.com 抓取 |

## 评估框架

分析一个仓库时回答：
1. **是什么**：工具/Skill/教程/服务？
2. **怎么用**：API/CLI/MCP/SKILL.md？
3. **和现有技能重复吗**：skip 已有覆盖的
4. **对用户有用吗**：用户是做 AI、编码、自动化、办公软件
5. **Hermes 兼容吗**：是 SKILL.md 格式？需要转换？纯文档？

## 常见陷阱

- 高星 ≠ 可用：很多是框架/课程，不是技能
- 付费墙：中国教育网站（道客巴巴、百度文库）基本都有付费墙，免费内容有限
- 40K 星以下纯工具区：Agent 技能很少
- API 限制：GitHub Search 最多返回 1000 条结果

## 技能安装并行模式

```
分析仓库 → 同时做三件事：
  1. 创建 SKILL.md（skill_manage create）
  2. 安装工具（pip/npm/git 后台）
  3. 同步 GitHub（rsync + git push）
```
