# A4 竖版打印布局优化

对 40 天暑假练习 DOCX 的布局优化方法论。2026-06-29 实战总结。

## 优化检查清单

生成或修改 40 天文件后，按此清单逐项验证：

1. **[ ] 答案泄漏** — 学生卷不应含答案/家长指导语
2. **[ ] 空白段落** — 连续空行 ≤ 1，不浪费纸
3. **[ ] 模块分隔** — 顶层模块间有清晰分隔线
4. **[ ] 家长卷完整** — 家长卷答案内容未误删

## 答案泄漏检测与修复

### 泄漏关键词（学生卷不应出现）

```python
LEAK_KW = [
    "答案与解析", "标准答案", "参考答案",
    "答案格式说明", "方便家长精准指导",
    "不要求和标准答案", "与标准答案完全一致",
    "没有标准答案",
]
```

### 泄漏原因

`append_doc(dst, path, skip_answers=True)` 的过滤不完全可靠。语文阅读模块源 DOCX 中的"答案与解析"段落可能漏过过滤逻辑。

### 修复方法

1. 定位泄漏段落（关键词匹配）
2. 从泄漏起始位置连续标记，直到遇到下一个模块标题或文档结束
3. 从 XML body 中删除泄漏段落

### ⚠️ 只修学生卷，别动家长卷

这是本 session 最大的教训。用关键词匹配时务必限定 scope 为 `学生卷` 文件。家长卷本身就应该包含"标准答案""参考答案"等关键词。

**安全做法：**
```python
if "学生卷" in file_path:
    remove_answer_leaks(doc)
# 家长卷跳过，不动
```

## 空白段落压缩

### 检测

```python
from docx import Document
doc = Document(path)
blank_runs = []
run_start = None
for i, p in enumerate(doc.paragraphs):
    if not p.text.strip():
        if run_start is None:
            run_start = i
    else:
        if run_start is not None and i - run_start >= 2:
            blank_runs.append((run_start, i - run_start))
        run_start = None
```

### 修复

遍历 XML body children，标记连续空段，保留第一个，删除其余：

```python
body = doc.element.body
children = list(body)
# 找到连续空段 runs，删除 run[1:] 部分
for elem in extras_to_remove:
    body.remove(elem)
doc.save(path)
```

## 模块分隔线

### 顶层模块识别规则

只给真正的顶层模块加分隔线，不给子标题加。

**匹配条件：**
1. 段落以模块 emoji 开头（🔢📐🧠📝📖🌅🌍🔤）
2. 包含"分钟"或"舒尔特"

**排除项（子标题，不加线）：**
- `📝 今日单词` — 英语模块的子板块
- `📖 短文阅读` — 英语模块的子板块
- `📖 阅读短文一/二` — 语文阅读内
- `📝 本日目标` — 语文基础内

### 实现（python-docx XML 操作）

```python
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

def add_separator_before(doc, element):
    """在 element 前插入浅灰横线"""
    p = OxmlElement('w:p')
    pPr = OxmlElement('w:pPr')
    
    jc = OxmlElement('w:jc')
    jc.set(qn('w:val'), 'center')
    pPr.append(jc)
    
    spacing = OxmlElement('w:spacing')
    spacing.set(qn('w:before'), '80')
    spacing.set(qn('w:after'), '40')
    pPr.append(spacing)
    
    pBdr = OxmlElement('w:pBdr')
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), '6')       # 线宽
    bottom.set(qn('w:space'), '4')
    bottom.set(qn('w:color'), 'BBBBBB')  # 浅灰
    pBdr.append(bottom)
    pPr.append(pBdr)
    
    p.append(pPr)
    r = OxmlElement('w:r')
    r.append(OxmlElement('w:rPr'))
    p.append(r)
    
    element.addprevious(p)
```

### 遍历 body children 而非 paragraphs

`doc.paragraphs` 是动态代理，在遍历期间修改会引发索引漂移。应使用：

```python
body = doc.element.body
children = list(body)  # 快照，不受后续插入影响
for child in children:
    tag = child.tag.split('}')[-1]
    if tag == 'p':
        # check and add separator
```

