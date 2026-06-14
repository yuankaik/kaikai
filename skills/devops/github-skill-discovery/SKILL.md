---
name: github-skill-discovery
description: GitHub 热门仓库技能发现与迁移工作流。从 GitHub 高星仓库中识别可迁移的技能，分析、改编、安装到 Hermes。适用于批量技能猎取场景。
---

# GitHub 技能发现与迁移

从 GitHub Trending/Top 仓库中猎取技能并迁移到 Hermes 的完整工作流。

## 触发条件

- 用户说"看看 GitHub 上有什么技能"
- "翻 GitHub 排行榜"
- "搜高星项目"
- "有没有什么好用的技能"

## 工作流

### Phase 1: 发现

```bash
# 按星标搜索，每页 10 个
curl -s "https://api.github.com/search/repositories?q=stars:%3E1&sort=stars&order=desc&per_page=10&page=N" \
  | python3 -c "..."  # 格式化输出
```

展示时标出：
- 🔥 可直接做成技能的
- ✅ 已有对应技能的
- ❌ 无法技能化的

### Phase 2: 评估

对每个候选仓库判断：

| 维度 | 问自己 |
|------|--------|
| 可用性 | 有 API/CLI/库吗？还是纯文档？ |
| 重复度 | Hermes 已有类似技能吗？ |
| 价值 | kai哥会用到吗？（偏好：AI、自动化、开发工具） |
| 难度 | 能快速迁移还是需要深度改造？ |

### Phase 3: 分析

用 `delegate_task` 并行分析多个仓库：
- 浏览器导航到仓库
- 用 `browser_console` 提取 `document.body.innerText`
- 或用 raw.githubusercontent.com 直接读文件

### Phase 4: 迁移

用 `skill_manage(action='create')` 创建 Hermes 技能：
- 保持 YAML frontmatter 规范
- 精简内容，去除平台特定细节
- 标注 `source:` 指向原仓库

如原仓库自带安装脚本（如 gstack），直接 clone + 运行。

## 网络注意事项

kai哥环境：
- **git clone** → 走代理 127.0.0.1:56666，通常可用
- **curl/wget** → 常超时，避免直连
- **npm install** → 加 `--proxy http://127.0.0.1:56666`
- **浏览器** → 间歇性超时，用 raw.githubusercontent.com 备用
- **pip** → 换清华源 `-i https://pypi.tuna.tsinghua.edu.cn/simple`

## 展示格式

每页 10 个，用表格呈现：
- # 排名
- 项目名 + ⭐
- 简介
- 标注：🔥可迁移 / ✅已有 / ❌不适合

让 kai哥挑选，不要说"要不要继续翻"——直接翻下一页，他发现宝藏会叫停。

## 常用搜索页

| 排名 | page |
|------|------|
| 1-10 | 1 |
| 11-20 | 2 |
| 21-30 | 3 |
| ... | ... |

翻了 10 页以上还没停，主动问要不要换个搜索策略。
