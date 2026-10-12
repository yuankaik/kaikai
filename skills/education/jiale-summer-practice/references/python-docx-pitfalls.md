# python-docx XML Manipulation Pitfalls (2026-07-01)

Lessons learned from the 40-day summer practice DOCX upgrade marathon.

## 1. Cross-document deepcopy → tripled text (FATAL)

**Symptom:** Text appears 3x in paragraph output (e.g., "hellohellohello").
**Cause:** `copy.deepcopy()` of XML elements between python-docx Documents copies text onto `<w:p>` and `<w:r>` elements, not just `<w:t>`.
**Detection:** `p_elem.text` is non-None on `<w:p>` elements.
**Fix:** Open DOCX as ZIP → modify `word/document.xml` with lxml → repack:
```python
for p in tree.iter(f'{{{NS}}}p'):
    if p.text and p.text.strip(): p.text = None
    for r in p.findall(f'{{{NS}}}r'):
        if r.text and r.text.strip(): r.text = None
```

## 2. OxmlElement text pollution

**Symptom:** `t = OxmlElement('w:t'); t.text = 'hello'` → `r.iter()` shows text on `<w:p>`, `<w:r>`, AND `<w:t>`.
**Fix:** Use `lxml.etree.Element` / `etree.SubElement` for paragraph creation. OxmlElement is fine for structural elements (tblPr, cantSplit, borders).

## 3. lxml iter() tag filter syntax

- `elem.iter(f'{{{NS}}}t')` — correct: finds all `<w:t>` descendants
- `elem.iter(f'.//{{{NS}}}t')` — WRONG: `.//` is XPath, not for iter()
- `elem.findall(f'.//{{{NS}}}t')` — correct for XPath search

## 4. WSL /mnt/c/ file locking

- **PermissionError on save:** File open in Windows Word → lock
- **Workaround:** `doc.save('/tmp/out.docx')` → `shutil.copy2('/tmp/out.docx', target_path)`
- **Still fails:** ask user to close Word

## 5. Removing page breaks

```python
for r in p_elem.findall(f'{{{NS}}}r'):
    for br in list(r.findall(f'{{{NS}}}br')):
        if br.get(f'{{{NS}}}type') == 'page':
            r.remove(br)
```

## 6. keepNext is unreliable for table grouping

`keepNext` works paragraph-to-paragraph, NOT paragraph-to-table reliably. For unbreakable table groups, wrap all tables + headers in a parent `<w:tbl>` with `cantSplit`.

## 7. Schulte wrapping: complete recipe

1. Find Schulte tables (3×3 or 6×6 digit-only)
2. Group consecutive ones (≤6 indices apart)
3. Unwrap old wrappers first (extract cell content)
4. Create parent table: 1 row × 1 col, `cantSplit=true`, invisible borders, full width (9072 twips)
5. Rebuild content with pure etree paragraphs: header → instruction → timing+table ×3 → spacer
6. Verify: cantSplit present, 3 timings, header text, all digits preserved
