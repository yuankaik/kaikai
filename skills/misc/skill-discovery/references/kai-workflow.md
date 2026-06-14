# kai哥 的 GitHub 技能发现工作流

## 工作节奏

"好的" "安装" "继续翻" — 快节奏，不要过度分析

## 排名浏览

- 30 个一批（3 页 × 10），用 curl + python3 -c 管道
- 高亮标记：🔥 Agent/技能相关 | 📚 参考库 | 🤖 AI 框架
- 已有技能标注 ✅ 跳过
- 问"要不要装"而非"要不要分析"

## 安装流程

1. delegate_task 并行分析（toolsets: ["browser"]）
2. skill_manage create（精简版，5 分钟内）
3. GitHub 自动备份

## 网络备忘

- git: 走代理 127.0.0.1:56666 ✅
- curl/npm: 需 --proxy http://127.0.0.1:56666
- pip: -i https://pypi.tuna.tsinghua.edu.cn/simple
- browser: 可能超时，用 browser_console 提取 innerText

## 备份命令

```bash
cd ~/kaikai
rsync -aq --delete ~/.hermes/skills/ skills/
git add -A && git commit -m "📦 同步技能" && git push
```
