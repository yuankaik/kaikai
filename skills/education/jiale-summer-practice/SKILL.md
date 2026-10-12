---
name: jiale-summer-practice
description: >
  佳乐暑假每日练习生成系统 V3。单一Python脚本生成全部40天DOCX。
  基于诊断：数学计算薄弱（竖式/进退位）、语文字词+阅读弱、英语单词大面积空白。
  核心原则：每天保持多样性（4种数学题类型），题量饱和（不撒胡椒面）。
  五上前20天0预习，后20天5题。英语20词/天覆盖1-4年级全785词。
  V3数学: 竖式10+脱式8+应用6+轮换6=30题/天(前20天) / 35题/天(后20天含预习)。
trigger: >
  用户说"生成每日练习""合并佳乐暑假""更新版面""加入舒尔特"
  "替换作文/英语/口算板块""调整练习版面""优化每日练习"
  "答题空行""A4打印""按模块""检查版式""打印检查""打印前检查"
  "摸底/诊断结果/重新计划/替换练习/改动有多大/针对性练习"
  "计算薄弱/字词弱/单词全要背/竖式/撒胡椒面"
  "数学题太少/再多点数学/加题目/空白页太多/换页符/不要空白页"
  "舒尔特跨页/打印排版"
---

# 佳乐暑假每日练习生成系统 V3

## 架构

**⚠️ `scripts/gen_summer_v3.py` 已丢失（2026-06-30 被技能系统覆盖为占位符）。** 当前工作流：直接修改已有 DOCX 文件（后处理模式），而非从零重新生成。修改型任务参考 `scripts/upgrade_math_v3.py` 的模式。

## 后处理脚本

| 脚本 | 用途 |
|------|------|
| `scripts/upgrade_math_v3.py` | 批量修改已有 DOCX：数学13→30题 + 删换页符 + 舒尔特链式保护 |
| `scripts/verify_40days.py` | 40天内容完整性验证 |

```
佳乐2026暑假-精简版/
  第1周（6月30日-7月4日）/学生卷/Day01~05-全部练习.docx
  ...
  第8周/...
```

## ⚠️ 资源优先原则（最高优先级）

**在动手生成任何内容之前，必须先检查桌面已有资源。** 不要创建模板/占位符内容。

| 内容类型 | 优先使用资源 | 路径 |
|---------|------------|------|
| 语文阅读短文 | 54篇真文 | `/tmp/reading_all_merged.json` (来自旧版暑假备份 + 60天阅读库) |
| 晨读作文范文 | 60篇真文 | `/tmp/essays_60.json` (来自 `五年级作文背诵范文60篇/`) |
| 英语词汇表 | 786词真数据 | `C:\Users\admin\Desktop\shanghai-exams\暑假英语词表_40天分配.json` (2026-07-02解析，与DOCX一致) |
| 英语阅读短文 | 40篇预生成 | `/tmp/eng_passages_all.json` (delegate_task并行生成) |

