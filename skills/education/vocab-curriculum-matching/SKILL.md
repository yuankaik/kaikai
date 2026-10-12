---
name: vocab-curriculum-matching
description: 将练习词汇与课标词汇表匹配，查漏补缺生成完整汇总 DOCX。适用于任何学科/年级。
---

# 词汇课标匹配 — 查漏补缺工作流

将已有练习中的词汇与课标参考词汇表进行比对，找出缺失词，合并生成完整 DOCX。

## 使用场景

- 暑假/寒假练习词汇 vs 教材课标词汇，查漏补缺
- 任何有"已有词表 + 参考词表"的匹配场景

## 工作流

### 1. 收集已有词汇

从练习材料中提取所有词汇（DOCX/PDF/Markdown），去重。
样例脚本见 `references/extract-vocab-from-docx.py`。

### 2. 获取课标参考词汇

三种来源优先级：

| 优先级 | 来源 | 方法 |
|:--:|------|------|
| 1 | 知乎文章 | `mcp__cn_scraper__zhihu_search` → CDP websocket 提取文章正文 |
| 2 | 小红书笔记 | `mcp__cn_scraper__xiaohongshu_search` → `xiaohongshu_note` |
| 3 | 自建知识库 | 如教材词汇表已掌握，直接用 `references/` 中的词汇表 |

**搜索关键词模板**：`{教材版本} {学段} 英语 词汇表 汇总`
例如：`沪教版牛津 小学英语 1-4年级 单词表`

**⚠️ 知乎文章 vs 回答：** `zhihu_answer` 只适用于 `type: "answer"` 的结果。对于 `type: "article"` 的内容（多为词汇表/汇总类长文），需用 CDP websocket 从已登录的 Chrome 提取。方法是先 `PUT http://127.0.0.1:9251/json/new?{article_url}` 打开页面，再用 websocket 连接 `webSocketDebuggerUrl` 发送 `Runtime.evaluate` 获取 `document.body.innerText`。详见 `elementary-routine-design` 技能中关于多平台搜索的说明。

**多平台验证：** 知乎 + 小红书 + 微博三平台同步搜索，交叉验证课标词汇的准确性。如果两个以上平台数据一致，可采信。

### 3. 解析参考词汇

从文章正文中解析 `英文 \t 中文` 格式的词汇对。
样例见 `references/parse-reference-vocab.py`。

### 4. 比对匹配

```python
# 构建集合
current_set = {w['english'].lower() for w in current_words}
reference_set = {eng.lower() for eng in reference_words}

missing = reference_set - current_set   # 课标有但练习缺
extra = current_set - reference_set     # 练习有但课标无（拓展词）
```

### 5. 生成 DOCX

输出格式参照桌面 `单词.docx` 的样式：
- 组头 `01` `02` ...
- 表头 `序号\t单词\t中文`
- 每组 20 词
- 前段为已有词汇，后段标注"← 补缺"

```python
from docx import Document
from docx.shared import Pt, Cm
from docx.oxml.ns import qn

doc = Document()
# ... 参考 references/generate-merged-docx.py
doc.save('/mnt/c/Users/admin/Desktop/XX英语词汇汇总-完整版.docx')
```

## 沪教版牛津英语参考数据

上海小学英语（沪教版牛津，五四制）：

| 年级 | 册数 | 词汇量（约） |
|:--:|------|:--:|
| 1年级 | 1A + 1B | ~120 词 |
| 2年级 | 2A + 2B | ~120 词 |
| 3年级 | 3A + 3B | ~150 词 |
| 4年级 | 4A + 4B | ~150 词 |
| **合计** | | **~540 词** |

关键特征：五年级开始难度跳升，1-4 年级以基础名词/动词/形容词为主，含大量功能词（a/an/the/is/am/are/this/that 等）。

## 输出物

- `{名称}-词汇汇总-完整版.docx`：合并后的完整词表，可直接打印
- 末尾附统计页：参考总量、已覆盖数、补缺数、拓展词数

## 陷阱

- **DOCX 格式**：词汇文件中的英文词组（如 `ride a bike`、`surf the Internet`）用普通正则 `\S+` 匹配不到，需用 `[a-zA-Z][a-zA-Z\'\- ]*?` 匹配含空格的英文
- **分组标记**：功能词（a/an/the/I/you/he/she）如果佳乐已掌握，可在打印时跳过对应的组
- **拓展词**：练习中超出课标的词（如 astronaut, volcano）不是"超标"，对阅读有益，保留不删
