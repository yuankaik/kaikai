---
name: skill-backup
description: 将 Hermes 技能库同步备份到 GitHub。每次新增技能后自动执行：rsync → commit → push。恢复时 clone 即可。
---

# 技能库 GitHub 备份

## 备份

```bash
cd ~/kaikai

# 清理嵌入的 git 仓库（如 gstack）
find skills/ -name ".git" -type d -exec rm -rf {} + 2>/dev/null

# 同步
rsync -aq --delete ~/.hermes/skills/ skills/
git add -A
git commit -m "📦 同步技能 ($(find skills -name 'SKILL.md' | wc -l) skills)"
git push origin main
```

## 首次备份（生成 README）

首次备份时需在 `skills/` 目录下生成 README.md，包含：
- 技能总数和分类统计
- 恢复方法
- 每个分类下的技能清单（方便 GitHub 直接浏览和搜索）

## 常见问题

- `embedded git repository` 警告 → `rm -rf skills/gstack/.git`
- `gstack` 整个目录是 clone 下来的，自带 `.git`，每次 rsync 后都可能出现
- 推送到 `origin main` 而非 `origin master`

## 恢复

```bash
git clone https://github.com/yuankaik/kaikai.git
cp -r kaikai/skills/* ~/.hermes/skills/
hermes gateway restart
```

## 何时触发

- 每次新增 1+ 技能后自动执行
- kai哥 说"同步到 GitHub"时
- 重装系统前最后一步
