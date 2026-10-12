---
name: jiale-english-tracker
description: >
  佳乐英语四模式追踪系统。A=词汇检测(1044词)→错词短文。B=技能检测(57点)→专项练习。
  C=原版阅读(My Weird School等)→圈词入库+艾宾浩斯自动排程。D=每日复习提醒。
  自动识别照片类型。核心原则：佳乐动作越少越好，只读+圈词，不写不填不查。
trigger: >
  英语检测表照片/书页圈词照/能力诊断表照；"英语错词/检测/单词/复习/今天复习什么/复习完成/未识别"等。
  术语：用"未识别词汇"禁用"错词"（孩子有压力）。
---

# 佳乐英语四模式追踪

## ⚠️ 核心原则（每次任务开始前检查）

1. **极简原则**：佳乐的动作越少越好。只读+铅笔圈词（每页≤2个）。不写、不猜、不填卡、不查字典。
2. **术语**：一律用"未识别词汇"，禁用"错词"（有压力）。文件、回复、表格全部用这个词。
3. **Plan先行**：涉及新设计/新流程时，先Plan分析→列出确认问题→等用户回复→再执行。不要自说自话直接开干。

---

## 模式速查

| 模式 | 触发 | 输入 | 输出 |
|---|---|---|---|
| A 词汇检测 | 拍词汇检测表 | ✓/✗/△标记 | 错词→短文练习 |
| B 技能检测 | 拍能力检测表 | ✅/❌标记 | 错点→专项练习 |
| C 原版阅读 | 拍圈词的书页 | 铅笔圈出的词 | 入库+艾宾浩斯排程 |
| D 每日复习 | 说"今天复习什么" | 无 | 今日待复习清单 |

---

## 模式C：阅读书页（My Weird School等原版书）

**⚠️ 阅读水平警告 (2026-07-03)：** My Weird School 对佳乐当前水平太早（AR 3.5-4.0 vs 佳乐1A级别）。详见 `references/reading-level-gap-2026-07-03.md`。建议先用牛津阅读树 Level 4-6 或 Fly Guy 过渡。

**触发：** 照片是英文书页（有段落文字），某些词被铅笔圈出。

**识别 prompt：**
```
vision_analyze(image_url=photo_path, question="这是一页英文书。有些单词被铅笔圈出来了。请只列出被圈出的单词，每个词附上它所在的完整句子。格式：单词|句子。如果没看到圈词，回答'无圈词'。")
```

**存储流程：**

1. 用 `execute_code` 追加到 `未识别词汇追踪.json`：
```python
import json
from datetime import date, timedelta

# Load tracker
with open("/mnt/c/Users/admin/Desktop/shanghai-exams/未识别词汇追踪.json") as f:
    data = json.load(f)

today = date.today().isoformat()
intervals = [1, 2, 4, 8, 15]  # Ebbinghaus intervals in days from learning

# New word entry
new_word = {
    "id": data["stats"]["total"] + 1,
    "date": today,
    "book": "#1 Miss Daisy Is Crazy!",
    "chapter": "Ch1",
    "page": "P3",
    "word": "weird",
    "sentence": "Miss Daisy is weird.",
    "meaning": "奇怪的",
    "reviews": 0,
    "next_review": (date.today() + timedelta(days=intervals[0])).isoformat(),
    "review_dates": []
}

data["words"].append(new_word)
data["stats"]["total"] = len(data["words"])
data["stats"]["learning"] = sum(1 for w in data["words"] if w["reviews"] < 5)
data["stats"]["mastered"] = sum(1 for w in data["words"] if w["reviews"] >= 5)

with open(tracker_path, "w") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
```

2. 同步更新 `未识别词汇总表.md`（追加表格行，更新顶部今日待复习）。

3. 回复用户：`+N词入库 · 下次复习：明天`。

---

## 模式D：每日复习

**触发：** 用户说"今天复习什么""复习""复习提醒"。

**流程：**
1. 读 `未识别词汇追踪.json`
2. 筛选 `next_review <= today AND reviews < 5`
3. 输出复习列表（序号/日期/书名/单词/释义）
4. 更新 `未识别词汇总表.md` 顶部「今日待复习」区域

**回复格式：**
```
📅 今日复习（6月23日）
1. weird — 奇怪的 (#1 Ch1 P3)
2. principal — 校长 (#1 Ch1 P5)
...
共N词 · 预计3分钟
```

---

**触发：** 用户说"复习完成""复习完了""已复习"。

**流程：**
1. 将所有 `next_review <= today` 的词 review 次数+1
2. 按艾宾浩斯间隔设置下一个 `next_review`
3. `reviews >= 5` → 标记为 mastered，不再排程
4. 更新 JSON + MD 总表

