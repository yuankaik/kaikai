# 阅读理解答案重排映射流程

## 场景

手里有一份**合并版答案文档**（如 `1.docx`，内含第1天～第60天的全部阅读理解答案），
需要按**暑假每日练习**（Day02～Day41）的顺序重排，
让每篇练习的答案出现在对应天数下，打印即可逐天核对。

## 标准流程（4步）

### 1. 解析源文档的 section 边界

源文档的每一天以 `第N天` 段落开头。扫描全部段落，
建立 `{day_num: para_start_index}` 映射。

```python
sections = {}
for i, p in enumerate(all_paras):
    m = re.match(r'第(\d+)天\b', p.text.strip())
    if m:
        sections[int(m.group(1))] = i
```

### 2. 提取暑假练习的文章标题

遍历暑假 `学生卷/DayXX-全部练习.docx`，从 `语文阅读` 板块用 `《(.+?)》` 正则提取文章标题，
去重保留顺序：

```python
titles = re.findall(r'《(.+?)》', reading_section_text)
clean = [t for t in titles if len(t) > 1 and len(t) < 60 and '.md' not in t]
summer_articles[day] = list(dict.fromkeys(clean))
```

### 3. 精确匹配：文章标题 → 源文档 section

**关键原则：用 EXACT 文章标题匹配，不用 fuzzy/keyword。**
Fuzzy 匹配会产生假阳性（如 "妈妈" 出现在多个 section 中）。

```python
# 对源文档每个 section，构建文章索引
for p_day, (start, end) in section_ranges.items():
    sec_text = '\n'.join(all_paras[i].text for i in range(start, end))
    for art in re.findall(r'《(.+?)》', sec_text):
        article_index[art.strip()] = p_day

# 对每个暑假天，查找每篇文章的确切位置
for s_day, articles in summer_articles.items():
    for art in articles:
        if art in article_index:
            p_day = article_index[art]
            # 找到了
```

### 4. 拆分多文章 section（关键！避免重复）

**一个问题 section 可能含多篇文章**（如"短文一：竞选班长"+"短文二：我们的菜园"在同一第10天）。
如果 Day02 和 Day03 都映射到第10天，整段会被输出两次。

**解法：** 在 section 内找 `短文X[：:]` 边界，只取当天需要的子区间：

```python
def find_article_spans(start, end):
    spans = []
    for i in range(start, end):
        m = re.match(r'短文[一二三四五六七八九十]+[：:]\s*(.+)', all_paras[i].text.strip())
        if m:
            spans.append((i, m.group(1).strip()))
    
    for j, (head_idx, title) in enumerate(spans):
        span_end = spans[j+1][0] if j+1 < len(spans) else end
        article_index[title] = (p_day, head_idx, span_end)
```

输出时只拷贝当天文章对应的 `[para_start, para_end)` 区间。

## 常见坑

| 坑 | 原因 | 解法 |
|----|------|------|
| 假匹配 | fuzzy/keyword 匹配（如 "妈妈" 出现在多个 section） | 用文章标题精确匹配 |
| section 重复 | 同 section 含多篇文章，多个暑假天映射到同一 section | 短文边界拆分 |
| 标题无《》括号 | 部分文章用 `短文一：标题` 格式 | 同时匹配 `短文X[：:]` 正则 |
| 背诵/拓展篇不匹配 | 暑假练习含《少年中国说》等背诵篇，不在阅读答案中 | 标注 unmatched，不硬塞错误答案 |

## 验证方法

输出后抽查 5 个关键天（最早、中间、最晚、多文章天），
确认每篇文章标题确实出现在对应 section 中：

```python
for s_day, p_day in spot_checks:
    assert summer_article_title in section_text[p_day]
```

## 本次实操数据（2026-07-14）

- 源文件：`C:\Users\admin\Desktop\1.docx`（48 sections，第1～60天，有跳跃）
- 暑假练习：Day02～Day41（40天）
- 最终匹配率：34/40 全匹配，6 天有缺失（背诵/拓展篇）
- 输出文件：`C:\Users\admin\Desktop\佳乐语文阅读理解答案汇总.docx`
- 重排脚本：`/mnt/c/Users/admin/Desktop/reorder_answers.py`（V4 终版）
