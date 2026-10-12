---
name: hermes-multiagent-team-setup
description: 在 Hermes 上搭建"CEO + 专家小组"多智能体团队——新建 worker profile、共享主技能库(软链)、清技能重名、用 kanban swarm 编排(并行worker→核对→汇总)、以飞书/Telegram 当入口。当用户想要"一个主脑接收任务→拆解分派给小组→逐层核对→汇总交付"时使用。
category: hermes
tags: [multi-agent, kanban, swarm, profiles, orchestration, feishu]
---

# Hermes 多智能体团队搭建（CEO + 小组）

把 Hermes 变成"一个 CEO 接收任务 → 分派给若干专业小组 → 逐层开发/核对 → CEO 汇总交付"的组织。
**关键认知：小组智能体 = Hermes profile；编排引擎 = kanban；入口 = 飞书/Telegram 等消息平台。**

## 触发条件

- 用户想"在飞书/聊天里让一个机器人当 CEO，下面有小组分头干活"
- 用户说"多智能体""智能体群""分工协作""逐层核对""互相沟通"
- 需要把一个大任务拆成并行工作流 + 审核 + 汇总

## 架构决策（先做这一步）

用户常以为"小组"要跑在聊天平台里（多个机器人互相 @）。**默认走 B 路线**：

| 路线 | 小组在哪 | 代价 |
|------|---------|------|
| A 多机器人 | 每个机器人=一个独立飞书应用，互相 @ 对话 | 要重复建应用+开权限，调试难，飞书对 bot 消息有限制 |
| **B 单CEO+内部编排（推荐）** | 聊天里只有 1 个机器人；小组是 Hermes profile，在 Hermes 内部跑 | 复用 kanban 依赖引擎，稳定、可控 |

**必须提前告知用户的现实约束**（不要回避）：
1. **宿主机不常开 = 整个团队停摆**。Hermes 在本地跑，关机就没有 CEO 也没有小组。需要常开机器或云部署。
2. **成本放大**：多层拆解+核对 = 大量 LLM 调用。
3. **"自由互相对话"易失控**（死循环、职责重叠）。用 kanban 的父子依赖控制流转，比自由对话可靠得多。

## 搭建步骤

### 1. 建 worker profile（每个小组一个）
```bash
hermes profile create w-data      # 数据组
hermes profile create w-doc       # 文档组
hermes profile create w-review    # 核对组
```
给每个写 `~/.hermes/profiles/<name>/SOUL.md` 定义角色（职责/工作方式/边界/环境背景）。

### 2. ⚠️ 让新 profile 看到主技能库（不修必崩）
新 profile 的 `skills/` 是**空的**，不继承 `~/.hermes/skills/`。任何 `-s <skill>` 或 swarm
自动挂的技能都会失败，worker 秒崩 exit 1。修法——把空的 skills 目录换成软链：
```python
import os
main = os.path.expanduser("~/.hermes/skills")
for prof in ["w-data", "w-doc", "w-review"]:
    p = os.path.expanduser(f"~/.hermes/profiles/{prof}/skills")
    if os.path.isdir(p) and not os.listdir(p):
        os.rmdir(p); os.symlink(main, p)
```

### 3. ⚠️ 给新 profile 注入 API key
新 profile 的 `.env` 也是空的，不注入 key 则连模型都调不了：
```python
import os
main_env = open(os.path.expanduser("~/.hermes/.env")).read()
keep = [l for l in main_env.splitlines()
        if l.startswith(("DEEPSEEK_API_KEY=", "DEEPSEEK_BASE_URL=", "TERMINAL_ENV="))]
for prof in ["w-data", "w-doc", "w-review"]:
    p = os.path.expanduser(f"~/.hermes/profiles/{prof}/.env")
    if "DEEPSEEK_API_KEY" not in open(p).read():
        open(p, "a").write("\n" + "\n".join(keep) + "\n")
```

