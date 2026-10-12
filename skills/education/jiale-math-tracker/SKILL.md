---
name: jiale-math-tracker
description: >
  佳乐数学知识点检测追踪系统。当用户通过微信或直接上传数学检测表照片时自动触发。
  用 vision 识别照片中的 ✅❌ 标记，提取错点，存入追踪JSON，
  并可生成针对性练习题。覆盖沪教版1-5年级167个知识点。
trigger: >
  用户发送含数学检测表/知识点表/诊断表的图片，或说"数学错题/数学检测/知识点掌握/数学拍给你"等。
  Plan先行：涉及新设计先Plan分析→等确认→再执行。
---

# 佳乐数学知识点检测追踪

自动化处理数学检测表照片 → 识别错点 → 存入追踪库 → 可生成针对性练习。

---

## 与英语版的区别

| | 英语 | 数学 |
|---|---|---|
| 检测内容 | 词汇（1044词） | 知识点（167点） |
| 检测方式 | 看英文说中文 | 做诊断题→家长对答案 |
| 标记 | ✓/✗/△ | ✅/❌ |
| 练习输出 | 含错词短文 | 针对性练习题（3-5题/点） |

---

## 文件位置

| 文件 | 路径 |
|---|---|
| 知识点库 | `C:\\Users\\admin\\Desktop\\shanghai-exams\\数学知识点库.json` |
| 检测表(新版) | `C:\\Users\\admin\\Desktop\\佳乐2026暑假-精简版\\参考资料\\能力检测工具\\数学能力综合检测表-学生卷.docx` |
| 检测指南(新版) | `C:\\Users\\admin\\Desktop\\佳乐2026暑假-精简版\\参考资料\\能力检测工具\\数学能力综合检测-家长指南.docx` |
| 错点JSON | `C:\\Users\\admin\\Desktop\\shanghai-exams\\错题追踪\\数学错点追踪.json` |
| 暑假每日练习 | `C:\\Users\\admin\\Desktop\\佳乐2026暑假-精简版\\第X周\\学生卷\\DayXX-1-口算-*.docx` + `DayXX-3-数学-*.pdf` |

WSL 前缀：`/mnt/c/Users/admin/Desktop/`

> **2026-06-25:** 新增综合检测表（100分·4板块：计算30+概念30+应用40），含家长评分指南。旧版PDF已删除，使用新版DOCX。

---

## 步骤1：接收照片并识别

### ⚠️ Vision后备方案（重要）

Vision 可能因以下原因失败：
- 主模型（deepseek）不支持 vision
- Ollama `/v1/chat/completions` 端点不支持 `image_url` 格式
- Ollama 原生 `/api/chat` 虽支持但 CPU 太慢（2-5分钟/张）

**此时必须走 OCR 后备方案，不要反复尝试 vision_analyze。**

### 方案A：Vision（优先尝试）

```
vision_analyze(image_url=photo_path, question="仔细查看这张数学知识点检测表照片。表有6列：编号|知识点|诊断题|答案|✅|❌。请逐一读取每一行，列出所有在❌列有标记（打勾、涂黑等）的知识点编号。例如：S3-8、S4-15。如果有多个，全部列出。忽略✅列有标记的行。如果全部是✅，回答'全部掌握'。")
```

### 方案B：Pix2Text OCR（Vision失败时，可靠后备）

```bash
source ~/ocr_env/bin/activate
p2t predict -i '<图片路径>' 2>&1 | sed -n '/^Outs:/,$ p'
```

OCR输出格式：`编号 知识点 题目 答案 标记符号`

**⚠️ OCR限制：**
- ✅/❌ 批改符号识别不可靠（√常被误读为 d/区/品/口/M口）
- 手写答案识别率约70-85%
- 数学公式和中文混排时精度下降

**应对策略：**
1. OCR提取文字 → 与`数学知识点库.json`逐条对比
2. 明确识别出√的 → 标记"已掌握"
3. 有答案但与标准答案不符 → 标记"漏洞"
4. 无答案/OCR混乱 → 标记"需确认"（让家长人工判断）
5. 5年级知识+无答案 → 标记"未学"（合理预期）
6. 输出结构化JSON，含confidence标记

**批量处理15张的完整流程见 `references/bulk-ocr-workflow.md`。**

**注意：**
- 只识别 ❌ 列（数学只有对错两态，不像英语有△半熟）
- 返回知识点编号即可（如 S3-8, S4-21），无需重复诊断题内容
- 如果照片模糊，让用户重拍

---

## 步骤2：匹配知识点详情

根据识别的编号（如 S3-8），从 `数学知识点库.json` 中查找完整的知识点信息：