**回复：** `✅ 复习完成 · N词已安排下次复习 · M词已掌握`

---

## 文件位置

| 文件 | 路径 |
|---|---|
| 词汇总表 | `C:\\Users\\admin\\Desktop\\shanghai-exams\\牛津英语1-5年级词汇总表.md` |
| 检测表PDF | `C:\\Users\\admin\\Desktop\\shanghai-exams\\词汇掌握率检测表.pdf` |
| 错词JSON | `C:\\Users\\admin\\Desktop\\shanghai-exams\\错词追踪\\错词追踪.json` |
| 工作流说明 | `C:\\Users\\admin\\Desktop\\shanghai-exams\\错词追踪\\workflow.md` |
| 暑假每日练习 | `C:\\Users\\admin\\Desktop\\佳乐2026暑假-精简版\\第X周\\学生卷\\DayXX-英语-词汇.docx` |
| 暑假语法练习 | `C:\\Users\\admin\\Desktop\\佳乐2026暑假-精简版\\第X周\\学生卷\\DayXX-英语-语法.docx` |
| 暑假阅读练习 | `C:\\Users\\admin\\Desktop\\佳乐2026暑假-精简版\\第X周\\学生卷\\DayXX-英语-阅读.docx` |
| 暑假写作练习 | `C:\\Users\\admin\\Desktop\\佳乐2026暑假-精简版\\第X周\\学生卷\\DayXX-英语-写作.docx` |

WSL 路径前缀：`/mnt/c/Users/admin/Desktop/`

## 暑假每日练习体系（2026-06-25 新增）

每日英语 = 4份练习纸（60分钟），对标沪教版四下期末卷9大语法考点：

| 模块 | 时长 | 内容 | 轮换 |
|------|------|------|------|
| 词汇 | 15min | 10词/天，按主题 | 学校/家庭/食物/动物/身体/天气/节日/日常/职业/自然 |
| 语法 | 25min | 8-10题/天 | 一般现在时→进行时→介词→疑问句→词性转换→There be→祈使/否定→综合（5轮） |
| 阅读 | 20min | 短文+非连文本 | 20篇短文+5篇非连（课表/天气图/海报/菜单/地图） |
| 写作 | 20min | 仿写→命题 | 前10天模板填空，后10天命题写作 |

40天语法轮换详情：
- Day 1,9,17,25,33 = 一般现在时 (do/does, have/has, 三单)
- Day 2,10,18,26,34 = 现在进行时 (am/is/are + V-ing)
- Day 3,11,19,27,35 = 介词 (in/on/at/under/behind)
- Day 4,12,20,28,36 = 特殊疑问句 (What/Where/When/Whose/How many)
- Day 5,13,21,29,37 = 词性转换 (n→adj, num→ord)
- Day 6,14,22,30,38 = There be 句型
- Day 7,15,23,31,39 = 祈使句/否定句
- Day 8,16,24,32,40 = 综合复习

---

## 步骤1：接收照片并识别

```
vision_analyze(image_url=photo_path, question="仔细查看这张词汇检测表照片。表格有6列：序号|英文单词|中文释义|✓|✗|△。请逐一读取每一行，列出所有在 ✗ 列或 △ 列有标记（如打勾、涂黑、画圈等）的单词。对每个错词，输出格式：英文单词|中文释义|标记类型(✗或△)。忽略✓列有标记的行。如果整个检测表中没有任何✗或△标记，回答'全部掌握'。")
```

**照片识别要点：**
- 一张照片可能包含多个单元/模块
- 注意手写标记可能不规范（涂黑、打叉、画圈都算✗）
- 如果是△标记（犹豫/半熟），按✗同等处理，但标注为"△"
- 如果照片模糊看不清，请用户重拍

---

## 步骤2：提取错词列表

从 vision 返回结果中解析错词，格式化为 Python 列表：

```python
wrong_words = [
    {"en": "typhoon", "cn": "台风", "mark": "✗"},
    {"en": "resource", "cn": "资源", "mark": "△"},
]
```

---

## 步骤3：推断年级/册

根据检测表照片中的标题（如"3年级上册 (3A)"），或让用户确认。如果无法从照片推断，用 `clarify` 工具询问。

已知的年级册映射：
- `1A`, `1B`, `2A`, `2B`, `3A`, `3B`, `4A`, `4B`, `5A`, `5B`

---

## 步骤4：更新错词追踪JSON

用 `execute_code` 执行以下逻辑：

