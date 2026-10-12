# Novel Layout CSS for A4 Portrait Printing

Continuous-print CSS for Chinese novels. No forced page breaks per chapter — chapters flow naturally with visual separation.

## Full CSS

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

/* Cover: full bleed */
@page cover { margin: 0; }

body {
    font-family: "Noto Serif CJK SC", "Noto Sans CJK SC", "SimSun", serif;
    font-size: 10.5pt;
    line-height: 1.9;
    color: #1a1a1a;
    text-align: justify;
}

/* Chapter headings: continuous flow, 28pt gap instead of page break */
h2 {
    font-size: 19pt;
    font-weight: bold;
    text-align: center;
    margin-top: 28pt;
    margin-bottom: 4pt;
    page-break-before: avoid;      /* ← KEY: not 'always' */
    page-break-after: avoid;
    letter-spacing: 3pt;
    font-family: "Noto Serif CJK SC", "SimSun", serif;
}

/* Body paragraphs */
p {
    text-indent: 1.8em;
    margin: 0 0 0.15em 0;
    text-align: justify;
}
h2 + p { text-indent: 0; }

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

/* Cover page elements */
.cover-box {
    page: cover;
    page-break-after: always;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    width: 100%;
    height: 100vh;
    text-align: center;
}
.cover-title { font-size: 28pt; font-weight: bold; letter-spacing: 5pt; }
.cover-subtitle { font-size: 13pt; color: #777; margin-bottom: 60pt; }
```

## Key Changes from Default md2pdf

| Property | Default | Novel |
|----------|---------|-------|
| h2 page-break-before | always | avoid |
| h2 margin-top | 0 | 28pt |
| Body font-size | 11pt | 10.5pt |
| Body line-height | 1.5 | 1.9 |
| Scene breaks | plain <hr> | ✦ ✦ ✦ |

## Full Cover Image Integration

For PDFs with cover images + text, use the pattern from `scripts/gen-cover-pdf.py`:
- Cover images as separate `<div class="cover-img-page">` with `@page cover { margin: 0 }`
- `max-width: 100%; max-height: 100%; object-fit: contain` for image scaling
- Text cover page between images and body
- Body uses `@page body { margin: 2.2cm 2cm 2.2cm 2cm; }`
