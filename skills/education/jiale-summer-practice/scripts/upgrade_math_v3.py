#!/usr/bin/env python3
"""
Upgrade summer practice DOCX files: double math problems + remove page breaks.
Post-processes existing Day02-Day41 files in-place.

V3 math upgrade (2026-06-30):
  - 竖式: 5→10 题
  - 脱式: 3→8 题
  - 应用: 3→6 题
  - 轮换: 2→6 题
  - 五上预习(Day21-40): 3-5→5 题
  - Removes all <w:br w:type="page"/> page breaks
  - Preserves Schulte cantSplit + chain keepNext

Usage:
  python3 scripts/upgrade_math_v3.py
"""
from docx import Document
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
import os, re, random, shutil, tempfile
from copy import deepcopy

BASE = "/mnt/c/Users/admin/Desktop/佳乐2026暑假-精简版"
random.seed(42)

# === Math Problem Generators ===

def gen_vertical_add(difficulty=1):
    if difficulty == 1:
        a = random.randint(10, 99)
        b = random.randint(10, 99)
    else:
        a = random.randint(100, 999)
        b = random.randint(100, 999)
    return f"列竖式计算：{a} + {b} = ______"

def gen_vertical_sub(difficulty=1):
    a = random.randint(50, 99)
    b = random.randint(10, a - 1)
    if difficulty >= 2:
        a = random.randint(100, 999)
        b = random.randint(50, a - 1)
    return f"列竖式计算：{a} - {b} = ______"

def gen_vertical_mul():
    a = random.randint(2, 9)
    b = random.randint(10, 99)
    return f"列竖式计算：{a} × {b} = ______"

def gen_vertical_div():
    a = random.randint(2, 9)
    b = a * random.randint(10, 99)
    return f"列竖式计算：{b} ÷ {a} = ______"

def gen_vertical_mixed():
    types = [
        lambda: f"列竖式计算：{random.randint(100,999)} + {random.randint(100,999)} = ______",
        lambda: f"列竖式计算：{random.randint(100,999)} - {random.randint(50,499)} = ______",
        lambda: f"列竖式计算：{random.randint(2,9)} × {random.randint(10,99)} = ______",
    ]
    return random.choice(types)()

def gen_vertical_decimal():
    a = round(random.uniform(1, 99), random.choice([1, 2]))
    b = round(random.uniform(1, 99), random.choice([1, 2]))
    op = random.choice(['+', '-'])
    return f"列竖式计算：{a} {op} {b} = ______"

def gen_tuoshi():
    templates = [
        f"{random.randint(10,99)} × {random.randint(2,9)} + {random.randint(10,99)}",
        f"{random.randint(100,999)} ÷ {random.randint(2,9)} + {random.randint(10,99)}",
        f"{random.randint(10,99)} + {random.randint(10,99)} × {random.randint(2,6)}",
        f"({random.randint(10,99)} + {random.randint(10,99)}) × {random.randint(2,6)}",
        f"{random.randint(100,999)} - {random.randint(10,99)} × {random.randint(2,9)}",
    ]
    return f"脱式计算：{random.choice(templates)} = ______"

def gen_jianbian():
    templates = [
        f"{random.randint(2,9)} × {random.randint(10,99)} × {random.choice([2,5,10,100])}",
        f"{random.randint(10,99)} + {random.randint(10,99)} + {random.randint(10,99)}",
        f"{random.randint(100,999)} - {random.randint(10,99)} - {random.randint(10,99)}",
        f"{random.choice([25,125])} × {random.randint(2,9)} × {random.choice([4,8])}",
        f"({random.randint(100,999)} + {random.randint(100,999)}) ÷ {random.choice([2,5,10])}",
    ]
    return f"简便计算：{random.choice(templates)} = ______"

def gen_fraction():
    num1 = random.randint(1, 9)
    den1 = random.randint(2, 12)
    num2 = random.randint(1, 9)
    den2 = random.randint(2, 12)
    op = random.choice(['+', '-'])
    return f"计算：{num1}/{den1} {op} {num2}/{den2} = ______"

