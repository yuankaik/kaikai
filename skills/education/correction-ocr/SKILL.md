---
name: correction-ocr
description: >-
  订正本/试卷错题 OCR 识别流水线。两步走：vision 预判分类（可跳过）→ Pix2Text OCR → 结构化入库。
  自动区分红笔批改 vs 原始文字，提取错题信息写入每日复习追踪.json。
  注意：Tesseract 中文不可用（已废弃），纯靠 Pix2Text。
trigger: >
  用户发送订正本/试卷/错题照片（微信或本地文件），或说"识别错题/OCR/扫描订正本"。
  自动触发：照片 + 提到"订正/错题/试卷/批改/红笔"等关键词。
---

# 订正本错题 OCR 识别流水线

## 核心思路

纯 OCR（Tesseract/Pix2Text）做不到两件事：
1. 区分红笔批改 vs 原始黑字
2. 识别手写订正内容

解决：**vision 看图 → OCR 取字 → 规则合并** 三步走。

## 三步流水线

### 第1步：Vision 预判（可选，失败时跳过）

**目的：** 看图说话，输出结构化信息。识别红笔批改区域。

**调用：** `vision_analyze(image_url, question=预判prompt)`

**⚠️ 常见失败（两种）：**

1. **vision 不可用时降级**：直接跳过 vision，用 Pix2Text OCR 全量文字（2026-09-16 起 deepseek-flash 已支持原生 vision，此降级很少触发）。

2. **辅助 vision 模型在中转站不存在**：`auxiliary.vision.model` 填的型号（如 `claude-sonnet-4-20250514`）在代理站不支持，返回 HTTP 400 `模型不存在`。修复：查中转站可用型号列表（aicodewith.com 见 `/zh/dashboard/pricing`），更新 `~/.hermes/config.yaml` 中 `auxiliary.vision.model`，重启 gateway。降级：跳过 vision，直接 Pix2Text。

（Ollama 已删除 2026-09-16，本地 vision 不再考虑。本地 OCR 唯一路径是 Pix2Text。）

详见到 devops/ocr-tools 技能中的 vision 备用方案。

**预判 prompt 模板：**
```
这是一张学生订正本/试卷照片。请分析并输出：

1. 科目：数学/语文/英语/其他
2. 内容类型：订正本/试卷/作业本/书页圈词
3. 红笔标记位置：描述红笔批改在页面的哪个区域（上/中/下/左/右）
4. 红笔标记内容：逐条列出被红笔打叉、圈出、或订正的内容，原文抄下来
5. 错误类型：计算错误/错别字/语法错误/阅读理解/其他
6. 手写/打印：哪些是打印体，哪些是手写

输出格式：
科目: xxx
类型: xxx
红笔区域: xxx
红笔内容:
- 内容1
- 内容2
...
错误类型: xxx
```

**关键：** 让 vision 专注描述"看到了什么"，不做 OCR（它不擅长精确文字识别）。

### 第2步：OCR 提取文字

⚠️ **只用 Pix2Text，不要用 Tesseract。** Tesseract 对中文完全不可用（输出乱码）。

**Pix2Text CLI（推荐，最稳定）:**
```bash
source ~/ocr_env/bin/activate
p2t predict -i '<图片路径>'
```
⚠️ **p2t 必须带子命令 `predict -i`！** `p2t <图片>` 会报 `No such command`。正确用法：`p2t predict -i <图片>`。
p2t 子命令：`predict`（OCR识别）、`serve`（HTTP服务）、`evaluate`（性能评估）。
首次运行自动下载模型（~500MB含DocLayout-YOLO+cnocr+RapidOCR+MFD+MFR）。OCR 结果打印到 stdout 的 `Outs:` 段落后。

**p2t 对中文试卷效果好（80-90%），但对英文混排试卷输出严重畸变**——中文OCR引擎强行解析英文文字导致乱码。
此时改用 **Tesseract `-l eng`** + PIL 预处理（灰度化→2x放大→95%品质JPEG）。

**p2t 超时处理：** 首次运行需下载多个模型，`execute_code` 300s 可能不够。如遇超时，用 `terminal(background=true, notify_on_complete=true)` 后台运行。

**Pix2Text Python API**（版本可能变化，备用）:
```python
from pix2text import Pix2Text
p2t = Pix2Text()
text = p2t.recognize_text(image_path)  # 纯文字模式
# 或
result = p2t.recognize(image_path)  # 混合模式（含公式）
```

### 第3步：结构化提取

**输入：** vision 分析结果 + Tesseract 文本 + Pix2Text 文本

**处理逻辑：**

1. **对齐红笔区域**：vision 说的红笔位置 → 在 OCR 结果中定位对应行
2. **提取错题条目**：每道红笔标记的错题提取为一条记录
3. **生成 JSON 条目**：按 daily-review-push 技能格式

**提取规则：**
- 数学错题：提取 原题 + 错误答案 + 正确答案（如果有订正）
- 语文错字：提取 错字 + 正确字
- 英语错句：提取 错误句子 + 正确句子
- 无法确定答案的：留空 answers 字段，标记 needs_review=true

