# DOCX 合并为每日单文件 · 完整模式

当需要将多个 DOCX 合并为一份每日练习卷时，使用此模式。

## 核心教训

**只复制 `doc.paragraphs` 会丢失表格！** 口算等内容的题目在表格中，必须遍历 `element.body`。

## 合并函数

```python
from docx import Document
from docx.oxml.ns import qn

def append_docx(dst, src_path):
    """复制整个DOCX内容（段落+表格）到目标文档"""
    if not src_path or not os.path.exists(src_path):
        return
    src = Document(src_path)
    pl = list(src.paragraphs)
    tl = list(src.tables)
    pi = ti = 0
    
    for child in src.element.body:
        if child.tag == qn('w:p') and pi < len(pl):
            sp = pl[pi]; pi += 1
            p = dst.add_paragraph()
            p.alignment = sp.alignment
            for run in sp.runs:
                r = p.add_run(run.text)
                r.bold = run.bold
                r.font.size = run.font.size or Pt(11)
        elif child.tag == qn('w:tbl') and ti < len(tl):
            copy_table(dst, tl[ti]); ti += 1
            dst.add_paragraph()  # spacing after table
```

## 表格复制

```python
def copy_table(dst, src_tbl):
    tbl = dst.add_table(rows=len(src_tbl.rows), cols=len(src_tbl.columns))
    try: tbl.style = src_tbl.style
    except: pass
    for i, sr in enumerate(src_tbl.rows):
        dr = tbl.rows[i]
        for j, sc in enumerate(sr.cells):
            dc = dr.cells[j]
            for px in dc.paragraphs: px.text = ""  # clear default
            first = True
            for para in sc.paragraphs:
                p = dc.paragraphs[0] if first else dc.add_paragraph()
                first = False
                p.alignment = para.alignment
                for run in para.runs:
                    r = p.add_run(run.text)
                    r.bold = run.bold
                    r.font.size = run.font.size or Pt(10)
```

## 答案过滤（学生卷）

60天阅读理解原版文件自带答案（标准答案/评分点/错因标签/家长批改提示），合并到学生卷时必须过滤。

```python
import re

def is_answer_line(txt):
    if not txt: return False
    # 强答案标记
    if any(txt.startswith(k) for k in ['标准答案','评分点','常见错因','错因标签',
        '依据段','家长批改提示','孩子重写任务']):
        return True
    # 评分点项目符号
    if re.match(r'^[•·]\s', txt): return True
    # 分值标注
    if re.match(r'^共\d+分', txt): return True
    # 错因标签
    if re.match(r'^#[^\s]', txt): return True
    # 答案引导
    if re.match(r'如果第\d', txt): return True
    if '答案速查' in txt or '用铅笔画出' in txt or '参考答案' in txt: return True
    if txt.startswith('示例开头'): return True
    return False

# 使用时还需要块级跳过：
skip_block = False
for para in source_paragraphs:
    if txt.startswith('家长批改提示') or txt.startswith('孩子重写任务'):
        skip_block = True; continue
    if skip_block and ('───' in txt or txt.startswith('短文')):
        skip_block = False
    if skip_block or is_answer_line(txt):
        continue
    # ... copy to student doc
```

## 文件锁定处理

WSL 写 Windows 桌面文件时，Word 打开的文件会 `PermissionError`。
```python
try:
    doc.save(path)
except PermissionError:
    # 先删再写
    os.remove(path)
    doc.save(path)
```

## 口算 MD 双格式解析

口算源文件有 table 格式（`|序号|题目|答案|`）和 list 格式（`1. 题目`）两种，解析时需同时处理：

```python
# Table 格式检测
if line.startswith('|') and line.endswith('|') and '---' not in line:
    cells = [c.strip() for c in line.split('|')[1:-1]]
    if '题目' not in cells and '序号' not in cells:
        table_rows.append(cells)

# List 格式检测
if re.match(r'^\d+[\.\、]', line):
    list_items.append(line)
```

## 口算按比例取样

不要取前N题（只练热身模块），应从每个子模块按比例取：
```python
TARGET_Q = 40
for i, (sec_name, questions) in enumerate(sections):
    if i == len(sections) - 1:
        take = remaining  # 最后一个模块拿剩下的
    else:
        take = max(1, int(TARGET_Q * len(questions) / total_q))
    take = min(take, len(questions))
```

## 英语阅读材料来源优先

⚠️ 优先使用题库真题，不自行编造：
- 道客巴巴提取的阅读/范文（`五年级特级教师资源-英语/`）
- 昂立/绿光教育测试卷（`其他教育品牌/` 下含阅读理解题）
- 牛津英语词汇总表（1044词）
- 不足时告知用户，不要 AI 生成替代
