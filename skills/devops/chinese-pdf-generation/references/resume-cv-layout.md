# Resume / CV PDF Layout (2-page controlled, ATS-safe)

Generating a **professional resume** PDF is a different problem from novels or worksheets.
The hard constraints are:

1. **Page count must be exactly N** (1–2 pages for most CVs). Recruiters reject 3-page resumes.
2. **No visual defects** — overlapping text, `**` residue, misaligned "columns" look amateur.
3. **ATS-parseable** — real text (not images), no text boxes, standard section headings.

---

## THE BIG PITFALL: do not hand-roll the Markdown→HTML renderer

Writing a custom line-by-line MD parser (heading/`-`/paragraph branches) **looks** easy and
**will** produce these two defects every time:

| Defect | Cause | Symptom |
|---|---|---|
| **Overlapping / smeared text** | `  `-indented continuation lines (standard in 80-col-wrapped MD) get appended to the wrong element or a `<p>` is opened without closing | Words pile on top of each other on the rendered page |
| **Literal `**` left in output** | Bold spanning a line break: `**批次追溯、\n  受控物料零误发**` — regex `\*\*(.+?)\*\*` without `re.S` fails to match across the `\n` | `**` visible in the PDF |

**Fix — use the `markdown` library, and merge wrapped lines BEFORE parsing:**

```python
import markdown, re, os
from weasyprint import HTML

src = open(md_path, encoding="utf-8").read()

# 1) Merge continuation lines FIRST (MD hard-wraps from editors/LLM output)
raw = src.split("\n")
merged = []
for ln in raw:
    s = ln.rstrip()
    if (merged and s.startswith("  ") and merged[-1].strip()
            and not merged[-1].strip().startswith(("#", "-", "|"))
            and merged[-1].strip() != "---"):
        merged[-1] = merged[-1].rstrip() + " " + s.strip()
    else:
        merged.append(s)
md = "\n".join(merged)

# 2) Let the library parse it — it handles bold/italic/tables/lists correctly
html_body = markdown.markdown(md, extensions=["tables", "fenced_code", "sane_lists"])
```

This eliminates BOTH defects at once. `sane_lists` also prevents stray `<ol>` nesting.

---

## ATS-safe resume CSS (2-page resume)

```css
@page { size: A4; margin: 1.15cm 1.5cm; }
body { font-family: "Noto Sans CJK SC","WenQuanYi Micro Hei","Microsoft YaHei",
       sans-serif; font-size: 9.3pt; line-height: 1.45; color:#222; margin:0; }
h1 { font-size:18pt; text-align:center; margin:0 0 3px; letter-spacing:3px;
     color:#003366; border:none; padding:0;
     page-break-before: avoid; }          /* ← CRITICAL, see below */
h1 + p { text-align:center; font-size:9.2pt; color:#333; margin:0; }
h2 { font-size:10.6pt; color:#003366; margin:9px 0 3px; padding-bottom:1.5px;
     border-bottom:1.3px solid #003366; }
h3 { font-size:9.8pt; color:#003366; margin:6px 0 2px; }
p  { margin:2px 0; text-align:justify; }
ul { margin:2px 0; padding-left:15px; }
li { margin:1.3px 0; text-align:justify; }
strong { color:#111; }
em { color:#666; font-style:normal; font-size:8.7pt; }
hr { border:none; border-top:1px solid #ddd; margin:6px 0; }
/* borderless 2-col table for the skills block — ATS reads it as plain text */
table { border-collapse:collapse; width:100%; margin:3px 0; font-size:9.2pt; }
td { border:none; padding:1px 4px; text-align:left; vertical-align:top; }
td:first-child { width:19%; white-space:nowrap; }
```

### Why `page-break-before: avoid` on h1 is critical

`scripts/md2pdf_cjk.py` ships with `h1 { page-break-before: always }`. On a **multi-section
resume** that forces a blank page after the header block, pushing a 2-page resume to 3.

Always override it for resumes, and verify:

```bash
pdfinfo out.pdf | grep -i pages     # must show 2, not 3
```

---

## Aligned "columns" without tables you can't control

Do **not** use full-width ideographic spaces (`　`, U+3000) to fake column alignment —
proportional CJK fonts render them at inconsistent widths and the columns drift.

Use a **borderless 2-column markdown table** instead:

```markdown
| | |
|---|---|
| **GMP合规专项** | 合规体系与飞检应对 · UDI与批次追溯 · 温湿度监控与记录管理 |
| **仓储运营** | 多仓运营与团队管理 · 新仓筹建与搬迁 · 库容布局与储位规划 |
```

Render with `extensions=['tables']`, style `td { border:none }`. Visually it's a clean
two-column layout; to an ATS parser it's still flat text.

---

## Page-count control (fit 2 pages)

Resume content always overflows on the first attempt. Tighten in this order:

1. `margin: 1.15cm 1.5cm` (from 1.8cm default) — biggest single win
2. `font-size: 9.3pt` body, `line-height: 1.45`
3. `margin: 2px 0` on `p`, `1.3px 0` on `li`
4. **Reduce content** — cut the weakest bullets, don't shrink font below 9pt

**Do not** go below ~9pt or 1.4 line-height; a "fits on 2 pages" resume nobody can read
is a loss. Better to cut a bullet.

---

## Verification loop (mandatory — do not skip)

```bash
# 1. Page count
pdfinfo out.pdf | grep -i pages

# 2. No residual markdown artifacts
pdftotext -enc UTF-8 out.pdf /tmp/chk.txt && grep -c '\*\*' /tmp/chk.txt   # expect 0

# 3. Visual check — overlaps only show up as pixels, not text
pdftoppm -png -r 95 out.pdf /tmp/chk
```

Then **look at the PNG with the vision tool** and ask specifically:
"any overlapping text, misaligned columns, or content cut at the page edge?"

A text-only check will pass while the page is visibly broken — overlapping glyphs still
extract as clean text. The pixel check is the only way to catch it.

---

## Reading an existing PDF resume

`read_file` on a PDF returns binary garbage. Extract first:

```bash
pdftotext -enc UTF-8 -layout resume.pdf /tmp/resume.txt
```
Then `read_file` the `.txt`. `-layout` preserves visual column structure, which matters
for resumes.
