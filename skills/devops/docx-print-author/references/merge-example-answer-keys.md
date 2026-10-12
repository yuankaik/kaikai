# DOCX Multi-File Merge: Session Example

## Scenario
User had 60 daily answer key files (第1天～第60天-答案与指导.docx) in a folder. Each file:
- Letter size (216×279mm), 32mm margins, 11pt body
- ~140-200 paragraphs per file
- Mixed content: story text, questions, answers, decorative separators
- Total across 60 files: ~310 estimated pages

## What We Did

### 1. Analyzed source format
Checked 3 sample files (Day 1, Day 30, Day 60) for page size, margins, font distribution, paragraph count.

### 2. Merged with compression
- Sorted by day number (natural sort on filename)
- Page break between each day
- Day header added: `══ 第N天 ══` (10pt bold blue)
- All paragraphs copied with font normalization
- Blank paragraphs stripped entirely
- Compact spacing: 0pt before, 0.3pt after, 1.08 line spacing

### 3. Font normalization map
| Original | → Merged | When |
|----------|---------|------|
| 15pt bold | 10pt | Major title |
| 13pt bold | 9.5pt | Section header |
| 11pt bold | 9pt | Sub-header |
| 11pt | 8.5pt | Body text |
| 8pt | 8pt | Preserved (footnotes) |

### 4. Layout optimization
- Page: A4 (210×297mm)
- Margins: top 10mm, bottom 8mm, left/right 15mm
- All paragraphs: keepLines protection
- Explicit page breaks before long pieces

## Result

| Metric | Original (60 files) | Merged (1 file) |
|--------|-------------------|-----------------|
| Files | 60 | 1 |
| Page size | Letter | A4 |
| Margins | 32mm all sides | 10-15mm |
| Body font | 11pt | 8.5pt |
| Pages | ~310 | ~132 |
| Paper saved | — | ~58% |

## Key Insight: Answer Key Content Ratio
Analysis of Day 1 showed:
- Story text: 31% (redundant — parent has student booklet)
- Questions: 12%
- Answers + explanations: 34%
- Headers/decorations: 23%

If story text were stripped, another ~30% paper savings possible. But only do this when user explicitly asks — they may want the stories for context when grading.
