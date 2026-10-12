#!/usr/bin/env python3
"""
从 D:\Kaideepseek 字海钓徒项目提取佳乐错题数据，迁移到每日复习追踪.json。

数据源：
  - practice/specs/Day*.json → 数学/英语/语文 错题 + 薄弱知识点
  - practice/problem_bank/数学P0题型模板.json → 数学常见错误
  - records/vocab-log.json → 英语词汇
  - records/mnemonic-log.json → 记忆法记录

输出：/mnt/c/Users/admin/Desktop/shanghai-exams/每日复习追踪.json
"""
import json, os, glob
from datetime import date

SRC = '/mnt/d/Kaideepseek/worktrees/ace-angler-phase1-checkpoint-a'
DST = '/mnt/c/Users/admin/Desktop/shanghai-exams/每日复习追踪.json'
today = date.today().isoformat()

items = []
iid = 1

def add(subj, typ, src, content, context="", meaning=""):
    global iid
    items.append({"id": iid, "subject": subj, "type": typ, "date": today,
        "source": src, "content": content, "context": context, "meaning": meaning,
        "reviews": 0, "next_review": today, "review_dates": []})
    iid += 1

# 1. 数学：Day specs 错题 + 薄弱知识点
for sf in sorted(glob.glob(f'{SRC}/practice/specs/Day*.json')):
    with open(sf) as f:
        spec = json.load(f)
    day = spec.get('day', '?')
    for wk in spec.get('decision_basis', {}).get('weak_knowledge', []):
        add('math', 'formula', f'字海钓徒-{day}-薄弱点', wk, f'来自{day}回炉版', '')
    for sec in spec.get('sections', []):
        for q in sec.get('questions', []):
            if q.get('subject', '') == '数学':
                add('math', 'error', f'字海钓徒-{day}', q.get('stem', q.get('id','?')),
                    q.get('knowledge', ''), q.get('answer_rule', q.get('correct_answer', '')))

# 2. 数学：P0 题型模板常见错误
tf = f'{SRC}/practice/problem_bank/数学P0题型模板.json'
if os.path.exists(tf):
    with open(tf) as f:
        bank = json.load(f)
    seen = set()
    for tpl in bank.get('templates', []):
        for stage in tpl.get('stages', []):
            for err in stage.get('common_errors', []):
                key = f"{tpl['level3']}-{err}"
                if key not in seen:
                    seen.add(key)
                    add('math', 'error', 'P0题型模板',
                        f"[{tpl.get('level2','')}] {stage.get('prompt_pattern','')}",
                        f"常见错误: {err}", stage.get('answer_rule', ''))

# 3. 英语：vocab-log 词汇
with open(f'{SRC}/records/vocab-log.json') as f:
    vocab = json.load(f)
for a in vocab.get('assignments', []):
    add('english', 'word', f"vocab-{a.get('day','?')}",
        a.get('word_id', '?'), a.get('unit', ''), '需要复习')

# 4. 英语/语文：Day specs 中的语英章节
for sf in sorted(glob.glob(f'{SRC}/practice/specs/Day*.json')):
    with open(sf) as f:
        spec = json.load(f)
    day = spec.get('day', '?')
    for sec in spec.get('sections', []):
        title = sec.get('title', '')
        for q in sec.get('questions', []):
            subj = q.get('subject', '')
            if subj == '英语':
                add('english', 'sentence' if '句型' in title else 'word',
                    f'字海钓徒-{day}-{title}', q.get('stem', q.get('id','?')),
                    q.get('knowledge', ''), q.get('answer_rule', ''))
            elif subj == '语文':
                add('chinese', 'character' if '字' in str(q) else 'sentence',
                    f'字海钓徒-{day}-{title}', q.get('stem', q.get('id','?')),
                    q.get('knowledge', ''), q.get('answer_rule', ''))

# 写入
db = {
    "_说明": "三科艾宾浩斯复习库。从 D:\\Kaideepseek 字海钓徒项目迁移。correction-ocr 技能自动维护。",
    "_艾宾浩斯间隔": [1, 2, 4, 8, 15],
    "_推送时间": "每日18:00（双通道：错题推送+单词推送）",
    "_科目": "english|math|chinese",
    "_类型": "word|sentence|error|formula|character|poem|word_cn|other",
    "items": items,
    "stats": {"total": len(items), "mastered": 0, "learning": len(items), "due_today": len(items)}
}
os.makedirs(os.path.dirname(DST), exist_ok=True)
with open(DST, 'w') as f:
    json.dump(db, f, ensure_ascii=False, indent=2)

print(f"Done: {len(items)} items → {DST}")
