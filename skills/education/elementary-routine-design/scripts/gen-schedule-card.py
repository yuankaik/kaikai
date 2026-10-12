# -*- coding: utf-8 -*-
"""生成可打印作息卡 DOCX（python-docx），输出到 Windows 桌面。

用法：改下方 CONFIG 区 → python3 gen-schedule-card.py
依赖：python-docx（pip install python-docx）
"""
from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

# ===================== CONFIG 区（改这里） =====================
OUT = "/mnt/c/Users/admin/Desktop/作息卡.docx"
TITLE = "作息表"
SUBTITLE = "睡眠 21:10→7:00 = 9小时40分"

# 工作日时间表：[(时间, 安排), ...]
SCHEDULE = [
    ("07:00", "起床 · 上学"),
    ("15:45 - 17:30", "在校作业"),
    ("17:30 - 18:15", "自由放松"),
    ("18:15 - 18:45", "吃饭"),
    ("18:45 - 19:00", "听英语 · 翻错题本"),
    ("19:00 - 19:20", "作业补漏（只查卡住的题）"),
    ("19:20 - 20:20", "运动"),
    ("20:20 - 20:35", "洗澡"),
    ("20:35 - 20:55", "背诵 20 分钟"),
    ("20:55 - 21:10", "睡前阅读"),
    ("21:10", "关灯睡觉"),
]
# 要高亮（浅蓝底）的行：按时间列前缀匹配
HIGHLIGHT_PREFIXES = ("19:00", "20:35", "21:10")

WEEKEND = [
    "周六          睡到自然醒 + 自由活动",
    "周日上午      一对一数学",
    "周日下午      14:00 - 16:00 毛笔写字班",
    "周日晚上      口头抽查 15 分钟",
]

BOTTOM_TITLE = "底线（一条都不能动）"
BOTTOM_LINES = [
    "① 周日抽查 15 分钟，雷打不动",
    "② 晚间背诵 20 分钟，不可断",
    "③ 考试低于 70 分 → 退出晚自习",
    "④ 运动是快乐，不是任务",
]
# ============================================================

doc = Document()

normal = doc.styles["Normal"]
normal.font.name = "微软雅黑"
normal.font.size = Pt(11)
normal._element.rPr.rFonts.set(qn("w:eastAsia"), "微软雅黑")


def set_run(run, size=11, bold=False, color=None):
    run.font.name = "微软雅黑"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "微软雅黑")
    run.font.size = Pt(size)
    run.font.bold = bold
    if color:
        run.font.color.rgb = RGBColor(*color)


def add_heading(text, size=16, color=(0x1F, 0x4E, 0x79)):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_run(p.add_run(text), size=size, bold=True, color=color)
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(4)


def add_line(text, size=11, bold=False, color=None):
    p = doc.add_paragraph()
    set_run(p.add_run(text), size=size, bold=bold, color=color)
    p.paragraph_format.space_after = Pt(2)


def shade_cell(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_color)
    tcPr.append(shd)


# 标题
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
set_run(p.add_run(TITLE), size=24, bold=True, color=(0x1F, 0x4E, 0x79))
p.paragraph_format.space_after = Pt(2)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
set_run(p.add_run(SUBTITLE), size=12, color=(0x66, 0x66, 0x66))
p.paragraph_format.space_after = Pt(8)

# 工作日表
add_heading("工作日", 16)
table = doc.add_table(rows=len(SCHEDULE), cols=2)
table.alignment = WD_TABLE_ALIGNMENT.CENTER
table.style = "Table Grid"
for i, (t, a) in enumerate(SCHEDULE):
    c0, c1 = table.rows[i].cells
    c0.width = Cm(4.2)
    c1.width = Cm(11.0)
    set_run(c0.paragraphs[0].add_run(t), size=11, bold=True)
    set_run(c1.paragraphs[0].add_run(a), size=11)
    if t.startswith(HIGHLIGHT_PREFIXES):
        shade_cell(c0, "DCE6F1")
        shade_cell(c1, "DCE6F1")
for row in table.rows:
    row.cells[0].width = Cm(4.2)
    row.cells[1].width = Cm(11.0)

# 周末
add_heading("周末", 16)
for line in WEEKEND:
    add_line(line, size=11)

# 底线
if BOTTOM_LINES:
    add_heading(BOTTOM_TITLE, 16, color=(0xC0, 0x00, 0x00))
    for line in BOTTOM_LINES:
        add_line(line, size=11, bold=True, color=(0xC0, 0x00, 0x00))

doc.save(OUT)
print("已生成:", OUT)
