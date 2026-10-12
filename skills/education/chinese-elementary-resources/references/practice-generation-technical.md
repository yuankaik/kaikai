# Practice Material Generation — Technical Reference

## DOCX Merge: Copying Tables Correctly

### The Bug
`doc.paragraphs` only returns `<w:p>` elements. Tables (`<w:tbl>`) are silently dropped.
If you just copy paragraphs, all table content (口算 problems in grids, etc.) disappears.

### The Fix
Iterate `element.body` children, handling both `w:p` and `w:tbl`:

```python
from docx.oxml.ns import qn

def append_docx_content(dst_doc, src_path):
    src = Document(src_path)
    plist = list(src.paragraphs)
    tlist = list(src.tables)
    pi = ti = 0
    
    for child in src.element.body:
        if child.tag == qn('w:p') and pi < len(plist):
            sp = plist[pi]; pi += 1
            p = dst_doc.add_paragraph()
            p.alignment = sp.alignment
            for run in sp.runs:
                r = p.add_run(run.text)
                r.bold = run.bold
                r.font.size = run.font.size or Pt(11)
                r.font.name = '宋体'
                r._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
        elif child.tag == qn('w:tbl') and ti < len(tlist):
            copy_table_to_doc(dst_doc, tlist[ti])
            ti += 1
            dst_doc.add_paragraph()  # spacing after table
```

### Table Copy Function

```python
def copy_table_to_doc(dst_doc, src_table):
    tbl = dst_doc.add_table(rows=len(src_table.rows), cols=len(src_table.columns))
    try:
        tbl.style = src_table.style
    except:
        pass
    
    for i, src_row in enumerate(src_table.rows):
        dst_row = tbl.rows[i]
        for j, src_cell in enumerate(src_row.cells):
            dst_cell = dst_row.cells[j]
            # Clear default empty paragraph
            for p in dst_cell.paragraphs:
                p.text = ""
            # Copy content
            first = True
            for para in src_cell.paragraphs:
                if first:
                    p = dst_cell.paragraphs[0]
                    first = False
                else:
                    p = dst_cell.add_paragraph()
                p.alignment = para.alignment
                for run in para.runs:
                    r = p.add_run(run.text)
                    r.bold = run.bold
                    r.font.size = run.font.size or Pt(10)
                    r.font.name = '宋体'
                    r._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
    return tbl
```

## 口算 (Oral Math) Generation

### MD Source Formats

Two formats exist in the source files:

**1. Table format** (most files: `08-三年级上-万以内加减法口算.md` etc.):
```
| 序号 | 题目 | 答案 | 序号 | 题目 | 答案 |
| 1 | 300+500= | 800 | 10 | 1600-800= | 800 |
```
Each row = 3 question groups (seq|q|a × 3 = 9 columns).
Must skip the header row (`'题目' in cells`).

**2. List format** (special files: `三年级-找规律口算.md`, `通用-竖式口算练习.md` etc.):
```
1. 2, 4, 6, 8, ( ), 12
2. 5, 10, 15, 20, ( ), 30
```
Match with `re.match(r'^\d+[\.\、]', line)`.

### Proportional Sampling

Goal: ~40 questions covering ALL sub-modules proportionally.

```python
TARGET = 40
counts = [(section_name, question_count_in_section) for each section]
total = sum(counts)

alloc = []
remaining = TARGET
for i, (name, n) in enumerate(counts):
    if i == len(counts) - 1:
        take = remaining  # last section takes remainder
    else:
        take = max(1, int(TARGET * n / total))
    take = min(take, n)
    alloc.append(take)
    remaining -= take

# Distribute any remainder
while remaining > 0:
    for i in range(len(alloc)):
        if remaining <= 0: break
        if alloc[i] < counts[i][1]:
            alloc[i] += 1
            remaining -= 1
```

### Student vs Parent Versions

- **Student**: 2-column table, no numbers, no answer quick-lookup table, spacious rows (`w:trHeight=480`)
- **Parent**: 4-column table (题目|答案|题目|答案), compact
- Filter sections with '答案' in title from student version

## Answer Hint Filtering

When merging reading comprehension into student version, filter paragraphs containing:
- '如果第' (if question X...)
- '题错了' (got it wrong)
- '答案速查' (quick answer lookup)
- '短文想告诉我们' (what the passage tells us)
- '用铅笔' (use pencil)
- '参考' (reference)
- '解题' (solution approach)

These are parent-guide content, not student-facing.

## File Locking on WSL→Windows Desktop

Writing to `/mnt/c/Users/admin/Desktop/...` can fail with `PermissionError` if Word has the file open.
Solution: `os.remove(path)` first, then write. If remove fails, skip that file and tell user to close Word.

## Pix2Text OCR for Test Papers

```bash
source ~/ocr_env/bin/activate
p2t predict -i '<image_path>'
```

Works well for Chinese test papers (80-90% accuracy). For English-heavy papers, use Tesseract:
```bash
# Preprocess: grayscale + 2x enlarge
python3 -c "from PIL import Image; img=Image.open('t.jpg').convert('L'); w,h=img.size; img.resize((w*2,h*2),Image.LANCZOS).save('e.jpg','JPEG',quality=95)"
tesseract e.jpg stdout -l eng
```

## Common Pitfalls

1. **Variable name shadowing**: `gen = 0` then `def gen():` → `TypeError: 'int' object is not callable`. Use distinct names.
2. **`execute_code` timeout**: 300s limit. For 80-file generation, use background `terminal()` with `notify_on_complete=true`.
3. **`delegate_task` timeout**: 600s limit. Sub-agents may not complete large generation tasks. Fall back to `execute_code` + `terminal(background=true)`.
4. **Old reading files are gold**: The original 60-day reading exercises (2 passages/day) are higher quality than AI-generated ones. Preserve them, don't regenerate.
