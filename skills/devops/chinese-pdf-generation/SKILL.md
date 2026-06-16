---
name: chinese-pdf-generation
description: Generate properly-rendered Chinese PDFs from Markdown (解决中文乱码). Use WeasyPrint + fonts-noto-cjk. Covers CJK font detection, fallback font chains, and the md2pdf_cjk.py script.
---

# Chinese PDF Generation

Generate PDFs from Markdown with correct Chinese character rendering. Use when Chinese text appears as garbled characters, empty boxes, or tofu in generated PDFs.

## Trigger Conditions

- User asks to convert .md to PDF and the content is Chinese
- PDF output shows garbled/missing Chinese characters
- Previous WeasyPrint PDF generation produced "tofu" (empty rectangle glyphs)

## Quick Start (one-off conversion)

```bash
python3 /tmp/md2pdf_cjk.py input.md output.pdf
```

## Prerequisites

### 1. Install CJK fonts (one-time)

```bash
sudo apt-get install -y fonts-noto-cjk
```

Verify: `fc-list :lang=zh | head -3` should show `Noto Sans CJK SC` or similar.

### 2. Install WeasyPrint (one-time)

```bash
pip install --break-system-packages weasyprint markdown
```

Note: On Python 3.11+ externally-managed environments, `--break-system-packages` is required. On older systems or venvs, omit the flag.

## Core Script: md2pdf_cjk.py

The script lives at `scripts/md2pdf_cjk.py` in this skill. It:
- Converts Markdown to HTML with `markdown` (tables + fenced_code + toc extensions)
- Renders to PDF with WeasyPrint using `"Noto Sans CJK SC"` as primary font
- Falls back through `"WenQuanYi Micro Hei"`, `"SimSun"`, then system sans-serif
- Sets proper A4 page size with 1.8cm margins
- Embeds fonts in the PDF (output typically 300-600KB for Chinese content)

Usage from any directory:
```bash
python3 ~/.hermes/skills/devops/chinese-pdf-generation/scripts/md2pdf_cjk.py input.md output.pdf
```

## Why Chinese PDFs Break

1. **Missing CJK fonts**: WSL/headless Linux typically has zero Chinese fonts. WeasyPrint embeds only the fonts it can find — if none support CJK, every Chinese character renders as ▯ or disappears.
2. **Wrong font-family in CSS**: Specifying `"SimSun"` or `"Microsoft YaHei"` on Linux silently fails because those fonts don't exist. Use `"Noto Sans CJK SC"` which is the free cross-platform standard.
3. **Small PDF size = missing glyphs**: A well-rendered Chinese PDF with embedded fonts is typically 300-600KB for a few pages. If the output is 20-30KB, the fonts weren't embedded and the PDF is broken.

## Batch Conversion

```bash
cd /path/to/directory
for f in *.md; do
  python3 /tmp/md2pdf_cjk.py "$f" "${f%.md}.pdf"
done
```

## Pitfalls

- **`apt-get` fails without sudo**: On restricted systems, use `apt list --installed | grep noto` to check if fonts already exist. If not, fall back to generating HTML files that the user opens in a browser (which has system fonts) and prints to PDF manually.
- **WeasyPrint timeout**: Large documents with many tables or code blocks can take 60-120 seconds. The first run after font install is slowest (font cache warm-up).
- **`--break-system-packages` is safe here**: WeasyPrint has no system-level conflicts. It's a leaf package.
- **Font fallback order matters**: `"Noto Sans CJK SC"` must come first in the CSS `font-family` chain. Putting `"SimSun"` first causes silent failure on Linux.
