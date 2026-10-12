#!/usr/bin/env python3
"""Schulte V5: Wrap Schulte groups in parent table with cantSplit. Definitive fix."""
from docx import Document
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import os, shutil, tempfile
from lxml import etree

BASE = "/mnt/c/Users/admin/Desktop/佳乐2026暑假-精简版"
NS = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'

def make_p_clean(text, bold=False, sz=22, color=None, sp_before=0, sp_after=40):
    """Create w:p using pure etree - avoids OxmlElement text pollution."""
    p = etree.Element(f'{{{NS}}}p')
    pPr = etree.SubElement(p, f'{{{NS}}}pPr')
    sp = etree.SubElement(pPr, f'{{{NS}}}spacing')
    if sp_before: sp.set(f'{{{NS}}}before', str(sp_before))
    if sp_after: sp.set(f'{{{NS}}}after', str(sp_after))
    r = etree.SubElement(p, f'{{{NS}}}r')
    rPr = etree.SubElement(r, f'{{{NS}}}rPr')
    rf = etree.SubElement(rPr, f'{{{NS}}}rFonts')
    rf.set(f'{{{NS}}}ascii', '宋体')
    rf.set(f'{{{NS}}}hAnsi', '宋体')
    rf.set(f'{{{NS}}}eastAsia', '宋体')
    if bold: etree.SubElement(rPr, f'{{{NS}}}b')
    if color:
        c = etree.SubElement(rPr, f'{{{NS}}}color')
        c.set(f'{{{NS}}}val', color)
    sz_e = etree.SubElement(rPr, f'{{{NS}}}sz')
    sz_e.set(f'{{{NS}}}val', str(sz))
    szC = etree.SubElement(rPr, f'{{{NS}}}szCs')
    szC.set(f'{{{NS}}}val', str(sz))
    t = etree.SubElement(r, f'{{{NS}}}t')
    t.text = text
    t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    return p

def fix_one(doc_path, day_num):
    doc = Document(doc_path)
    body = doc.element.body
    children = list(body)
    wrappers = []
    for child in children:
        if child.tag == f'{{{NS}}}tbl':
            nested = child.findall(f'.//{{{NS}}}tbl')
            if len(nested) >= 2:
                wrappers.append(child)
    if not wrappers:
        return "no wrappers"
    for wi, wrapper in enumerate(wrappers):
        tc = wrapper.find(f'.//{{{NS}}}tc')
        if tc is None: continue
        schulte_tbls = []
        for child in list(tc):
            if child.tag == f'{{{NS}}}tbl':
                rows = child.findall(f'{{{NS}}}tr')
                if len(rows) in [3, 6]:
                    fc = ''.join(t.text or '' for t in child.findall(f'.//{{{NS}}}t')).strip()
                    if fc and all(c.isdigit() or c.isspace() for c in fc[:30]):
                        schulte_tbls.append(child)
        for child in list(tc):
            if child.tag.split('}')[-1] != 'tcPr':
                tc.remove(child)
        group_label = "①" if wi == 0 else "②"
        tc.append(make_p_clean(f'🧠 舒尔特专注力训练 {group_label}（入门 3×3）', bold=True, sz=24, sp_before=60, sp_after=40))
        tc.append(make_p_clean('从1开始按顺序指读，越快越好！', sz=20, color='808080', sp_after=60))
        for si, tbl in enumerate(schulte_tbls):
            tc.append(make_p_clean(f'第{si+1}格   用时：___秒', sz=20, sp_before=40, sp_after=20))
            tc.append(tbl)
        tc.append(make_p_clean('', sz=20, sp_after=20))
    tmp = os.path.join(tempfile.gettempdir(), f"Day{day_num:02d}-schulte-v5.docx")
    doc.save(tmp)
    shutil.copy2(tmp, doc_path)
    os.remove(tmp)
    return f"{len(wrappers)} groups"

if __name__ == "__main__":
    for week_num in range(1, 9):
        week_dirs = [d for d in os.listdir(BASE) if d.startswith(f"第{week_num}周")]
        if not week_dirs: continue
        student_dir = os.path.join(BASE, week_dirs[0], "学生卷")
        if not os.path.exists(student_dir): continue
        for fname in sorted(os.listdir(student_dir)):
            if not (fname.startswith("Day") and fname.endswith(".docx") and "答案" not in fname):
                continue
            day_num = int(fname.split('Day')[1].split('-')[0])
            fpath = os.path.join(student_dir, fname)
            result = fix_one(fpath, day_num)
            print(f"  Day{day_num:02d}: {result}")
    print("\nDone")
