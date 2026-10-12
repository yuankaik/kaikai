# Improved CSS for multi-section Chinese PDFs

The default `md2pdf_cjk.py` uses `page-break-before: always` on `h1`, which forces each top-level section to start on a new page. For dense multi-section documents (diagnosis tables, knowledge point summaries), this wastes paper. Use the CSS below instead.

## Multi-section CSS (no forced page breaks)

```css
@page { size: A4; margin: 1.5cm 1.2cm; }
body {
    font-family: "Noto Sans CJK SC", "WenQuanYi Micro Hei", sans-serif;
    font-size: 9.5pt; line-height: 1.5; color: #222;
}
h1 { font-size: 15pt; border-bottom: 2px solid #333; padding-bottom: 4pt; margin-top: 10pt; }
h2 { font-size: 12pt; margin-top: 12pt; border-bottom: 1px solid #999; padding-bottom: 2pt; }
h3 { font-size: 10.5pt; margin-top: 8pt; }
table { border-collapse: collapse; width: 100%; margin: 6pt 0; font-size: 8.5pt; }
th, td { border: 1px solid #888; padding: 3pt 5pt; text-align: left; vertical-align: top; }
th { background: #e8e8e8; font-weight: bold; font-size: 8pt; }
td { word-break: break-all; }
tr:nth-child(even) td { background: #fafafa; }  /* alternating row colors */
p { margin: 4pt 0; }
blockquote { border-left: 3px solid #ccc; margin: 4pt 0; padding: 2pt 10pt; color: #555; font-size: 9pt; background: #f9f9f9; }
code { background: #f4f4f4; padding: 1pt 3pt; font-size: 8pt; }
hr { border: none; border-top: 1px solid #ddd; margin: 12pt 0; }
```

## Key differences from default

| Feature | Default script | Improved CSS |
|---------|:---:|:---:|
| Page breaks on h1 | ❌ forced | ✅ none (continuous) |
| Alternating row colors | ❌ none | ✅ nth-child(even) |
| Font size | 11pt | 9.5pt (fits more content) |
| Margins | 1.8cm | 1.5cm (tighter) |
| em styling | italic | red (#c00) for emphasis |

## When to use which

- **Single-section document** (one report/article) → use default CSS (page breaks on h1 are fine)
- **Multi-section dense doc** (diagnosis tables, knowledge point lists) → use improved CSS
- **Warning/emphasis heavy** → improved CSS renders `<em>` and `<blockquote>` with visual distinction

## Verification checklist

After generating a PDF:
1. File size > 50KB → fonts embedded ✅
2. CJK byte traces > 1000 → Chinese content present ✅
3. Check for "Noto" in raw PDF bytes → correct font ✅
4. If file < 30KB → fonts missing, reinstall `fonts-noto-cjk`