def gen_application(type_name="归一"):
    problems = {
        "归一": [
            f"小明{random.randint(3,8)}天看了{random.randint(60,200)}页书，照这样计算，{random.randint(10,20)}天能看多少页？",
            f"{random.randint(3,6)}台机器{random.randint(4,8)}小时生产{random.randint(120,480)}个零件，1台机器1小时生产多少个？",
            f"买{random.randint(3,6)}本同样的笔记本花了{random.randint(12,36)}元，买{random.randint(8,15)}本需要多少钱？",
            f"{random.randint(3,5)}个工人{random.randint(4,8)}天修路{random.randint(200,600)}米，照这样，{random.randint(6,10)}个工人1天修多少米？",
        ],
        "余数": [
            f"有{random.randint(50,200)}个苹果，每{random.randint(6,9)}个装一袋，能装几袋？还剩几个？",
            f"一根绳子长{random.randint(20,60)}米，每{random.randint(3,7)}米剪一段，能剪几段？剩几米？",
            f"{random.randint(30,80)}个同学，每{random.randint(4,8)}人一组，可分几组？多几人？",
            f"一本书{random.randint(100,300)}页，每天看{random.randint(10,25)}页，几天看完？",
        ],
        "几何": [
            f"一个长方形长{random.randint(8,20)}cm，宽{random.randint(5,12)}cm，周长和面积各是多少？",
            f"一个正方形边长{random.randint(5,15)}cm，它的周长和面积各是多少？",
            f"一块长方形菜地长{random.randint(10,30)}米，宽{random.randint(5,15)}米，围栏需要多长？",
            f"教室长{random.randint(8,12)}米，宽{random.randint(6,9)}米，铺边长{random.choice([30,50,60])}厘米的方砖，大约要多少块？",
        ],
        "单位": [
            f"一袋大米重{random.randint(10,50)}千克，吃了{random.randint(3,20)}千克{random.randint(100,900)}克，还剩多少克？",
            f"一瓶饮料{random.randint(250,1000)}毫升，喝了{random.randint(100,350)}毫升，还剩多少升？（用小数表示）",
            f"从家到学校{random.randint(1,5)}千米{random.randint(100,900)}米，已经走了{random.randint(500,2000)}米，还剩多少米？",
            f"一桶油{random.randint(3,8)}升{random.randint(100,900)}毫升，用去一半，还剩多少毫升？",
        ],
        "综合": [
            f"小明有{random.randint(100,500)}元，买书花了{random.randint(20,80)}元，买文具花了{random.randint(10,40)}元，还剩多少元？",
            f"一列火车每小时行{random.randint(80,200)}千米，{random.randint(2,6)}小时行多少千米？",
            f"果园有苹果树{random.randint(20,80)}棵，梨树是苹果树的{random.randint(2,4)}倍，两种树共多少棵？",
            f"一批货物重{random.randint(100,500)}吨，用载重{random.randint(5,10)}吨的卡车运，需要几辆？",
        ],
    }
    return random.choice(problems.get(type_name, problems["归一"]))

def gen_other(type_name):
    templates = {
        "大数": [
            f"{random.randint(100000,99999999):,} 读作：______________",
            f"写出：{random.choice(['五十六万八千','三千零四万二千','九百万零六十'])} = ______",
            f"比较大小：{random.randint(100000,999999)} ____ {random.randint(100000,999999)}",
        ],
        "分数": [
            f"{random.randint(1,7)}/{random.randint(2,9)} + {random.randint(1,7)}/{random.randint(2,9)} = ______",
            f"比较大小：{random.randint(1,6)}/{random.randint(3,9)} ____ {random.randint(1,6)}/{random.randint(3,9)}",
            f"把 {random.randint(1,9)}/{random.randint(2,9)} 化成最简分数",
        ],
        "小数": [
            f"{round(random.uniform(1,99), random.choice([1,2]))} + {round(random.uniform(1,99), random.choice([1,2]))} = ______",
            f"{round(random.uniform(1,99), 1)} × {random.choice([10,100])} = ______",
            f"比较：{round(random.uniform(0,10), 2)} ____ {round(random.uniform(0,10), 2)}",
        ],
        "几何": [
            f"一个三角形，∠1={random.randint(30,60)}°，∠2={random.randint(30,80)}°，∠3=____°",
            f"用三角尺画一个{random.choice([45,60,90,120,135])}°的角",
            f"一个长方形周长{random.randint(20,60)}cm，长{random.randint(6,15)}cm，宽是多少？",
        ],
        "估算": [
            f"估算：{random.randint(100,999)} × {random.randint(2,9)} ≈ ______",
            f"估算：{random.randint(1000,9999)} + {random.randint(1000,9999)} ≈ ______",
            f"{random.randint(100,999)} ÷ {random.choice([3,6,7,8,9])} ≈ ______（估算到整十）",
        ],
        "验算": [
            f"计算并验算：{random.randint(100,999)} + {random.randint(100,999)} = ______",
            f"计算并验算：{random.randint(100,999)} - {random.randint(50,499)} = ______",
            f"用逆运算验算：{random.randint(2,9)} × {random.randint(10,99)} = {random.randint(2,9) * random.randint(10,99)}",
        ],
    }
    return random.choice(templates.get(type_name, templates["大数"]))


