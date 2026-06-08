"""Travel pack generator — 出海补给包.
Generates N days of offline paper practice for when the captain is away from the computer.
"""

from __future__ import annotations

import csv
import re
from datetime import date, timedelta
from pathlib import Path
from typing import Any


TRAVEL_PACK_DIR = "travel-packs"

FISH_EMOJI = ["🐟", "🦈", "🐋", "🐙", "🦑", "🐠", "🐡", "🦀", "🐬", "🦞"]


def generate_travel_pack(root: Path, days: int = 7) -> Path:
    """Generate a travel pack with N days of offline practice."""
    pack_dir = root / TRAVEL_PACK_DIR / f"pack-{date.today().isoformat()}"
    pack_dir.mkdir(parents=True, exist_ok=True)

    # Collect recent mistakes for entry tests
    mistakes = _read_recent_mistakes(root)
    mistake_knowledges = [m.get("knowledge", "") for m in mistakes[:10]]

    pages = []
    for day_offset in range(days):
        day_num = _current_day(root) + day_offset
        page = _generate_day_page(day_num, day_offset + 1, mistake_knowledges)
        pages.append(page)

    # Write the main travel booklet
    with open(pack_dir / "出海补给包-练习册.md", "w", encoding="utf-8") as f:
        f.write(_pack_header(days))
        for p in pages:
            f.write(p)
        f.write(_pack_footer(days))

    # Write the first mate guide
    with open(pack_dir / "出海补给包-大副指南.md", "w", encoding="utf-8") as f:
        f.write(_mate_guide(days))

    print(f"Travel pack generated: {pack_dir}")
    print(f"  - 出海补给包-练习册.md ({len(pages)} days)")
    print(f"  - 出海补给包-大副指南.md")
    return pack_dir


def _current_day(root: Path) -> int:
    """Get the latest day number from specs."""
    specs_dir = root / "practice" / "specs"
    max_day = 6
    for path in sorted(specs_dir.glob("*.json")):
        match = re.search(r"Day(\d+)", path.name)
        if match:
            max_day = max(max_day, int(match.group(1)))
    return max_day


def _read_recent_mistakes(root: Path) -> list[dict]:
    path = root / "records" / "grading-log.csv"
    if not path.exists():
        return []
    mistakes = []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            if row.get("is_correct") == "0" or (row.get("status") or "").strip() in ("bad", "review"):
                mistakes.append(dict(row))
    return mistakes[-20:]


def _generate_day_page(day_num: int, pack_day: int, mistake_knowledges: list[str]) -> str:
    """Generate one day's offline practice page."""
    fish = FISH_EMOJI[(day_num - 1) % len(FISH_EMOJI)]
    sea_idx = min((day_num - 1) // 4, 4)
    sea_names = ["新手沙滩", "珊瑚礁", "沉船湾", "深海裂谷", "远古深渊"]
    sea = sea_names[sea_idx]

    # Entry test (pick 2 from mistakes)
    entry_qs = ""
    if mistake_knowledges and pack_day % 3 == 1:
        k1 = mistake_knowledges[pack_day % len(mistake_knowledges)]
        k2 = mistake_knowledges[(pack_day + 1) % len(mistake_knowledges)]
        entry_qs = f"""
### 进门测（1分钟，先做再下海）
1. 回忆一下「{k1}」的关键规则，写一句话：____________
2. 回忆一下「{k2}」的关键规则，写一句话：____________
"""

    # Math questions
    a, b = 10 + day_num * 7, 20 + day_num * 3
    c = 30 + day_num * 5

    return f"""
---

## Day{day_num} · 第{pack_day}天补给 {fish} {sea}

{entry_qs}
### 数学甩竿（3竿）

1. {a} × {b} + {c} = ____  
   答案：________

2. {a+day_num} ÷ {3+day_num%5} = ____ 余 ____  
   答案：________ 余 ________

3. 一瓶果汁 {200+day_num*10}ml，倒进 {40+day_num%3*10}ml 的小杯，可倒满 ____ 杯，剩 ____ ml  
   答案：____ 杯，剩 ____ ml

### 英语词汇（记2个词）
- 新词1：_______________（今天路上看到/听到的英文）
- 新词2：_______________（造一个句子）

### Boss讲题（父问子讲，录音/录视频 10秒）
> 大副问："这道除法的题，你是怎么算出来的？一步一步讲给大副听。"

孩子讲完后大副勾选： □ 讲清了  □ 部分讲清  □ 没讲清

### 今日渔获
今天做对了几题？______/5  
今天感觉（圈一个）：😊 开心  😐 一般  😞 累

---
"""


def _pack_header(days: int) -> str:
    return f"""# 出海补给包 · {days}日离线练习册

> 船长袁佳乐专属。不在电脑边也能每天甩几竿。
> 打印出来，带一支铅笔，每天15分钟。

---

## 每天流程（15分钟）

1. **进门测**（1分钟）— 先回忆昨天的知识点
2. **数学甩竿**（5分钟）— 3道数学题
3. **英语词汇**（3分钟）— 记2个词
4. **Boss讲题**（3分钟）— 父问子讲，录音10秒
5. **今日渔获**（1分钟）— 自我评价

**只做不批，回家后大副拍照上传即可。**

---
"""


def _pack_footer(days: int) -> str:
    return f"""

---

## 补给包完成确认

全部 {days} 天完成后，回家把练习册拍照发给系统。

**船长签字：**______________  **大副签字：**______________

日期：____年____月____日
"""


def _mate_guide(days: int) -> str:
    return f"""# 出海补给包 · 大副操作指南

> 爸爸 = 大副，不是老师。只需要做这几件事：

## 你的任务（每节10分钟）

### 1. 发卷子
拿出当天那页，放到船长面前。说一句：
> "船长，今天补给包到了，甩几竿？"

### 2. 别教
孩子做题时，你只需要在旁边。不要教、不要催、不要说"这个都不会？"

他会做的自然会做，不会的让他写"我还不太会"——这是有用的数据。

### 3. Boss讲题（最重要）
做完数学后，指着 Boss 题问：
> "这道题你是怎么算出来的？一步一步讲给大副听。"

用手机录 10 秒视频或语音。然后勾选：讲清 / 部分讲清 / 没讲清。

**这条录音是最有价值的反馈，比做对做错还重要。**

### 4. 收卷子
做完后说：
> "今天出海结束！"（不管做对几题）

不要加题。不要因为全对就奖励更多题。不要因为错得多就批评。

### 5. 回家后
把练习册拍照，一次性批量上传到系统 `/api/school-mistake`。

---

## 铁律（21天不变）

- 不催  
- 不骂  
- 不加题  
- 不说"这个都不会"  
- 每天说"船长，今天渔获如何？"

---

## 紧急情况

- **孩子不想做**：跳过今天，不勉强。休息一天不会退步。
- **旅途太累**：只做 Boss 讲题+自我评价，数学可以不做。
- **3天没做**：没关系，回家后从 Day1 重新开始即可。

---

祝你和大副旅途愉快 🌊
"""


if __name__ == "__main__":
    import sys
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    root = Path(__file__).resolve().parents[1]
    generate_travel_pack(root, days=days)
