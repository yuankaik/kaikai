# Reading Answer Filter Checklist

Use this when merging 60-day reading DOCX files into student worksheets.
Source files embed answer guides inline — filter aggressively.

## Line-Level Filter (`is_answer_line`)

Skip any paragraph whose stripped text matches:

### Exact Prefixes
- `标准答案`
- `评分点`
- `常见错因`
- `错因标签`
- `依据段`
- `家长批改提示`
- `孩子重写任务`

### Bullet Patterns
- Lines starting with `•` or `·` (scoring point details)
- Regex: `^共\d+分`

### Error Tags
- `#中心`, `#信息`, `#词语`, `#句子`, `#原因`
- Regex: `^#[^\s]` (any hashtag-style tag)

### Guide Patterns
- `如果第X题错了` (regex: `如果第\d`)
- `答案速查`
- `用铅笔画出`
- `参考答案`
- `示例开头`

## Block-Level Filter (`skip_block`)

When entering a block that should be entirely skipped:

**Trigger:** Paragraph starts with `家长批改提示` or `孩子重写任务`

**Action:** Set `skip_block = True`, continue

**Exit conditions (resume normal filtering):**
- Separator line containing `───`
- Next passage heading: `短文一` or `短文二`
- Day heading: `第X天`

## Verification

After merge, scan student file's reading section:
```python
for p in merged_doc.paragraphs:
    if is_answer_line(p.text.strip()):
        print(f"LEAK: {p.text[:80]}")
```

Zero leaks expected. Any leak means a format variant was missed — add the keyword and re-merge.

## Files Tested

Validated on all 60 days of `reading-practice-60days-docx/reading-practice-60days/第X天-阅读理解练习.docx`. Four different formatting styles across the 60 files, all handled by the above rules.
