# Education DOCX Generation Patterns

Recurring patterns for generating printable education DOCX files using python-docx. All output goes to Windows desktop (`/mnt/c/Users/admin/Desktop/`).

## Vocabulary Lists (英语/语文词汇)

### English Word Lists

Format matching existing `单词.docx` style:

```
01
序号  单词  中文
1     school    学校
2     classroom 教室
...
```

Key rules:
- Groups of 20 words per section header (01, 02, 03...)
- Tab-separated: `序号\t单词\t中文`
- Font: 宋体 9pt for words, 11pt bold for section headers
- Compact spacing: `space_after=Pt(1)`, `space_before=Pt(0)`
- Source: read DOCX paragraph text, parse `"  1. word    chinese"` format with regex `r'^\s*\d+[\.\、\)]\s*([a-zA-Z][a-zA-Z\'\- ]*?)\s{2,}(.+)'`

### Chinese Character Lists (生字表)

Compact 5-per-row layout:
```
1  一  yī    2  二  èr    3  三  sān    4  十  shí    5  木  mù
```

Key rules:
- 5 characters per row separated by double-tab `\t\t`
- Each: `序号\t汉字\t拼音`
- Font: 宋体 8pt for density
- Grouped by grade with clear headers

### Chinese Word Lists (词语表)

4-per-row layout:
```
1  天地  tiān dì    2  人口  rén kǒu    3  上下  shàng xià    4  日月  rì yuè
```

### Classical Chinese / Poetry (古诗文言文)

Structure:
- Part headers (第一部分: 古诗词)
- Poem title in 《》marks, author + dynasty on separate line
- Each verse line as separate paragraph, 11pt
- Theme notes in 9pt italic below each poem
- Final section: checklist with □ checkboxes for tracking

## Habit Tracking Tables (习惯打卡)

### 66-Day Tracker

Simple DOCX with python-docx tables:

```python
table = doc.add_table(rows=1, cols=5)
table.style = 'Table Grid'
# Headers: 日期 | 天数 | ☐晨读 | ☐背诵 | 备注
# 66 data rows with ☐ checkboxes (Unicode \u2610)
# Phase markers at days 1, 7, 21, 42, 66
```

Key rules:
- Font: 宋体 8-9pt, compact
- Weekend rows: light gray background via `OxmlElement('w:shd')`
- Phase notes in column 5: "← 开始！", "← 21天！", "← 66天！"
- User prefers 2 habits max, simple format, no more than 5 columns

### Father-Son Joint Tracker

Same table, 2 extra columns for parent:
```
日期 | 天数 | 爸① | 爸② | 乐① | 乐② | 备注
```

Parent habits pair with child habits parasitically:
- 爸① 不刷手机 ← pairs with 乐① 晨读
- 爸② 睡前写3件事 ← pairs with 乐② 晚间背诵

## Poetry/Classical Chinese Compilation

Structure for 《五上必背古诗词文言文》:
1. Title page
2. Part 1: 古诗词 (poem text + theme notes)
3. Part 2: 文言文 (full text + notes)
4. Part 3: 日积月累 (sayings/proverbs)
5. Part 4: 背诵清单 (□ checkboxes for tracking)

Use 《》for poem titles, 【】for section labels, 宋体 throughout.

## Common Pitfalls

- **font.color.rgb crash**: Don't set `run.font.color.rgb = Pt(0)`. Use `RGBColor` or skip.
- **Chinese quotes in Python strings**: Use \u300a \u300b for 《》, \u3014 \u3015 for 【】
- **PermissionError on /mnt/c/**: Windows locks open DOCX files. Catch and report.
- **Tab alignment in DOCX**: Tabs don't visually align perfectly in Word. Acceptable.
