#!/usr/bin/env python3
"""Check EPUB version (2.0 vs 3.0) for all EPUBs in a directory."""
import zipfile, re, sys, os
from pathlib import Path

target = sys.argv[1] if len(sys.argv) > 1 else "."
path = Path(target)

if path.is_dir():
    epubs = sorted(path.glob("*.epub"))
else:
    epubs = [path]

v2, v3, err = 0, 0, 0
for ep in epubs:
    try:
        z = zipfile.ZipFile(ep)
        container = z.read('META-INF/container.xml').decode('utf-8')
        opf_path = re.search(r'full-path="([^"]+)"', container).group(1)
        opf = z.read(opf_path).decode('utf-8')
        version = re.search(r'version="([^"]+)"', opf).group(1)
        if version == '2.0':
            v2 += 1
            tag = "EPUB2 ✓"
        else:
            v3 += 1
            tag = "EPUB3"
        print(f"  {tag}  {ep.name}")
        z.close()
    except Exception as e:
        err += 1
        print(f"  ERROR  {ep.name}: {e}")

print(f"\nEPUB2: {v2}, EPUB3: {v3}, errors: {err}")
