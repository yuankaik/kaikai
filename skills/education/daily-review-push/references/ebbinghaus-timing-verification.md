# 艾宾浩斯间隔验证（2026-07-02）

## 关键Bug修复：next_review 偏移

### Bug
`add_daily_words.py` 曾将新词 `next_review` 设为 `today_str`（当天），导致首次复习在 D+0 而非 D+1，整个复习链偏移1天。

### 修复
改为 `next_review = date.today() + timedelta(days=1)` → 首次复习 D+1。

### 验证（已通过）

以 Day02 入库的 20 词为例追踪完整复习链：

```
intervals = [1, 2, 4, 8, 15]   （代码中 ebbinghaus_intervals）
索引: reviews=1→intervals[1]=2, reviews=2→intervals[2]=4, ...

Day02 学习 → next_review = D+1 (July 3)
Day03 D+1 → 复习1, reviews=1, delta=intervals[1]=2 → next = D+1+2 = D+3 ✓
Day05 D+3 → 复习2, reviews=2, delta=intervals[2]=4 → next = D+3+4 = D+7 ✓
Day09 D+7 → 复习3, reviews=3, delta=intervals[3]=8 → next = D+7+8 = D+15 ✓
Day17 D+15 → 复习4, reviews=4, delta=intervals[4]=15 → next = D+15+15 = D+30 ✓
Day32 D+30 → 复习5, reviews=5 → not < 5 → next_review = "2999-12-31" (mastered) ✓
```

## 稳态负荷计算

```
每天入库: 20新词
艾宾浩斯间隔: D+1, D+3, D+7, D+15, D+30（5个活跃间隔）

稳态（30天后）= 20 × 5 = 100 词/天
generate_daily_review.py 上限 = 200 → 永不触发溢出
每词生命周期 = 5次复习 → mastered（退出循环）
```

## process_subject 溢出处理

```python
selected = unique[:max_items]   # 取前 max_items 条
overflow = unique[max_items:]   # 超出部分

for it in overflow:
    it["next_review"] = (today + timedelta(days=1)).isoformat()  # 推到明天
```

上限 200 > 稳态 100 → overflow 永远为空。若将来调低上限，溢出词不会丢失，只是推迟1天。

## 幂等保护

- `add_daily_words.py`: `last_add_date == today_str` → SKIP
- `generate_daily_review.py`: `佳乐每日复习/YYYY-MM-DD.docx` 已存在 → SKIP
- 四条 cron（10:00/13:00/16:00/19:00）只有最先成功的那条会生成，其余 SKIP
