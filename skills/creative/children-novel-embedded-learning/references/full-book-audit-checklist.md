# Full-Book Audit Checklist

Run this 10-dimension audit after any bulk chapter generation, before declaring the book complete.
Developed from the 深海钓徒 V3 爆笑版审校.

## 1. Timeline Consistency

- [ ] Countdown/days tracked correctly across all chapters
- [ ] Each BOSS chapter advances the counter (check no skips)
- [ ] Chapter-end countdown matches next chapter's start
- [ ] Verify: 7→5→4→3→2→2→1→0 pattern correct (two BOSSes on same day = no advance)
- [ ] Check for duplicate countdown values caused by subagent gaps

## 2. Skill System Consistency

- [ ] Every named skill appears at acquisition point
- [ ] Skills don't disappear mid-book (grep each skill name across all chapters)
- [ ] AOE skill (墨笼乾坤) and single-target skill (墨星贯日) both get multiple uses
- [ ] Equipment (永夜伞) appears in every BOSS chapter — or explicitly explained why not
- [ ] Training/failure scenes exist before major breakthroughs (at least 2 failed attempts per new skill)
- [ ] Base attack (字击) never forgotten

## 3. Character Consistency

- [ ] 比目鱼: Checked every chapter. If missing >2 consecutive chapters, add transition line.
- [ ] 大公龟的花: Never falls. Verify with grep.
- [ ] 河童: Notebook entry every chapter. Count them.
- [ ] Each companion: Check presence after joining chapter. If absent >5 chapters, add callback.
- [ ] Moray/abandoned characters: Either delete single-appearance one-liners or add proper arc.

## 4. Running Gag System

- [ ] Goldie薯片: Dropped/traded at least once per 2 chapters
- [ ] Sword剑尖偏二度: Every appearance
- [ ] 河童斗笠 damage: Tracks cumulatively
- [ ] Octo "Trust me": Every appearance after Ch5
- [ ] 锅炸: At least 3 explosions across training chapters
- [ ] Count total occurrences of each gag. Flag if any drops below threshold.

## 5. Grievance Thread (李老登 / Any Running Complaint)

- [ ] Introduced in Chapter 1 with specific detail (not generic)
- [ ] Appears every 1-2 chapters — grep for keyword
- [ ] Maximum gap: 1 chapter without mention. Flag if >1.
- [ ] Different angle each time (罚抄, 骂人, 告家长, 填鸭, 竞争 — rotate)
- [ ] Final chapter delivers thesis: ties grievance to story theme
- [ ] If subagents wrote bulk chapters, ALWAYS post-audit scan for this

## 6. BOSS Progression

- [ ] Every BOSS fight has: 碾压 + 搞笑 + 升级 (all three)
- [ ] BOSS order matches planned progression
- [ ] Power scaling: each BOSS feels stronger than the last
- [ ] 离谱破局: each BOSS defeated by absurd logic, not just power
- [ ] 围观震惊: all present companions react after every BOSS

## 7. Foreshadowing & Payoff

- [ ] Old man/grandfather: All appearances logged and verified
- [ ] Coats: Count them. Each appearance consistent.
- [ ] Notes/纸条: Timeline check — no note received before it was left
- [ ] Cross-file references: "和XX一样" must reference something that actually exists in text
- [ ] Specific bug: check for "前面两张纸条" before any notes received; "岚灵花鸟市场外套" when no外套 in that chapter

## 8. Equipment Upgrade Path

- [ ] Each rod tier explicitly named at upgrade moment
- [ ] Upgrade node matches BOSS chapter
- [ ] No "预告未兑现": if text says "传奇竿打底",传奇竿 must be explicitly obtained
- [ ] Gems: count (5 total), verify acquisition chapters, verify release description

## 9. Comedy Density

- [ ] 河童 notebook: ≥1 per chapter
- [ ] Physical comedy: ≥1 per chapter (crashes, smacks, flying objects)
- [ ] 吐槽/Deadpan: ≥1 per chapter from protagonist
- [ ] Non-河童 comedy sources: at least 3 different characters providing humor
- [ ] Middle chapters (40-70% of book) not significantly less funny than opening

## 10. Ending Payoff

- [ ] Reality callback: returns to opening situation
- [ ] Teacher/school arc closed (not left hanging)
- [ ] Catchphrase delivered with maximum weight at finale
- [ ] Open-ended hook for continuation ("续")
- [ ] All companion fates mentioned (even one-liners)

## Post-Audit Fix Priority

1. **Critical**: Timeline errors, missing skill acquisitions, BOSS not defeated
2. **High**: Running gag gaps >3 chapters, grievance thread dropped, cross-reference errors
3. **Medium**: Companion absence >5 chapters, missing 围观 reactions
4. **Low**: Secondary character cameos, 珠宝 release description polish

## Post-Audit Fix Patterns (from production runs)

### Pattern A: Term-insertion via character voice

When audit finds a named technique/term ("字击") that should exist but never appears in-text:
- Do NOT insert a new standalone sentence or paragraph — it breaks flow.
- Append to an existing character notebook/diary entry where the character would naturally name it.
- Best targets: 河童's observations after first ability use, protagonist internal monologue, companion records.
- Result: +3-5 lines near the first ability demonstration, zero layout impact.

### Pattern B: Inline count correction

When audit finds the internal tally is off ("纸条：三张" vs actual 2 received):
1. Trace every receipt scene — verify physical paper count at each point.
2. Replace all inline references character-for-character ("三张"→"两张", "三次外套"→"两次外套").
3. Update the per-chapter stats block with exact breakdown (e.g. "两张。一张正面'沧龙'背面'等'，另一张正面'等'背面'下面就是蛇颈龙'。两张纸，正反共五条信息。").
4. Final grep for any leftover old counts — even one missed instance creates reader confusion.
5. If the character count changes (e.g. "三十张"→"两张"), warn the user before proceeding — layout WILL shift.

### Pattern C: Regenerate without layout change

When fixes preserve character count parity (same-length Chinese numerals):
- Re-run the same PDF generation script with unchanged CSS.
- Verify output file size is approximately the same (±2%).
- If line count changed by >5, spot-check 2-3 random pages for layout drift.
