#!/usr/bin/env python3
"""
A4竖版小说PDF — 自动发现封面图片 + 连续排版正文
Usage: Edit DESKTOP and MD_PATH below, then run.
Features:
  - Auto-discovers all PNG files in output dir as full-bleed cover pages
  - Text cover page (title/subtitle/dedication) extracted from MD
  - Continuous flow (no forced page breaks) for economical printing
  - Noto Serif CJK SC body, 10.5pt, line-height 1.9
  - Scene breaks styled as ✦ ✦ ✦
  - Epigraph framed with border-lines
"""

import re, os, sys
import markdown
from weasyprint import HTML

# ── CONFIGURE THESE ──
DESKTOP = "/mnt/c/Users/admin/Desktop/佳乐暑假完整练习库"
MD_PATH = os.path.join(DESKTOP, "字海钓徒-全文.md")
OUT_PDF = os.path.join(DESKTOP, "字海钓徒-全文-A4竖版.pdf")

# ═══════════════════════════════════════════════════════
# 1. Auto-discover cover images
# ═══════════════════════════════════════════════════════
cover_images = sorted([
    os.path.join(DESKTOP, f) for f in os.listdir(DESKTOP)
    if f.endswith('.png')
])
print(f"Cover images ({len(cover_images)}):")
for img in cover_images:
    exists = "✓" if os.path.exists(img) else "✗ MISSING"
    size_mb = os.path.getsize(img)/1024/1024 if os.path.exists(img) else 0
    print(f"  {exists} {os.path.basename(img)} ({size_mb:.1f}MB)")

# ═══════════════════════════════════════════════════════
# 2. Read markdown
# ═══════════════════════════════════════════════════════
with open(MD_PATH, "r", encoding="utf-8") as f:
    md_text = f.read()

# Extract cover text
cover_title = "字海钓徒"
cover_subtitle = "一支漏水的水笔，一把会发光的钓竿"
cover_dedication = "写给佳乐"
m = re.search(r'<center>\s*# (.+?)\n+### (.+?)\n.*?写给(.+?)\n', md_text, re.DOTALL)
if m:
    cover_title = m.group(1).strip()
    cover_subtitle = m.group(2).strip()
    cover_dedication = f"写给{m.group(3).strip()}"

# Body starts from # 目录
body_start = md_text.find("# 目录")
if body_start < 0:
    body_start = md_text.find("佳乐从来不知道")
body_md = md_text[body_start:] if body_start >= 0 else md_text

# ═══════════════════════════════════════════════════════
# 3. Convert body MD → HTML
# ═══════════════════════════════════════════════════════
md = markdown.Markdown(extensions=['toc', 'tables', 'fenced_code'])
body_html = md.convert(body_md)

# Fix epigraph
body_html = body_html.replace(
    '<p>佳乐从来不知道，他那支漏水的水笔，是一把钓竿。</p>',
    '<div class="epigraph"><p>佳乐从来不知道，他那支漏水的水笔，是一把钓竿。</p></div>'
)

# Fix chapter subtitle splits (h2 + short <p> → merged)
def merge_subtitles(html):
    def replacer(m):
        h2 = m.group(1)
        sub = m.group(2).strip()
        if not sub or len(sub) > 30:
            return m.group(0)
        return h2.replace('</h2>', f'<br><span class="ch-subtitle">{sub}</span></h2>')
    return re.sub(r'(<h2>[^<]+)</h2>\s*<p>([^<]{1,30})</p>', replacer, html)
body_html = merge_subtitles(body_html)

# ═══════════════════════════════════════════════════════
# 4. CSS — continuous flow novel layout
# ═══════════════════════════════════════════════════════
CSS = r"""
@page cover { size: A4 portrait; margin: 0; }
.cover-img-page {
    page: cover; page-break-after: always;
    display: flex; align-items: center; justify-content: center;
    width: 100%; height: 100vh; margin: 0; padding: 0;
    overflow: hidden; background: #000;
}
.cover-img-page img { max-width: 100%; max-height: 100%; object-fit: contain; }

@page textcover { size: A4 portrait; margin: 0; }
.cover-text-page {
    page: textcover; page-break-after: always;
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    width: 100%; height: 100vh; text-align: center;
}
.cover-title { font-size: 28pt; font-weight: bold; letter-spacing: 5pt;
    margin-bottom: 10pt; font-family: "Noto Serif CJK SC", serif; }
.cover-subtitle { font-size: 13pt; color: #777; margin-bottom: 60pt; }
.cover-to { font-size: 12pt; color: #555; margin-top: 20pt; letter-spacing: 2pt; }

@page body {
    size: A4 portrait; margin: 2.2cm 2cm 2.2cm 2cm;
    @bottom-center {
        content: "— " counter(page) " —";
        font-family: "Noto Serif CJK SC", serif; font-size: 8pt; color: #aaa;
    }
}
body {
    font-family: "Noto Serif CJK SC", "Noto Sans CJK SC", "SimSun", serif;
    font-size: 10.5pt; line-height: 1.9; color: #1a1a1a; text-align: justify;
}

.epigraph {
    text-align: center; font-size: 11pt; color: #666;
    margin: 50pt 0 40pt 0; padding: 18pt 30pt;
    border-top: 1px solid #ccc; border-bottom: 1px solid #ccc;
    font-style: italic;
}

h2 {
    font-size: 19pt; font-weight: bold; text-align: center;
    margin-top: 28pt; margin-bottom: 4pt;
    page-break-before: avoid; page-break-after: avoid;
    letter-spacing: 3pt;
    font-family: "Noto Serif CJK SC", "SimSun", serif;
}
span.ch-subtitle {
    display: block; font-size: 14pt; font-weight: normal; color: #666;
    letter-spacing: 2pt; margin-top: 4pt;
}

p { text-indent: 1.8em; margin: 0 0 0.15em 0; text-align: justify; }
h2 + p { text-indent: 0; }

hr { border: none; text-align: center; margin: 20pt 0; overflow: visible; }
hr::after {
    content: "✦   ✦   ✦"; font-size: 9pt; color: #bbb; letter-spacing: 4pt;
}

blockquote { border-left: 3px solid #ccc; margin: 8pt 20pt;
    padding: 4pt 14pt; color: #555; font-size: 10pt; }
"""

# ═══════════════════════════════════════════════════════
# 5. Build HTML and render
# ═══════════════════════════════════════════════════════
cover_html = ""
for img_path in cover_images:
    cover_html += f'<div class="cover-img-page"><img src="{img_path}"></div>\n'

text_cover = f'''<div class="cover-text-page">
<div class="cover-title">{cover_title}</div>
<div class="cover-subtitle">{cover_subtitle}</div>
<div style="height: 60pt;"></div>
<div class="cover-to">{cover_dedication}</div>
</div>'''

full_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="utf-8"><style>{CSS}</style></head>
<body>
{cover_html}
{text_cover}
<div class="body-content">{body_html}</div>
</body></html>"""

tmp = os.path.join(DESKTOP, "_render_tmp.html")
with open(tmp, "w", encoding="utf-8") as f:
    f.write(full_html)

print(f"\nRendering PDF with {len(cover_images)} cover images...")
HTML(tmp).write_pdf(OUT_PDF)
os.remove(tmp)

size_kb = os.path.getsize(OUT_PDF) / 1024
print(f"Done: {OUT_PDF} ({size_kb:.0f} KB)")
