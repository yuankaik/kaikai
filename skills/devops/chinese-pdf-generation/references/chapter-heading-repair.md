# Chapter Heading Repair Patterns

When Markdown chapter headings get corrupted (split across lines, merged with body text, embedded in scene breaks), the fix approach matters. This reference covers patterns seen in real-world Chinese novel MD sources and how to fix them reliably.

## Common Damage Patterns

### Type A: Heading Split
Chapter title split across heading line + orphan line(s):
```
## 第一章：水

坑
```
→ Should be `## 第一章：水坑`

### Type B: Subtitle Merged Into Heading
Body text leaked into the heading line:
```
## 第五章：字母群岛字母鱼住在

一

片环形珊瑚礁里。二十六条鱼...
```
→ Should be `## 第五章：字母群岛` with body starting "字母鱼住在一片环形珊瑚礁里..."

### Type C: Embedded in Scene Break
```
---  ## 第三章：战争  "Oran

g

e head！"
```
→ Should be properly separated.

### Type D: Heading Duplicate in Body
```
## 第十六章：合成海域 & 金丹
章：合成海域 & 金丹词语鱼是成对出现的。
```
→ Remove duplicate heading text from body start.

## Fix Strategy: Exact String Matching > Regex

**TL;DR: Use `patch` tool with exact old/new strings. Avoid complex regex in Python scripts.**

### Why Regex Fails
- Newline counts differ subtly between what you read and what's actually in the file
- execute_code `read_file` can corrupt content with line-number prefixes (see CRITICAL pitfall in SKILL.md)
- Multi-line regex patterns with `\n` are fragile — one extra or missing blank line breaks the match

### Recommended Workflow

1. **Backup first**: `cp file.md file-backup.md`
2. **Read the exact bytes** with `read_file` tool (line-by-line view shows exact content)
3. **Copy the exact text** from the file view — include ALL newlines and spaces
4. **Use `patch` tool** with `old_string` = exact original text, `new_string` = corrected text
5. **Verify with `grep -n '^## '`** to check all headings

### Example patch call
```
patch(
  path="story.md",
  old_string="## 第一章：水\n\n坑\n\n",
  new_string="## 第一章：水坑\n\n"
)
```

### When to Use a Batch Script
Only when there are 10+ identical pattern fixes. Even then, use **exact string replacement** (Python `str.replace`) not regex:
```python
fixes = [
    ('\n## 第一章：水\n\n坑\n\n', '\n## 第一章：水坑\n\n'),
    ('\n## 第二章：第一条鱼字母鱼真的\n...', '\n## 第二章：第一条鱼\n\n...'),
]
for old, new in fixes:
    if old in text:
        text = text.replace(old, new, 1)
```

### Recovery
If a fix batch goes wrong: `cp file-backup.md file.md` and redo individually.