**来源仓库：**
- 60天阅读理解: `C:\Users\admin\Desktop\reading-practice-60days-docx\学生卷\`
- 作文范文: `C:\Users\admin\Desktop\shanghai-exams\五年级作文背诵范文60篇\`
| 英语词库 | `C:\Users\admin\Desktop\shanghai-exams\暑假英语词表_40天分配.json` (786词，与DOCX一致) |
- 旧版暑假备份: `C:\Users\admin\Desktop\期末卷\暑假作业备份\`

## V3 每天模块结构（2026-06-30 定稿）

| 顺序 | 板块 | 时长 | 来源 |
|------|------|------|------|
| 🔢 口算 | 15min | 代码内嵌生成，40题（20通用+20进退位密集） |
| 📐 数学基础复习 | 30min | 代码内嵌生成，4槽结构（V3: 30题） |
| 📐 数学五上预习 | 0/5min | Day1-20=0题，Day21-40=5题 |
| 🧠 舒尔特×3 | — | 代码内嵌 `make_schulte_table()` |
| 📝 语文基础 | 15min | 代码内嵌，6种类型轮换 |
| 📖 语文阅读 | 30min | 54篇真文循环（`/tmp/reading_all_merged.json`），每题后2空行 |
| 🌅 晨读 | 10min | **60篇真文**循环（`/tmp/essays_60.json`，来自 `五年级作文背诵范文60篇/`），古诗已全砍 |
| 🌍 英语单词 | 25min | 786词（`暑假英语词表_40天分配.json`），20词/天，已接入艾宾浩斯滚动复习 |
| 🌍 英语阅读 | — | 40篇预生成短文（`/tmp/eng_passages_all.json`） |
| 📐 英语语法 | 20min | 代码内嵌，8考点×5轮 |
| 🧠 舒尔特×3 | — | 代码内嵌 |

## 数学 V3：4槽每日结构（30题/天，2026-06-30 定稿）

**核心原则：** 每天4种类型，题量饱和。期末60分→暑假必须逼量，1分钟/题。

| 槽位 | 题型 | V2题数 | V3题数 | 轮换 |
|------|------|--------|--------|------|
| 槽1 | 竖式计算 | 5 | **10** | 6天循环：加→减→乘→除→混合→小数 |
| 槽2 | 脱式/混合运算 | 3 | **8** | 4天循环：脱式→简便→分数→综合 |
| 槽3 | 应用题 | 3 | **6** | 5天循环：归一→余数→几何→单位→综合 |
| 槽4 | 其他轮换 | 2 | **6** | 大数/分数/小数/几何/估算/验算（6种） |

**五上预习：** Day1-20=0题，Day21-40=5题小数乘除+解方程。
**总计：** Day1-20=30题，Day21-40=35题。口算40题不在此列。

## ⚠️ 版面原则：禁止强制换页符

**用户明确要求：** 不要空白页。板块之间让内容自然流动，**禁止**使用 `<w:br w:type="page"/>` 或 `pageBreakBefore` 强制换页。

- ❌ 不要在数学/语文/英语板块间插换页符
- ❌ 不要在舒尔特后插换页符
- ✅ 内容紧凑自然流到下一页
- 数学增容后页面自然更满，更不需要换页

## 英语 V2：20词/天，1-4年级全785词

沪教版1-4年级共785词：1A:85, 1B:68, 2A:81, 2B:76, 3A:109, 3B:114, 4A:125, 4B:127。

| 天数 | 年级 | 词数 |
|------|------|------|
| Day01-04 | 1A | 85词 |
| Day05-07 | 1B | 68词 |
| Day08-11 | 2A | 81词 |
| Day12-15 | 2B | 76词 |
| Day16-20 | 3A | 109词 |
| Day21-26 | 3B | 114词 |
| Day27-32 | 4A | 125词 |
| Day33-40 | 4B | 127词 |

### ✅ 艾宾浩斯已接入（2026-07-02 修复）

每天20个新词通过 `daily-review-push/scripts/add_daily_words.py` 自动写入 `每日复习追踪.json`，由 cron 在每日 10:00 触发。完整机制：

- **词表**：`暑假英语词表_40天分配.json`（桌面 shanghai-exams/，786词，与DOCX验证一致）
- **入库**：add_daily_words.py 每天取当天20词 → 写入 每日复习追踪.json → next_review = D+1
- **复习**：generate_daily_review.py 英语上限200词，艾宾浩斯 D+1/3/7/15/30 五次循环
- **稳态**：100词/天（5间隔×20新词），口头过约5分钟
- **进度**：`每日单词进度.txt` 追踪当前 Day 编号，幂等（同日不重复入库）

**英语阅读短文粗体处理：** 使用 `add_bold_parse_text()` 函数解析 `**word**` 为真实DOCX粗体，不要直接用 `add_text()` 导致星号残留。

```python
def add_bold_parse_text(doc, text, size=11, color=None, indent=None):
    """解析 **word** 为真实粗体run"""
    import re
    parts = re.split(r'(\*\*.*?\*\*)', text)
    for part in parts:
        if part.startswith('**') and part.endswith('**'):
            run = p.add_run(part[2:-2])
            run.bold = True
        else:
            run = p.add_run(part)
