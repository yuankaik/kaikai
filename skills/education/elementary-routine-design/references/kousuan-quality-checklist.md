# 口算 Quality Checklist

## Symbol Audit

After generating 口算 DOCX files, scan all cells for these symbols:

| Symbol | Meaning | Action |
|--------|---------|--------|
| `→` | Arrow (速算 intermediate step) | **REMOVE** — confusing for students. Split at arrow, keep only clean question |
| `△ □ ★ ◆ ○ ●` | Pattern/math substitution | **KEEP** — standard elementary math notation |
| `○` (in comparison) | Comparison operator placeholder (fill >, <, =) | **KEEP** — valid comparison exercise |

Example of → cleanup:
```
Input:  "9+1 = ______10，10+4 = ______"  (→ shows intermediate result)
Output: "9+1 = ______"                   (clean standalone question)
```

Use regex: `re.sub(r'______\d+', '______', text)` to strip intermediate answers after blanks.

## Question Count Consistency

Do NOT force all 40 days to the same question count. Natural variation by problem type:

| Type | Seconds/question | ~Questions in 15 min |
|------|-----------------|---------------------|
| Simple arithmetic (300+500=) | 3-5s | 40-50 |
| Multi-digit (±×÷) | 8-15s | 25-40 |
| Pattern finding | 15-25s | 20-30 |
| Step calculation (递等式) | 20-35s | 15-25 |
| Competition/word problems | 30-45s | 10-20 |

A day with 20 pattern-finding questions is equivalent to a day with 40 simple arithmetic questions. If the user flags the inconsistency, explain the cognitive load difference. Never pad light days by repeating questions.
