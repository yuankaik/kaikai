# Pre-Print Final Audit Template

When a children's novel manuscript is "almost done" but the user wants one more review before printing, run through this structure. This template is derived from the《受着呗》final audit workflow.

## Audit Structure

### Section 1: Main Theme Check
State the book's core thesis in one sentence. Verify the thesis is:
- Reflected in the opening chapter setup
- Confirmed by the closing chapter payoff
- Not contradicted by any mid-book event

### Section 2: Hard Bugs (MUST FIX)

These are text contradictions that make the book internally inconsistent. Fix ALL before printing.

#### 2.1 Opening/Closing Alignment
- Does Ch1 character introduction match Ch17 payoff?
- Common bug: Ch1 says "作文交了" but Ch17 says "作文没交"
- Rule: Ch17 is usually the canonical/newer version; fix Ch1 to match

#### 2.2 Grade/Age Consistency
- `grep -n '四年级|五年级|三年级|六年级'` across the whole manuscript
- All references must agree on one grade level
- Common bug: early drafts used "四年级" but target shifted to "五年级"

#### 2.3 Score Consistency
- `grep -n '75|78|七十五|七十八'` — identify all score mentions
- The Ch17 score (正文) and any 河童 notebook / epilogue reference must match
- Common bug: 75 in body text, 78 in 河童's epilogue note

#### 2.4 Timeline Smoothness
- `grep -n '深渊竿上的数字亮了|倒计时.*天'` — trace the day counter
- Every transition must have either (a) a natural 1-day decrement or (b) an explicit explanation
- Common bug: 7→5 jump with no "time works differently here" transition
- Fix: insert 1-2 sentence explanation; do NOT change the day numbers

### Section 3: Running Joke / Callback Closure
Audit each recurring joke/motif for complete closure:

| Element | Check | Status |
|---------|-------|--------|
| Catchphrase | Does it evolve across the book? | |
| Companion arc | Does every companion get closure? | |
| Running joke #1 | Does it fire in every chapter? | |
| Running joke #2 | Last appearance = closure? | |
| Antagonist payoff | Setup in Ch1 → payoff in last chapter? | |

### Section 4: Illustration Alignment
For illustrated books with `[插图: ...]` placeholders:

- Map each illustration page to its surrounding text
- Check image content matches chapter scene (P16 should show ghost ray, not turtle shop)
- Check image style consistency (all semi-realistic anime OR all realistic photo — not mixed)
- Check image-caption deduplication: caption should describe what's VISIBLE, not narrate what's happening

### Section 5: Grade-Level Adaptation
- Flag vocabulary > grade level (same-length replacements preferred)
- Flag sentence complexity (>100 chars per sentence)
- Flag adult/abstract concepts without kid-friendly context
- Note: 河童's English notebook entries are bonus content — never flag as blockers

### Section 6: Final Judgment

```
内容主线: PASS / FAIL
包袱系统: PASS / FAIL  
插画系统: PASS / FAIL (with notes)
年级适配: PASS / FAIL
最终打印版: PASS / FAIL

If FAIL: list specific items blocking print readiness
If PASS: book is ready for print
```

## Fix Priority Order

1. Section 2 hard bugs (MUST FIX — contradictions)
2. Section 3 callback closure gaps (SHOULD FIX — weaken the book)
3. Section 4 illustration issues (image-dependent — user must provide new art)
4. Section 5 readability polish (NICE TO HAVE — doesn't block printing)
