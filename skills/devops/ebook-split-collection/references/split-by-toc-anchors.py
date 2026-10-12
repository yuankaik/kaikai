"""
Split multi-book epub collection into individual mobi files by TOC anchors.
Working script — tested on 沈石溪 26-volume collection (43MB → 26 × ~300KB mobi).

Usage: python3 split-by-toc-anchors.py <source.epub> <output_dir>
"""
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import os, re, subprocess, sys

def sanitize(name):
    return re.sub(r'[\\/*?:"<>|]', '_', name).strip()

def find_anchor_position(soup, anchor):
    """Find id=anchor or a[name=anchor] in BeautifulSoup tree."""
    if not anchor:
        return None
    elem = soup.find(id=anchor)
    if elem:
        return elem
    elem = soup.find('a', attrs={'name': anchor})
    return elem

def extract_book_body(html_docs, book_start, book_end):
    """Extract one book's HTML body from merged docs.
    
    book_start/end: {'filename': 'index_split_NNN.html', 'anchor': 'fileposXXXXX'}
    Returns BeautifulSoup body element.
    """
    from bs4 import BeautifulSoup
    new_body = BeautifulSoup('<body></body>', 'html.parser').body
    
    start_file = book_start['filename']
    start_anchor = book_start['anchor']
    end_file = book_end['filename'] if book_end else None
    end_anchor = book_end['anchor'] if book_end else None
    
    collecting = False
    
    for fname in html_docs:
        soup = html_docs[fname]['soup']
        if not soup.body:
            continue
        body = soup.body
        
        if fname == start_file and not collecting:
            collecting = True
            if start_anchor:
                pos_elem = find_anchor_position(soup, start_anchor)
                if pos_elem:
                    # Find top-level body child containing this anchor
                    elem = pos_elem
                    while elem.parent and elem.parent != body:
                        elem = elem.parent
                    started = False
                    for child in list(body.children):
                        if child == elem or child is elem:
                            started = True
                        if started:
                            if end_file == fname and end_anchor:
                                end_elem = find_anchor_position(soup, end_anchor)
                                if end_elem:
                                    end_parent = end_elem
                                    while end_parent.parent and end_parent.parent != body:
                                        end_parent = end_parent.parent
                                    if child == end_parent or child is end_parent:
                                        break
                            new_body.append(child)
                else:
                    for child in list(body.children):
                        new_body.append(child)
            else:
                for child in list(body.children):
                    new_body.append(child)
        
        elif collecting:
            if end_file and fname == end_file and end_anchor:
                pos_elem = find_anchor_position(soup, end_anchor)
                if pos_elem:
                    elem = pos_elem
                    while elem.parent and elem.parent != body:
                        elem = elem.parent
                    for child in list(body.children):
                        if child == elem or child is elem:
                            break
                        new_body.append(child)
                    collecting = False
                    break
            for child in list(body.children):
                new_body.append(child)
            if end_file and fname == end_file:
                collecting = False
                break
    
    return new_body


def split_collection(epub_path, output_dir):
    """Main entry point."""
    os.makedirs(output_dir, exist_ok=True)
    
    # Read epub
    book = epub.read_epub(epub_path)
    
    # Build HTML doc index
    html_docs = {}
    for item_id, linear in book.spine:
        item = book.get_item_with_id(item_id)
        if item and item.get_type() == ebooklib.ITEM_DOCUMENT:
            content = item.get_content().decode('utf-8', errors='ignore')
            html_docs[item.get_name()] = {
                'content': content,
                'soup': BeautifulSoup(content, 'html.parser')
            }
    
    # Collect CSS
    css_items = []
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_STYLE:
            css_items.append(item)
    
    # Parse TOC (skip first item = 总目录/index)
    toc_entries = []
    for item in list(book.toc)[1:]:  # Skip index page
        if isinstance(item, epub.Link):
            parts = item.href.split('#')
            toc_entries.append({
                'title': item.title.strip(),
                'filename': parts[0],
                'anchor': parts[1] if len(parts) > 1 else ''
            })
    
    print(f"Found {len(toc_entries)} books in TOC (skipped index page)")
    
    # Split each book
    success = 0
    for i, entry in enumerate(toc_entries):
        title = entry['title']
        print(f"[{i+1}/{len(toc_entries)}] {title}...", end=' ')
        
        start_info = {'filename': entry['filename'], 'anchor': entry['anchor']}
        end_info = {'filename': toc_entries[i+1]['filename'], 'anchor': toc_entries[i+1]['anchor']} if i+1 < len(toc_entries) else None
        
        book_body = extract_book_body(html_docs, start_info, end_info)
        text = book_body.get_text().strip()
        
        if len(text) < 500:
            print("⚠️ too short, skipping")
            continue
        
        # Build epub
        new_book = epub.EpubBook()
        new_book.set_identifier(f'split-{i+1:03d}')
        new_book.set_title(title)
        new_book.set_language('zh')
        new_book.add_author('Author')
        
        # Add CSS
        for ci in css_items:
            new_book.add_item(epub.EpubItem(
                uid=ci.id, file_name=ci.get_name(),
                media_type=ci.media_type, content=ci.get_content()
            ))
        
        # Create content
        css_links = ''.join(f'<link rel="stylesheet" type="text/css" href="{ci.get_name()}"/>\n' for ci in css_items)
        html = f'<?xml version="1.0" encoding="utf-8"?>\n<!DOCTYPE html>\n<html xmlns="http://www.w3.org/1999/xhtml" lang="zh">\n<head><title>{title}</title>\n{css_links}</head>\n{book_body}\n</html>'
        
        chapter = epub.EpubHtml(title=title, file_name='content.xhtml', lang='zh')
        chapter.set_content(html.encode('utf-8'))
        new_book.add_item(chapter)
        new_book.spine = [chapter]
        new_book.add_item(epub.EpubNcx())
        new_book.add_item(epub.EpubNav())
        
        safe_title = sanitize(title)
        epub_out = os.path.join(output_dir, f'{safe_title}.epub')
        epub.write_epub(epub_out, new_book)
        
        # Convert to mobi
        mobi_out = os.path.join(output_dir, f'{safe_title}.mobi')
        result = subprocess.run([
            'ebook-convert', epub_out, mobi_out,
            '--title', title,
        ], capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            kb = os.path.getsize(mobi_out) / 1024
            print(f"→ {kb:.0f}KB ✅")
            success += 1
        else:
            print(f"❌ conversion failed")
        
        os.remove(epub_out)  # Clean up intermediate epub
    
    print(f"\nDone: {success}/{len(toc_entries)} books → {output_dir}")


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python3 split-by-toc-anchors.py <source.epub> <output_dir>")
        sys.exit(1)
    split_collection(sys.argv[1], sys.argv[2])
