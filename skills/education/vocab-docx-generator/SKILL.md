---
name: vocab-docx-generator
description: 从练习材料提取词汇 → 匹配课标 → 查漏补缺 → 生成带拼音/释义的 DOCX 汇总。适用于语文生字词、英语单词表。
category: education
---

# 教育词汇表 DOCX 生成器

通用 workflow：从佳乐的练习材料（DOCX/MD）中提取词汇，匹配课标（沪教版/部编版），查漏补缺，生成格式化 DOCX 放桌面。

## 触发条件

- 用户要求"汇总/整理 40天练习中的单词/生字"
- 用户要求"匹配课标/教材，查漏补缺"
- 用户要求"生成词汇表 DOCX，带拼音/中文释义"
- 用户说"像桌面《单词.docx》那样汇总"

## 完整流程

### 1. 定位源材料

```bash
# 常见路径
桌面/佳乐2026暑假-精简版/英语新内容/01-词汇/  # 英语40天词汇
桌面/佳乐暑假完整练习库/                      # 综合练习库
桌面/佳乐2026暑假-精简版/语文新内容/          # 语文
```

### 2. 提取词汇（Python + python-docx）

```python
from docx import Document
import re, glob, os

files = sorted(glob.glob('路径/Day*-词汇-*.docx'))
for f in files:
    doc = Document(f)
    in_vocab_section = False
    for p in doc.paragraphs:
        text = p.text.strip()
        if '单词表' in text or 'Words' in text:
            in_vocab_section = True
            continue
        if in_vocab_section and ('填空' in text or '练习' in text):
            in_vocab_section = False
            continue
        if in_vocab_section:
            # 匹配 "1. word   中文" 或 "  1. word phrase    中文"
            m = re.match(r'^\s*\d+[\.\、\)]\s*([a-zA-Z][a-zA-Z\'\- ]*?)\s{2,}(.+)', text)
            if m:
                eng, chn = m.group(1).strip().lower(), m.group(2).strip()
                words.append({'english': eng, 'chinese': chn})
```

**注意**：多词短语如 "ride a bike"、"surf the Internet" 需要正则支持空格。

### 3. 获取课标参考词汇

**英语**：用知乎搜索 "上海牛津版小学英语词汇表" 或 "沪教版小学各年级英语单词列表"。

```python
# 知乎搜索
mcp__cn_scraper__zhihu_search(keyword="沪教版小学各年级英语单词列表", limit=10)
# 找到文章后，用 CDP websocket 提取（type: article 不能用 zhihu_answer）
```

加载 cn-scraper-mcp skill 获取 CDP 提取流程。

**语文**：上海使用部编版。用知乎搜索 "小学语文生字表 拼音 1-6年级"。

如果平台内容不可用，使用内置知识（部编版生字表是公开标准的）。

### 4. 匹配与补缺

```python
# 构建已覆盖集合
current_set = {w['english'].lower() for w in current_words}

# 找缺失
missing = {eng: chn for eng, chn in reference.items() if eng not in current_set}

# 找拓展（练习有但课标无）
extra = {w['english']: w['chinese'] for w in current_words if w['english'] not in reference}
```

### 5. 生成 DOCX

格式**必须**匹配桌面《单词.docx》样式：

```
01
序号	单词	中文
1	word	释义
2	word	释义
...
```

关键参数：
- 页边距：上下 1.5cm，左右 2cm
- 标题：宋体 18pt 加粗居中
- 正文：宋体 9pt，每 20 词一组
- 组之间空行分隔
- 不同来源用 "← 补缺"、"← 五上预习" 标注
- 末尾加统计页

