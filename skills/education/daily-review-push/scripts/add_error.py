#!/usr/bin/env python3
"""
手动录入错题 — kai哥在微信/CLI发文本即可。
格式: 录一条: <科目> <内容>[,<错因>]
示例:
  录一条: 数学 63-28=35,忘了借位
  录一条: 英语 beautiful,3A M2U1,总是拼成beautifull
  录一条: 语文 拔和拨搞混,提手旁和发字旁

支持在微信中通过 iLink 接收后自动解析入库。
"""
import json, os, re, sys
from datetime import date, timedelta

TRACKING_FILE = "/mnt/c/Users/admin/Desktop/shanghai-exams/每日复习追踪.json"
EBBINGHAUS = [1, 2, 4, 8, 15]
TODAY = date.today().isoformat()

SUBJECT_MAP = {
    "数学": "math", "math": "math",
    "英语": "english", "english": "english", "英文": "english",
    "语文": "chinese", "chinese": "chinese", "中文": "chinese",
}

def parse_entry(text):
    """Parse: 录一条: 数学 63-28=35,忘了借位"""
    # Remove prefix
    text = re.sub(r'^录一条[:：]\s*', '', text.strip())
    
    # Extract subject
    subject = None
    for key, val in SUBJECT_MAP.items():
        if text.startswith(key):
            subject = val
            text = text[len(key):].strip()
            break
    
    if not subject:
        return None, "无法识别科目（数学/英语/语文）"
    
    # Split by comma for content, context, meaning
    parts = [p.strip() for p in text.split(',')]
    
    content = parts[0] if parts else ""
    context = parts[1] if len(parts) > 1 else ""
    meaning = parts[2] if len(parts) > 2 else ""
    
    return {
        "subject": subject,
        "content": content,
        "context": context,
        "meaning": meaning,
    }, None


def add_entry(parsed):
    """Add entry to tracking JSON and return summary"""
    with open(TRACKING_FILE, 'r', encoding='utf-8') as f:
        db = json.load(f)
    
    items = db.get('items', [])
    next_id = max([it.get('id', 0) for it in items], default=0) + 1
    
    # Determine type
    typ = "error"
    if parsed['subject'] == 'english':
        typ = "word"
    elif parsed['subject'] == 'chinese':
        typ = "character"
    
    entry = {
        "id": next_id,
        "subject": parsed['subject'],
        "type": typ,
        "date": TODAY,
        "source": "手动录入",
        "content": parsed['content'],
        "context": parsed['context'],
        "meaning": parsed['meaning'],
        "reviews": 0,
        "next_review": TODAY,  # 今天就到期，明天复习
        "review_dates": []
    }
    
    items.append(entry)
    db['items'] = items
    
    # Update stats
    db['stats'] = {
        "total_items": len(items),
        "math_items": sum(1 for it in items if it['subject'] == 'math'),
        "english_items": sum(1 for it in items if it['subject'] == 'english'),
        "chinese_items": sum(1 for it in items if it['subject'] == 'chinese'),
        "mastered": sum(1 for it in items if it.get('reviews', 0) >= 5),
    }
    
    with open(TRACKING_FILE, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    
    return entry['id'], parsed['content']


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 add_error.py '录一条: 数学 63-28=35,忘了借位'")
        print("  或 echo '录一条: ...'  | python3 add_error.py --stdin")
        sys.exit(1)
    
    if sys.argv[1] == '--stdin':
        text = sys.stdin.read().strip()
    else:
        text = ' '.join(sys.argv[1:])
    
    parsed, error = parse_entry(text)
    if error:
        print(f"❌ {error}")
        sys.exit(1)
    
    eid, content = add_entry(parsed)
    subject_cn = {"math": "数学", "english": "英语", "chinese": "语文"}.get(parsed['subject'], parsed['subject'])
    print(f"✅ 已录入 [{subject_cn}] #{eid}: {content}")
    print(f"   明天15:00自动加入复习清单")
