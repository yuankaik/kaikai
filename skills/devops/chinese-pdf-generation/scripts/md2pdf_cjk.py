#!/usr/bin/env python3
"""Convert Markdown to PDF with proper Chinese (CJK) font rendering.
Requires: pip install --break-system-packages weasyprint markdown
          sudo apt-get install fonts-noto-cjk
Usage: python3 md2pdf_cjk.py input.md [output.pdf]
"""
import markdown
import weasyprint
import sys, os

md_path = sys.argv[1]
out_pdf = sys.argv[2] if len(sys.argv) > 2 else md_path.replace('.md', '.pdf')

with open(md_path, 'r', encoding='utf-8') as f:
    md_text = f.read()

html_body = markdown.markdown(md_text, extensions=['tables', 'fenced_code', 'toc'])

full_html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<style>
@page {{ size: A4; margin: 1.8cm; }}
body {{
    font-family: "Noto Sans CJK SC", "WenQuanYi Micro Hei", "SimSun", sans-serif;
    font-size: 11pt; line-height: 1.8; color: #222;
}}
h1 {{ font-size: 18pt; border-bottom: 2px solid #333; padding-bottom: 6pt;
      margin-top: 24pt; page-break-before: always; }}
h1:first-of-type {{ page-break-before: avoid; }}
h2 {{ font-size: 14pt; margin-top: 18pt; border-bottom: 1px solid #999; padding-bottom: 3pt; }}
h3 {{ font-size: 12pt; margin-top: 14pt; }}
table {{ border-collapse: collapse; width: 100%; margin: 10pt 0; font-size: 10pt; }}
th, td {{ border: 1px solid #888; padding: 5pt 7pt; text-align: left; }}
th {{ background: #eee; font-weight: bold; }}
code {{ background: #f4f4f4; padding: 1pt 4pt; border-radius: 3pt; font-size: 9pt; }}
blockquote {{ border-left: 3px solid #ccc; margin-left: 0; padding-left: 15pt; color: #555; }}
p {{ margin: 6pt 0; }}
hr {{ border: none; border-top: 1px solid #ddd; margin: 20pt 0; }}
em {{ font-style: italic; }}
</style>
<title>Document</title>
</head>
<body>
{html_body}
</body>
</html>'''

weasyprint.HTML(string=full_html).write_pdf(out_pdf)
size_kb = round(os.path.getsize(out_pdf) / 1024, 1)
print(f'OK: {out_pdf} ({size_kb}KB)')