**输出格式（每条）：**
```json
{
  "id": <自增>,
  "subject": "math|chinese|english",
  "type": "error|character|word|sentence|formula",
  "date": "YYYY-MM-DD",
  "source": "订正本 | 试卷 | 来源描述",
  "content": "原题或错误内容",
  "context": "错因或上下文",
  "meaning": "正确答案或正确写法",
  "reviews": 0,
  "next_review": "",
  "review_dates": []
}
```

## 完整流程脚本模板

```python
#!/usr/bin/env python3
"""订正本 OCR 流水线"""
import json, os, sys
from datetime import date, timedelta
from PIL import Image
import pytesseract
from pix2text import Pix2Text

# === 配置 ===
TRACKING_FILE = "/mnt/c/Users/admin/Desktop/shanghai-exams/每日复习追踪.json"
EBBINGHAUS_INTERVALS = [1, 2, 4, 8, 15]  # D+1, D+3, D+7, D+15, D+30

# === 第1步：Vision 预判（需在外部先调用 vision_analyze） ===
# vision_result = { "subject": "math", "red_areas": [...], ... }

# === 第2步：双引擎 OCR ===
def ocr_both(image_path):
    """Tesseract + Pix2Text 双引擎"""
    img = Image.open(image_path)
    
    # Tesseract
    tess_text = pytesseract.image_to_string(img, lang='chi_sim')
    
    # Pix2Text
    p2t = Pix2Text()
    p2t_text = p2t.recognize_text(image_path)
    
    return tess_text, p2t_text

# === 第3步：结构化入库 ===
def merge_and_save(vision_result, tess_text, p2t_text):
    """合并结果并写入 JSON"""
    items = []
    
    # 根据 vision 的红笔区域描述，在 OCR 文本中定位
    # 提取错题条目...
    
    # 写入 tracking JSON
    with open(TRACKING_FILE, 'r') as f:
        db = json.load(f)
    
    today = date.today().isoformat()
    next_id = max([item.get('id', 0) for item in db['items']], default=0) + 1
    
    for item in items:
        item['id'] = next_id
        item['date'] = today
        next_id += 1
    
    db['items'].extend(items)
    
    with open(TRACKING_FILE, 'w') as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    
    return len(items)
```

## 引擎安装确认

```bash
# Pix2Text（Python — 唯一需要的 OCR 引擎）
pip install pix2text
```

当前环境已全部安装就绪：
- Pix2Text ✅（CLI: `p2t predict -i <image>`）
- deepseek-flash vision ✅（auxiliary.vision，原生多模态）
- Ollama ❌ 已删除（2026-09-16）
- Tesseract ❌ 中文不可用，已废弃

## 已知限制 & 规避

| 限制 | 规避方案 |
|------|---------|
| 手写字识别差 | 只取打印体部分，手写内容由 LLM 推断 |
| 红黑不分 | vision 看图定位红笔区域（如 vision 不可用则跳过，全量 OCR 后 LLM 推断） |
| 数学公式乱 | Pix2Text 可转 LaTeX |
| 拍照模糊 | 引导用户"正对拍摄、光线充足、避免反光" |
| Vision 方案（已定型） | **deepseek-flash 已支持原生 vision**（`model=deepseek-flash` + `api.deepseek.com`，OpenAI 格式传 `image_url` base64），三科错题识别全部准确，可直接替代 Pix2Text 全流程（后者对中英混排畸变、且分不清红笔批改）。⚠️ 必须关 thinking：请求体加 `"thinking":{"type":"disabled"}`，否则思考把 max_tokens 吃光→答案截断、慢约5倍、reasoning 也计费。 |
| Tesseract 中文 | 完全不可用（输出乱码），已从流程中移除 |
| **WeChat send_message 不可靠** | iLink 限频无法规避，3次retry均失败（含5min等待）。**识别完错题后不要调用 send_message 推微信**——直接在聊天中回复结果即可。每日复习推送由 `daily-review-push` cron（15:00）生成桌面 DOCX 处理，不走微信。 |

### Vision-only 快捷路径（打印体英语试卷）

当照片满足以下条件时，**跳过 OCR，直接用 vision_analyze 完成全流程**：
- 打印体英文为主（非手写）
- 红笔批改清晰可见
- 题目结构规整（选择题/填空题/连词成句）

2026-07-01 验证：auxiliary vision (claude-sonnet-4-6, aicodewith.com) 对打印体英语订正本识别准确，能正确提取题号、原题、学生错误答案和红笔订正。此场景下 Pix2Text 反而因中英混排输出畸变，不如 vision 直接。

