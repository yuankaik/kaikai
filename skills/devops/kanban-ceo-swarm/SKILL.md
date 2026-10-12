---
name: kanban-ceo-swarm
description: 用 Hermes Kanban Swarm 搭建「CEO + 小组智能体」多Agent编排——飞书/CLI 派任务给 CEO，CEO 拆解并分派给专业小组 profile，并行执行→独立核对→打回修正→汇总交付。已验证工作场景（仓库KPI周报）。当用户要在飞书里让一个"CEO智能体"接收任务、分派小组、逐层开发核对、汇总交付时使用。
category: devops
tags: [kanban, swarm, multi-agent, orchestration, feishu, ceo, 编排, 多智能体]
---

# CEO + 小组智能体编排 (Kanban Swarm)

用 Hermes 原生 Kanban Swarm 实现「CEO 接收任务 → 分派小组 → 逐层开发核对 → 汇总交付」。
飞书/CLI 是 CEO 的入口，小组智能体=独立 profile，在 Hermes 内编排（不是飞书里多个机器人）。

## ★ 自动拆解（内建 decomposer）—— 实现"CEO自动分配"

Hermes **原生内建**了任务自动拆解器，不用装任何第三方。

### 配置（~/.hermes/config.yaml 的 kanban 段）

```yaml
kanban:
  auto_decompose: true          # 落到 triage 列的任务，dispatcher 每tick自动拆解
  auto_decompose_per_tick: 3    # 每tick最多拆几个（防突发烧钱）
  orchestrator_profile: default # 谁拥有编排/root任务（CEO）
  default_assignee: w-data      # LLM选不出profile时的兜底
  dispatch_in_gateway: true     # dispatcher 跑在 gateway 里
  failure_limit: 2              # 连崩2次自动block
```

### ★ 关键前提：profile 必须有 description

decomposer 靠 **profile 的 description** 决定分派给谁。没描述的 profile 只能按名字路由，不准。

```bash
hermes profile describe w-data --text "仓库运营数据处理专家。负责从Excel/CSV提取清洗统计数据..."
hermes profile describe w-doc  --text "中文商务文档与报表产出专家..."
hermes profile describe w-review --text "质检与审校专家。独立复核他人产出，发现问题打回..."
# 也可 --auto 让 LLM 从技能的skill+model自动生成
```

### 实际效果（2026-10-12 实测）

建 1 个 triage 任务：
```bash
hermes kanban create "把仓库9月KPI做成月报：整理数据+生成文档+核对无误" --assignee default --triage
```
dispatcher 自动拆成 3 个子任务并正确分派：
```
父任务(default)
 ├─ w-data   "整理9月仓库KPI数据并计算指标"
 ├─ w-doc    "撰写9月仓库KPI月报文档"
 └─ w-review "独立核对月报数据与文档准确性"   ← 依赖前两个
```
**完全自动**：识别角色 → 按描述路由 → 建依赖链。

### 手动控制（不想要自动拆解时）

```bash
hermes kanban decompose <id>   # 手动触发拆解
hermes kanban specify <id>     # 只补规格不拆（单任务）
# config: kanban.auto_decompose: false 关闭自动拆解
```

## 官方 9 大协作模式（Hermes 内建）

| 模式 | 形态 | 例子 |
|------|------|------|
| P1 Fan-out | N个同角色并行 | "并行研究5个角度" |
| P2 Pipeline | 角色链 scout→editor→writer | 每日简报 |
| P3 Voting/quorum | N个+1聚合器 | 3研究员→1审核挑选 |
| P4 Long-running journal | 同profile+共享目录+cron | 知识库 |
| P5 Human-in-the-loop | worker block→用户评论→unblock | 模糊决策 |
| P6 @mention | 散文里内联路由 | "@reviewer 看这个" |
| P7 Thread-scoped | /kanban here 在线程 | 每项目一个线程 |
| P8 Fleet farming | 1profile管N对象 | 50个社交账号 |
| P9 Triage specifier | 粗想法→triage→自动展开 | "把一句话变成规格化任务" |

**CEO+小组 = P1 fan-out + P2 pipeline 组合。**

## 飞书 → CEO → 结果回飞书（原生支持）

从 gateway 创建的任务，**自动订阅回原聊天**：
- 飞书里 `/kanban create "..."` 或自然语言让CEO建任务
- 任务完成/blocked/crashed 时，**结果自动推回那个飞书会话**
- 无需轮询、无需记task_id
- 订阅会跨 done→reopen 周期存活

## 现成的第三方方案（评估结论：不需要）

- **PolyBrain** (mosesman831, 23⭐)：专为Hermes的多模型编排，orchestrator→并行researchers→synthesizer→verifier，带引用强制+源验证。**适用多模型路由场景**，本项目用不上。
- **a-team** (22⭐)：26专家agent+19工作流技能+首席编排官
- **claude-plugins** (2389-research, 97⭐)：28插件含多agent编排
- Hermes 官方文档内置的 9 模式 = 最权威，且已内建，优先用官方。

## 架构（已验证跑通）

```
飞书群「xxx智能助手」← 用户派任务
      ↓
  【CEO = default profile】接任务 → kanban swarm 建图
      ↓ 分派
  ┌──────────┬──────────┐
  │ 数据组    │ 文档组    │  (并行 workers)
  └──────────┴──────────┘
      ↓ 黑板共享
  【核对组】verifier 独立验证 → 有错则打回
      ↓
  【CEO】synthesizer 汇总 → 回复用户
```

