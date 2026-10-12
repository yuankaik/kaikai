# Recovering MD from Corrupted PDF

When `execute_code`'s `write_file` corrupts an MD file (embedding "LINE|CONTENT" line numbers), 
you may need to recover text from a previously-generated PDF.

## Recovery Script

```bash
pip install PyPDF2 --break-system-packages -q

python3 -c "
from PyPDF2 import PdfReader
import re
reader = PdfReader('file.pdf')
all_text = ''
for page in reader.pages[3:]:  # Skip cover pages (adjust index)
    text = page.extract_text()
    if text:
        cleaned = re.sub(r'\b\d+\|', '', text)
        cleaned = re.sub(r'\n\d+\n', '\n', cleaned)
        all_text += cleaned + '\n'
with open('recovered.md', 'w') as f:
    f.write(all_text)
print(f'Recovered: {len(all_text)} chars')
"
```

## Limitations

- **Tables are lost**: PDF extraction flattens tables to plain text
- **Paragraph breaks are merged**: Sentences run together
- **Chapter heading structure is preserved** (## markers survive)
- **Cover pages have no extractable text** — skip them
- **Total recovery rate**: ~70% of original content, needs manual reformatting

## Post-Recovery Cleanup

After extracting, fix common artifacts:
```python
import re
text = re.sub(r'^\d{1,4}\|', '', text, flags=re.MULTILINE)
text = re.sub(r'\n +', '\n', text)
text = re.sub(r'\n{4,}', '\n\n\n', text)
# Fix chapter heading fusion: "## Chaptertext" → "## Chapter\ntext"
text = re.sub(r'(## 第[^\n]{1,20}章[^\n]{1,20})([^\n\s#>-])', r'\1\n\n\2', text)
```

## Prevention

**NEVER use execute_code's write_file for MD files.** Use `terminal` with Python heredoc instead:
```bash
python3 << 'PYEOF'
with open("file.md", "w") as f:
    f.write(content)
PYEOF
```

Or use `patch` for targeted changes.