```

## 语文 V2 轮换表

古诗完全删除。拼音和字形频次×2.4倍。

| 类型 | 天数 | 日期 |
|------|------|------|
| 看拼音写词语 | 12天 | 1,4,7,10,13,16,19,22,25,28,31,34 |
| 字音字形 | 12天 | 2,5,8,11,14,17,20,23,26,29,32,35 |
| 成语典故 | 5天 | 3,15,27,36,39 |
| 修改语段 | 5天 | 6,18,30,38,40 |
| 句式仿写 | 3天 | 9,24,37 |
| 说明方法 | 3天 | 12,21,33 |

## 用户设计偏好

- **"每天保持多样性，但突破基础的题量总量不能变少"** — 数学每天4种类型，V3=30题/天
- **"数学再多点"** — 用户认为13题太少，V3拉满到30题（≈1分钟/题）
- **"空白页太多了"** — 禁止板块间强制换页符，内容自然流动
- **写字不额外加** — 用户单独陪练
- **古诗彻底砍掉** — 全部删除
- **作文晨读不变** — 40天保留
- **五上前20天=0** — 基础60分先别预习
- **资源优先** — 先搜桌面再生成，不要创建模板占位符
- **口算够了** — 40题/天不变，只加非口算数学

## 内容数据文件

| 文件 | 用途 |
|------|------|
| `/mnt/c/Users/admin/Desktop/shanghai-exams/暑假英语词表_40天分配.json` | 40天英语词表（786词，2026-07-02从牛津词表解析，与DOCX一致） |
| `/tmp/eng_passages_all.json` | 40篇英语阅读短文（含中文翻译） |
| `/tmp/reading_all_merged.json` | 56篇语文阅读真文（52备份+4shanghai-exams） |
| `/tmp/essays_60.json` | 60篇作文范文真文（来自 `五年级作文背诵范文60篇/`） |
| `scripts/gen_summer_v3.py` | ⚠️ 已丢失（2026-06-30被覆盖）。当前改为后处理模式直接修改DOCX |

## 语文阅读排布：长文1篇/天 + 短文2篇/天，零重复

**目标：** 40天零重复使用所有阅读篇目。如篇数不足导致最后几天出现重复（间隔≥17天），用户接受。

**算法 (`get_reading_passages_for_day`):**
1. 统计长文(≥1000字)和短文(<1000字)数量
2. Day 1-N：长文每天1篇 (N=长文数)
3. Day N+1~40：短文每天2篇，从 shorts 列表顺序取，取完循环

**当前(2026-06-30)排布：** 56篇(21长+35短) → Day1-21长文★ + Day22-40短文×2。59个位用56篇，3篇在Day39-40重复（距首现17天）。

| 来源 | 篇数 |
|------|------|
| 旧版暑假备份 `期末卷/暑假作业备份/` | 52篇（主力，状态机提取） |
| `shanghai-exams/语文/语文_三四年级_阅读理解专项训练.md` | 4篇《蚂蚁的趣闻》《美丽的晚霞》《蜡烛和台灯》《粽子》 |

**注意：** `reading-practice-60days-docx` 与备份内容重叠，已去重。使用 `get_reading_passages_for_day()` 而非旧的 `get_reading_passage(idx)`。

## DOCX阅读提取：状态机解析

旧版暑假DOCX中的阅读短文需用状态机提取，处理多种格式：

```
状态: seeking → in_text → in_questions → skipping_answers

格式1: 阅读短文一：《TITLE》 (bold) → 正文 → （全文约XXX字） → 题目 → 第N题 → 答案与解析
格式2: 短文一：CATEGORY (bold) → TITLE(下一行) → 正文 → 题目 → 题N：TYPE
格式3: TITLE (bold standalone) → 正文 → 练习题 → 问题文本
```

**关键点：** 跳过 `答案与解析` 段落，只提取题目。`题目` 行(bold)是问题区开始标记。

## ⚠️ 常见Bug

### Day编号偏移（已用过Day01需顺延）
如果旧版Day01已打印使用，需将所有Day编号+1（Day01→Day02 ... Day40→Day41）。**必须从Day40倒序处理**避免文件名冲突：
```python
for old_day in range(40, 0, -1):  # 倒序！
    new_day = old_day + 1
    # 1. 加载DOCX
    # 2. 批量替换所有run.text中的编号模式
    #    - Day\s*0?N → Day NN
    #    - 第N天 → 第NN天  
    # 3. 保存为新文件名
    # 4. os.remove(旧文件)
```
替换后需抽样验证Day02无\"Day01\"残留、Day41有\"Day 41\"。

### random.choice空序列
口算进退位生成时 `unit_a=0`(整十数) 导致 `[x for x in range(1,10) if x+0>=10]` 为空：
```python
# 修复：处理 unit_a==0 边界
if unit_a == 0:
    b = random.randint(1, 9)
else:
    candidates = [x for x in range(1, 10) if x + unit_a >= 10]
    b = random.choice(candidates) if candidates else random.randint(1, 9)
```

### 舒尔特表组跨页（终极修复：父表包裹法）

**⚠️ keepNext 链式方案已被证明不可靠（2026-07-01 验证）。** `keepNext` 对段落-表格边界支持不稳定，Word 仍可能在组内拆分。

#### 终极方案：父表 cantSplit 包裹

**原理：** 将每组的标题 + "用时"段落 + 3个舒尔特表全部塞进一个外层 `<w:tbl>` 表格，设置 `cantSplit`。Word **无法**拆分有 `cantSplit` 的单表。

**实现（`scripts/schulte_v5.py` 模式）：**
```python
from lxml import etree
NS = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'

