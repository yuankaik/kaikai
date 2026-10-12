# 词汇掌握率检测与错词追踪 · 完整工作流

## 一、检测表生成

### HTML 模板结构

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="utf-8">
<style>
@page { size: A4; margin: 1.5cm 1.2cm; @bottom-center { content: counter(page); font-size: 8pt; color: #999; } }
body { font-family: "Noto Sans CJK SC", sans-serif; font-size: 9pt; line-height: 1.55; }
h1 { font-size: 16pt; text-align: center; border-bottom: 2px solid #333; }
h2 { font-size: 13pt; page-break-before: always; border-bottom: 1px solid #aaa; }
h3 { font-size: 10.5pt; color: #555; }
h4 { font-size: 9pt; color: #777; font-style: italic; }
table { border-collapse: collapse; width: 100%; font-size: 9pt; }
th, td { border: 0.5pt solid #bbb; padding: 2pt 4pt; }
th { background: #e8e8e8; }
th:nth-child(1) { width: 30pt; text-align: center; }
th:nth-child(4), th:nth-child(5), th:nth-child(6) { width: 32pt; text-align: center; }
td:nth-child(4), td:nth-child(5), td:nth-child(6) { text-align: center; font-size: 14pt; }
.summary { background: #f0f0f0; padding: 6pt 10pt; border-left: 3pt solid #666; }
.new-badge { color: #d00; font-weight: bold; }
</style></head>
<body>
<h1>上海牛津英语 1-5年级 词汇掌握率检测表</h1>
<div style="text-align:center; font-size:8pt; color:#999;">✓ 已掌握 | ✗ 未掌握 | △ 半熟</div>
<!-- 逐册生成：h2(年级册) → h3(Module) → table → summary -->
</body></html>
```

### 表格行格式

```html
<!-- 单元标题行 -->
<tr><td colspan="6"><h4>Unit 1 Hello</h4></td></tr>
<!-- 词汇行 -->
<tr><td>1</td><td>hello</td><td>你好</td><td>☐</td><td>☐</td><td>☐</td></tr>
<!-- 汇总行 -->
<div class="summary">本册共 <b>94</b> 词 | 掌握：___/___ | 掌握率：___%</div>
```

### PDF 转换

```python
import weasyprint
weasyprint.HTML(filename='词汇掌握率检测表.html').write_pdf('词汇掌握率检测表.pdf')
```

输出约 850KB（含完整 Noto CJK 字体嵌入）。

---

## 二、错词追踪 JSON Schema

```json
{
  "_说明": "佳乐英语错词追踪数据库",
  "_状态说明": {
    "new": "新发现，尚未练习",
    "practicing": "已生成短文练习，待复测",
    "mastered": "复测通过，已掌握",
    "stubborn": "多次练习仍未掌握"
  },
  "records": [
    {
      "date": "2026-06-22",
      "grade": "5A",
      "source": "检测表拍照",
      "words": [
        {"en": "typhoon", "cn": "台风", "status": "new"},
        {"en": "environment", "cn": "环境", "status": "new"}
      ]
    }
  ],
  "summary": {
    "total_wrong_ever": 0,
    "currently_new": 0,
    "currently_practicing": 0,
    "currently_stubborn": 0,
    "total_mastered": 0
  }
}
```

### 状态流转规则

```
new ──→ practicing ──→ mastered
  │         │
  └─────────┴──→ stubborn (3次练习仍未掌握)
```

- `new`: vision 首次识别到 ✗/△
- `practicing`: 已为这些词生成短文练习
- `mastered`: 复测时标记为 ✓
- `stubborn`: 连续3次标记为 ✗（需重点攻克方案）

### 每次更新时

1. 追加新的 `records[]` 条目
2. 更新 `summary` 各计数
3. 对已有词：匹配 `en` 字段，更新 `status`

---

## 三、Vision 识别流程

### 用户触发

用户通过微信发送检测表拍照 → Hermes 收到 `[image]` → agent 调用 `vision_analyze`

### 识别 Prompt 要点

```
这是小学英语词汇掌握率检测表。请识别：
1. 当前是哪一册（标题中的年级/学期）
2. 逐一读取每一行：英文单词、中文释义、三个勾选框的标记（✓/✗/△/空白）
3. 只返回 ✗ 和 △ 的词（英文+中文）
4. 格式：英文 | 中文 | 标记
```

### Vision 回退

- 主模型有 vision → 直接用
- 无 vision → 走 `auxiliary.vision` 配置（Ollama minicpm-v:8b 在 Windows）
- Ollama vision 慢：小图 ~32秒，大图可能超时。分页拍照（一页一张）更可靠

### 识别后操作

1. 解析 vision 返回的错词列表
2. 读取 `错词追踪.json`
3. 追加 records，更新 summary
4. 写回 JSON
5. 返回确认：列出识别的错词 + 总计

---

## 四、短文生成

### 参数

- 目标错词：5-10个/篇
- 长度：80-150词
- 难度：对应佳乐当前水平（四年级→五年级过渡，D水平）
- 主题：体育(游泳/篮球)、动物(龟)、冒险故事（贴合兴趣）

### 短文结构

```
Title: [有趣的标题]

[短文正文，粗体标注目标错词]

中文翻译：
[逐句翻译]

重点词：
| 英文 | 中文 | 教材册 |
|------|------|--------|
| word | 释义 | 5A |
```

### 练习方式

1. 朗读短文（2遍）
2. 圈出粗体目标词
3. 看英文说中文
4. 看中文说英文
5. 遮住短文默写目标词

---

## 五、文件路径规范

所有文件放 Windows 桌面（WSL 中对应 `/mnt/c/Users/admin/Desktop/`）：

```
shanghai-exams/
├── 牛津英语1-5年级词汇总表.md
├── 牛津英语1-5年级词汇总表.pdf
├── 词汇掌握率检测表.html
├── 词汇掌握率检测表.pdf
└── 错词追踪/
    ├── workflow.md
    └── 错词追踪.json
```
