---
name: ebook-split-collection
description: Split multi-book epub/mobi collections into individual ebooks. Use when user has a "套装"/"合集" epub or mobi and wants each volume as a standalone file, or when a child can't flip pages in a large collection file.
category: devops
---

# Ebook Collection Splitter

Split a multi-volume ebook collection (套装/合集) into individual standalone ebooks.

## When to Use
- User has a "合集" (collection) mobi/epub and wants single books
- "合集翻不了页" — reader can't handle large collection files
- "拆成1本1个" — split into one file per volume

## Prerequisites
```bash
pip install --break-system-packages ebooklib beautifulsoup4
# Calibre must be installed for mobi conversion
which ebook-convert  # should return a path
```

## Workflow

### Step 1: Convert to EPUB (if source is MOBI)
```bash
ebook-convert "合集.mobi" /tmp/collection.epub
```
Large files (40+ MB) take 1-3 minutes. Use background mode with notify_on_complete.

### Step 2: Analyze TOC Structure
```python
import ebooklib
from ebooklib import epub

book = epub.read_epub('/tmp/collection.epub')
for item in book.toc:
    if isinstance(item, epub.Link):
        print(f"{item.title} → {item.href}")
```
This reveals how many volumes and which HTML files/anchors each occupies.

### Step 3: Split by Anchor Boundaries
Key insight: each volume in the TOC points to `filename.html#fileposNNNNN`. These anchor IDs exist in the HTML as `id="fileposNNNNN"` elements.

Strategy:
1. Load all HTML docs from spine order
2. For each book: find its start anchor → collect all body children from that point to the next book's start anchor
3. Package each chunk as a standalone epub

See `references/split-by-toc-anchors.py` for the full Python script.

### Step 4: Convert to MOBI
```bash
for epub in /tmp/split_books/*.epub; do
    ebook-convert "$epub" "/path/to/output/$(basename "$epub" .epub).mobi" \
        --title "书名" --authors "作者"
done
```

## Pitfalls
- **目录页干扰**: The TOC page (usually index_split_000.html) lists ALL book titles. Don't search for titles in merged body — use TOC hrefs to locate exact anchors instead.
- **同一文件多本书**: Some volumes share an HTML file, separated by `filepos` anchors. Must split inside the HTML, not just by file boundaries.
- **CSS/Images**: Minimal splitting (CSS only, no images) produces working mobi files at ~300KB each. Full resource copying is possible but images bloat file size.
- **最后一本**: The last book extends to end-of-file — its `end_file` is None.

## Reference
- `references/split-by-toc-anchors.py` — Full working script for 沈石溪 26-volume collection split
