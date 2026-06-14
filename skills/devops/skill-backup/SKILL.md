---
name: skill-backup
description: 将 Hermes 技能库同步备份到 GitHub。每次新增技能后自动执行：rsync → commit → push。恢复时 clone 即可。
---

# 技能库 GitHub 备份

## 备份

```bash
cd ~/kaikai
rsync -aq --delete ~/.hermes/skills/ skills/
git add -A
git commit -m "📦 同步技能"
git push origin main
```

注意：如果 `skills/gstack` 目录包含 `.git`，需先删除：
```bash
rm -rf skills/gstack/.git
```

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
