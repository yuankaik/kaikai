# Split Multi-Book Collection into Individual Ebooks

Use when a single mobi/epub file contains a collection of books (e.g., "沈石溪品藏书系套装共26册") and the user needs individual files per book.

## Workflow

```
mobi collection → epub → analyze TOC → split by anchors → individual epubs → mobi
```

## Step 1: Convert to EPUB (if source is mobi)

```bash
ebook-convert "collection.mobi" "collection.epub"
```

For 40MB+ files, expect 1-3 minutes. The EPUB is easier to parse programmatically.

## Step 2: Analyze TOC Structure

```python
import ebooklib
from ebooklib import epub

book = epub.read_epub('collection.epub')

# TOC is a list of epub.Link objects
for item in book.toc:
    print(f"{item.title} → {item.href}")
# Output: "牧羊神豹 → index_split_000.html#filepos3059"
```

Each TOC entry has:
- `title`: book name
- `href`: `filename#anchor` — the anchor (`#fileposXXXXX`) marks the exact position in the HTML file

Skip `toc[0]` if it's a 总目录/table-of-contents entry.

## Step 3: Extract Per-Book Content

Core strategy: for book N, collect all HTML content from its TOC anchor to the next book's TOC anchor.

```python
from bs4 import BeautifulSoup

def find_anchor_element(soup, anchor):
    """Find the element with id=anchor or <a name=anchor>"""
    elem = soup.find(id=anchor)
    if not elem:
        elem = soup.find('a', attrs={'name': anchor})
    return elem

def collect_book_body(html_docs, start, end):
    """Collect body children from start anchor to end anchor across HTML files"""
    new_body = BeautifulSoup('<body></body>', 'html.parser').body
    collecting = False
    
    for fname in sorted(html_docs.keys()):
        soup = html_docs[fname]['soup']
        if not soup.body:
            continue
        
        if fname == start['filename'] and not collecting:
            collecting = True
            pos = find_anchor_element(soup, start['anchor'])
            # Walk up from anchor to find top-level body child, then collect from there
            # ... (see split_books_v2.py for full implementation)
        
        elif collecting:
            if fname == end['filename']:
                pos = find_anchor_element(soup, end['anchor'])
                # Collect up to the anchor element, then stop
                break
            else:
                # Middle file: collect all body children
                for child in soup.body.children:
                    new_body.append(child)
    
    return new_body
```

Key pitfall: many collections have a directory page that lists ALL book titles (e.g., `index_split_000.html`). Do NOT search for book titles in the body text — use the TOC anchor links (`#fileposXXXXX`) which are reliable positional markers.

## Step 4: Generate Individual EPUBs

```python
from ebooklib import epub

new_book = epub.EpubBook()
new_book.set_title(title)
new_book.set_language('zh')
new_book.add_author('沈石溪')

# Add CSS from source
for css_name, css_content in css_files.items():
    css_item = epub.EpubItem(
        uid=f'css_{i}',
        file_name=css_name,
        media_type='text/css',
        content=css_content
    )
    new_book.add_item(css_item)

# Create chapter
chapter = epub.EpubHtml(title=title, file_name='content.xhtml', lang='zh')
html_content = f'''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" lang="zh">
<head><title>{title}</title>
<link rel="stylesheet" type="text/css" href="stylesheet.css"/>
</head>
{str(book_body)}
</html>'''
chapter.set_content(html_content.encode('utf-8'))
new_book.add_item(chapter)
new_book.spine = [chapter]

epub.write_epub(f'{title}.epub', new_book)
```

## Step 5: Batch Convert to MOBI

```bash
for epub in *.epub; do
  name="${epub%.epub}"
  ebook-convert "$epub" "${name}.mobi" --title "$name" --authors "沈石溪"
done
```

## Pitfalls

1. **Directory page interference**: Don't search body text for book titles — use TOC anchors.
2. **File-level vs anchor-level**: Some books span multiple HTML files, some share a file with neighbors (separated by anchors). Handle both.
3. **Last book**: has no `end` boundary — collect to EOF.
4. **CSS must be copied**: Without CSS, the output mobi loses formatting. Collect all `.css` items from the source epub.
5. **Image references**: For simplicity, images are NOT copied in the basic approach. Content is preserved but images are dropped. If images are critical, also copy image items and adjust `src` paths.
6. **Content validation**: Skip books with <500 characters of extracted text — anchor lookup may have failed.

## Verification

- Each output mobi should be 250-450KB for a typical children's novel
- 43MB collection → 26 × ~350KB = ~9MB total (smaller because images are dropped)
- Quick content check: `ebook-meta "book.mobi"` to verify title
