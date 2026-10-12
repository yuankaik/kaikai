# 循证教育 Skill 库调研（2026-09-21）

任务背景：为上海五年级学生做学习方案综合研判，需要"下载 GitHub 排名靠前的教育技能并应用"。

## 搜到的 Top 5 教育技能库

| 仓库 | Stars | 规模 | 质量评价 | 适用场景 |
|------|------:|------|---------|---------|
| **GarethManning/education-agent-skills** | 790 | 165 个 SKILL.md | ★★★★★ 每个 skill 都带论文依据（evidence_strength + evidence_sources），格式规范 | 任何循证教学设计/学习科学问题 |
| DreambigOu/ELI5 | 1430 | 1 skill | ★★★☆☆ 按年龄段降维解释（含 Age 10 = elementary 档，可直接给孩子讲题） | 把概念降到指定年龄 |
| Li-Evan/Bloom | 269 | 7 skills | ★★★★☆ learn-* 学习法族（feynman / occam / graph / crossover / prototype / deep） | 教用户/孩子学新概念 |
| Polaris-Aeterna/loom-notes | 155 | 1 skill | ★★★☆☆ XeLaTeX 主动回忆填空 | 生成复习填空笔记 |
| flysheep-ai/education-skills | 101 | 5 skills | ★★☆☆☆ 只有高考五科 | 高中学段，小学不适用 |

下载位置：`~/.hermes/skills/gh-edu/`（共 311 文件）
`_meta.json` 记录了各仓库文件数。

## GarethManning 库里最值得记住的几个 Skill

路径前缀：`~/.hermes/skills/gh-edu/165-evidence-grounded-edu-skills/skills/`

| Skill | 路径 | 核心内容 |
|-------|------|---------|
| **implementation-intention-designer** | `wellbeing-motivation-agency/implementation-intention-designer/` | if-then 触发器 + WOOP。Gollwitzer&Sheeran(2006) 94项元分析 d=0.65。**核心洞察：失败的自我调节不是动机失败，是缺 WHEN/WHERE/HOW 计划** |
| **spaced-practice-scheduler** | `memory-learning-science/spaced-practice-scheduler/` | Cepeda(2006) 254项元分析：**复习间隔 ≈ 目标记忆时长的 10-20%**。Ebbinghaus 曲线：不复习24h忘70%。Kornell&Bjork(2008)：**学生觉得集中练习更有效，但间隔效果更好——要顶住这个偏好** |
| ai-feedback-design-principles | `ai-learning-science/` | 反馈设计 |
| goal-setting-protocol-designer | `self-regulated-learning/` | 目标设定 |
| motivation-diagnostic-task-redesign | `wellbeing-motivation-agency/` | 动机诊断 |

## 检索这些库的关键词（实测有效）

```
"education agent skills"        → GarethManning 等成套库
"claude skills education"       → 同上 + ELI5
"children learning assistant llm" → 命中少（该方向开源少）
"<platform> crawler"            → 中文平台爬虫
```

## 可复用的"应用"套路

1. 遍历所有 SKILL.md，按任务关键词计数打分 → 排序
2. 读 top 2-3 正文，提取**可执行框架**（不是收藏链接）
3. 在交付物里明确写"应用了哪个 skill + 循证依据 + 怎么落地"

例：给家长的方案里，把"早上要晨读"改写成 if-then 触发器（"如果早上刷完牙坐在餐桌前，那么我翻开小古文读10分钟"），依据标注 Gollwitzer 元分析。
