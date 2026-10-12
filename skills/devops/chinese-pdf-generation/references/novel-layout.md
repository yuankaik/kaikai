# A4 Portrait Novel PDF Layout

For children's novels and fiction books printed on A4 portrait. Optimized for continuous printing (no wasted blank pages from forced chapter breaks).

## CSS Template

```css
@page {
    size: A4 portrait;
    margin: 2.2cm 2cm 2.2cm 2cm;

    @bottom-center {
        content: "— " counter(page) " —";
        font-family: "Noto Serif CJK SC", serif;
        font-size: 8pt;
        color: #aaa;
    }
}

@page cover {
    margin: 0;
}

body {
    font-family: "Noto Serif CJK SC", "Noto Sans CJK SC", "SimSun", serif;
    font-size: 10.5pt;
    line-height: 1.9;
    color: #1a1a1a;
    text-align: justify;
}

/* Cover pages — full bleed */
.cover-img-page {
    page: cover;
    page-break-after: always;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    height: 100vh;
    overflow: hidden;
    background: #000;
}
.cover-img-page img {
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
}

/* Text cover page */
.cover-text-page {
    page: textcover;
    page-break-after: always;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    width: 100%;
    height: 100vh;
    text-align: center;
}
.cover-title {
    font-size: 28pt;
    font-weight: bold;
    letter-spacing: 5pt;
    font-family: "Noto Serif CJK SC", serif;
}
.cover-subtitle {
    font-size: 13pt;
    color: #777;
    margin-bottom: 60pt;
}

/* Chapter headings — CONTINUOUS FLOW, NO forced page break */
h2 {
    font-size: 19pt;
    font-weight: bold;
    text-align: center;
    margin-top: 28pt;
    margin-bottom: 4pt;
    page-break-before: avoid;
    page-break-after: avoid;
    letter-spacing: 3pt;
    font-family: "Noto Serif CJK SC", "SimSun", serif;
}

/* Body text */
p {
    text-indent: 1.8em;
    margin: 0 0 0.15em 0;
    text-align: justify;
}
h2 + p {
    text-indent: 0;
}

/* Scene breaks */
hr {
    border: none;
    text-align: center;
    margin: 20pt 0;
    overflow: visible;
}
hr::after {
    content: "✦   ✦   ✦";
    font-size: 9pt;
    color: #bbb;
    letter-spacing: 4pt;
}

/* Epigraph */
.epigraph {
    text-align: center;
    font-size: 11pt;
    color: #666;
    margin: 50pt 0 40pt 0;
    padding: 18pt 30pt;
    border-top: 1px solid #ccc;
    border-bottom: 1px solid #ccc;
    font-style: italic;
}
```

## Key Differences from Default (multi-section) Layout

| Feature | Multi-section | Novel |
|---------|:---:|:---:|
| h2 page-break-before | always | avoid |
| h2 margin-top | 0 | 28pt |
| Body font | 9.5pt sans-serif | 10.5pt serif |
| Line height | 1.5 | 1.9 |
| Paragraph indent | none | 1.8em |
| Scene breaks | none | ✦ ✦ ✦ |

## When to Use

- **Novel layout**: Fiction, children's books, story collections — when chapters should flow continuously to save paper on print
- **Multi-section layout**: Reference documents, diagnosis tables, knowledge point lists — when each section is a self-contained unit

## MD Pre-Cleaning Checklist

Before rendering, clean the markdown:

1. **Join hard line breaks** — paragraphs artificially split at ~40-50 chars need to be joined into continuous lines
2. **Normalize spaces** — double/triple spaces → single space
3. **Remove trailing spaces** — spaces before newlines
4. **Check chapter headings** — `## 第X章：TITLE` must be complete, no split titles ("水" + "坑" → "水坑")

A cleaning script pattern: join consecutive non-empty lines that don't end with sentence-ending punctuation (。！？"」』) and are not headings/scene breaks/HTML.

## Pitfalls

- The Python `markdown` library does NOT parse markdown inside `<div>` or `<center>` HTML blocks — keep headings outside HTML wrappers
- Cover images must be added via custom HTML (not markdown img tags) for full-bleed rendering
- Large cover images (~3MB each) produce large PDFs (~10MB for 3 covers) — this is expected
- WSL without GPU will be slow for rendering; 30-90 seconds is normal for 80K+ word novels
- **Children's font sizing**: 10.5pt is the adult minimum. For 10-year-old readers, use 13pt body minimum. The difference is not aesthetic — it's whether the child can comfortably read 200+ pages.

## Children's Novel Variant (Ages 8-12)

When the target reader is a child, override the defaults:

```css
body {
    font-size: 13pt;        /* was 10.5pt — children need larger */
    line-height: 1.8;       /* was 1.9 — tighter works at 13pt */
}
h2 {
    font-size: 20pt;        /* chapter titles big and clear */
}
@page {
    margin: 1.6cm;          /* less waste, shorter page count */
}
```

Illustration insertion:
```css
.illustration {
    page-break-inside: avoid;
    text-align: center;
    margin: 20pt 0;
}
.illustration img {
    max-width: 100%;
    max-height: 72vh;       /* ~72% of A4 page height */
    object-fit: contain;
}
.illustration-caption {
    font-size: 10pt;
    font-style: italic;
    color: #888;
    margin-top: 6pt;
}
```

## Reference Script

A complete working script is at `scripts/gen-novel-a4.py` — it handles cover image extraction, MD→HTML conversion with the novel CSS, chapter subtitle merging, and epigraph styling. Usage:

```bash
python3 scripts/gen-novel-a4.py
```

Configure paths (DESKTOP, MD_PATH, cover_images) at the top of the script before running.
