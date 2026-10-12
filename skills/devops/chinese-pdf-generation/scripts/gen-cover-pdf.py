#!/usr/bin/env python3
"""Generate PDF from Markdown with full-page cover images.
Usage: python3 gen-cover-pdf.py input.md cover1.png cover2.png cover3.png output.pdf
The script reads the MD, finds where body text starts ("佳乐从来不知道" or similar),
prepends cover images as full A4 pages, then renders the body.
"""
import markdown, os, sys
from weasyprint import HTML

if len(sys.argv) < 4:
    print("Usage: gen-cover-pdf.py input.md cover1.png [cover2.png ...] output.pdf")
    sys.exit(1)

md_path = sys.argv[1]
output_pdf = sys.argv[-1]
cover_images = sys.argv[2:-1]

with open(md_path, "r", encoding="utf-8") as f:
    md_text = f.read()

# Find body start: look for common story opening markers
start = -1
for marker in ["佳乐从来不知道", "第一章", "> 佳乐"]:
    pos = md_text.find(marker)
    if pos > 0:
        start = pos
        break

body_md = md_text[start:] if start > 0 else md_text

md = markdown.Markdown(extensions=['toc', 'tables', 'fenced_code'])
body_html = md.convert(body_md)

# Build cover pages
cover = ""
for img_path in cover_images:
    if not os.path.exists(img_path):
        print(f"WARNING: {img_path} not found, skipping")
        continue
    cover += f'<div style="page-break-after:always;display:flex;align-items:center;justify-content:center;width:100%;height:100vh;margin:0;padding:0"><img src="{img_path}" style="max-width:100%;max-height:100%"></div>\n'

html = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>
@page {{ size: A4; margin: 0; }}
@page body {{ size: A4; margin: 1.8cm; }}
body {{ font-family: "Noto Sans CJK SC", sans-serif; font-size: 10pt; line-height: 1.8; }}
h1 {{ font-size: 14pt; page-break-before: always; border-bottom:1px solid #ccc; }}
h2 {{ font-size: 12pt; page-break-before: always; }}
table {{ border-collapse: collapse; width: 100%; font-size: 9pt; }}
th,td {{ border: 1px solid #ccc; padding: 4pt; }}
</style></head><body>
{cover}
{body_html}
</body></html>"""

tmp = os.path.join(os.path.dirname(output_pdf) or ".", "_tmp_cover.html")
with open(tmp, "w", encoding="utf-8") as f:
    f.write(html)

HTML(tmp).write_pdf(output_pdf)
os.remove(tmp)
print(f"OK: {output_pdf} ({os.path.getsize(output_pdf)/1024:.0f}KB)")