```python
import json
from datetime import date

tracker_path = "/mnt/c/Users/admin/Desktop/shanghai-exams/错词追踪/错词追踪.json"

with open(tracker_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# 新检测记录
today = date.today().isoformat()
grade = "5A"  # 替换为实际检测的册
new_words = [
    {"en": "typhoon", "cn": "台风", "status": "new"},
    {"en": "resource", "cn": "资源", "status": "new"},
]

# 去重：如果该词已标记为 mastered，不改状态
# 如果该词已是 new/practicing/stubborn，保持原状态
for w in new_words:
    existing = None
    for record in data["records"]:
        for rw in record["words"]:
            if rw["en"] == w["en"]:
                existing = rw
                break
    if existing:
        if existing["status"] == "mastered":
            # 重新出现的错词，重置为new
            existing["status"] = "new"
    else:
        # 新错词
        pass  # already "new"

# 添加本次记录
record = {
    "date": today,
    "grade": grade,
    "words": new_words,
}
data["records"].append(record)

# 更新统计
all_words = []
for r in data["records"]:
    for w in r["words"]:
        all_words.append(w)

data["summary"]["total_wrong_ever"] = len(all_words)
data["summary"]["currently_new"] = sum(1 for w in all_words if w["status"] == "new")
data["summary"]["currently_practicing"] = sum(1 for w in all_words if w["status"] == "practicing")
data["summary"]["currently_stubborn"] = sum(1 for w in all_words if w["status"] == "stubborn")
data["summary"]["total_mastered"] = sum(1 for w in all_words if w["status"] == "mastered")

with open(tracker_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(json.dumps(data["summary"], ensure_ascii=False))
```

**去重规则：**
- 同一英文单词在已 "mastered" 状态 → 重置为 "new"（说明忘了）
- 同一英文单词在 "new"/"practicing"/"stubborn" → 保持原状态
- 同一英文单词在同一次检测中重复出现 → 只记录一次

---

## 步骤5：报告用户

生成中文摘要：

```
📊 本次检测结果（5年级上册 5A）

✗ 未掌握：N 个
△ 半熟：M 个

错词列表：
1. typhoon — 台风
2. resource — 资源
...

📈 累计统计
总错词数：X  |  新发现：Y  |  练习中：Z  |  顽固：W  |  已掌握：V

💡 建议：需要我现在用这些错词生成短文练习吗？
```

---

## 步骤6（可选）：生成错词短文

用户说"生成短文""练习"时触发。

**短文生成规则：**
1. 从 JSON 中取 status=="new" 或 "practicing" 的词（优先取当前检测的册）
2. 每篇短文涵盖 5-10 个目标错词
3. 短文长度 80-150 词
4. 目标词在短文中至少出现 1 次（可加粗标注）
5. 内容贴合佳乐兴趣：运动（游泳、篮球）、动物（龟）、冒险故事
6. 不要超出对应年级的语法难度
7. 附中文翻译 + 目标词列表
8. 输出为 MD 文件，自动转换 PDF 放到桌面

**短文模板：**
```
# 错词练习短文 — {date}

## 目标词
| 英文 | 中文 |
|---|---|
| word1 | 释义1 |
| ... | ... |

## 短文
(English passage with target words in **bold**)

## 中文翻译
(Chinese translation)

## 练习任务
1. 朗读短文 3 遍
2. 圈出所有目标词
3. 看英文说中文（家长检查）
4. 看中文说英文（家长检查）
```