### 4. ⚠️ 清技能重名（否则引用技能的自动化全线失败）
两个 SKILL.md 同名 → `-s <name>` 报 "Unknown skill(s)" → dispatched worker 崩。
先扫描：
```python
import os, re, collections
names = collections.defaultdict(list)
for root,_,fs in os.walk(os.path.expanduser("~/.hermes/skills")):
    if "SKILL.md" in fs:
        c = open(os.path.join(root,"SKILL.md"), encoding="utf-8").read()
        m = re.search(r"^name:\s*(.+)$", c, re.M)
        if m: names[m.group(1).strip()].append(root)
print({k:v for k,v in names.items() if len(v)>1})
```
对每组冲突用 `patch` 给其中一个改名（加前缀）。实测一台机器上曾发现 60 组冲突
（~50 来自陈旧的嵌套 `gstack/.hermes/skills/` 副本，另有 `misc/super-*` vs
`software-development/*` 等真实冲突）。

### 5. 单 worker 冒烟测试（分派前必做）
```bash
hermes -p w-data chat -q "用一句话回答：12000 SKU × 2 分钟 = 多少工时？"   # 能答=OK
hermes -p w-review -s "requesting-code-review" chat -q "回答OK"          # 能加载技能=OK
```
两条都过再往下，否则 swarm 会白白烧掉两次重试。

### 6. 初始化 kanban + 起编排
```bash
hermes kanban init      # dispatcher 内嵌在 gateway 里，默认每 60s tick 一次
```
`kanban swarm` = 你要的三段式架构（**并行 worker → verifier → synthesizer**）：
```bash
hermes kanban swarm "<总目标>" \
  --worker "w-data:整理数据" \
  --worker "w-doc:生成报表" \
  --verifier w-review \
  --synthesizer default \
  --json
# 返回 {root_id, worker_ids[], verifier_id, synthesizer_id}，依赖已自动链接
```
依赖语义：worker 并行 ready；verifier 等所有 worker done；synthesizer 等 verifier done。
`hermes kanban list` 观察状态流转（ready→running→done/blocked）。

### 7. 入口 = 消息平台
CEO 就是 default profile，已接入飞书等平台（见 `hermes-messaging-setup` 技能）。
用户在聊天里派任务 → CEO 建 swarm → 小组在后台跑 → 汇总回聊天。

## 工作流要点

- **任务描述要具体**。"整理KPI数据" 这种模糊任务会让 worker 瞎找；写成"从
  Warehouse_KPI2026年9月.xlsx 提取双仓月度数据，输出宽表CSV+汇总JSON"。
- **黑板共享**：swarm 的 root 卡是共享黑板。worker 用 `[swarm:blackboard]` 注释写结论，
  下游 worker 读取后接手（实测：数据组写结论 → 文档组直接采用）。
- **核对组会"打回"——这是正确行为**。实测核对组独立重算后发现文档组 2 处事实错误
  （"连续4个月下行"实际只连跌2月；"稳定3.1-3.6天"实际2.84~4.24），block 打回。
- **修正任务用新建卡，不重跑原卡**：核对发现问题的标准处置是
  `hermes kanban create "修正XX" --assignee <原小组> --parent <verifier卡id>`。
- **注意死锁**：若"修正卡依赖 verifier 卡"，而 verifier 又 block 等修正，会成环。
  处置：verifier 已出结论就直接完成它（结论留注释），再让修正卡跑。

## 关键坑清单

1. **新 profile 空 skills 目录** → worker 崩 exit 1（已两次重试后 gave_up）。见步骤2。
2. **新 profile 空 .env** → 调不了模型。见步骤3。
3. **技能重名** → "Unknown skill(s)" → worker 崩。见步骤4。
4. **dispatcher 只在 gateway 运行时 tick**；gateway 停 → 任务永远 ready。
5. **`hermes kanban create` 用 `--parent`（单数，可重复）**，不是 `--parents`。
6. **scratch workspace 是临时的**，任务完成即删；要保留产物用
   `--workspace worktree:<path>` 或 `dir:/abs/path`，或直接把文件写到桌面。
7. **任务图先给用户看再建卡**（kanban-orchestrator 的准则：decompose, don't execute）。

## 相关技能

- `kanban-orchestrator` / `kanban-worker` — 编排/worker 的详细 playbook（hub 安装，勿改）
- `hermes-messaging-setup` — 飞书等平台接入（CEO 对外入口）
- `dispatching-parallel-agents` — 单进程内并行子任务（轻量替代）

## 参考

- `references/swarm-live-run.md` — 一次真实 swarm 运行的完整记录（拓扑、黑板注释、
  核对组发现的错误、死锁处理），可作为复现模板。
