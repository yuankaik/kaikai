# 阅读理解答案合并工作流

## 场景

当有多日练习的答案分散在不同文件中（或在一个合并文件但顺序与练习不同），需要按练习日顺序重新排列输出一份可打印的汇总 DOCX。

## 典型问题

- 60天阅读练习答案 → 需要按暑假40天（Day02-Day41）顺序排列
- 合并答案文件（如桌面 `1.docx`）包含所有天内容，但顺序不匹配
- 两套体系文章不完全重叠，需要按文章标题匹配

## 标准流程

### 1. 定位源文件

```bash
find /mnt/c/Users/admin/Desktop -name "1.docx" -o -name "*答案汇总*" 2>/dev/null
ls /mnt/c/Users/admin/Desktop/reading-practice-60days-docx/家长答案/
```

常见源：
- 桌面 `1.docx` — 60天答案合并单文件
- `reading-practice-60days-docx/家长答案/第N天-答案与指导.docx` — 单天分散文件

### 2. 解析合并文件结构

如果源是单文件合并（如 `1.docx`），用 `第N天` 模式识别段落边界：

```python
sections = {}
for i, text in enumerate(paras):
    m = re.match(r'第(\d+)天\b', text.strip())
    if m:
        sections[int(m.group(1))] = i
```

### 3. 提取练习文章标题

从暑假练习的学生卷中提取每天的阅读文章：

```python
doc = Document(path)
text = '\n'.join([p.text for p in doc.paragraphs])
idx = text.find('语文阅读')
section = text[idx:idx+4000]
titles = re.findall(r'《(.+?)》', section)
```

### 4. 模糊匹配

文章标题可能不完全一致（有的有《》有的没有），用关键词匹配：

```python
def match_score(summer_titles, section_text):
    score = 0
    for title in summer_titles:
        if title in section_text:
            score += 10
        else:
            parts = re.findall(r'[\u4e00-\u9fff\w]{2,}', title)
            for part in parts:
                if len(part) >= 3 and part in section_text:
                    score += 3
    return score
```

- score ≥ 10 → 可靠匹配
- score 5-9 → 低置信度，需人工验证
- score < 5 → 不匹配

### 5. 重新排序输出

按 summer_day → source_section_day 映射，逐节复制到输出 DOCX。

### 6. 验证

抽取 5-7 个关键天，确认源段落文本中包含练习的文章标题。

## 常见陷阱

- 匹配分数虚高：关键词碰巧出现在其他文章的上下文中，必须抽查验证
- 文章不在源文件中：约 5-10% 的文章可能完全不存在于答案集中，需标注"请自行批改"
- `1.docx` 与分散文件内容可能不同：桌面 `1.docx` 是手工合并的，通常更完整
