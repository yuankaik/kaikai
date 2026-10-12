#!/usr/bin/env python3
"""艾宾浩斯复习计算器 — 输出今天该复习的所有 Day 批次单词"""
from datetime import date, datetime, timedelta
import os

WORK_DIR = os.path.expanduser("~/错题")
META_FILE = os.path.join(WORK_DIR, "艾宾浩斯_meta.txt")

# 艾宾浩斯复习间隔（从学习日算起的天数）
REVIEW_INTERVALS = [1, 3, 6, 14, 29]

def load_meta():
    days = {}
    if not os.path.exists(META_FILE):
        return days
    with open(META_FILE) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) >= 2:
                day_name = parts[0]  # e.g. Day01
                try:
                    learn_date = datetime.strptime(parts[1], "%Y-%m-%d").date()
                    days[day_name] = learn_date
                except ValueError:
                    pass
    return days

def get_word_file(day_name):
    fpath = os.path.join(WORK_DIR, f"艾宾浩斯_{day_name}.txt")
    if os.path.exists(fpath):
        return fpath
    return None

def read_words(fpath):
    words = []
    with open(fpath) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            # Format: "word 中文" or "word中文"
            parts = line.split(maxsplit=1)
            if len(parts) >= 2:
                words.append((parts[0], parts[1]))
            elif len(parts) == 1:
                words.append((parts[0], ""))
    return words

def main():
    today = date.today()
    meta = load_meta()

    # Categorize: new_learn vs review
    reviews = {}  # day_name -> (interval_num, words)

    for day_name, learn_date in sorted(meta.items()):
        days_since = (today - learn_date).days

        if days_since == 0:
            # Today is learning day — not review
            continue

        for i, interval in enumerate(REVIEW_INTERVALS):
            if days_since == interval:
                fpath = get_word_file(day_name)
                if fpath:
                    words = read_words(fpath)
                    if words:
                        # interval_num for display: 1→Day2, 3→Day4, etc.
                        reviews[day_name] = (interval + 1, words)
                break

    if not reviews:
        print("今天不是任何单词的复习日。")
        return

    # Output
    today_str = today.strftime("%m/%d")
    print(f"📝 艾宾浩斯单词复习 — {today_str}")
    print()

    for day_name in sorted(reviews.keys()):
        interval_day, words = reviews[day_name]
        print(f"▸ {day_name}（第{interval_day}天复习）")
        for word, chinese in words:
            print(f"  {word} — {chinese}")
        print()

    total = sum(len(w) for _, w in reviews.values())
    print(f"📊 今日曝光 {len(reviews)} 个批次，共 {total} 个单词")

if __name__ == "__main__":
    main()