def wrap_schulte_group(tc_elem, schulte_tbls, group_label):
    """tc_elem: 包裹单元格 | schulte_tbls: 3个舒尔特表的lxml元素"""
    # 清空 tc
    for child in list(tc_elem):
        if child.tag.split('}')[-1] != 'tcPr':
            tc_elem.remove(child)
    
    # 重建内容（纯 lxml.etree，不用 OxmlElement — 后者会污染父级 .text）
    tc_elem.append(make_etree_p(f'🧠 舒尔特专注力训练 {group_label}（入门 3×3）', 
                                 bold=True, sz=24))
    tc_elem.append(make_etree_p('从1开始按顺序指读，越快越好！', 
                                 color='808080', sz=20))
    for si, tbl in enumerate(schulte_tbls):
        tc_elem.append(make_etree_p(f'第{si+1}格   用时：___秒', sz=20))
        tc_elem.append(tbl)
    tc_elem.append(make_etree_p('', sz=20))

def make_etree_p(text, bold=False, sz=22, color=None, sp_before=0, sp_after=40):
    """用纯 lxml.etree 创建 w:p — OxmlElement 会污染父级 .text 导致三倍重复"""
    p = etree.Element(f'{{{NS}}}p')
    pPr = etree.SubElement(p, f'{{{NS}}}pPr')
    sp = etree.SubElement(pPr, f'{{{NS}}}spacing')
    if sp_before: sp.set(f'{{{NS}}}before', str(sp_before))
    if sp_after: sp.set(f'{{{NS}}}after', str(sp_after))
    r = etree.SubElement(p, f'{{{NS}}}r')
    rPr = etree.SubElement(r, f'{{{NS}}}rPr')
    rf = etree.SubElement(rPr, f'{{{NS}}}rFonts')
    rf.set(f'{{{NS}}}ascii', '宋体')
    rf.set(f'{{{NS}}}eastAsia', '宋体')
    if bold: etree.SubElement(rPr, f'{{{NS}}}b')
    if color:
        c = etree.SubElement(rPr, f'{{{NS}}}color')
        c.set(f'{{{NS}}}val', color)
    sz_e = etree.SubElement(rPr, f'{{{NS}}}sz')
    sz_e.set(f'{{{NS}}}val', str(sz))
    t = etree.SubElement(r, f'{{{NS}}}t')
    t.text = text
    t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    return p
```

**父表构建（带 cantSplit + 无边框 + 全宽）：**
```python
parent = OxmlElement('w:tbl')
tbl_pr = OxmlElement('w:tblPr')
cant_split = OxmlElement('w:cantSplit')
cant_split.set(qn('w:val'), 'true')
tbl_pr.append(cant_split)
# 无边框
for bn in ['top','left','bottom','right','insideH','insideV']:
    b = OxmlElement(f'w:{bn}')
    b.set(qn('w:val'), 'none'); b.set(qn('w:sz'), '0')
    tbl_pr.append(b)
parent.append(tbl_pr)
# 全宽单列
gc = OxmlElement('w:gridCol'); gc.set(qn('w:w'), '9072')
parent.append(OxmlElement('w:tblGrid')).append(gc)
# 单行单格
tc = OxmlElement('w:tc')
tc_w = OxmlElement('w:tcW'); tc_w.set(qn('w:w'), '9072')
tc.append(OxmlElement('w:tcPr')).append(tc_w)
parent.append(OxmlElement('w:tr')).append(tc)
# 插入 body
body.insert(pos, parent)
```

**验证：** 包裹后每组的 `<w:t>` 文本应包含：舒尔特标题 + 指令 + 3个"用时" + 3组数字。
```python
texts = [t.text for t in wrapper.iter(f'{{{NS}}}t') if t.text and t.text.strip()]
assert any('舒尔特' in t for t in texts), "缺标题"
assert sum(1 for t in texts if '用时' in t) == 3, "缺用时"
assert wrapper.find(f'{{{NS}}}tblPr/{{{NS}}}cantSplit') is not None, "缺cantSplit"
```

#### 已弃用方案（记录，勿复用）

- ❌ `keepNext` 链式保护 — 对段落-表格边界不可靠
- ❌ `deepcopy` 跨文档复制 — 导致文字三倍重复
- ❌ `OxmlElement` 创建段落 — `.text` 污染父级元素

### ⚠️ 跨文档 deepcopy 导致文字三倍重复（致命陷阱）

**症状：** 段落文字显示三遍（如 "佳乐暑假练习 Day 02佳乐暑假练习 Day 02佳乐暑假练习 Day 02"），但 `<w:t>` 元素内容正确。

**根因：** `copy.deepcopy()` 在 python-docx 文档间复制 XML 元素时，文本节点被错误地复制到 `<w:p>` 和 `<w:r>` 元素的 `.text` 属性上（而不只在 `<w:t>` 里）。lxml 的 `iter()` 遍历所有后代元素，三个元素各有相同文本 → 显示三遍。

**检测：**
```python
# 检查是否有寄生文本
for p_elem in body.iter(f'{{{NS}}}p'):
    if p_elem.text and p_elem.text.strip():
        print(f"寄生文本在w:p: {p_elem.text[:50]}")
    for r_elem in p_elem.findall(f'{{{NS}}}r'):
        if r_elem.text and r_elem.text.strip():
            print(f"寄生文本在w:r: {r_elem.text[:50]}")