生成后存入 `C:\Users\admin\Desktop\shanghai-exams\错词短文\` 目录。

---

## 步骤7（可选）：更新掌握状态

用户说"复测""掌握了""通过了"时触发。

用 `execute_code` 更新 JSON 中指定单词的 status：
- `new` → `practicing`（已练习短文）
- `practicing` → `mastered`（复测通过）
- `practicing` → `stubborn`（多次复测仍错）
- `stubborn` → `mastered`（终于攻克）

重新计算 summary 并保存。

---

## 跨册检测支持

如果用户一次测了多册（多张照片），逐张处理，分别记录。每次检测记录独立的 `grade` 字段。

---

## 模式E：批量暑假词汇生成（无vision回退方案）

**触发场景：** 用户上传词汇摸底PDF但vision不可用（DeepSeek不支持多模态，Ollama不可达），或用户明确说"大部分都是不会"不需要逐词检测。

**策略：** 不逐词识别，直接基于沪教版1-5年级词汇总表，按年级递进批量生成40天计划。

### 数据源
- 词汇总表：`C:\Users\admin\Desktop\shanghai-exams\牛津英语1-5年级词汇总表.md`（1044词，1454行）
- 如PDF可提取文字（PyMuPDF），优先OCR；否则回退到总表全量覆盖

### 生成标准
```
785词 = 1-4年级全部词汇（1A:85, 1B:68, 2A:81, 2B:76, 3A:109, 3B:114, 4A:125, 4B:127）
40天 × 约20词/天 = Day01-39每天20词，Day40余5词
排列：1A→1B→2A→2B→3A→3B→4A→4B（按年级难度递进）
去重：同英文单词取最低年级的释义
```

### 输出结构（两个DOCX）

**学生卷** `佳乐英语每日单词-学生卷.docx`：
- Day 01-40，每2天一页
- 每天包含：
  - 📝 单词表（序号|单词|中文释义，蓝色加粗英文）
  - 📖 嵌入式短文（100-200词，当天10词自然嵌入，用【】在家长版标注）
  - ❓ 读后小测（3题轮换：人物/地点/圈词/造句/复述）
  - 🔁 艾宾浩斯复习提示（D+1/3/7/15/30回顾词列表）

**家长答案** `佳乐英语每日单词-家长答案.docx`：
- 同上 + 短文中生词标红 + 参考答案 + 家长抽测指南

### 短文设计要求
- 每篇独立故事，不跨天依赖
- 主题覆盖：学校/家庭/运动/动物/自然/城市/旅行/节日/梦想
- 当天10词在文中自然出现≥1次（不堆砌）
- 语法控制在对应年级水平（前10天用简单句，逐渐加入复合句）
- 贴合佳乐兴趣：运动(游泳/篮球)、动物(龟)、冒险

### 页面排版
- 字体：微软雅黑，正文11pt，标题14pt
- 单词表：3列表格（蓝底白字表头，交替行无底色）
- 短文：11pt正文，段落间0.5cm缩进
- 灰色提示文字：9pt，用于复习提示和使用说明

### 首次生成参考脚本
`/tmp/gen_english_vocab.py`（2026-06-27生产版本，含400词+40篇短文+艾宾浩斯逻辑）
→ 如有调整需求，修改ALL_WORDS和READING_PASSAGES后重跑

### 去重规则
- 同英文单词在总表中跨年级出现时，取最低年级的释义
- 1A/1B基础词优先（hello/hi/goodbye等），即使简单也不能跳过

---

## 诊断结果 → 暑假练习生成

诊断结果直接驱动 `jiale-summer-practice` 技能的练习生成策略：

| 诊断结果 | 练习策略 |
|----------|----------|
| 词汇大面积空白（>60%❌） | 400词从零方案（1A→5A递进，10词/天+嵌入式短文） |
| 语法大面积❌ | 8考点×5轮集中训练，不新增内容 |
| 听力薄弱 | 当前40天练习中听力为0，需额外补充 |
| 个别词不认识（<20%❌） | 错词入库→艾宾浩斯→短文练习 |

佳乐当前诊断结果：单词基本全要背 → 使用模式E全量生成（785词全覆盖1-4年级，20词/天×40天）。见 `jiale-summer-practice`。

**铁律：英语词汇检测如果vision不可用（DeepSeek不支持多模态），不要反复尝试，直接走模式E全量生成。**

---

## 语法订正本（订正本）处理

当照片是英语订正本/练习题（非词汇检测表），有红笔批改时，**转交 `correction-ocr` 技能处理**，不走本技能的词汇检测流程。

correction-ocr 会：vision_analyze 识别红笔标记 → 提取错题 → 确认 → 写入 `错题追踪/错题追踪.json`。

本技能专注于词汇检测表、书页圈词、能力检测表。

## 注意事项

- **Vision 可用（2026-07-01 验证）**：主模型 DeepSeek 不支持多模态，但 auxiliary vision (claude-sonnet-4-6, aicodewith.com) 对打印体英语材料识别准确。**不要依赖 Ollama minicpm-v（CPU太慢）**，直接调用 vision_analyze 走辅助 vision。
- 如果 vision 返回结果模糊或不完整，请求用户重拍（光线充足、正对拍摄）。
- 首次使用前确认 JSON 文件存在，如不存在则初始化。
- **WSL 网络不可用时**，用 browser 工具通过百度等搜索词汇相关内容，不用 curl。
- 文件名、路径全部使用 `/mnt/c/Users/admin/Desktop/` 前缀。
- **PDF扫描版（无文字层）→ PyMuPDF (fitz) 转PNG → vision_analyze**。如果vision也不可用，回退到模式E全量生成。
- ⚠️ **不要用 send_message 推微信**。iLink 限频无法可靠规避。复习结果在聊天中直接回复，每日复习由 `daily-review-push` cron（15:00）生成桌面 DOCX。