```python
import json
with open("/mnt/c/Users/admin/Desktop/shanghai-exams/数学知识点库.json") as f:
    kp_db = json.load(f)

wrong_ids = ["S3-8", "S4-21"]  # from vision
wrong_kps = [kp for kp in kp_db if kp["id"] in wrong_ids]
```

---

## 步骤3：推断检测的册

从错点编号推断。如 S3-8 和 S3-12 → 三年级上(3A)。如果跨册（如 S2-x和S3-x混在一起），可能是测了多册。

---

## 步骤4：更新错点追踪JSON

用 `execute_code`：

```python
import json
from datetime import date

tracker_path = "/mnt/c/Users/admin/Desktop/shanghai-exams/错题追踪/数学错点追踪.json"
kp_db_path = "/mnt/c/Users/admin/Desktop/shanghai-exams/数学知识点库.json"

with open(tracker_path, "r", encoding="utf-8") as f:
    data = json.load(f)
with open(kp_db_path, "r", encoding="utf-8") as f:
    kp_db = json.load(f)

today = date.today().isoformat()
detected_ids = ["S3-8"]  # from vision

new_entries = []
for kid in detected_ids:
    kp = next((k for k in kp_db if k["id"] == kid), None)
    if kp:
        new_entries.append({
            "id": kp["id"],
            "grade": kp["grade"],
            "topic": kp["topic"],
            "question": kp["question"],
            "answer": kp["answer"],
            "status": "new"
        })

# 去重
for entry in new_entries:
    existing = None
    for rec in data["records"]:
        for rw in rec["words"]:
            if rw["id"] == entry["id"]:
                existing = rw
                break
    if existing and existing["status"] == "mastered":
        existing["status"] = "new"
    elif not existing:
        pass  # stays "new"

grade = new_entries[0]["grade"] if new_entries else "unknown"
record = {"date": today, "grade": grade, "items": new_entries}
data["records"].append(record)

# 更新统计
all_items = []
for r in data["records"]:
    for it in r["items"]:
        all_items.append(it)

data["summary"]["total_wrong_ever"] = len(all_items)
data["summary"]["currently_new"] = sum(1 for it in all_items if it["status"]=="new")
data["summary"]["currently_practicing"] = sum(1 for it in all_items if it["status"]=="practicing")
data["summary"]["currently_stubborn"] = sum(1 for it in all_items if it["status"]=="stubborn")
data["summary"]["total_mastered"] = sum(1 for it in all_items if it["status"]=="mastered")

with open(tracker_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
```

---

## 步骤5：报告用户

```
📊 数学检测结果（三年级上册 3A）

❌ 未通过：N 个知识点

错点列表：
S3-8 | 多位数乘一位数（进位）| 156×3=？ | 答案：468
S3-21 | ...

📈 累计统计
总错点数：X | 新发现：Y | 练习中：Z | 顽固：W | 已掌握：V

💡 建议：需要我生成针对性练习题吗？
```

---

## 步骤6（可选）：生成针对性练习

用户说"生成练习题""出题""练习"时触发。

**出题规则：**
1. 从 JSON 中取 status=="new" 或 "practicing" 的知识点
2. 每个错点生成 3-5 道同类题（变数字不变题型）
3. 难度梯度：基础(1题) → 巩固(2题) → 变式(1题)
4. 附完整答案
5. 输出为 MD 文件，自动转 PDF

**练习模板：**
```
# 数学针对性练习 — {date}

## 错点回顾
| 编号 | 知识点 | 原错题 | 正确答案 |
|---|---|---|---|
| S3-8 | 多位数乘一位数（进位）| 156×3 | 468 |

## 练习
### S3-8 多位数乘一位数（进位）
- 【基础】147×3 = ?
- 【巩固】238×4 = ?
- 【巩固】365×2 = ?
- 【变式】小明买了3本练习册，每本128页，一共多少页？

## 答案
...
```

保存到 `C:\Users\admin\Desktop\shanghai-exams\错题练习\` 目录。

---

## 诊断结果 → 暑假练习生成

诊断结果直接驱动 `jiale-summer-practice` 技能的练习生成策略：

| 诊断结果 | 练习策略 |
|----------|----------|
| 计算类大面积❌（竖式/进退位/口诀） | 6阶段集中突破模式，每天10-15题同类计算 |
| 个别知识点❌（<5个） | 混合轮换模式，每天1-2题穿插复习 |
| 应用题大面积❌ | 同类应用题集中练3-5天 |
| 五上预习内容❌ | 正常（未学，预期结果） |

**铁律：60分以下学生禁止"每天各类型1题"的撒胡椒面模式。** 必须按阶段集中突破。

详情见 `jiale-summer-practice` 技能中的「内容设计原则」章节。

---

## 步骤7（可选）：更新掌握状态

用户说"复测了""通过了""掌握了"时触发。
用 `execute_code` 更新指定编号的 status。