```

**修复（唯一可靠方法）：** 直接操作 DOCX ZIP 内的 document.xml：
```python
import zipfile, shutil
from lxml import etree

def fix_parasitic_text(docx_path):
    tmp = docx_path + '.tmp'
    with zipfile.ZipFile(docx_path, 'r') as zin:
        with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)
                if item.filename == 'word/document.xml':
                    tree = etree.fromstring(data)
                    NS = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
                    for p in tree.iter(f'{{{NS}}}p'):
                        if p.text and p.text.strip():
                            p.text = None  # 清除 w:p 寄生文本
                        for r in p.findall(f'{{{NS}}}r'):
                            if r.text and r.text.strip():
                                r.text = None  # 清除 w:r 寄生文本
                    data = etree.tostring(tree, xml_declaration=True, encoding='UTF-8', standalone=True)
                zout.writestr(item, data)
    shutil.move(tmp, docx_path)
```

**教训：** 永远不要用 `deepcopy` 在 python-docx 文档间复制元素。用以下安全替代方案：
1. **XML 级插入：** 用 `OxmlElement` 手工构建段落，`body.insert(pos, elem)` 插入（见上方修复逻辑）
2. **同文档 add + reorder：** 用 `doc.add_paragraph()` 加到最后，再通过 `body.remove()` + `body.insert(0, elem)` 移到前面
3. **ZIP 级修改：** 直接改 document.xml（最可靠，用于批量文本修复）

### 修改已有 DOCX 的安全流程

当需要批量修改已有 DOCX（而非从零生成）时，遵循：
1. **先备份** — `shutil.copy2(path, path + '.bak')` 
2. **写入 `/tmp/` 再复制** — 避免 WSL `/mnt/c/` 锁文件问题
3. **改完验证** — 检查标题、数学题数、英语词数、换页符、舒尔特保护
4. **遇到 PermissionError** — 文件被 Windows 端 Word 占用，让用户关掉再试

**症状：** `'str' object is not callable` 在 mathtype=="综合" 的天。
**原因：** `random.choice([gen_tuoshi(), gen_jianbian()])()` — 括号调用了函数返回字符串，然后对字符串再加 `()`。

```python
# ❌ 错误：先调用了函数，choice 拿到的是两个字符串
random.choice([gen_tuoshi(), gen_jianbian()])()

# ✅ 正确：choice 拿到两个函数引用，然后调用选中的那个
random.choice([gen_tuoshi, gen_jianbian])()
```

**影响：** 每4天触发一次（脱式轮换第4天=综合），恰好是 Day04/08/12/16/20/24/28/32/36/40。

### 生成后内容缺失检查
- 阅读：文字>300字/篇 ✅，不能只有149字模板 ❌
- 作文：正文>300字 ✅，不能只有\"朗读范文...\"占位符 ❌  
- 英语：粗体词数>0 ✅，不能有 `**word**` 星号 ❌
- 英语词表：每天20词(Day40余数除外)，来自真词表

## ⚠️ 生成后验证

### 批量DOCX修改先备份
```python
import shutil
bak = path + '.bak'
shutil.copy2(path, bak)
```

### WSL文件锁
写 `/mnt/c/` 下DOCX时如被Word打开会 PermissionError → 先写 `/tmp/` 再 `shutil.copy2`。

### 生成后关键检查项
- 语文阅读：文字>300字/篇，不能只有第一段
- 晨读作文：有正文，不能只是"朗读范文..."占位符
- 英语阅读：`**word**` 已被解析为粗体，无星号残留
- 英语单词：每天20词（Day40为余数），来自真词表

## 关键路径
```
BASE = /mnt/c/Users/admin/Desktop/佳乐2026暑假-精简版
BACKUP = /mnt/c/Users/admin/Desktop/期末卷/暑假作业备份
READING_60 = /mnt/c/Users/admin/Desktop/reading-practice-60days-docx
EXAMS = /mnt/c/Users/admin/Desktop/shanghai-exams
```
