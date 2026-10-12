#!/usr/bin/env python3
"""Clean hard line breaks and extra spaces from Chinese markdown novels.
Fixes:
  1. Mid-sentence hard breaks (四\n十分钟 → 四十分钟)
  2. Double/triple spaces → single space
  3. Trailing spaces before newlines
Preserves: headings, HTML blocks, scene breaks (---), dialogue markers."""

import re, sys

def clean_md(path):
    with open(path, "r") as f:
        text = f.read()

    lines = text.split('\n')
    SENTENCE_END = set('。！？…"\'」』）)')

    def is_sentence_end(s):
        return s and s[-1] in SENTENCE_END

    def should_join(prev, nxt):
        if not prev or not nxt: return False
        if prev.startswith('#') or prev.startswith('---') or prev.startswith('<'): return False
        if nxt.startswith('#') or nxt.startswith('---') or nxt.startswith('<'): return False
        if is_sentence_end(prev): return False
        if nxt.startswith('"') or nxt.startswith('—'): return False
        return len(prev + nxt) <= 120

    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped:
            new_lines.append(line)
            i += 1
            continue
        if stripped.startswith('#') or stripped.startswith('<') or stripped == '---':
            new_lines.append(line)
            i += 1
            continue
        if i + 1 < len(lines) and should_join(stripped, lines[i+1].strip()):
            joined = line.rstrip('\n') + lines[i+1].lstrip()
            new_lines.append(joined)
            i += 2
            continue
        new_lines.append(line)
        i += 1

    text = '\n'.join(new_lines)
    text = re.sub(r'  +', ' ', text)       # double+ spaces → single
    text = re.sub(r' +\n', '\n', text)      # trailing spaces

    with open(path, "w") as f:
        f.write(text)

    return len(lines), len(new_lines)

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else None
    if not path:
        print("Usage: python3 clean-hard-breaks.py <file.md>")
        sys.exit(1)
    before, after = clean_md(path)
    print(f"Lines: {before} → {after} (joined {before - after} hard breaks)")