# === Math problem type configurations ===
VERTICAL_TYPES = ["加法", "减法", "乘法", "除法", "混合", "小数"]
TUOSHI_TYPES = ["脱式", "简便", "分数", "综合"]
APP_TYPES = ["归一", "余数", "几何", "单位", "综合"]
OTHER_TYPES = ["大数", "分数", "小数", "几何", "估算", "验算"]


def generate_vertical_problems(day_num, count=10):
    idx = (day_num - 1) % 6
    problems = []
    for i in range(count):
        if idx == 0: p = gen_vertical_add(random.randint(1, 2))
        elif idx == 1: p = gen_vertical_sub(random.randint(1, 2))
        elif idx == 2: p = gen_vertical_mul()
        elif idx == 3: p = gen_vertical_div()
        elif idx == 4: p = gen_vertical_mixed()
        else: p = gen_vertical_decimal()
        problems.append(f"{i+1}. {p}")
    return problems

def generate_tuoshi_problems(day_num, count=8):
    idx = (day_num - 1) % 4
    problems = []
    for i in range(count):
        if idx == 0: p = gen_tuoshi()
        elif idx == 1: p = gen_jianbian()
        elif idx == 2: p = gen_fraction()
        else: p = random.choice([gen_tuoshi, gen_jianbian])()  # NOTE: function refs, not calls!
        problems.append(f"{i+1}. {p}")
    return problems

def generate_app_problems(day_num, count=6):
    idx = (day_num - 1) % 5
    type_name = APP_TYPES[idx]
    problems = []
    for i in range(count):
        p = gen_application(type_name)
        problems.append(f"{i+1}. {p}")
    return problems

def generate_other_problems(day_num, count=6):
    idx = (day_num - 1) % 6
    type_name = OTHER_TYPES[idx]
    problems = []
    for i in range(count):
        p = gen_other(type_name)
        problems.append(f"{i+1}. {p}")
    return problems


def make_problem_paragraph(doc, text, indent=0):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.font.size = Pt(11)
    run.font.name = '宋体'
    if indent:
        p.paragraph_format.left_indent = Inches(indent)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.space_before = Pt(1)
    return p


def make_math_subsection(doc, title, problems, score_per=3, total_score=None):
    if total_score is None:
        total_score = len(problems) * score_per
    p = doc.add_paragraph()
    run = p.add_run(f"{title}（每题{score_per}分，共{total_score}分）")
    run.bold = True
    run.font.size = Pt(11)
    run.font.name = '宋体'
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(4)
    
    for prob in problems:
        make_problem_paragraph(doc, prob)


def remove_page_breaks(doc):
    """Remove all <w:br w:type='page'/> elements and pageBreakBefore"""
    body = doc.element.body
    removed = 0
    
    for p_elem in body.findall(qn('w:p')):
        for r in list(p_elem.findall(qn('w:r'))):
            for br in list(r.findall(qn('w:br'))):
                if br.get(qn('w:type')) == 'page':
                    r.remove(br)
                    removed += 1
        
        pPr = p_elem.find(qn('w:pPr'))
        if pPr is not None:
            pb = pPr.find(qn('w:pageBreakBefore'))
            if pb is not None:
                pPr.remove(pb)
                removed += 1
    
    return removed


