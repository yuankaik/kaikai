# Day3 Structured Practice Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Day3 generation path that turns Day2 grading results into a structured practice spec and a print-readable A4 PDF.

**Architecture:** Keep planning, typography, and rendering separate. `tutor_core/day3_spec.py` produces pure data, `rendering/typography.py` handles line wrapping, and `rendering/day_pdf.py` renders the final PDF. `scripts/make_day3_from_day2.py` is the command-line entry point.

**Tech Stack:** Python standard library, ReportLab, pypdf, unittest.

---

### Task 1: Regression Tests

**Files:**
- Create: `tests/test_day3_generation.py`

- [x] **Step 1: Write failing tests**

Tests cover Day3 spec selection, protected unit wrapping, and PDF question font size metadata.

- [x] **Step 2: Run tests to verify they fail**

Run: `python -m unittest discover -s tests -v`

Expected before implementation: import failures for missing `tutor_core.day3_spec` and `rendering.typography`.

### Task 2: Day3 Spec Builder

**Files:**
- Create: `tutor_core/day3_spec.py`
- Create: `tutor_core/__init__.py`

- [ ] **Step 1: Implement grading CSV reader**

Read `grading-result.csv` with UTF-8 BOM support.

- [ ] **Step 2: Implement `build_day3_spec(rows)`**

Return a dictionary containing metadata, modules, questions, feynman prompt, classroom radar, and handwriting words.

- [ ] **Step 3: Verify tests pass for spec behavior**

Run: `python -m unittest tests.test_day3_generation.Day3SpecTests -v`

### Task 3: Typography Wrapper

**Files:**
- Create: `rendering/typography.py`
- Create: `rendering/__init__.py`

- [ ] **Step 1: Implement tokenization**

Keep digit-unit chunks such as `255ml`, `6升641ml`, `10cm` together.

- [ ] **Step 2: Implement width-based wrapping**

Use `reportlab.pdfbase.pdfmetrics.stringWidth`.

- [ ] **Step 3: Verify unit wrapping tests**

Run: `python -m unittest tests.test_day3_generation.TypographyTests -v`

### Task 4: PDF Renderer

**Files:**
- Create: `rendering/day_pdf.py`

- [ ] **Step 1: Implement constants**

Use `QUESTION_FONT_SIZE = 10.8` and `BODY_FONT_SIZE = 9.0`.

- [ ] **Step 2: Render A4 pages**

Render page 1 practice, page 2 Boss/Feynman/radar, page 3 handwriting and parent observation.

- [ ] **Step 3: Verify renderer metadata tests**

Run: `python -m unittest tests.test_day3_generation.PdfRendererTests -v`

### Task 5: CLI Generation

**Files:**
- Create: `scripts/make_day3_from_day2.py`

- [ ] **Step 1: Read Day2 grading**

Input defaults to `submissions/2026-06-04-Day2/grading-result.csv`.

- [ ] **Step 2: Write JSON spec**

Output `practice/specs/Day3-海王龙的逆向追踪.json`.

- [ ] **Step 3: Write PDF**

Output `Day3-海王龙的逆向追踪.pdf`.

- [ ] **Step 4: Verify all tests and generate outputs**

Run:

```powershell
python -m unittest discover -s tests -v
python scripts\make_day3_from_day2.py
```

Expected: all tests pass, then script prints the spec and PDF paths.
