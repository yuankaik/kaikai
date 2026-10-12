---
name: docx-print-author
description: Create print-ready DOCX documents for Chinese users with python-docx. Covers A4 layout, font sizing, paragraph protection, multi-file merging, and print optimization. Use when generating educational materials, reference documents, answer keys, or any DOCX intended for A4 printing.
---

# DOCX Print Author

Create DOCX files with python-docx that are ready to print on A4 paper. Chinese users expect: A4 not Letter, tight margins, compact fonts, and no mid-paragraph page splits.

## Trigger Conditions

- User asks to create a .docx file for printing
- User asks to merge multiple .docx files into one
- User wants printable educational materials, reference sheets, or answer keys
- User complains about font being too large, paper waste, or content splitting across pages

## CRITICAL: Full Content Required

**When user asks for printable material (especially 必背古诗文, 练习题, 答案), ALWAYS include the full text content — never output title-only.** The user wants to print and use immediately. A document with only titles is useless. If there are 100 entries, all 100 must have their complete body text.

## A4 Print Layout Checklist

Apply these settings to every print-ready DOCX:

### Page Setup
```python
from docx.shared import Pt, Cm
section.page_width = Cm(21.0)    # A4
section.page_height = Cm(29.7)   # A4
section.top_margin = Cm(1.0)
section.bottom_margin = Cm(0.8)
section.left_margin = Cm(1.5)
section.right_margin = Cm(1.5)
```

### Font Sizing (by document type)

| Document Type | Body | Sub-title | Main Title |
|--------------|------|-----------|------------|
| Reference / answer key | 8.5pt | 9pt | 10pt |
| Student worksheet | 10pt | 11pt | 12pt |
| Novel / reading material | 10.5pt | 12pt | 14pt |
| Poem anthology | 10pt | 10.5pt bold | 11pt bold |

### Paragraph Protection (prevents page-split)
```python
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

# Every content paragraph: don't split mid-paragraph
pPr = paragraph._element.get_or_add_pPr()
keep = OxmlElement('w:keepLines')
pPr.append(keep)

# Poem/article titles: stay with next paragraph
if is_title:
    keep_next = OxmlElement('w:keepNext')
    pPr.append(keep_next)
```

### Page Breaks
- Add explicit page breaks before paragraphs >350 characters (long classical prose)
- Add page breaks between major sections (different days, different grades)
- Don't rely on Word's auto-pagination for long pieces

### Spacing
```python
paragraph.paragraph_format.space_before = Pt(0)
paragraph.paragraph_format.space_after = Pt(0.3)
paragraph.paragraph_format.line_spacing = 1.08
```

## Merging Multiple DOCX Files

When merging many DOCX files (e.g., 60 daily answer sheets):

```python
from docx import Document
import re, os

files = sorted(os.listdir(dir_path), 
               key=lambda x: int(re.search(r'(\d+)', x).group(1)))

merged = Document()
# Apply A4 + tight margins to merged document first

for i, fname in enumerate(files):
    if i > 0:
        merged.add_page_break()
    src = Document(os.path.join(dir_path, fname))
    for para in src.paragraphs:
        if not para.text.strip():
            continue  # skip blank paragraphs
        # Copy paragraph with font normalization
        copy_paragraph(para, merged)
```

### Font Normalization During Merge
- Map original font sizes down: 15pt→10pt, 13pt→9.5pt, 11pt→8.5pt
- Keep bold/italic/color attributes
- Remove excessive blank paragraphs

## Verification

After generating any DOCX, verify:
1. A4 page size: check `section.page_width / 36000 == 21.0`
2. Content exists: spot-check several entries have full body text
3. Font sizes: sample paragraphs to confirm body is in expected range
4. Page breaks: confirm long pieces have explicit breaks
5. File size: a content-rich DOCX should be 40-200KB, not <10KB (title-only)

```python
v = Document(output_path)
print(f"Pages: {len(v.sections)}, A4: {v.sections[0].page_width/36000:.0f}mm")
# Spot-check content
for p in v.paragraphs:
    if len(p.text) > 100:
        print(f"Content OK: {p.text[:60]}...")
        break
```

## Batch Merge: Source File Problems & Paper Savings

When merging DOCX files from various sources, these format issues are common. Fix them during merge:

| Problem | Fix |
|---------|-----|
| Letter尺寸(216×279) | 改为 A4(210×297) |
| 边距 32mm | 改为 15mm |
| 字号 11-15pt | 降为 8.5-10pt |
| 行距默认 | 设为 1.08 |
| 无防跨页 | 加 keepLines |

Font normalization map during merge:
```python
if src_run.bold and orig_pt >= 15:   dst_run.font.size = Pt(10)
elif src_run.bold and orig_pt >= 13: dst_run.font.size = Pt(9.5)
elif src_run.bold:                   dst_run.font.size = Pt(9)
elif orig_pt >= 13:                  dst_run.font.size = Pt(9)
elif orig_pt <= 7:                   dst_run.font.size = Pt(orig_pt)  # 保持小字
else:                                dst_run.font.size = Pt(8.5)
```

Typical paper savings: 40-60% vs original files. This comes from combined effect of font shrinking, margin tightening, and removing blank paragraphs.

## Education Materials: Full Content Principle

**When user asks for printable reference materials (必背古诗文, 知识点汇总, 答案合并), ALWAYS include the full text content — never output title-only.** The user wants to print and use immediately. A document with only titles is useless.

- ❌ 错误：只有标题+作者，没有正文
- ✅ 正确：每篇含标题、作者、**完整原文**

User feedback: "你不能光给我一个标题。内容也要给我。我的需求是打印出来，拿到手就可以给佳乐背的。"

### Chinese Font Naming

Set both western and east-Asian font names for proper rendering:
```python
run.font.name = '宋体'
run.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
```

Font hierarchy for Chinese education materials:
| 元素 | 字号 | 样式 |
|------|------|------|
| 大标题 | 11-13pt | 黑体加粗 |
| 章节标题 | 10-11pt | 加粗 |
| 正文 | 8.5-10pt | 宋体常规 |
| 注释/脚注 | 8-9pt | 灰色斜体 |

- 家长答案/参考资料：正文 8.5pt（省纸，仍可读）
- 学生用材料：正文 10pt（护眼）

### Two-Column Warning

python-docx two-column layout (`w:cols num="2"`) makes section headers appear in left column only. Prefer single-column for mixed title+body content.

## Pitfalls

- **`Cm` import**: Must import from `docx.shared`: `from docx.shared import Pt, Cm, RGBColor`
- **Letter vs A4**: python-docx default is Letter (215.9×279.4mm). Always override to A4 for Chinese users.
- **keepLines on every paragraph**: Can cause Word to push large blocks to next page. Balance with explicit page breaks before long content.
- **Two-column layout**: python-docx two-column (`w:cols num="2"`) makes section headers appear in left column only. Prefer single-column for mixed title+body content.
- **Answer key optimization**: Parent answer keys can use 8-8.5pt body text. They're reference material, not reading material. The parent has the student booklet with full stories — story text in answer keys is ~30% redundant.
- **Never output title-only documents**: User frustration when a "必背古诗文" document has titles but no poem text. Always include complete content.
