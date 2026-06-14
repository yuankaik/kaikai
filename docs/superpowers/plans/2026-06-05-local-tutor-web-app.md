# Local Tutor Web App Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a zero-dependency local web app shell so Yuan Jiale can complete daily web lessons, record voice, and save learning data into SQLite.

**Architecture:** Keep the existing daily spec/PDF/static generation intact, and add an application layer around it. The new layer serves a child-facing Captain page, writes answers and recordings to local storage, and prepares clean data for later AI grading and DayN generation.

**Tech Stack:** Python standard library HTTP server, SQLite, vanilla HTML/CSS/JavaScript, existing `practice/specs/*.json` daily lesson specs.

---

### Task 1: SQLite Learning Store

**Files:**
- Create: `engine/learning_store.py`
- Test: `tests/test_learning_store.py`

- [x] Define `LearningStore` with `initialize`, `save_result`, `save_recording`, and `list_results`.
- [x] Store data in `data/learning.db`.
- [x] Cover table creation and inserts with unit tests.

### Task 2: Captain Page Renderer

**Files:**
- Create: `app/captain_renderer.py`
- Test: `tests/test_captain_app_renderer.py`

- [x] Render a child-facing page from a daily spec.
- [x] Include answer inputs, browser microphone recording, and submit-to-server behavior.
- [x] Exclude child-facing buttons named "大副查看" or "记录".

### Task 3: Local Tutor Server

**Files:**
- Create: `app/local_tutor_server.py`
- Create: `scripts/start_tutor_site.py`
- Test: `tests/test_local_tutor_server.py`

- [x] Serve `/`, `/captain/<day>`, `/api/result`, `/api/recording`, and selected media files.
- [x] Accept JSON answer submissions and audio blobs.
- [x] Provide a one-command startup script.

### Task 4: Verification

**Files:**
- Modify tests only as needed for the new app contract.

- [ ] Run `python -m unittest discover -s tests -v`.
- [ ] Confirm the new app can be started with `python scripts/start_tutor_site.py`.
