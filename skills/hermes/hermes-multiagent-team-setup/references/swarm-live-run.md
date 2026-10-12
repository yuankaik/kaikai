# Live swarm run — 仓库KPI周报（2026-10-12）

一次真实的 `kanban swarm` 端到端运行的完整记录，可作为复现/调试模板。

## 目标与拓扑

```
目标: "处理仓库KPI周报任务：把数据整理+文档产出+核对全流程走通"

hermes kanban swarm "<目标>" \
  --worker "w-data:整理KPI数据" \
  --worker "w-doc:生成KPI报表" \
  --verifier w-review \
  --synthesizer default --json
```

返回：
```json
{"root_id":"t_f8cf552c",
 "worker_ids":["t_2b4b378b","t_346fffba"],
 "verifier_id":"t_120812b2",
 "synthesizer_id":"t_50e96985"}
```

依赖自动链接：
```
root(CEO锚点,立即done)
 ├─ w-data  (worker, 并行)
 ├─ w-doc   (worker, 并行)
 ├─ w-review(verifier, parents=[两个worker])
 └─ default (synthesizer, parents=[verifier])
```

## 状态流转时间线（真实）

```
11:52 root done, 两个 worker ready
11:53 dispatcher 自动 claim，两个 worker 从 ready→running
11:57 w-data done  (跑 272s)  → 黑板写 kpi_data 结论
11:58 w-doc done              → 黑板写 handoff
11:59 verifier promoted ready → claim → spawn
12:00 verifier 崩 exit 1 (run4)
12:01 verifier 崩 exit 1 (run5) → gave_up（2次重试上限）
12:04 手动 unblock → run6 正常心跳
12:08 verifier blocked：核对完成，发现文档2处事实错误，打回
```

## worker 的真实产出（不是 demo）

- **w-data**：读 `Warehouse_KPI2026年9月.xlsx`，提取 2024-01~2026-09 共 33 个月双仓数据，
  输出宽表 CSV + 长表 JSON + 汇总 JSON 到 `桌面/工作/KPI周报_数据整理_20261012/`。
  算出 9 月核心 KPI：收发总量 43334，人均日产出 125.45，同比 +15.77%。
- **w-doc**：生成 `仓库KPI月报_2026年9月.docx` + `_数据报表.xlsx`，
  发现异常"DC发货时效5.9天偏高"。

## 黑板（swarm root 卡是共享黑板）

worker 用结构化注释共享机器可读结论，下游 worker 直接采用：
```json
[swarm:blackboard] {"key":"kpi_data","worker":"w-data","status":"done",
  "output_dir":"...","files":{...},"2026-09核心KPI":{...},"同比":{...}}
[swarm:blackboard] {"key":"worker:t_346fffba:handoff","role":"w-doc",
  "deliverables":[...],"key_metrics":{...},"attention":"DC发货时效5.9天偏高"}
```

## 核对组抓到的真实错误（证明"逐层核对"有效）

verifier 独立重算后 block，理由：
```
数据层与文档数字全部核对通过（独立重算一致，抽数/公式/同比/环比均正确，交付物齐全），
但文档「三、趋势分析」有2处实质事实错误：
①「Campus连续4个月下行」——实际 6月4.13→7月4.81(年内最高)→8月2.99→9月2.72，仅连续2个月回落；
②「DC稳定在3.1-3.6天」——全年实为 2.84~4.24天。
```
→ 标准处置：新建修正卡
```bash
hermes kanban create "修正KPI月报趋势分析2处事实错误" \
  --assignee w-doc --parent t_120812b2 --body "..."
```

## 崩溃根因（exit 1，两次后 gave_up）

verifier 卡带 `skills: ['requesting-code-review']`。复现：
```bash
hermes -p w-review -s "requesting-code-review" chat -q "回答OK"
# → Error: Unknown skill(s): requesting-code-review
```
两个叠加病因：
1. 新建 w-review profile 的 `skills/` 为空 → 看不到主技能库。
2. 全机有 60 组技能重名（含 `requesting-code-review` 出现两次）→ `-s` 歧义。

**修复**：软链 profile skills 目录到主库 + 重命名冲突技能之一 →
`hermes -p w-review -s "requesting-code-review" chat -q "回答OK"` 成功。

## 死锁

"修正卡 t_dccc2857 依赖 verifier t_120812b2"，但 verifier 又 block 等修正 → 成环。
处置：verifier 已给出有效结论，直接完成它（结论在注释里），再放行修正卡。
