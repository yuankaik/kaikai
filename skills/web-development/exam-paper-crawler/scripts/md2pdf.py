#!/usr/bin/env python3
"""Convert markdown to PDF using weasyprint.
Usage: python3 md2pdf.py <input.md> [output.pdf]

Requires: pip install --break-system-packages weasyprint markdown
"""
import markdown
import weasyprint
import sys

md_path = sys.argv[1] if len(sys.argv) > 1 else exit("Usage: md2pdf.py <input.md> [output.pdf]")
out_path = sys.argv[2] if len(sys.argv) > 2 else md_path.replace('.md', '.pdf')

with open(md_path, 'r', encoding='utf-8') as f:
    md_text = f.read()

html_body = markdown.markdown(md_text, extensions=['tables', 'fenced_code', 'toc'])

CSS = """
@page { size: A4; margin: 2cm; }
body { font-family: "Noto Sans CJK SC", "SimSun", "Microsoft YaHei", sans-serif;
       font-size: 11pt; line-height: 1.8; color: #222; }
h1 { font-size: 18pt; border-bottom: 2px solid #333; padding-bottom: 6pt;
     margin-top: 24pt; page-break-before: always; }
h1:first-of-type { page-break-before: avoid; }
h2 { font-size: 14pt; margin-top: 18pt; border-bottom: 1px solid #999; padding-bottom: 3pt; }
h3 { font-size: 12pt; margin-top: 14pt; }
table { border-collapse: collapse; width: 100%; margin: 10pt 0; font-size: 10pt; }
th, td { border: 1px solid #888; padding: 5pt 7pt; text-align: left; }
th { background: #eee; font-weight: bold; }
code { background: #f4f4f4; padding: 1pt 4pt; border-radius: 3pt; font-size: 10pt; }
blockquote { border-left: 3px solid #ccc; margin-left: 0; padding-left: 15pt; color: #555; }
p { margin: 6pt 0; }
strong { color: #000; }
hr { border: none; border-top: 1px solid #ddd; margin: 20pt 0; }
"""

full_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="utf-8"><style>{CSS}</style></head>
<body>{html_body}</body>
</html>"""

weasyprint.HTML(string=full_html).write_pdf(out_path)
print(f'PDF: {out_path}')