**vision prompt 模板（英语订正本）：**
```
这是一张学生的英语练习题照片。有红笔批改标记。请仔细分析：

1. 识别所有红笔打叉（✗/❌）或圈出的题目
2. 对每个被标记的题目，提取：原题内容、学生的错误答案、红笔写的正确答案（如有）
3. 如果有红笔写的订正内容，逐字抄下来
4. 题目的编号或序号
5. 注意区分：只有红笔负面标记（打叉、圈出、订正）的才是错题，没有标记的内容跳过
```
| **vision_analyze 400 错误（模型不存在）** | aicodewith.com 中转站不支持 `claude-sonnet-4-20250514`，调用返回 `模型不存在` 400。正确名称是 `claude-sonnet-4-6`（2026-07-01 确认）。快速修复：`sed -i 's/model: claude-sonnet-4-20250514/model: claude-sonnet-4-6/' ~/.hermes/config.yaml && hermes gateway restart`。查可用 Claude 模型：`curl -s https://api.aicodewith.com/v1/models -H "Authorization: Bearer <KEY>" \| python3 -c "import json,sys; [print(m['id']) for m in json.load(sys.stdin)['data'] if 'claude' in m['id']]"`。降级备用：直接用 Pix2Text OCR 全量提取文字。详见 `references/aicodewith-models.md`。 |
| **Pix2Text 对英文卷失效** | Pix2Text 的中文识别模型在处理英文+中文混排试卷时输出严重畸变（中文OCR引擎强行解析英文文字）。此时用 **Tesseract `-l eng`** + 图片预处理（PIL灰度化 + 2x放大 + 95%质量JPEG输出）替代，输出虽不完美但足够辨认题目结构。见 `references/english-test-paper-ocr.md`。 |
| **检测表批量OCR（摸底/诊断场景）** | 处理含✅❌标记的知识点检测表时，Pix2Text对勾叉符号识别不可靠。应采用：批量OCR → 与知识点库JSON逐条对比 → 分三级标记(ok/gap/check) → 输出结构化缺失清单。完整流程见 `jiale-math-tracker` 技能的 `references/bulk-ocr-workflow.md`。 |

### 英文试卷 OCR 特殊处理

当需要分析小学英语期末卷（中英混排，英文为主）时：

```bash
# 1. 预处理：灰度化 + 2x放大
python3 -c "
from PIL import Image
img = Image.open('test.jpg').convert('L')
w, h = img.size
img.resize((w*2, h*2), Image.LANCZOS).save('enhanced.jpg', 'JPEG', quality=95)
"

# 2. Tesseract 英文模式
tesseract enhanced.jpg stdout -l eng
```

Pix2Text 在此场景不可用（输出中文乱码混在英文中）。不要尝试用它处理英文试卷。

## 与 daily-review-push 技能的衔接

本技能输出条目写入追踪 JSON。**注意有两个 JSON 文件：**

| 文件 | 键名 | 使用者 |
|------|------|--------|
| `错题追踪/错题追踪.json` | `records` | jiale-english-tracker（英语词汇/语法错题） |
| `每日复习追踪.json` | `items` | daily-review-push cron（三科每日复习生成） |

录入一条错题的完整链路：
```
微信拍照 → vision_analyze（或Pix2Text OCR）→ 确认 → 写入JSON → 聊天回复结果
                                                              ↓
                                         daily-review-push cron 15:00 → 桌面DOCX
```

⚠️ **不要用 send_message 推微信！** iLink 限频无法可靠规避（详见 daily-review-push 的 iLink 限频灾难记录）。结果直接在聊天中回复，每日复习由 cron 生成桌面 DOCX。

## 快捷路径：微信预分析（WeChat Quick Capture）

当图片通过微信平台发送时，微信可能会预先进行 vision 分析并注入到消息中。
此时可直接使用分析结果，跳过 OCR 步骤。详见 `references/wechat-quick-capture.md`。

**适用：** 普通练习题快速归档（非正式检测表、非红笔订正）
**保存：** 临时存 `~/错题/`，正式检测仍走 JSON 追踪体系

## ⚠️ 关键规则：不是所有内容都是错题！

**照片中只有被明确标记为错的内容才是错题。** 教师/家长用红笔打叉（✗/❌）、圈出、或写"订正"的地方才是需要记录的。没有负面标记的内容 = 已掌握/练习，不应记录为错题。

**工作流强制步骤：**
1. 识别照片中所有 X / ✗ / ❌ / 打叉 / 圈出 / "订正" 标记
2. **仅提取有标记的题目**，向用户列出并确认题号
3. 用户确认后，再写入 JSON / 错题本
4. 明确告知用户：哪些没有标记所以跳过

**典型案例：** 一张练习题照片有 10 道题，其中 3 道被打叉，正确做法：
- ✅ 提取那 3 道打叉的题，让用户确认
- ❌ 把 10 道题全部当错题记录

**用户指令关键词：** "打叉的" = 只处理被标记✗的，"不会的" = 只处理不会的（即打叉的）。

---

## 注意事项

- **先确认再记录**：识别到打叉标记后，先列出题号让用户确认，不要直接入库
- vision 预判优先尝试（deepseek-flash 已支持原生 vision），不可用时直接跳过做全量 OCR，由 LLM 推断错题位置
- 微信传入的图片如已含 vision 预分析结果，直接使用，无需重复调用 vision_analyze
- Tesseract 中文完全不可用（输出乱码），已从流程移除，OCR 只用 Pix2Text
- 无法确定的内容标记 `needs_review=true`，推送到微信时标注"⚠️需人工确认"
- 首次使用 Pix2Text 会下载 ONNX 模型（~130MB），后续缓存
