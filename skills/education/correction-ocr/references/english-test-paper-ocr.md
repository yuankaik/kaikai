# English Test Paper OCR Strategy

## Problem

Pix2Text (trained for Chinese text) produces severely garbled output on English+Chinese mixed test papers. The Chinese OCR engine interprets English characters through Chinese character models, resulting in nonsense like:
```
Anlnetony nedenedoes → 原本是 "I. Listen and judge."
Mnuaernrnm → 原本是英文题目文本
```

## Solution: Tesseract + Image Preprocessing

### Step 1: Enhance the image

```python
from PIL import Image

img = Image.open('test_paper.jpg')
img = img.convert('L')  # grayscale
w, h = img.size
img = img.resize((w*2, h*2), Image.LANCZOS)  # 2x upscale for better OCR
img.save('enhanced.jpg', 'JPEG', quality=95)
```

### Step 2: OCR with Tesseract

```bash
tesseract enhanced.jpg stdout -l eng
```

### Output quality

- Readable but imperfect — expect ~70-80% accuracy
- Good enough to identify question types, grammar points, and overall structure
- Some words will be garbled; fill gaps by context

## When to use which tool

| Paper type | Tool | Reason |
|-----------|------|--------|
| Chinese test paper (语文) | Pix2Text (`p2t predict -i`) | Excellent Chinese recognition |
| English test paper (英语) | Tesseract `-l eng` + enhancement | Pix2Text garbles English |
| Math paper (数学) | Pix2Text | Math formulas + Chinese labeling |
| Mixed content page | Try Pix2Text first; if garbled, fall back to Tesseract |

## Verified: 2026-06-25

Tested on 3 English final exam papers (四年级下). Tesseract + 2x upscale produced usable output for gap analysis. Pix2Text on the same images produced unusable garbage.
