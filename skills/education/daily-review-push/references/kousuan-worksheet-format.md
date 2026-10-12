# 口算练习题排版标准

当生成或处理口算（mental math）练习题 DOCX 时，必须遵循以下排版规则。

## 核心原则

1. **学生卷绝对不能含答案** — 答案列必须清空，答案汇总表必须删除
2. **作答格要够大** — 至少 2cm 宽，方便小学生手写
3. **拼音等参考大文件不放入每日文件夹** — 在参考资料中统一存放，不重复打印

## 表格列宽标准

口算表常见两种布局：

### 9列布局（3题/行）
```
序号(0.8cm) | 题目(3.0cm) | 作答(2.0cm) | 序号(0.8cm) | 题目(3.0cm) | 作答(2.0cm) | ...
```
总宽约 17.4cm，适配 A4。

### 3列布局（1题/行）
```
序号(0.8cm) | 题目(9.0cm) | 作答(5.5cm)
```

## python-docx 列宽设置（关键）

**必须用表格级 gridCol，不能用单元格级 tcW。** 单元格级 tcW 不可靠，设置后实际渲染宽度仍为 0。

```python
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

def set_grid_widths(table, widths_cm):
    """Set column widths at table grid level — this is what actually works."""
    tblGrid = table._tbl.find(qn('w:tblGrid'))
    if tblGrid is None:
        tblGrid = OxmlElement('w:tblGrid')
        table._tbl.insert(0, tblGrid)
    
    # Clear existing
    for gc in tblGrid.findall(qn('w:gridCol')):
        tblGrid.remove(gc)
    
    # Set new
    for w in widths_cm:
        gc = OxmlElement('w:gridCol')
        gc.set(qn('w:w'), str(int(w * 360000)))  # cm → EMU/100
        tblGrid.append(gc)
```

## 答案剥离流程

口算 DOCX 的特征：表格中每 3 列一组（序号|题目|答案），最后还有一个独立答案汇总表。

### 步骤

1. **清空答案列**：每行第 3、6、9... 列（0-indexed: 2、5、8...）的文本清空
2. **改表头**：答案列表头从"答案"改为"作答"
3. **删除答案汇总表**：识别末尾只有"题号|答"列的纯答案表，从 XML 中移除
4. **添加书写底线**：在作答格底部加浅灰色边框（`color=AAAAAA`），引导书写位置

```python
def style_answer_cell(cell, is_header=False):
    """Style an answer cell with bottom border as writing guide."""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    
    tcBorders = OxmlElement('w:tcBorders')
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), '6')
    bottom.set(qn('w:color'), 'AAAAAA')
    tcBorders.append(bottom)
    tcPr.append(tcBorders)
    
    # Bottom-align text
    vAlign = OxmlElement('w:vAlign')
    vAlign.set(qn('w:val'), 'bottom')
    tcPr.append(vAlign)
    
    # Set header "作答" or clear content
    for p in cell.paragraphs:
        p.clear()
        if is_header:
            run = p.add_run('作答')
            run.font.size = Pt(9)
```

### 识别答案汇总表

答案汇总表特征：表头只有"题号"和"答"（或"答案"），不含"题目"列。遍历 `doc.tables` 检查第一行表头：

```python
def is_answer_summary(table):
    header = [cell.text.strip() for cell in table.rows[0].cells]
    joined = ''.join(header)
    return '答' in joined and '题目' not in joined
```

用 `table._element.getparent().remove(table._element)` 从 XML 中删除。

## 注意事项

- **字体**：11pt 宋体，行间距上下各 3pt
- **不要用 python-docx 删除列**：库不支持，会破坏表格结构。清空单元格内容即可。
- **处理完验证**：遍历所有作答格，确认残留答案数为 0
- **家长版保留原文件**：直接复制原始带答案的文件到家长卷/，重命名加"答案"后缀
- **大文件不要重复**：拼音速成方案 PDF（600KB+）、贴墙版等参考文件只在参考资料目录存一份，不要在每日文件夹中重复
