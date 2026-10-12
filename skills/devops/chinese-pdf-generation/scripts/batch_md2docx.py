#!/usr/bin/env python3
"""Fast batch .md → .docx converter using python-docx.
Usage: python3 batch_md2docx.py /path/to/directory

Walks recursively, converts every .md without an existing .docx/.pdf counterpart.
Preserves: headings (#), bold (**), italic (*), code (`), tables (|...|),
lists (-/*), blockquotes (>), horizontal rules (---).
Output: .docx with SimSun 10-11pt, table formatting, heading hierarchy.
"""

import os, re, sys
from docx import Document
from docx.shared import Pt, Cm

def md_to_docx(md_path, docx_path):
    with open(md_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    doc = Document()
    style = doc.styles['Normal']
    style.font.name = 'SimSun'
    style.font.size = Pt(11)
    
    in_code_block = False
    code_lines = []
    in_table = False
    table_rows = []
    
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        
        if line.startswith('```'):
            if in_code_block:
                code_text = '\n'.join(code_lines)
                p = doc.add_paragraph()
                run = p.add_run(code_text)
                run.font.name = 'Courier New'
                run.font.size = Pt(9)
                code_lines = []
                in_code_block = False
            else:
                in_code_block = True
            i += 1
            continue
        
        if in_code_block:
            code_lines.append(line)
            i += 1
            continue
        
        if line.startswith('|') and line.endswith('|'):
            if not in_table:
                in_table = True
                table_rows = []
            if re.match(r'^\|[\s\-:|]+\|$', line):
                i += 1
                continue
            cells = [c.strip() for c in line.split('|')[1:-1]]
            table_rows.append(cells)
            i += 1
            continue
        elif in_table:
            if table_rows:
                num_cols = max(len(r) for r in table_rows)
                table = doc.add_table(rows=len(table_rows), cols=num_cols)
                table.style = 'Table Grid'
                for ri, row_data in enumerate(table_rows):
                    for ci, cell_text in enumerate(row_data):
                        if ci < num_cols:
                            cell = table.rows[ri].cells[ci]
                            cell.text = ''
                            p = cell.paragraphs[0]
                            run = p.add_run(cell_text)
                            run.font.size = Pt(9)
                            run.font.name = 'SimSun'
                            if ri == 0:
                                run.bold = True
                doc.add_paragraph()
            in_table = False
            table_rows = []
            continue
        
        if not line:
            i += 1
            continue
        
        heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)
        if heading_match:
            level = min(len(heading_match.group(1)), 3)
            text = re.sub(r'\*\*(.+?)\*\*', r'\1', heading_match.group(2))
            text = re.sub(r'__(.+?)__', r'\1', text)
            h = doc.add_heading(text, level=level)
            for run in h.runs:
                run.font.name = 'SimSun'
            i += 1
            continue
        
        if re.match(r'^[-*_]{3,}\s*$', line):
            doc.add_paragraph('─' * 60)
            i += 1
            continue
        
        list_match = re.match(r'^(\s*)([-*+]|\d+[.)])\s+(.+)$', line)
        if list_match:
            text = list_match.group(3)
            p = doc.add_paragraph(style='List Bullet')
            parts = re.split(r'(\*\*.+?\*\*)', text)
            for part in parts:
                if part.startswith('**') and part.endswith('**'):
                    run = p.add_run(part[2:-2])
                    run.bold = True
                else:
                    run = p.add_run(part)
                run.font.name = 'SimSun'
                run.font.size = Pt(10)
            i += 1
            continue
        
        if line.startswith('>'):
            text = line[1:].strip()
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Cm(1)
            run = p.add_run(text)
            run.font.name = 'SimSun'
            run.font.size = Pt(10)
            run.italic = True
            i += 1
            continue
        
        p = doc.add_paragraph()
        parts = re.split(r'(\*\*.+?\*\*|\*.+?\*|`.+?`)', line)
        for part in parts:
            if part.startswith('**') and part.endswith('**'):
                run = p.add_run(part[2:-2])
                run.bold = True
            elif part.startswith('*') and part.endswith('*') and not part.startswith('**'):
                run = p.add_run(part[1:-1])
                run.italic = True
            elif part.startswith('`') and part.endswith('`'):
                run = p.add_run(part[1:-1])
                run.font.name = 'Courier New'
                run.font.size = Pt(9)
            else:
                run = p.add_run(part)
            run.font.name = 'SimSun'
            run.font.size = Pt(10)
        i += 1
    
    if in_table and table_rows:
        num_cols = max(len(r) for r in table_rows)
        table = doc.add_table(rows=len(table_rows), cols=num_cols)
        table.style = 'Table Grid'
        for ri, row_data in enumerate(table_rows):
            for ci, cell_text in enumerate(row_data):
                if ci < num_cols:
                    cell = table.rows[ri].cells[ci]
                    cell.text = ''
                    p = cell.paragraphs[0]
                    run = p.add_run(cell_text)
                    run.font.size = Pt(9)
                    if ri == 0:
                        run.bold = True
    
    doc.save(docx_path)

if __name__ == '__main__':
    target = sys.argv[1] if len(sys.argv) > 1 else '.'
    converted = skipped = failed = 0
    
    for root, dirs, files in os.walk(target):
        for f in files:
            if not f.endswith('.md'):
                continue
            md_path = os.path.join(root, f)
            base = f[:-3]
            if os.path.exists(os.path.join(root, base + '.pdf')):
                skipped += 1
                continue
            if os.path.exists(os.path.join(root, base + '.docx')):
                skipped += 1
                continue
            
            docx_path = os.path.join(root, base + '.docx')
            try:
                md_to_docx(md_path, docx_path)
                converted += 1
            except Exception as e:
                failed += 1
                if failed <= 3:
                    print(f"FAIL: {os.path.relpath(md_path, target)} - {e}")
    
    print(f"MD→DOCX: converted={converted}, skipped={skipped}, failed={failed}")