```python
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

doc = Document()
for section in doc.sections:
    section.top_margin = Cm(1.5)
    section.bottom_margin = Cm(1.5)
    section.left_margin = Cm(2)
    section.right_margin = Cm(2)

# 分组输出，每组 20 词
group_size = 20
for i in range(0, len(words), group_size):
    group = words[i:i+group_size]
    # 组号 + 来源标记
    p = doc.add_paragraph()
    run = p.add_run(f'{group_num:02d}{section_label}')
    run.font.size = Pt(11)
    run.font.bold = True
    
    # 列头
    p = doc.add_paragraph()
    run = p.add_run('序号\t单词\t中文')
    run.font.size = Pt(9)
    run.font.bold = True
    
    # 词条
    for idx, w in enumerate(group, 1):
        p = doc.add_paragraph()
        run = p.add_run(f'{idx}\t{w["english"]}\t{w["chinese"]}')
        run.font.size = Pt(9)
```

### 6. 语文生字表特殊处理

语文需要汉字 + 拼音，格式：
```
序号	汉字	拼音		序号	汉字	拼音		...
1	一	yī		2	二	èr		...
```

每行排 5 个字（5 列）紧凑显示。按年级分组，五上标"（预习）"。

## 输出路径

所有文件放桌面：`/mnt/c/Users/admin/Desktop/佳乐XXX词汇汇总.docx`

## 常见平台搜索策略

| 内容类型 | 搜知乎 | 搜小红书 | 搜微博 |
|------|:--:|:--:|:--:|
| 英语词汇表/单词表 | ✅ 最佳 | ❌ 少 | ❌ 少 |
| 语文生字表 | ✅ | ❌ | ❌ |
| 教材版本确认 | ✅ | - | - |
| 教辅推荐 | ✅ | ✅ | - |

## 五上预习扩展模式

当用户要求 "五年级上也补进去" 时：

1. 获取五年级上册课标词汇（知乎文章通常包含全年级）
2. 对已合并的 1-4 年级集合做差集，只添加新词
3. 在 DOCX 末尾追加，标注 "← 五上预习"
4. 三部分结构：40天练习词（前段）→ 1-4年级补缺（中段）→ 五上预习（末段）

```python
# 合并顺序
merged = list(current_words)  # 40天练习词
merged += [w for eng, w in sorted(g14_missing.items())]  # 1-4年级补缺
merged += [w for eng, w in sorted(g5_new.items())]  # 五上预习
```

## 语文词语表生成

除生字表（单字+拼音）外，用户还可能需要每课词语表（多字词组）。

格式：`序号\t词语\t拼音`，每行 4 词组，按年级分组。

```python
# 词语数据格式
("词语", "pinyin"),  # e.g. ("观潮", "guān cháo")
```

词语按年级独立列表：`g1_words`, `g2_words`, `g3_words`, `g4_words`, `g5_words`

完整 DOCX 结构：第一部分生字表 → 第二部分词语表 → 统计页。

## 文言文/古诗词背诵资料生成

用户可能要求 "五上古诗词和文言文都列出来"。

输出格式：
- 标题：《篇名》+ 作者朝代
- 正文每行一句，段间空行
- 每首附【主题】注释
- 末尾附背诵清单（□ 勾选框）+ 日积月累名言

``python
# 数据格式
poems = [
    ('示儿', '陆游〔宋代〕', [
        '死去元知万事空，',
        '但悲不见九州同。',
        ...
    ], '【主题】爱国诗。'),
]
```

## 注意事项

- 上海语文现在用**部编版**（非沪教版），英语用**沪教版牛津**
- 桌面《单词.docx》的 tab 分隔格式必须精确复制
- 文件名用中文，直接放桌面
- 每组 20 词，与 40 天练习的每日 10-20 词结构对应
- 缺失词里会有大量基础功能词（a/an/the/is/am/are 等）——都补上保证完整性
- python-docx 写中文字体需同时设 `run.font.name = '宋体'` 和 `run._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')`
- 中文引号在 Python 字符串中可能引发语法错误，用 `\u300a` `\u300b`（书名号）或 `\u3014` `\u3015` 替代
- 部编版五上必背：古诗词7首（示儿/题临安邸/己亥杂诗/山居秋暝/枫桥夜泊/长相思/渔歌子）+ 文言文2篇（少年中国说/古人谈读书）+ 日积月累2组
