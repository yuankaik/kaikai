# DOCX 排版优化与批量修复

针对佳乐暑假 40 天 DOCX 的排版问题修复记录。

## 答案泄漏修复

### 问题
原始文件中"答案与解析"段落混入学生卷。简单删除导致**误删阅读短文二**——因为答案区内部有 `───` 分隔线，被误判为停止信号。

### 正确做法
```
答案区结构:
  ─── 分隔线
  答案与解析          ← 触发删除
  第1题               ← 删除
  ─── 分隔线           ← 不停止！
  第2题               ← 删除
  ...
  ─── 分隔线
  如果第X题错了...      ← 家长指导，也要删
  ─── 分隔线
  阅读短文二：...       ← 真正的停止信号
```

**停止条件只能是：** `阅读短文` 开头 或 模块标题（🌅📐等 emoji 开头），不能是分隔线。

### 代码模式
```python
if text == '答案与解析':
    in_answer = True
    to_remove.add(child)
elif in_answer:
    if text.startswith('阅读短文') or is_module_header(text):
        in_answer = False  # 停止
    else:
        to_remove.add(child)  # 包括分隔线、题号、家长指导
```

## 家长指导语残留

即使答案区已删，还有零散的家长指导语散布在题目间：

| 模式 | 示例 |
|------|------|
| 批改指导 | "请鼓励孩子大胆表达"、"批改核心" |
| 重写任务 | "孩子重写任务"、"重写时在每道" |
| 评分提示 | "不要求和标准答案完全一致"、"不必追求" |
| 错因引导 | "如果第X题错了..." |

这些不影响答题但会在打印件上暴露给佳乐。统一关键词匹配删除。

## 答题空行

### 题目格式多样性
40 天中有 4 种题目编号格式：
- `第1题（信息提取题）` — 中文括号
- `题1：信息提取题` — 冒号格式
- `第1题【句子理解题】` — 中文方括号
- `第4题` — 无标签（少数天）

### 插入策略
必须先**清除题目间所有已有空行**，再**统一插入恰好 2 行**。否则会堆叠成 3-4 行。

```python
# 步骤1：找到题目块的 body_end（最后一个非空内容段）
# 步骤2：删除 body_end 和下一个元素之间的所有空段
# 步骤3：在 body_end 后插入恰好 2 个空段
```

**注意：** 有些题目的题干内含示范答案（"第一步…"、"原因①…"、"表面意思…"），body_end 检测需要跳过这些，否则空行会加到错误位置。约 91% 题目可自动化，剩余 9% 需人工判断。

## 页面规格

### A4 修正
原始文件为 US Letter（8.5×11"=215.9×279.4mm），国内打印必须 A4（210×297mm）。

```python
from docx.shared import Cm
A4_W = int(21.0 * 360000)  # EMU
A4_H = int(29.7 * 360000)
section.page_width = A4_W
section.page_height = A4_H
```

### 边距
上下 13mm，左右 18mm。可用宽度 174mm。

## 字体规范

| 用途 | 字体 | 字号 |
|------|------|------|
| 中文全部 | 宋体 | 8-16pt |
| 正文 | 宋体 | 11pt |
| 模块标题 | 宋体加粗 | 12pt |
| 分隔线 | 宋体 | 8pt |
| 舒尔特数字 | Arial | — |

**Arial 只用于舒尔特表格数字**，这是正确的——Arial 数字比宋体清晰。审计时不要误报。

## 模块分隔线

语法：XML 级插入带底部边框的空段落。

```python
def make_separator():
    p = OxmlElement('w:p')
    pPr = OxmlElement('w:pPr')
    # center align + tight spacing
    pBdr = OxmlElement('w:pBdr')
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), '6')       # 线宽
    bottom.set(qn('w:color'), 'BBBBBB')  # 浅灰
    pBdr.append(bottom)
    pPr.append(pBdr)
    p.append(pPr)
    # 必须加空 run，否则无效
    r = OxmlElement('w:r')
    rPr = OxmlElement('w:rPr')
    r.append(rPr)
    p.append(r)
    return p
```

只给顶层模块加（含"分钟"或"舒尔特"的 emoji 行），跳过子标题（"📝 今日单词"、"📖 短文阅读"）。

## DOM 操作陷阱

| 陷阱 | 现象 | 解决 |
|------|------|------|
| addprevious 后索引失效 | 后续元素位置偏移 | 每次插入后重建 children 列表 |
| 用 id() 追踪元素 | 跨 DOM 树可能失效 | 用 id→element map 在操作前建立 |
| body.remove() 失败 | 元素已不在树中 | try/except 包裹 |
| 空段落无 run | 渲染异常 | 始终加 `<w:r><w:rPr/></w:r>` |

## WSL 文件操作

所有操作直接读写 `/mnt/c/Users/admin/Desktop/...`，python-docx save() 可能遇 PermissionError（Word 打开文件时）。解决：先写 `/tmp/` 再 `shutil.copy2`。

## 舒尔特表组防跨页（链式 keepNext）

### 问题背景
`cantSplit` 只防止单个表格内部行跨页断裂，`keepNext` 只绑定"用时→表"一对。当一组 3 个舒尔特表靠近页面底部时，Word 仍可能把第 2 或第 3 个表挤到下一页，导致整组分页断裂。即使所有表都有 `cantSplit` 且所有"用时"都有 `keepNext`，组内空段落缺少 `keepNext` 导致链不完整。

### 修复策略
对每组连续的舒尔特表，形成不可分割的链：
1. 每个舒尔特表 → `cantSplit`（防行内断裂）
2. 每个"用时"段落 → `keepNext`（防标签与表分离）
3. **组内表间空段落 → `keepNext`**（链式整体保护，关键！）

```python
# 检测舒尔特表分组（间隔 ≤3 个元素的视为同组）
# 对每组：
for g in range(len(group) - 1):
    for mid_idx in range(group[g] + 1, group[g + 1]):
        mid_child = children[mid_idx]
        if is_paragraph(mid_child) and not has_keep_next(mid_child):
            add_keep_next(mid_child)
```

### 判别舒尔特表
3×3 或 6×6 表格，所有单元格内容为纯数字（单字符）。

## 批量修复参考

完整代码见会话记录 `/tmp/final_v3.py` 及各中间版本。核心流程：备份→删答案→减空白→加分隔线→加空行→校验。每次修复后必须用 `scripts/verify_40days.py` 验证。