## 答案泄漏精确修复（2026-06-29 关键教训）\n\n### 原始答案区结构\n\n答案区在原始 DOCX 中的典型结构：\n\n```\n─── separator\n答案与解析              ← 触发点\n第1题                   ← 答案内\n─── separator           ← ⚠️ 不是停止信号！\n第2题                   ← 答案内\n─── separator\n...\n第5题\n─── separator\n如果第X题错了：...       ← 家长指导语（也要删）\n─── separator\n阅读短文二：《...》       ← ✅ 这才是停止信号\n```\n\n### ❌ 错误做法：遇分隔线就停\n\n```python\nif is_separator(text):\n    in_answer = False  # BUG! 答案区内部的分隔线不是停止信号\n```\n\n这会导致答案只删到第一个分隔线，后面的 \"第2题\"~\"第5题\" 和\"阅读短文二\"之间的内容残留。\n\n### ✅ 正确做法：只在下个阅读短文或模块标题处停\n\n```python\nif is_reading_passage_header(text) or is_module_header(text):\n    in_answer = False  # 正确：只有真正的文档结构边界才停\n    continue\n```\n\n### 额外需要删除的家长指导语\n\n```python\n# 独立出现在问题区后的家长指导（不在答案区内）\nif '如果第' in text and '题错了' in text:\n    to_remove.add(child)\n\nGUIDE_KW = [\n    '方便家长精准指导', '不要求和标准答案',\n    '与标准答案完全一致', '没有标准答案',\n    '答案格式说明', '家长批改',\n]\n```\n\n## 阅读题答题空行插入\n\n### 题目格式变体（4 种）\n\n| 格式 | 示例 | 出现的天 |\n|------|------|----------|\n| 中文括号 | `第1题（信息提取题）` | Day1-2, 28-40 |\n| 冒号型 | `题1：信息提取题` | Day3-25 |\n| 方括号 | `第1题【句子理解题】` | Day26-27, 30 |\n| 无标签 | `第4题`（无题型标注） | Day40 个别题 |\n\n### 检测规则\n\n```python\ndef is_question(text):\n    return bool(re.match(r'^(第\\d+题|题\\d+)[（(【：:].*|^第\\d+题$|^题\\d+[：:]', text))\n```\n\n裸 `第N题`（无题型标签）需额外检查：只有紧接题干内容才算真题，紧接分隔线的是答案区残留，跳过。\n\n### 插入逻辑\n\n1. 在语文阅读 section 内找到所有 question header\n2. 确定 body_end = 题干最后一段（不包含已有的空行）\n3. 删除 body_end 和 next element（下一题/分隔线）之间的现有空行\n4. 在 body_end 后插入恰好 2 个空段（11pt 字号，保持与正文字号一致）\n\n```python\n# 创建空段落（与 body 字号一致）\ndef make_blank():\n    p = OxmlElement('w:p')\n    pPr = OxmlElement('w:pPr')\n    rPr = OxmlElement('w:rPr')\n    sz = OxmlElement('w:sz')\n    sz.set(qn('w:val'), '22')  # 11pt\n    rPr.append(sz)\n    pPr.append(rPr)\n    p.append(pPr)\n    p.append(OxmlElement('w:r'))\n    return p\n```\n\n### ⚠️ 复杂题干处理\n\n部分日期的题干内含示范答案段落（如 \"第一步——分头侦查...\"\"原因①...\"\"表面意思...\"\"深层意思...\"\"对比①...\"）。这些不是答案泄漏，是题目设计的组成部分。\n\n对这些题目，body_end 检测可能不准确（可能选到示范答案段落而非纯题干）。结果：约 9% 的题目空行数偏差 ±1 行（380 题中 35 题），可接受。\n\n如需精确处理，可在 body_end 检测时跳过含这些关键词的段落：\n```python\nEMBEDDED_HINT_KW = ['第一步', '第二步', '第三步', '原因①', '原因②', \n                     '对比①', '对比②', '表面意思', '深层意思']\n```\n\n## 批量修改安全守则

1. **先备份**：`shutil.copy2(path, backup_path)` 后再改
2. **限 scope**：明确只改学生卷还是家长卷，不要一刀切
3. **先小样**：先改 1-2 天验证效果，确认无误再批处理 40 天
4. **改后验证**：跑 `scripts/verify_40days.py` 确认未引入新问题

## A4 页面尺寸修复

原始生成的文件使用 US Letter（8.5×11 英寸），国内打印需改为 A4（210×297mm）。

```python
from docx.shared import Cm

A4_W = int(21.0 * 360000)   # 210mm = 7560000 EMU
A4_H = int(29.7 * 360000)   # 297mm = 10692000 EMU

for section in doc.sections:
    section.page_width = A4_W
    section.page_height = A4_H
```

验证公式：`section.page_width / 36000` = 毫米值。边距保留 ≥13mm（上下）、≥18mm（左右）确保打印不出血。

## 字体尺寸规范化

原始文件中部分空行被设为 4pt 或 6pt（肉眼不可见但影响间距一致性）。修复方法：

```python
from docx.shared import Pt

for p in doc.paragraphs:
    for r in p.runs:
        if r.font.size and r.font.size < Pt(8):
            r.font.size = Pt(8)  # 最小可读尺寸
```

同样处理表格内的 runs。检查范围：段落 + 所有表格的所有单元格。