def upgrade_day_docx(doc_path, day_num):
    """Upgrade a single day's DOCX: new math + remove page breaks"""
    
    doc = Document(doc_path)
    original_body = doc.element.body
    
    in_math = False
    math_start = None
    math_end = None
    non_math_paragraphs_before = []
    non_math_paragraphs_after = []
    
    body_children = list(original_body)
    
    for i, child in enumerate(body_children):
        tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
        if tag == 'p':
            text = ''.join(r.text or '' for r in child.findall('.//'+qn('w:t')))
            if '📐 数学' in text and ('基础' in text or '复习' in text):
                math_start = i
                in_math = True
                continue
            elif in_math and ('🧠 舒尔特' in text or '💡' in text):
                math_end = i
                in_math = False
    
    if math_start is None:
        print(f"  Day{day_num:02d}: 找不到数学区段,跳过")
        return 0
    
    for i, child in enumerate(body_children):
        if i < math_start:
            non_math_paragraphs_before.append(child)
        elif math_end is not None and i >= math_end:
            non_math_paragraphs_after.append(child)
    
    new_doc = Document()
    
    for section in doc.sections:
        new_section = new_doc.sections[0]
        new_section.page_width = section.page_width
        new_section.page_height = section.page_height
        new_section.top_margin = section.top_margin
        new_section.bottom_margin = section.bottom_margin
        new_section.left_margin = section.left_margin
        new_section.right_margin = section.right_margin
        break
    
    for section in doc.sections:
        if section.header:
            for p in section.header.paragraphs:
                new_p = new_doc.sections[0].header.add_paragraph()
                for run in p.runs:
                    new_run = new_p.add_run(run.text)
                    if run.font.size: new_run.font.size = run.font.size
                    if run.font.name: new_run.font.name = run.font.name
        if section.footer:
            for p in section.footer.paragraphs:
                new_p = new_doc.sections[0].footer.add_paragraph()
                for run in p.runs:
                    new_run = new_p.add_run(run.text)
                    if run.font.size: new_run.font.size = run.font.size
                    if run.font.name: new_run.font.name = run.font.name
        break
    
    new_body = new_doc.element.body
    
    for child in non_math_paragraphs_before:
        new_body.append(deepcopy(child))
    
    # Math header
    p = new_doc.add_paragraph()
    run = p.add_run('📐 数学（基础复习·30分钟）')
    run.bold = True
    run.font.size = Pt(14)
    run.font.name = '宋体'
    p.paragraph_format.space_before = Pt(10)
    
    p = new_doc.add_paragraph()
    run = p.add_run(f'数学练习 Day {day_num}')
    run.font.size = Pt(11)
    run.font.name = '宋体'
    p.paragraph_format.space_after = Pt(4)
    
    # Slot 1-4
    vertical = generate_vertical_problems(day_num, 10)
    make_math_subsection(new_doc, '一、竖式计算', vertical, score_per=3, total_score=30)
    
    tuoshi = generate_tuoshi_problems(day_num, 8)
    make_math_subsection(new_doc, '二、脱式与混合运算', tuoshi, score_per=3, total_score=24)
    
    app = generate_app_problems(day_num, 6)
    make_math_subsection(new_doc, '三、应用题', app, score_per=3, total_score=18)
    
    other = generate_other_problems(day_num, 6)
    make_math_subsection(new_doc, '四、综合练习', other, score_per=2, total_score=12)
    
    # 五上预习 (Day 21-40 only)
    if day_num >= 21:
        p = new_doc.add_paragraph()
        run = p.add_run('五、五上预习（5题）')
        run.bold = True
        run.font.size = Pt(11)
        run.font.name = '宋体'
        p.paragraph_format.space_before = Pt(8)
        
        for i in range(5):
            if i < 3:
                a = round(random.uniform(1, 99), random.choice([1, 2]))
                b = random.choice([10, 100, 0.1, 0.01])
                prob = f"{i+1}. 计算：{a} × {b} = ______"
            else:
                x_val = random.randint(1, 50)
                a = random.randint(2, 10)
                b = a * x_val + random.randint(-5, 5)
                prob = f"{i+1}. 解方程：{a}x + {b - a*x_val} = {b}"
            make_problem_paragraph(new_doc, prob)
    else:
        p = new_doc.add_paragraph()
        run = p.add_run('💡 五上预习暂停，集中巩固基础。开学前2周恢复。')
        run.font.size = Pt(10)
        run.font.name = '宋体'
        run.font.color.rgb = RGBColor(128, 128, 128)
    
    for child in non_math_paragraphs_after:
        new_body.append(deepcopy(child))
    
    remove_page_breaks(new_doc)
    
    tmp_path = os.path.join(tempfile.gettempdir(), f"Day{day_num:02d}-upgraded.docx")
    new_doc.save(tmp_path)
    shutil.copy2(tmp_path, doc_path)
    os.remove(tmp_path)
    
    return 30 + (5 if day_num >= 21 else 0)


if __name__ == "__main__":
    print("=== 数学增容 V3: 13→30题 + 删换页符 ===\n")
    
    total = 0
    for week_num in range(1, 9):
        week_dirs = [d for d in os.listdir(BASE) if d.startswith(f"第{week_num}周")]
        if not week_dirs:
            continue
        student_dir = os.path.join(BASE, week_dirs[0], "学生卷")
        if not os.path.exists(student_dir):
            continue
        
        day_files = sorted([f for f in os.listdir(student_dir) 
                          if f.startswith("Day") and f.endswith(".docx") and "答案" not in f])
        
        for df in day_files:
            day_num = int(re.search(r'Day(\d+)', df).group(1))
            fpath = os.path.join(student_dir, df)
            
            try:
                n_problems = upgrade_day_docx(fpath, day_num)
                total += n_problems
                print(f"  {df}: {n_problems}道数学题 ✅")
            except PermissionError:
                print(f"  {df}: ⚠️ 文件占用,跳过")
            except Exception as e:
                print(f"  {df}: ❌ {e}")
    
    print(f"\n总计: 每天30题(五上预习外) → 40天约{40*30}道数学基础题")
    print("换页符: 已清除")
    print("舒尔特链式keepNext: 保留(之前已修复)")
