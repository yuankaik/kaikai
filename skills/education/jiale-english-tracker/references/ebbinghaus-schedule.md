# 艾宾浩斯遗忘曲线 — 复习排程规则

## 间隔
学习当天 = Day 0（不入复习）
D+1 → D+3 → D+7 → D+15 → D+30 → 掌握

## JSON 字段
```json
{
  "reviews": 0,          // 已复习次数 (0=新词, 5=掌握)
  "next_review": "date", // 下次复习日期 (ISO格式, "mastered"=已掌握)
  "review_dates": []     // 历史复习日期列表
}
```

## 间隔数组 (from 0 reviews)
intervals = [1, 2, 4, 8, 15]

- 0次复习 → next_review = today + 1天
- 1次复习后 → next_review = today + 2天 (实际D+3)
- 2次复习后 → next_review = today + 4天 (实际D+7)
- 3次复习后 → next_review = today + 8天 (实际D+15)
- 4次复习后 → next_review = today + 15天 (实际D+30)
- 5次复习后 → next_review = "mastered"

## 每日复习查询
```python
today = date.today().isoformat()
due = [w for w in words if w["next_review"] <= today and w["reviews"] < 5]
# due MAY be empty — that's OK
```

## 复习完成更新
```python
for w in due:
    w["reviews"] += 1
    w["review_dates"].append(today)
    if w["reviews"] >= 5:
        w["next_review"] = "mastered"
    else:
        next_gap = intervals[w["reviews"]]
        w["next_review"] = (today + timedelta(days=next_gap)).isoformat()
```
