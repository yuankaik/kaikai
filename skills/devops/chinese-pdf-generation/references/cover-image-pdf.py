#!/usr/bin/env python3
"""
Generate PDF from markdown with full-page cover images.
Use when md2pdf_cjk.py can't handle cover images.

Usage: python3 cover_image_pdf.py input.md output.pdf cover1.png cover2.png cover3.png
"""
import markdown, os, sys
from weasyprint import HTML

if len(sys.argv) < 4:
    print("Usage: python3 cover_image_pdf.py input.md output.pdf cover1.png [cover2.png cover3.png]")
    sys.exit(1)

md_path = sys.argv[1]
pdf_path = sys.argv[2]
cover_images = sys.argv[3:]

# Read markdown
with open(md_path, "r", encoding="utf-8") as f:
    md_text = f.read()

# Convert to HTML
md = markdown.Markdown(extensions=['tables', 'fenced_code'])
body_html = md.convert(md_text)

# Build cover HTML (each image on its own page)
cover_html = ""
for img_path in cover_images:
    abs_path = os.path.abspath(img_path)
    cover_html += f'''<div style="page-break-after: always; display: flex; align-items: center; justify-content: center; width: 210mm; height: 297mm; margin: 0; padding: 0;">
<img src="{abs_path}" style="max-width: 210mm; max-height: 297mm;">
</div>
'''

full_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
@page {{ size: A4; margin: 1.8cm; }}
body {{ font-family: "Noto Sans CJK SC", sans-serif; font-size: 10pt; line-height: 1.8; }}
h1 {{ font-size: 14pt; page-break-before: always; border-bottom: 1px solid #ccc; }}
h2 {{ font-size: 12pt; page-break-before: always; }}
h3 {{ font-size: 11pt; }}
table {{ border-collapse: collapse; width: 100%; font-size: 9pt; }}
th, td {{ border: 1px solid #ccc; padding: 4pt; }}
</style>
</head>
<body>
{cover_html}
{body_html}
</body>
</html>"""

HTML(string=full_html).write_pdf(pdf_path)
sz = os.path.getsize(pdf_path)
print(f"PDF OK: {sz:,} bytes ({sz/1024:.1f} KB)")
