#!/usr/bin/env python3
"""Batch convert text-based PDFs (kgbook 6寸PDF) to EPUB via PyMuPDF + EbookLib.

Environment: source ~/ocr_env/bin/activate && pip install pymupdf ebooklib
Usage: python scripts/pdf2epub.py
  Default: converts all PDFs on Desktop (C:\Users\admin\Desktop\) to EPUB.
  Or: python scripts/pdf2epub.py /path/to/dir
"""

import sys
import os
import re
from pathlib import Path

import fitz  # PyMuPDF
from ebooklib import epub

# Common PDF headers to strip (per-page artifacts from kgbook PDFs)
HEADER_PATTERNS = [
    re.compile(r'^.+Edited by Skywalker\s*$', re.MULTILINE),
    re.compile(r'^.+kgbook\.com.*$', re.MULTILINE),
    re.compile(r'^\s*苦瓜书盘.*$', re.MULTILINE),
]


def extract_text(doc):
    """Extract all text from PDF, stripping known headers and merging broken lines."""
    paragraphs = []
    for page_num in range(doc.page_count):
        text = doc[page_num].get_text()
        for pat in HEADER_PATTERNS:
            text = pat.sub('', text)
        text = text.strip()
        if not text:
            continue
        for line in text.split('\n'):
            line = line.strip()
            if not line:
                if paragraphs and paragraphs[-1] != '':
                    paragraphs.append('')
                continue
            # Skip TOC dotted lines
            if '......' in line or '.....' in line:
                continue
            # Merge broken line (prev doesn't end with sentence-ending punctuation)
            if paragraphs and paragraphs[-1] and paragraphs[-1][-1] not in '。！？）」「』"\'…—':
                paragraphs[-1] += line
            else:
                paragraphs.append(line)
    return paragraphs


def pdf_to_epub(pdf_path, epub_path):
    """Convert one PDF to EPUB. Returns (title, paragraph_count, bytes_written) or None."""
    doc = fitz.open(pdf_path)
    title = doc.metadata.get('title') or Path(pdf_path).stem
    author = doc.metadata.get('author') or 'Unknown'
    paragraphs = extract_text(doc)
    doc.close()

    if not paragraphs:
        return None

    book = epub.EpubBook()
    book.set_identifier(f"epub-{abs(hash(pdf_path))}")
    book.set_title(title)
    book.set_language('zh')
    book.add_author(author)

    css_content = (
        'body{font-family:serif;line-height:1.8;margin:1em;max-width:40em}'
        'h1{text-align:center;margin:1.5em 0;font-size:1.4em}'
        'p{text-indent:2em;margin:0.5em 0}'
    )
    css = epub.EpubItem(uid="style", file_name="style/default.css",
                        media_type="text/css", content=css_content.encode('utf-8'))
    book.add_item(css)

    html = ('<html><head>'
            '<link rel="stylesheet" href="style/default.css"/>'
            '</head><body>\n'
            f'<h1>{title}</h1>\n')
    for p in paragraphs:
        if p == '':
            html += '<br/>\n'
        else:
            html += f'<p>{p}</p>\n'
    html += '</body></html>'

    ch = epub.EpubHtml(title=title, file_name='content.xhtml', lang='zh')
    ch.content = html.encode('utf-8')
    ch.add_item(css)

    book.add_item(ch)
    book.toc = [epub.Link('content.xhtml', title, 'content')]
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    book.spine = ['nav', ch]

    epub.write_epub(epub_path, book)
    sz = os.path.getsize(epub_path)
    return (title, len(paragraphs), sz)


if __name__ == '__main__':
    target_dir = sys.argv[1] if len(sys.argv) > 1 else "/mnt/c/Users/admin/Desktop"
    pdf_files = sorted(
        f for f in os.listdir(target_dir)
        if f.lower().endswith('.pdf')
    )
    if not pdf_files:
        print(f"No PDFs found in {target_dir}")
        sys.exit(0)

    print(f"Converting {len(pdf_files)} PDFs in {target_dir}...\n")
    ok = 0
    for fname in pdf_files:
        pdf_path = os.path.join(target_dir, fname)
        epub_path = os.path.join(target_dir, fname.replace('.pdf', '.epub'))
        result = pdf_to_epub(pdf_path, epub_path)
        if result:
            title, paras, sz = result
            print(f"  OK  {title}: {paras} paras, {sz/1024:.0f}KB  ->  {fname.replace('.pdf', '.epub')}")
            ok += 1
        else:
            print(f"  SKIP  {fname}: no extractable text")

    print(f"\nDone: {ok}/{len(pdf_files)} converted")
