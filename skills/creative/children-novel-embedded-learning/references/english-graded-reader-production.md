# English Graded Reader Production (Bookworms-Style)

When English graded readers (Oxford Bookworms, Oxford Reading Tree, RAZ, etc.) are needed but can't be sourced from ebook sites, write custom readers calibrated to the learner's vocabulary list.

## When to Use

- 佳乐 needs English reading practice at his level
- Oxford Bookworms / graded readers can't be downloaded (sou.st doesn't cover English books)
- User prefers self-generated content over fighting with blocked download sites

## Oxford Bookworms Starter Format

A complete Bookworms-style reader includes these sections in order:

### 1. BEFORE YOU READ (1 page)
- 3 simple pre-reading questions
- Activate background knowledge + predict content
- Focus on cover image, topic, and personal connection

### 2. CHAPTERS (5 chapters, ~300 words each)
- Total: ~1,500 words, 5 chapters
- Dialogue-heavy (50%+ of text should be dialogue)
- Dialogue in italics or indented, narration in regular
- Each chapter = one story beat (setup → problem → journey → climax → resolution)
- Sentence length: 5-10 words average
- Tense: present simple + present continuous only (no past tense for Starter)

### 3. AFTER YOU READ (1-2 pages)

**A. Yes or No?** (5 questions)
- Factual comprehension check
- Write "Yes" or "No" — minimal writing burden

**B. Short Answer** (5 questions)
- One-sentence answers
- Answer lines provided

**C. Talk About It** (2 questions)
- Open-ended, discuss with parent
- No writing required — just talking

### 4. GLOSSARY (1 page)
- 15-20 new words
- Format: Word | Chinese meaning | Example sentence from the book
- Bold English word, grey Chinese, italic example

## Vocabulary Calibration for 佳乐

Source: 沪教版牛津英语1-4年级词汇表 (~786 words)

| Reader Level | Vocabulary Source | Headwords | Character Type |
|-------------|-------------------|-----------|----------------|
| Starter | Grade 1 only | ~150 | Animals, family, colors |
| Starter+ | Grade 1-2 | ~250 | Simple adventures |
| Level 1 | Grade 1-3 | ~400 | Short mysteries |

**Rule**: Zero out-of-curriculum words. Every word must be from 佳乐's known vocabulary list. The goal is fluency practice, not new vocabulary acquisition — new words come from the Glossary (pre-taught before reading).

## Story Design for 佳乐 (10-year-old sports boy)

- Protagonist MUST be competent (not learning, not rescued)
- Animal protagonists preferred (turtles = his pets)
- Ocean/deep sea setting preferred
- Humor beats: physical comedy > deadpan snark > misunderstandings
- Short chapters with clear payoff per chapter
- NO "educational" tone — the reader shouldn't feel they're being taught

## Production Pipeline

1. Read vocabulary file: `/mnt/c/Users/admin/Desktop/shanghai-exams/暑假英语词表_40天分配.json`
2. Filter to target grade level (e.g., Grade 1-2 for Starter)
3. Write story in Markdown first (review structure)
4. Generate DOCX with `docx-print-author` skill formatting:
   - A4, 11pt body text, 10pt for exercises
   - Page breaks between chapters
   - Dialogue in italic grey
   - Glossary in two-column format
5. Output to: `C:\Users\admin\Desktop\`

## Example Story: "Tom Turtle and the Big Sea" (2026-07-03)

- Starter level, ~200 unique words, ~1,500 total words
- Protagonist: Tom (small turtle, shell marked "家") — direct connection to 佳乐's 大母龟
- Theme: bravery > speed (emotional hook for the sports-kid-who-struggles-academically)
- Result: 40KB DOCX on desktop, ready to print

## Pitfalls

- **Don't use past tense in Starter level.** Keep to present simple + present continuous. Past tense (went, was, were) is Grade 4+ in 沪教版.
- **Don't make the protagonist "learn" something.** Tom doesn't learn to be brave — he discovers he already was. The reader doesn't need to improve; they need to see themselves.
- **Dialogue must dominate.** If narration exceeds 40% of text, the reading burden is too heavy for a weak reader.
- **Chapter 3 is the danger zone.** In a 5-chapter arc, Chapter 3 (the journey) naturally loses energy. Inject a surprise (Tom finds a lost baby fish instead of Finn — unexpected side quest keeps interest).
