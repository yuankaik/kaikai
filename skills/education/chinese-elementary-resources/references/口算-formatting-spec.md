# 口算 Worksheet Formatting Spec

## Two-Version Workflow

Every 口算 worksheet MUST be produced in TWO separate DOCX files:

| File | Location | Content |
|------|----------|---------|
| 学生卷 | `学生卷/` | Problems only, blank answer columns, no answer summary table |
| 家长卷 | `家长卷/` | Full problems + answers in columns + answer summary table + solution hints |

**Never combine them.** A single "练习+答案" file is useless for student practice.

## Table Layout

### 9-column layout (3 problems per row) — the standard

```
| 序号 | 题目 | 作答 | 序号 | 题目 | 作答 | 序号 | 题目 | 作答 |
```

Column widths (grid-level, NOT cell-level):
- 序号: 0.8cm (just wide enough for 1-2 digit numbers)
- 题目: 3.0cm (fits problems like "345 + 278 =")
- 作答: 2.0cm (room for child handwriting)
- Total: 17.4cm — fits A4 with standard margins

### 3-column layout (1 problem per row) — for word problems

```
| 序号 | 题目 | 作答 |
```

Column widths: 序号 0.8cm, 题目 9.0cm, 作答 5.5cm.

## Answer Cell Styling

Each answer cell in the student version:
1. **Bottom border**: single line, sz=6, color=#AAAAAA (light gray writing guide)
2. **Vertical alignment**: bottom (text sits on the line)
3. **Header text**: "作答" (not "答案" — that implies answers are already there)
4. **Clear existing content**: all paragraphs cleared before adding the guide

## Answer Summary Table Removal

Most 口算 files end with an answer summary table (pure answers, no problems). This MUST be removed from the student version. Detection: header row contains "答" but no "题目" or "题".

## python-docx Implementation Notes

### Column Widths: Use gridCol, NOT tcW

**Cell-level widths (tcW) are unreliable in python-docx.** Always set widths at the table grid level:

```python
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

def set_grid_widths(table, widths_cm):
    """Set column widths at table grid level. widths_cm is list of floats."""
    tblGrid = table._tbl.find(qn('w:tblGrid'))
    if tblGrid is None:
        tblGrid = OxmlElement('w:tblGrid')
        table._tbl.insert(0, tblGrid)
    
    # Remove existing gridCols
    for gc in tblGrid.findall(qn('w:gridCol')):
        tblGrid.remove(gc)
    
    # Add new gridCols
    for w in widths_cm:
        gc = OxmlElement('w:gridCol')
        gc.set(qn('w:w'), str(int(w * 360000)))  # cm → EMU/20
        tblGrid.append(gc)
```

### Answer Cell Bottom Border

```python
def set_answer_cell_writing_line(cell):
    """Add light gray bottom border as writing guide."""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    
    tcBorders = OxmlElement('w:tcBorders')
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), '6')
    bottom.set(qn('w:color'), 'AAAAAA')
    tcBorders.append(bottom)
    tcPr.append(tcBorders)
    
    # Bottom vertical alignment
    vAlign = OxmlElement('w:vAlign')
    vAlign.set(qn('w:val'), 'bottom')
    tcPr.append(vAlign)
```

### Stripping Answers from Existing Files

When processing existing 口算 files that have answers embedded:
1. Detect answer columns: every 3rd column (index 2, 5, 8 for 9-col; index 2 for 3-col)
2. Clear answer cell content (paragraphs cleared, replaced with "作答" header or blank)
3. Remove answer summary table (detected by header pattern matching)
4. Set column widths at grid level
5. Save back as student version
6. Copy original with answers to parent folder as `*-口算-答案.docx`

### Full Processing Script Pattern

```python
for f in student_dir:
    if '口算' not in f or '答案' in f:
        continue
    
    # 1. Copy original to parent as answer key
    answer_name = f.replace('口算', '口算-答案')
    shutil.copy2(src, parent_dir / answer_name)
    
    # 2. Strip answers from student copy
    doc = Document(src)
    for table in doc.tables:
        nc = len(table.columns)
        widths = W9 if nc == 9 else W3
        set_grid_widths(table, widths)
        
        for row in table.rows:
            for ci, cell in enumerate(row.cells):
                is_answer = (nc == 9 and ci % 3 == 2) or (nc == 3 and ci == 2)
                if is_answer:
                    set_answer_cell_writing_line(cell)
                    if row is header:
                        set_cell_text(cell, '作答')
    
    # 3. Remove answer summary tables
    for ti in reversed(find_answer_tables(doc)):
        remove_table(doc, ti)
    
    doc.save(src)
```

## Font Spec

- Body: 11pt 宋体 (SimSun) — readable for Grade 3-5
- Problem numbers: same font, no need to differentiate
- Header "序号"/"题目"/"作答": 9pt, lighter weight OK
- Cell padding: paragraph space_before=Pt(3), space_after=Pt(3)
