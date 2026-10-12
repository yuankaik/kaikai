"""
Extract vocabulary from DayXX-词汇-*.docx files (40-day practice format).

Format: each file has "【第一部分】单词表 Words" section with lines like:
   1. school               学校
  10. ride a bike          骑自行车

Returns: list of {english, chinese} dicts, with multi-word support.
"""
from docx import Document
import os, glob, re, json

def extract_from_directory(base_dir, pattern='Day*-词汇-*.docx'):
    """Extract all vocab from DOCX files matching pattern."""
    files = sorted(glob.glob(os.path.join(base_dir, pattern)))
    all_words = []
    
    for f in files:
        doc = Document(f)
        in_section = False
        
        for p in doc.paragraphs:
            text = p.text.strip()
            if '单词表' in text or 'Words' in text:
                in_section = True
                continue
            if in_section and ('──' in text or '填空' in text or '练习' in text):
                in_section = False
                continue
            if in_section:
                # Match "  1. english word/phrase    chinese"
                m = re.match(r'^\s*\d+[\.\、\)]\s*([a-zA-Z][a-zA-Z\'\- ]*?)\s{2,}(.+)', text)
                if m:
                    eng = m.group(1).strip()
                    chn = m.group(2).strip()
                    all_words.append({'english': eng, 'chinese': chn})
    
    # Deduplicate
    seen = set()
    unique = []
    for w in all_words:
        key = w['english'].lower()
        if key not in seen:
            seen.add(key)
            unique.append(w)
    
    return unique

if __name__ == '__main__':
    import sys
    words = extract_from_directory(sys.argv[1] if len(sys.argv) > 1 else '.')
    print(json.dumps(words, ensure_ascii=False, indent=2))
    print(f'Count: {len(words)}', file=sys.stderr)
