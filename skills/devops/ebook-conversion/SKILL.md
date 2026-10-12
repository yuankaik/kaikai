---
name: ebook-conversion
description: Convert ebooks between formats (EPUB/PDF/HTML→MOBI/AZW3) for Kindle and other e-readers. Covers calibre ebook-convert, format selection, and common pitfalls.
---

# Ebook Format Conversion

Use when the user needs to convert ebooks — especially EPUB→MOBI/AZW3 for Kindle USB side-loading, or any cross-format ebook conversion.

## Format Selection for Kindle

| Format | USB Side-load | Send to Kindle | Compatibility |
|--------|:---:|:---:|------|
| MOBI   | ✓ | ✓ (legacy) | All Kindles, universal |
| AZW3   | ✓ | ✗ | Kindle 4th gen+, best formatting |
| EPUB   | ✗ | ✓ (2022+) | Side-load fails on older Kindles |

**Default: MOBI** for USB transfer. AZW3 has better typography but MOBI avoids edge cases.

## Basic Conversion

```bash
ebook-convert "input.epub" "output.mobi"
```

Batch convert all EPUBs in a directory:
```bash
for f in *.epub; do
  name="${f%.epub}"
  ebook-convert "$f" "${name}.mobi"
done
```

## The libxml2 Pitfall (WSL/Ubuntu)

**Symptom:** `ebook-convert` fails on EPUB3 files with:
```
RuntimeError: html5-parser and lxml are using different versions of libxml2.
libxml2 versions: html5-parser: (2, 15, 2) != lxml: (2, 14, 6)
```

EPUB2 files convert fine; only EPUB3 triggers this (EPUB3 nav document parsing uses html5-parser).

**Root cause:** A pip-installed `lxml` at `/usr/local/lib/python3.14/dist-packages/` shadows the system apt version. The pip wheel was compiled against an older libxml2.

**Fix:**
```bash
# Verify both use same libxml2 version
python3 -c "import lxml.etree; print(lxml.etree.LIBXML_VERSION); import html5_parser; print(html5_parser.LIBXML_VERSION)"

# If mismatched, remove pip lxml so Python uses apt system version
sudo rm -rf /usr/local/lib/python3.14/dist-packages/lxml /usr/local/lib/python3.14/dist-packages/lxml-6.*.dist-info
```

After this, both modules link against the system libxml2 and EPUB3 conversion works.

## Check EPUB Version

Run the bundled script (`scripts/check-epub-version.py`) or check inline:

```bash
python3 ~/.hermes/skills/devops/ebook-conversion/scripts/check-epub-version.py /path/to/epubs/
```

Manual inline check:
```python
import zipfile, re
z = zipfile.ZipFile("book.epub")
container = z.read('META-INF/container.xml').decode()
opf_path = re.search(r'full-path="([^"]+)"', container).group(1)
opf = z.read(opf_path).decode()
version = re.search(r'version="([^"]+)"', opf).group(1)
print(f"EPUB {version}")
```

## Batch Conversion Pitfalls

### Do NOT pipe to tail in background mode

Piping `ebook-convert ... | tail -3` causes output buffering — no output is visible
until the process exits. In background mode this makes the process look dead when it's
actually working. Use direct output:

```bash
# WRONG (no output until done):
ebook-convert "book.epub" "book.mobi" 2>&1 | tail -3

# RIGHT (output streams live):
ebook-convert "book.epub" "book.mobi" && echo "DONE: book"
```

### Parallel conversion hurts on WSL

`ebook-convert` is CPU-bound and single-threaded (100% CPU, ~360MB RAM per instance).
Running 4+ in parallel on WSL saturates the CPU and each conversion takes longer.
Serial is faster overall — batch them in a single shell command:

```bash
ebook-convert "a.epub" "a.mobi" && echo "DONE a" && \
ebook-convert "b.epub" "b.mobi" && echo "DONE b" && \
ebook-convert "c.epub" "c.mobi" && echo "DONE c" && \
echo "ALL DONE"
```

### Output stays 0 bytes until complete

`ebook-convert` writes the entire MOBI at the end — the output file remains 0 bytes
throughout the conversion. Don't use file size to check progress. Use `ps aux | grep ebook-convert`
to verify the process is alive and consuming CPU.

### Time expectations (WSL)

Roughly ~30-60 seconds per MB of input EPUB. A 6MB file takes 2-3 minutes.
Total conversion time = sum of all file sizes × ~40s/MB when serial.

## Splitting Multi-Book Collections

When a single mobi/epub contains a collection of books (e.g., "套装共26册"), use the TOC-based splitting technique documented in `references/split-collection.md`. Workflow: mobi→epub→parse TOC anchors→split→individual epubs→mobi.

## Verification

After batch conversion, verify all outputs exist and have reasonable size:
```bash
ls -lhS output_dir/
```
Files under 5KB likely failed — check the specific file.
