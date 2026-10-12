#!/usr/bin/env python3
"""
清理 Markdown 源文件中的排版问题，为 PDF 生成做准备。

修复内容：
  1. 段落内硬换行合并（"四\\n十分钟" → "四十分钟"）
  2. 多余空格标准化（双/三空格 → 单空格）
  3. 行尾空格清除
  4. 保留标题、HTML标签、场景分隔线、对话结构

用法：
  python3 clean-md-for-pdf.py /path/to/file.md
  或修改脚本内的 PATH 变量。
"""

import re, sys

if len(sys.argv) > 1:
    PATH = sys.argv[1]
else:
    PATH = "/mnt/c/Users/admin/Desktop/佳乐暑假完整练习库/字海钓徒-全文.md"

with open(PATH, "r", encoding="utf-8") as f:
    text = f.read()

lines = text.split('\n')
SENTENCE_END = set('。！？…」』）')

def should_join(prev, nxt):
    """判断上一行是否应该与下一行合并"""
    if not prev or not nxt:
        return False
    if prev.startswith('#') or prev.startswith('---') or prev.startswith('<'):
        return False
    if nxt.startswith('#') or nxt.startswith('---') or nxt.startswith('<'):
        return False
    if prev[-1] in SENTENCE_END:
        return False
    if nxt.startswith('"') or nxt.startswith('—'):
        return False
    combined = prev + nxt
    if len(combined) > 120:
        return False
    return True

# Pass 1: join broken lines
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
    
    if i + 1 < len(lines):
        next_stripped = lines[i+1].strip()
        if should_join(stripped, next_stripped):
            joined = line.rstrip('\n') + next_stripped.lstrip()
            new_lines.append(joined)
            i += 2
            continue
    
    new_lines.append(line)
    i += 1

text = '\n'.join(new_lines)

# Pass 2: normalize spaces
text = re.sub(r'  +', ' ', text)   # multiple spaces → single
text = re.sub(r' +\n', '\n', text)  # trailing spaces

with open(PATH, "w", encoding="utf-8") as f:
    f.write(text)

old_count = len(lines)
new_count = len(new_lines)
print(f"Lines: {old_count} → {new_count} (joined {old_count - new_count})")
print(f"Done: {PATH}")
