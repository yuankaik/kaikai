# 可打印参考文档生成模式 (Printable Reference DOCX)

当用户要求生成"背诵清单""必背篇目""知识点汇总"等可打印参考文档时，遵循此模式。

## ⚠️ 核心原则：必须含完整内容

用户说的："你不能光给我一个标题。内容也要给我。我的需求是打印出来，拿到手就可以给佳乐背的。"

→ 任何可打印教育资料都必须包含**完整正文**，不是仅标题/索引。打印=拿到手直接用。

## A4 打印布局参数

```python
from docx.shared import Pt, Cm

# 页面
section.page_width = Cm(21.0)
section.page_height = Cm(29.7)
section.top_margin = Cm(1.8)
section.bottom_margin = Cm(1.5)
section.left_margin = Cm(2.0)
section.right_margin = Cm(2.0)
```

## 防跨页保护（三大机制）

### 1. keepLines — 每段正文不拆分
```python
from docx.oxml import OxmlElement
for p in doc.paragraphs:
    pPr = p._element.get_or_add_pPr()
    keep = OxmlElement('w:keepLines')
    pPr.append(keep)
```

### 2. keepNext — 标题与正文不分离
```python
# 仅对诗歌/篇目标题（bold + 短文本 < 60字）
for p in doc.paragraphs:
    is_bold = any(r.bold for r in p.runs)
    text = p.text.strip()
    if is_bold and len(text) < 60 and text:
        pPr = p._element.get_or_add_pPr()
        kn = OxmlElement('w:keepNext')
        pPr.insert(0, kn)
```

### 3. 显式分页 — 长篇文章前分页
```python
# 正文 > 350字的长篇前自动加分页符
for i, p in enumerate(doc.paragraphs):
    if len(p.text.strip()) > 350 and i > 0:
        prev = doc.paragraphs[i-1]
        if any(r.bold for r in prev.runs) and len(prev.text.strip()) < 80:
            new_run = OxmlElement('w:r')
            br = OxmlElement('w:br')
            br.set(qn('w:type'), 'page')
            new_run.append(br)
            prev._element.insert(0, new_run)
```

## 字体规格

| 元素 | 字号 | 样式 |
|------|------|------|
| 篇目标题 | 10.5pt | 加粗 |
| 正文内容 | 10pt | 常规 |
| 作者/朝代 | 9pt | 灰色 |
| 大标题 | 13-18pt | 黑体加粗 |

## 文档结构

```
封面标题页
  ↓ 分页符
主体内容（按年级/类别分章）
  - 每章标题: h1 (13pt 黑体)
  - 每节标题: h2 (11.5pt 蓝色)
  - 条目: 序号 + 标题(加粗) + 作者 + 正文
```

## 验证清单

生成后检查：
- [ ] 页面为 A4 (210×297mm)
- [ ] 所有条目含完整正文（不止标题）
- [ ] 长篇文章（木兰诗、岳阳楼记等）前有分页符
- [ ] keepLines + keepNext 已设置
- [ ] Windows 桌面路径: `/mnt/c/Users/admin/Desktop/`