## 本机已配置

```
profiles: w-data(数据组) / w-doc(文档组) / w-review(核对组)
gateway:  运行中（内嵌 dispatcher，每60秒 tick）
kanban:   已 init
```

## 核心命令

### 创建 swarm（一步建图）

```bash
hermes kanban swarm "<总目标>" \
  --worker "w-data:整理数据" \
  --worker "w-doc:生成文档" \
  --verifier w-review \
  --synthesizer default \
  --json
```
返回 `{root_id, worker_ids[], verifier_id, synthesizer_id}`，依赖自动链接：
workers 并行 → verifier(等所有worker) → synthesizer(等verifier)。

### 查看进度

```bash
hermes kanban list            # 全部任务状态
hermes kanban show <task_id>  # 单任务详情+注释+事件
hermes kanban tail <task_id>  # 跟踪
hermes kanban stats
```

### 打回修正（核对发现问题时）

**不要重跑原任务**，新建修正任务：
```bash
hermes kanban create "修正XX" --assignee w-doc --parent <verifier_id> \
  --body "核对组发现：1... 2... 请修正后重新生成"
```

### 解除死锁（重要）

verifier block 等修正，但修正任务 parent=verifier → 死锁。
**解法**：verifier 结论已记录，直接 complete 它，修正任务自动推进：
```bash
hermes kanban complete <verifier_id> \
  --result "核对完成：...转 w-doc 修正(t_xxx)" \
  --metadata '{"gate":"pass_with_notes","fix_task":"t_xxx"}'
```

### 恢复卡住的 worker

```bash
hermes kanban reclaim <task_id>              # 释放claim重置ready
hermes kanban reassign <task_id> <profile> --reclaim
hermes kanban unblock <task_id>              # 解除blocked
```

## 关键坑（实测踩过）

### 1. ★ 新 profile 看不到主技能库 → worker 崩溃

新建 profile 的 `skills/` 目录是空的。若 swarm 给 worker 挂了技能（如 verifier 自动挂
`requesting-code-review`），会报 `Error: Unknown skill(s): xxx` → 进程 exit 1 → 崩溃2次后 gave_up。

**修复**：软链 profile 技能目录到主库：
```python
import os
main = os.path.expanduser("~/.hermes/skills")
for prof in ["w-data","w-doc","w-review"]:
    pdir = os.path.expanduser(f"~/.hermes/profiles/{prof}/skills")
    if os.path.isdir(pdir) and not os.listdir(pdir):
        os.rmdir(pdir); os.symlink(main, pdir)
```

### 2. ★ profile 缺 API key

新 profile 的 `.env` 是空的，需从主 `.env` 复制 `DEEPSEEK_API_KEY` / `DEEPSEEK_BASE_URL`。

### 3. ★ 技能名冲突会让 skill 加载失败

若两个 SKILL.md 的 `name:` 相同，`-s <name>` 报 `Ambiguous` 或 `Unknown`。
排查：
```python
import os, re, collections
SK = os.path.expanduser("~/.hermes/skills")
names = collections.defaultdict(list)
for root,_,fs in os.walk(SK):
    if "SKILL.md" in fs:
        c = open(os.path.join(root,"SKILL.md"),encoding="utf-8").read()
        m = re.search(r"^name:\s*(.+)$", c, re.M)
        if m: names[m.group(1).strip()].append(root)
dups = {k:v for k,v in names.items() if len(v)>1}
```
修复：给重复项改名（加来源前缀，如 `super-`/`agents-`/`opt-`）。

### 4. profile 变量
每个 worker 的 `.env` 独立；多 profile 时 `FEISHU_GROUP_POLICY` 等要放各自 profile 的 .env。

### 5. 任务描述要具体
worker 是独立会话，不知道上下文。任务要写清：数据源路径、要算什么、输出到哪、什么格式。
含糊的任务（"整理KPI数据"）worker 会自己找文件，可能找错。

### 6. dispatcher 依赖 gateway
任务建好后靠 gateway 内嵌 dispatcher 执行（每60秒 tick）。**gateway 没跑 → 任务永远 ready 不动**。
本机电脑不常开 = 关机时整个 CEO+小组停摆。

## 关于"飞书里多个机器人互相@"

**不推荐**：飞书每个机器人=独立应用，要重复建应用+开权限；飞书对 bot-to-bot 消息有限制；
自由对话最容易失控（死循环、职责重叠）。
**推荐**：飞书只放1个CEO机器人，小组在 Hermes 内用 kanban 编排（父子依赖控制流转）。

## 已验证案例（2026-10-12）

任务："处理仓库KPI周报" → 6 张卡全部 done，产出 6 个真实文件：
- w-data: 33个月KPI数据整理（CSV+JSON×2）
- w-doc: KPI月报docx + Excel报表
- w-review: 独立复算，抓出文档2处事实错误+2处措辞问题 → block
- w-doc 修正任务: 改正4处并重生成
- default 汇总: 《全流程核对说明》+ 3条关注项

**结论**：数据→文档→核对→修正→汇总 全链路自动跑通，核对组真能独立抓错。

## 相关技能

- `kanban-orchestrator` — 拆解 playbook（orchestrator 视角）
- `kanban-worker` — worker 视角的坑
- `feishu-api` — 飞书文档/云盘读写（CEO 交付到飞书用）
