# 技能库 GitHub 备份与恢复

## 为什么需要

技能存在本地 `~/.hermes/skills/`，系统重装或 Hermes 重置后会丢失。推送到 GitHub 作为持久备份。

## 备份流程

```bash
# 1. 同步本地技能到仓库
rsync -aq --delete ~/.hermes/skills/ ~/kaikai/skills/

# 2. 提交推送
cd ~/kaikai
git add -A
git commit -m "📦 同步技能库 (N skills)"
git push origin main
```

## 恢复流程

```bash
git clone https://github.com/yuankaik/kaikai.git
cp -r kaikai/skills/* ~/.hermes/skills/
hermes gateway restart
```

## 注意事项

- 如果技能目录包含 git 仓库（如 gstack clone），先删除内嵌 `.git`：`rm -rf skills/gstack/.git`
- 大文件（>50MB）GitHub 可能拒绝，排除大型二进制文件
- 新增技能后及时同步，告诉 Hermes "同步技能到 GitHub"
