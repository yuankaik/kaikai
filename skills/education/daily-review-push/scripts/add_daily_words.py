#!/usr/bin/env python3
"""
每日英语单词入库脚本 — 把暑假练习当天的新词喂进艾宾浩斯追踪。
由 cron 在 generate_daily_review.py 之前调用。

读取：
  - 暑假英语词表_40天分配.json (Day01~40 各20词)
  - 每日单词进度.txt (记录当前进展到第几天)
  - 每日复习追踪.json (艾宾浩斯数据库)

写入：
  - 每日复习追踪.json (追加当天新词，next_review=D+1)
  - 每日单词进度.txt (day+1)

幂等：同一天重复执行会跳过（检查当天是否已有对应日期的词）。
"""

import json, os, sys
from datetime import date, datetime, timedelta

BASE = "/mnt/c/Users/admin/Desktop/shanghai-exams"
WORD_ALLOC_PATH = os.path.join(BASE, "暑假英语词表_40天分配.json")
REVIEW_JSON_PATH = os.path.join(BASE, "每日复习追踪.json")
PROGRESS_PATH = os.path.join(BASE, "每日单词进度.txt")

today = date.today()
today_str = today.isoformat()

# 1. Read word allocation
if not os.path.exists(WORD_ALLOC_PATH):
    print(f"[ERROR] 词表文件不存在: {WORD_ALLOC_PATH}")
    sys.exit(1)

with open(WORD_ALLOC_PATH, "r", encoding="utf-8") as f:
    word_data = json.load(f)

allocation = word_data["allocation"]

# 2. Read or init progress
if os.path.exists(PROGRESS_PATH):
    with open(PROGRESS_PATH, "r", encoding="utf-8") as f:
        lines = f.read().strip().split("\n")
    current_day = int(lines[0].strip())
    last_add_date = lines[1].strip() if len(lines) > 1 else ""
else:
    current_day = 1
    last_add_date = ""

# 3. Check if already done today
if last_add_date == today_str:
    print(f"[SKIP] 今天 ({today_str}) 已入库过，current_day={current_day}")
    sys.exit(0)

# 4. Read review JSON
if not os.path.exists(REVIEW_JSON_PATH):
    print(f"[ERROR] review JSON 不存在: {REVIEW_JSON_PATH}")
    sys.exit(1)

with open(REVIEW_JSON_PATH, "r", encoding="utf-8") as f:
    review_data = json.load(f)

items = review_data.get("items", [])

# 5. Get today's words
day_key = f"Day{current_day:02d}"
if day_key not in allocation:
    print(f"[DONE] 词表已用完 (Day{current_day:02d} 不存在)，共 {current_day-1} 天全部入库。")
    sys.exit(0)

today_words = allocation[day_key]
if not today_words:
    print(f"[DONE] {day_key} 无单词，全部入库完成。")
    sys.exit(0)

# 6. Add words to review items
max_id = max((it.get("id", 0) for it in items), default=0)

new_count = 0
existing_words = set()
for it in items:
    if it.get("subject") == "english" and it.get("type") == "word":
        existing_words.add(it["content"].lower())

for w in today_words:
    word_text = w["word"]
    if word_text.lower() in existing_words:
        print(f"  [DUP] {word_text} — 已存在，跳过")
        continue
    
    max_id += 1
    items.append({
        "id": max_id,
        "subject": "english",
        "type": "word",
        "date": today_str,
        "source": f"暑假练习{day_key}",
        "content": word_text,
        "context": w["grade"],
        "meaning": w["meaning"],
        "reviews": 0,
        "next_review": (date.today() + timedelta(days=1)).isoformat(),  # D+1首次复习
        "review_dates": []
    })
    new_count += 1

# 7. Update stats
stats = review_data.get("stats", {})
stats["total_items"] = stats.get("total_items", 0) + new_count
stats["english_items"] = stats.get("english_items", 0) + new_count

# 8. Write back
review_data["items"] = items
review_data["stats"] = stats

with open(REVIEW_JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(review_data, f, ensure_ascii=False, indent=2)

# 9. Update progress
current_day += 1
with open(PROGRESS_PATH, "w", encoding="utf-8") as f:
    f.write(f"{current_day}\n{today_str}\n")

print(f"✅ {day_key}: 入库 {new_count} 个新词 (total english: {stats['english_items']}, all items: {len(items)})")
print(f"   进度: Day {current_day-1}/40 已完成 → 下次 Day {current_day}")
