# Cover Image PDF Pattern

When markdown-generated PDFs need cover pages with high-resolution images, the standard md2pdf pipeline (markdown→HTML→PDF) handles text well but struggles with full-page images. Use a custom Python script instead.

## Template Script

```python
#!/usr/bin/env python3
import markdown, os
from weasyprint import HTML

# Paths
desktop = "/path/to/folder"
image_files = ["cover1.png", "cover2.png", "cover3.png"]  # sorted as needed

# Read markdown body
with open(os.path.join(desktop, "story.md"), "r") as f:
    md_text = f.read()

# Convert markdown to HTML
md = markdown.Markdown(extensions=['toc', 'tables', 'fenced_code'])
body_html = md.convert(md_text)

# Build cover pages
cover_pages = ""
for fname in image_files:
    img_path = os.path.join(desktop, fname)
    cover_pages += f'''<div style="page-break-after: always; display: flex; 
    align-items: center; justify-content: center; 
    width: 210mm; height: 297mm; margin: 0; padding: 0; overflow: hidden;">
<img src="{img_path}" style="max-width: 210mm; max-height: 297mm;">
</div>
'''

# Full HTML
full_html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
@page {{ size: A4; margin: 0; }}
@page body {{ size: A4; margin: 1.8cm; }}
body {{ font-family: "Noto Sans CJK SC", sans-serif; font-size: 10pt; line-height: 1.8; }}
h1 {{ font-size: 14pt; page-break-before: always; }}
h2 {{ font-size: 12pt; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ border: 1px solid #ccc; padding: 4pt; }}
</style></head>
<body>
{cover_pages}
<div class="body">{body_html}</div>
</body></html>"""

# Write
html_path = os.path.join(desktop, "temp.html")
with open(html_path, "w") as f:
    f.write(full_html)

pdf_path = os.path.join(desktop, "output.pdf")
HTML(html_path).write_pdf(pdf_path)
os.remove(html_path)
```

## Key CSS for Cover Pages
- `@page { size: A4; margin: 0; }` — zero margins for full-bleed images
- `max-width: 210mm; max-height: 297mm` — A4 dimensions for image constraint
- `page-break-after: always` — each cover image on its own page
- `overflow: hidden` — prevent image overflow

## Pitfalls
- File paths must be absolute or relative to the script's working directory
- Large images (~3MB each) produce large PDFs (~10MB for 3 covers)
- WeasyPrint reads images at render time — keep images accessible until PDF is written
- The md2pdf_cjk.py script is NOT suitable for cover images; use this custom approach
