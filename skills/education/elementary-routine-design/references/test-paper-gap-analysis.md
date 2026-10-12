# Test Paper Gap Analysis Workflow

Complete end-to-end workflow validated on Chinese and English 四升五 final exams (2026-06-25).

## Step 1: OCR the Test Paper

**Chinese papers:**
```bash
source ~/ocr_env/bin/activate && p2t predict -i 'image.jpg'
```
Pix2Text works well for Chinese (80-90% accuracy). Output is readable prose.

**English papers:**
```bash
# Enhance image first, then Tesseract
from PIL import Image
img = Image.open('image.jpg').convert('L')
img = img.resize((w*2, h*2), Image.LANCZOS)
img.save('enhanced.jpg')
```
```bash
tesseract enhanced.jpg stdout -l eng
```
Pix2Text fails badly on English+Chinese mixed papers (garbage output). Tesseract with `-l eng` on 2x grayscale is the correct approach.

**Fallback (slow, use as last resort):**
Ollama minicpm-v:8b on CPU takes 2-5 min per image. Only use for single critical images.

## Step 2: Map Question Types → Skill Categories

### Chinese 四升五 Test Paper Structure (~100 points)

| Section | Weight | Question Types |
|---------|--------|---------------|
| 基础积累 | ~40% | 看拼音写词语, 字音字形选择, 成语典故, 说明方法判断, 课文判断, 句式仿写 |
| 修改语段 | ~5% | 用修改符号修改（错别字/重复/的地得/搭配） |
| 阅读理解 | ~55% | 说明文 + 记叙文 + 非连续性文本 |
| 背诵 | embedded | 古诗默写 |

### English 四升五 Test Paper Structure (~100 points)

| Section | Weight | Question Types |
|---------|--------|---------------|
| 听力 | ~30% | 听音判断, 听音选择 |
| 词汇语法 | ~35% | 词形变换, 选择填空, 适当形式填空 |
| 连词成句/改写 | ~15% | 连词成句, 单复数转换, 划线提问 |
| 阅读 | ~20% | 短文阅读 + 公告/海报阅读 |

**9 Key Grammar Points:**
1. 一般现在时 (do/does, have/has)
2. 现在进行时 (am/is/are + V-ing)
3. 介词 (in/on/at/under/behind)
4. 特殊疑问句 (What/Where/When/Whose/How many)
5. 词性转换 (n→adj: noise→noisy, music→musical, nine→ninth)
6. There be 句型
7. 祈使句/否定句 (Don't..., Let's...)
8. 连词成句
9. 改写句子

## Step 3: Gap Analysis

Compare each test paper section against the existing summer plan. Mark:
- ✅ Covered: practice exists for this skill
- ⚠️ Partial: some coverage but insufficient
- ❌ Gap: zero coverage

**Common gaps found:**
- Chinese: 看拼音写词语, 字音字形, 成语, 修改语段, 非连文本 — often missing from reading-only plans
- English: Often entirely missing from math-focused plans
- Both: 说明文 reading underrepresented vs 记叙文

## Step 4: Generate Targeted Materials

For each gap, design 40-day rotating practice:
- 8-day rotation × 5 cycles = 40 days
- Each skill type appears 8 times across the 40 days
- Rotate to prevent monotony while ensuring spaced repetition

## Step 5: Generate Diagnostic Tool

Create a 100-point diagnostic test covering ALL identified skill areas:
- Student version: clean, answer blanks
- Parent guide: answer key + scoring rubric + weak-area→practice-day mapping
- Administer before summer starts, re-test after

## Step 6: Merge into Daily Files

One file per day. See `elementary-routine-design` skill for merge technique.

## Lessons Learned

- **Always start with real test paper analysis.** Plans designed without test paper comparison miss 40-50% of the tested content.
- **Chinese gap analysis is non-obvious.** A "reading plan" naturally covers 阅读 but misses 基础积累, 修改语段, and 非连文本.
- **English gap analysis reveals total absence.** Many summer plans focus on math + Chinese and have zero English content.
- **Update all three subject diagnostics together.** Mismatched diagnostic quality leads to uneven targeting.
- **Existing materials > AI generation.** Search `os.walk` across entire desktop before generating. 60-day curated reading sets and 道客巴巴 English passages are higher quality than anything AI produces.
