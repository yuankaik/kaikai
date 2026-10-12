---
name: children-novel-embedded-learning
description: Write children's adventure novels that naturally embed educational content (English vocabulary, Chinese literacy, subject knowledge) through story mechanics — not textbook inserts. Covers story base planning, character engines, multi-phase revision, and per-chapter learning density tracking.
---

# Children's Novel with Embedded Learning

Write long-form children's fiction (20K-40K words) where educational content is embedded as story mechanics, not lessons. The reader should feel they're reading a fun adventure, not a disguised textbook. 适用于将英语词汇、语文学科知识、写字训练等自然融入儿童冒险故事。

## Trigger Conditions

- User asks to write a children's story that includes educational content
- User wants to "embed" English/Chinese/math into fiction
- User references 一念永恒 or similar comedic cultivation novels as style reference
- User asks for a story that teaches without the reader noticing

## Core Principles

1. **Knowledge is the key, not the lesson.** Vocabulary opens doors, solves puzzles, or is spoken by characters who naturally speak that language. Never "teach" — let the protagonist figure it out.

2. **Comedy first, learning second.** The reader stays for the laughs. They absorb the English because the fish are funny when they argue in broken English, not because they're being taught.

4. Protagonist must be proactive and strong. The reader identifies with capability, not vulnerability. A protagonist who falls into adventure by accident should immediately start dominating — not being rescued, not being taught. Sports champions (swimming, running) translate directly to physical competence in the story world. Catchphrase should be defiant, not pleading.

5. Partners are allies, not pets. Every companion should have their own agenda, competence, and distance. No character exists to be cute. The shy turtle has the strongest power; the clumsy turtle once fought a dragon; the comic-relief guide has buried 11 previous fishers. Edge beats cute.

6. Arcade rhythm, not storybook pacing. Every chapter is a level — enter, face challenge, upgrade/solve, move on. The coin→unlock→boss→upgrade loop from arcade games is the right structure. No chapter should be setup-only or vibes-only.

## Story Base Structure

Create a `完整底座.md` document before writing. Use `references/story-base-template.md` as the starting template.

The base should include:

```
- 阅读参数 (chapters, word count, reading period)
- 世界观 (core mechanic: how learning = power in this world)
- 修炼体系 (if cultivation-themed: levels, breakthroughs, comedy beats)
- 角色设定 (protagonist + companions + antagonist, each with comedy/drama function)
- 装备系统 (items that embody learning: pen = sword, notebook = spellbook)
- 支线 (side quests for bonus items/breakthroughs)
- 每章大纲 (one-line summary per chapter)
- **每章节拍密度**: Minimum 3 beats per chapter (hook → event A → upgrade/reversal → event B → payoff/cliffhanger). 2000-2500 words per chapter. Single-event chapters feel "过家家" to target readers.
- **BOSS命名体系**: Reference real arcade/fishing game naming conventions (王牌钓手 style: 材质+特征+兽). Examples: 鬼蝠魟, 大白鲨, 大王乌贼, 巨齿鲨, 深渊帝王龙. Never use made-up or childish-sounding BOSS names.
- 每章英语密度表 (target: <3% total text, NOT per-chapter uniform percentage)
- 笑点引擎 (which jokes fire per chapter at what frequency)
```

## Audience Calibration: The 10-Year-Old Sports Boy

When the reader is a ~10-year-old athletic boy (NOT a studious, bookish child):

**What they want:**
- Strong protagonist who dominates (not passive, not "learning")
- Fast pace, payoff every chapter
- Physical comedy (crash, splash, face-plant)
- Cool factor: weapons, upgrades, boss fights, collectibles
- Protagonist with attitude: 痞气, cheeky, talks back
- BOSS names that sound like arcade games, not textbooks

**What they reject (instant turn-off):**
- Protagonist being protected, saved, or taught
- Long setup before action
- Wordplay puns that require thinking
- Cute/mascot treatment of animal companions
- Excessive English that feels like homework
- "Educational" tone — even well-hidden

**Style reference:** Arcade rhythm (王牌钓手) + 热血漫 pacing, NOT children's picture book.

## English Strategy (V3: Minimalist)

**Rule: English is a weapon, not a lesson.** Target <3% of total text.

English appears ONLY as:
1. **Character identifiers**: Fish names (A鱼, B鱼…) — visual tags, zero reading burden
2. **Comedy engine**: 河童's deliberately broken English (\"Help\"→\"You are heavy\") — funny, not educational
3. **Boss-trigger words**: Single words that unlock power (\"Spell.\" \"Pass.\") — 1-2 per volume max

**NEVER:**
- Explain what English words mean
- Use English in narration
- Insert English dialogue for \"learning moments\"
- Target grade-level vocabulary coverage

**The old density curve (6-27%) is deprecated.** V2 reader feedback: \"英语太多\" was the #1 complaint. English density >5% feels like homework to a 10-year-old sports boy.

## Humor System (V3)

Three engines, in priority order:

### Engine 1: Physical Comedy (60%)
- Crash, splash, face-plant, brake-failure, friendly fire
- 大母龟 is the physical comedy core — every entrance destroys something
- Fish getting smacked by other fish
- Items falling, shelves collapsing, Octo's tentacles tangling mid-transaction

### Engine 2: Deadpan Snark / 吐槽 (25%)
- Protagonist roasts everything: the rules, the monsters, his own situation
- \"你们金鱼帮收保护费是用薯片结算的？这叫什么黑社会。\"
- \"这条龙比我体育老师还爱拖堂。\"
- Catchphrase: \"受着呗\" — said before doing something reckless

### Engine 3: Misunderstanding / 反差 (15%)
- 河童 translation disasters: \"Danger\"→\"Dance\", \"Run\"→\"Fun\"
- 大公龟: strongest shell inscriptions in the abyss, hides from stranger fish
- The scariest fish being the most timid (BOSS cries mid-fight)

**Anti-patterns (feel 幼稚 to target audience):**
- Wordplay puns (F+U = bad word — requires thinking, not laughing)
- Knowledge-based gags (拼音鱼 vs 英语鱼 arguing pronunciation)
- "Cute" animal behavior without edge

## 插画占位与插入 (Illustration Placeholders)

When a manuscript will receive illustrations later:

1. **Placeholder format**: `[插图: 一句话场景描述]` on its own line, right before the scene it depicts. Place at the most dramatic/visual/funny moment, not at scene setup.

2. **Naming convention**: Number images sequentially (1.png through 22.png) + `封面.png` for the cover. Keep in a dedicated `插画/` folder. Provide the user a naming table so they can rename files correctly.

3. **Auto-insertion**: Read the folder, sort by filename, match to placeholders in order. Replace `[插图: ...]` with `<img>` tags. Use `max-height: 72vh` for A4 portrait layout, with a small italic caption below. See `references/illustration-naming-template.md` for the user-facing naming guide.

4. **Font sizing for children**: 10-year-olds need 13pt minimum body text. Captions at 10pt. Chapter titles at 20pt. Anything below 10pt is unreadable for the target audience. The difference between 11pt and 13pt is the difference between "佳乐看着费劲" and comfortable reading.

**Mid-section humor injection**: In any 爽文, chapters 6-11 naturally lose comedy density as BOSS scale increases. When an external diagnostic confirms this ("中段偏燃/史诗化过重"), inject one 歪逻辑名场面 per middle chapter — e.g. 沧龙's swimming pattern is predictable because it's old, 凯撒火龙's fire always misses left, 深渊帝王龙's "massive" body was just piled-up failed words. Never let three consecutive middle chapters go without a破坏气氛 gag.

## 创作总纲 (Creation Manifesto)

Before writing, distill the entire book into one sentence. This is the 书胆 (book's heart):

> 佳乐只想逃掉一节语文课，结果把整个深海世界写崩了。

This sentence should answer: who is the protagonist, what do they want (small, personal), and what actually happens (absurdly large). The gap between the small want and the huge result IS the comedy engine.

**Do NOT write:** "A boy learns to love writing through adventure" — that's功利 (instrumental). The爽点 is NOT that the protagonist \"improves\" — it's that they discover they were always capable, just trapped in too small a world.

## 三大喜剧发动机 (Three Comedy Engines)

Every children's 爽文 needs three character-types that turn every story event into a cascade of absurd consequences:

1. **商业化发动机** (Commercialization Engine) — e.g. 吴薯片: Turns every boss fight into merchandise. After each victory: \"纪念品事业部新品发布！\" Crashes, drops snacks, creates a歪理 ecosystem.

2. **假货/吐槽发动机** (Scam/Critique Engine) — e.g. 朱八爪: Sells fake everything. One real item he can't sell. Evolves through punctuation (\"Trust me.\" → \"Trust me?\"). The world's absurdity reflected in his shop sign.

3. **现实对照发动机** (Reality Contrast Engine) — e.g. 李老登: The real-world \"BOSS\" whose rules are unclear. Defeated not by confrontation but by the protagonist writing something real for the first time. Score: 75/100, \"主题不积极，但语句通顺.\"

These three engines should fire after EVERY major event: commercialization → scam reaction → reality callback.

## 对标分析 (Benchmark Analysis)

Before writing, compare against a known successful work:

1. Break down the reference work's framework (characters, humor engine, equipment, levels, relationships)
2. Match each element to your story
3. Score each dimension honestly
4. Identify gaps and propose fixes BEFORE writing
The comparison serves as a development roadmap, not a scorecard.

**一念永恒 style recipe:** See `references/yinian-yongheng-recipe.md` for the full combat rhythm, artifact design, comedy layering, and BOSS design rules extracted from the V3 深海钓徒 rewrite. Key principle: 爽文 power + 一念永恒 comedy = the unbeatable combo for a 10-year-old sports boy.

**爆笑爽文 comedy engine:** See `references/baoxiao-shuangwen-engine.md` for the full system: 离谱破局 battle pattern, 围观震惊 reactions, recurring joke system, per-chapter comedy template, and BOSS absurdity archetypes. This is the upgrade from "燃+奇幻+史诗" to "爽文+爆笑爽文" — the difference between a protagonist who wins and one who wins absurdly while everyone stares in disbelief.

**Treasure dungeon pattern:** See `references/treasure-dungeon-pattern.md` for the Forbidden Door structure — when a major artifact needs an origin that matches its power level. Core rule: treasures at ultimate tier cannot be purchased, only earned through internal trials. The predecessor must have been here first and left a marker; the protagonist goes further.

**Power fantasy checklist:** See `references/shuangwen-checklist.md` for the 爽文 diagnostic — when the user says a draft "还不够爽", run through the talent+grind+surpass triad before rewriting. Core rules: innate gift visible from Chapter 1, training failures shown mid-book, predecessor surpassed by the end.

**Full-book audit checklist:** See `references/full-book-audit-checklist.md` for the 10-dimension systematic review (timeline, skills, characters, running gags, BOSS progression, equipment, foreshadowing, comedy density). Run this after any bulk chapter generation before declaring the book complete.

**V3 rewrite pattern:** See `references/v3-rewrite-pattern.md` for the reader-feedback-driven overhaul protocol — when the target reader rejects the story, don't tweak, rebuild with clear diagnostics.

## Expansion Planning (Million-Word Scale)

When scaling a completed novel from ~40K to 1M+ words (multi-volume expansion), use
parallel subagent research workflow described in `references/expansion-research-workflow.md`.

Four-phase process (~30-40 min planning):
1. **Benchmark Research** — 3 parallel subagents analyze 20 reference works across humor, power systems, and team dynamics
2. **Synthesis** — 2 parallel subagents produce expansion blueprint + complete world system
3. **Samples + Schedule** — 2 parallel subagents write sample chapters + chapter-by-chapter production tables (chunk if timeout)
4. **Master Summary** — 1 subagent consolidates everything into a readable executive summary

Key principle: 底座不变 (base stays). Characters, voice, humor engine, and core
mechanics are preserved — the expansion adds scale (more continents, deeper cultivation,
larger cast) without replacing what works.

**Chunking rule:** If a subagent times out on large tasks (Vol 1-4 chapter schedule),
split into Vol 1-2 then Vol 3-4 as separate subagents. Use `read_file` with offset/limit
to feed each subagent only the relevant blueprint sections.

## 五年级可读性审查 (5th-Grade Readability Review)

When the user asks to review a completed children's novel for age-appropriateness ("以五年级水平审视全文", "看看阅读有没有困难"), run a systematic 4-dimensional scan. Use `references/readability-review-5th-grade.md` for the full workflow — Python scan scripts, judgment criteria, and output template.

Four passes:
1. **P1: 词汇难度** — regex-scan for adult/business/abstract vocabulary, mark each as "自解释/建议改/可跳过"
2. **P2: 句式复杂度** — measure sentence length distribution, flag >100char sentences
3. **P3: 逻辑/情节** — manual trace of chapter clarity, foreshadowing, progression
4. **P4: 幽默适龄** — categorize jokes by hit rate for 10-year-olds

Output: 4-dimension report with scoring table and fix suggestion table.

**Key rule:** Only suggest fixes for items not self-explained by context. 河童's English notebook entries are bonus content — never flag them as readability blockers. Suggestions are advisory ("修不修?") not commands.

## 教育价值分析 (Educational Value Analysis)

When the user asks "这本书对学习有帮助吗" (does this book help with learning?), run a 3-subject diagnostic: reading comprehension, writing, and English vocabulary. Use `references/readability-review-5th-grade.md` P6 for the full Python scan scripts.

**Three Subjects:**

**语文阅读 (Chinese Reading, weight 50%):**
- Count multi-thread narratives: 深海主线 + 校园线 + 传闻线 + 商业线 + 河童记录线 + 彩蛋线
- Count emotion markers: fear → hesitation → acceptance → pride transition chain
- Count metaphor density: 186 metaphors in ~55K Chinese chars is the《受着呗》baseline
- Map to 沪教版 5th-grade exam points: 概括主要内容, 体会思想感情, 理解含义深刻的句子, 分析人物形象
- Key insight: the 嘴/脑子 split structure directly trains "what was the author trying to say?" — exactly the skill 佳乐 scores 58 on

**语文写作 (Chinese Writing, weight 30%):**
- Count 嘴/脑子 pairings: 95 pairs = 95 psychological description examples
- Count short sentences (<15 chars): 5,827 = short-sentence style friendly for slow writers
- Identify imitable templates: BOSS=flaw metaphor, rumor endings, repeat callback evolution
- Key insight: the book models "writing with details" and "non-template立意" — exactly what's missing from 佳乐's 75-point essays

**英语单词 (English Vocabulary, weight 20%):**
- Match all English words against 沪教版 Oxford 1-5 vocabulary list
- Split: 已学词 (curriculum, consolidation value) vs 超纲词 (story-immersed acquisition)
- Top 15 high-frequency for each category
- Key metric: English word count ÷ Chinese character count. <7% = no reading burden.
- Conclusion: immersion-level, not textbook-level. Expect natural acquisition of 30-50 story-high-frequency words

**Output Format:**
```
一、语文阅读 — 高度对口 (★★★★★)
二、语文写作 — 可直接模仿 (★★★★☆)
三、英语单词 — 辅助浸泡 (★★☆☆☆)
总结 — 三科加权评分表
```

## Multi-Phase Revision

### Phase 1 (P0): Structural fixes
- Timeline/logic contradictions
- Missing origin stories for key items
- Incomplete character arcs (name reveals, closure)

### Phase 2 (P1): Enhancement
- Fill missing comedy beats (误解梗 per chapter)
- Restore English density in weak chapters
- Side quests that were planned but not written
- Foreshadowing/recycling for minor characters

### Phase 3 (P2): Polish
- Break long sentences for child readability
- Convert abstract descriptions to concrete images
- Fix minor continuity (chapter numbering, name consistency)

### Final Pass: Proofread
- Typo check
- Timeline consistency (verify day-of-week, chapter references)
- Character name spelling (case consistency for English names)
- Chapter count accuracy (main + bonus chapters)

## Pitfalls

- **Don't explain vocabulary.** If a fish says "Help!", the context shows what it means. Never add "佳乐学会了help就是救命的意思" — that kills the story.
- **Don't make English density uniform.** A natural curve (low→high→medium) feels organic. Uniform 20% every chapter feels like a textbook.
- **Don't skip the comedy engines.** If a chapter has zero误解梗 and zero fixed jokes, it's probably too serious for a 10-year-old.
- **Don't let "Papier fish" through.** If using English for learning input, avoid pseudo-foreign words that look like English but aren't. Use "Paper fish" instead.
- **Verify chapter timing.** If Chapter 1 says "星期三要交周记", Chapter 24 can't say "周二要交". Track timeline across chapters.
- **Count chapters correctly.** "24 main + 2 bonus = 26 reading units", not "25 chapters". Be precise in summaries.
- **The execute_code write_file can corrupt.** If using `write_file` inside `execute_code` with content from `read_file` (which has line numbers), the line numbers get embedded. Use `terminal` with `cat`/heredoc or direct `write_file` tool for critical content.
- **Never invent verifiable real-world details.** Class size, weekly schedules, specific assignments — these can be disproven by the actual reader (especially when the protagonist is a real person). Ask the user. 「佳乐没有这个日程」is a critical correction signal.
- **Catchphrase timing matters.** 受着呗 goes AFTER the dominant action, not before it. Pre-action = self-pep-talk (weak). Post-action = casual dismissal (strong). This is a 一念永恒 tonal rule.
- **BOSSes don't need to die.** The strongest enemies choosing to step aside is cooler than killing them. It builds world depth.
- **Use real game data verbatim.** When the user provides actual game fish names, BOSS stats, or level data, use those exact names. Don't invent A-Z letter fish when real ones exist.
- **Teacher antagonists must feel real, not cartoonish.** Specific behaviors land harder than labels. Let the protagonist name the abuse.
- **For game-loving kids, reference material may be a Switch game, not a novel.** Extract mechanics from the game. The coin to unlock to boss to upgrade loop IS the chapter structure.
- **Running personal grievances must persist across the whole book.** A teacher complaint, school frustration, or any personal grievance introduced in Chapter 1 MUST appear every 2-3 chapters throughout. When delegating chapters to subagents, explicitly list "continue the [grievance] thread" in the context. Subagents maintain skills but drop personal threads unless explicitly told. See references/running-threads-rule.md.
- **爽文 tone check: "还不是爽文" = rewrite now, don't tweak.** When the user says the current draft "不是爽文", the fix is not small adjustments — it's a scene-level rewrite. Signs: protagonist is clever/strategic instead of dominant, wins are close instead of overwhelming, bystanders are unsurprised, catchphrase used before action. Fix: BOSS fight = I walk in → I destroy → bystanders are stunned → I say catchphrase and leave. No cleverness, no teamwork, no struggle. See references/yinian-yongheng-recipe.md for the full combat rhythm.
- **Skill/technique naming: 4 characters is the floor for ultimate moves.** When the user rejects a name as "不够霸气" (not domineering enough), the minimum bar is 4 Chinese characters conveying world-scale weight (墨笼乾坤, not 墨域; 水泽国度, not 水域). Two-character names feel incomplete for ultimate techniques.
- **Post-subagent grievance scan is mandatory.** After subagents write bulk chapters, grep every chapter for the running grievance keyword. Chapters without it need a 1-2 sentence callback inserted at a natural comparison point. Use different angles each time — never repeat the same comparison. The final chapter should deliver the thesis statement that ties the grievance to the story's theme.\n- **嘴/脑 density kills rhythm.** The \"嘴硬脑怂\" (mouth-brave, brain-panicking) split is the strongest protagonist voice hook — but only when used sparingly. Fire at exactly 3 moments per chapter: before BOSS fight (心理建设), at the absurd decision point (钻鱼嘴/写\"六\"), and after victory (装淡定). Delete ALL other instances — casual dialogue, observation, transitions. Over-use turns a signature comedy device into noise that dilutes the big moments. When polishing: grep for \"嘴：\" and \"脑子：\", keep the 3 key beats, delete the rest. Target: remove ~30% to restore rhythm.\n- **Physical-vs-information counting.** When the book tracks items, check whether the text counts physical objects or information units. A paper with front+back content is 1 physical item but 2 messages. Fix: trace every receipt, adjust all inline counts, update the per-chapter stats block.

- **Missing term fix: append to existing character voice entries.** When audit reveals a named technique ("字击") never appears in-text but should, don't insert a new standalone paragraph. Append to an existing character notebook/diary entry where that character would naturally name it. Preserves flow and adds no layout impact.

- **Layout-preserving number fixes.** When correcting inline counts that affect the same paragraph structure, use Chinese-character-count-equal replacements. Verify all occurrences across the whole book are updated.

- **Adult vocabulary → kid vocabulary: same-length replacement.** When readability review flags business/political/abstract terms (\"朝贡体系\", \"版权分成\", \"保险理赔\"), replace with same-character-count kid-friendly alternatives (\"主动上供\", \"卖了分钱\", \"最大的麻烦\"). Constraint: new phrase MUST have identical character count to old — prevents layout shifts in typeset PDF. If no same-length alternative exists, the term is probably fine as-is (kids infer from context).

- **Illustration caption must not duplicate body text.** When `[插图: 事件描述]` is followed by a paragraph that narrates the SAME event with the SAME words, the caption should be trimmed to visual-only language — what the viewer sees in the image, not what happens in the story. Do NOT delete the body text; it carries the narrative. Only fix obvious verbatim repetition (2-3 worst cases). Stylistic overlap with different wording is acceptable and expected. Trigger: user review flags \"图注式句子像占位符残留\" or \"插图和正文重复\". Fix: shorten caption to scene-setting only, remove action verbs that body text already delivers.

- **Pre-print consistency audit: 5 mandatory checks.** Before declaring a children's novel "ready to print", grep for and fix these five categories — they are the most common last-mile bugs missed by earlier audits:
  1. **Grade/year consistency**: All "四年级" or all "五年级" — never mixed. `grep -n '四年级\|五年级'` and unify.
  2. **Score consistency**: One score number, ALL references agree. `grep -n '75\|78\|七十五\|七十八'` and unify. The Ch17 score and the epilogue河童 note referencing it must match.
  3. **Timeline smoothness**: No unexplained day-jumps. `grep -n '深渊竿上的数字亮了'` and verify each transition. If a 2-day gap (7→5) has no explanation, insert 1-2 sentences: "他以为只过了一会儿...但深海的时间不一样。" Keep the same day count; don't change numbers mid-book or the entire timeline unspools.
  4. **Opening/closing alignment**: The Ch1 character introduction must match the Ch17 payoff. If Ch1 says "作文交了及格" but Ch17 says "作文没交", fix Ch1 to match Ch17 (Ch17 is usually the newer/canonical version).
  5. **Character stat coherence**: Every in-text ability claim must match the character's scored performance. `grep -n '奥数\|数学课代表\|英语好\|作文好\|语文好'` and verify. "奥数第三名" cannot coexist with "数学能及格/75分". "数学课代表" implies top-tier math, contradicting average scores. When found: replace with neutral phrasing that aligns with actual scores ("数学能及格", "最怕数学的那个"). This check also applies to any superlative ability claims introduced in Ch1 that the rest of the book contradicts.

- **Double page-break creates blank P2.** When a cover div has `page-break-after: always` in CSS AND the markdown source has `<div style="page-break-after: always;"></div>` between `</center>` and the first content, WeasyPrint produces a blank page 2 with only a page number. Fix: remove the `style` attribute from the markdown div (change to `<div></div>`). The cover's CSS break is sufficient. Verify: regen PDF and check that page 1=cover, page 2=first chapter.\n\n- **Image replacement by PDF page number.** When user says \"replace P16/P79/P108\", the page numbers refer to the PRINTED PDF. The gen script maps illustrations sequentially: 1st `[插图:]` → 1.png, 2nd → 2.png, etc. To map page numbers to illustration numbers, extract all captions in order (`re.findall(r'\\[插图: ([^\\]]+)\\]', text)`), match against the review's per-page content description (e.g. \"P16 = 鬼蝠魟前奏\"), and `cp P16.png → N.png` where N is the matched illustration index. Backup originals first. See `references/image-replace-by-page.md` for the full mapping table and script.\n\n- **External diagnostic → fix priority order.** When the user provides a structured review document (\"建议.MD\", \"最终修改.MD\"), extract items marked MUST FIX / 硬伤 first. Fix them all before touching bonus items. The bonus section (插图风格不一致, 个别句子可优化) is advisory — confirm with user before acting. Never skip hard bugs to work on bonus items. See `references/pre-print-final-audit-template.md` for the reusable diagnostic structure.

- **Book title must be a punchline, not a setting name.** 深海钓徒 was rejected as too literal and descriptive. The winning title was the protagonist's catchphrase: 受着呗. For children's 爽文, the title should be short, mysterious, and preferably the same word/phrase the protagonist says at every climactic moment. Never use X海Y徒 format — it sounds like a textbook. ("三张"→"两张", both 2 chars). Verify all occurrences across the whole book are updated. \"深海钓徒\" was rejected as too literal and descriptive. The winning title was the protagonist's catchphrase: \"受着呗\". For children's 爽文, the title should be short, mysterious, and preferably the same word/phrase the protagonist says at every climactic moment. Never use \"X海Y徒\" format — it sounds like a textbook. A title that makes no sense until you've read the book is better than one that explains the premise.\n- **Mid-section humor always drops; plan for it.** In any爽文 with a 3-act structure (入局 Ch1-5 → 连战 Ch6-11 → 终局 Ch12-17), the middle section naturally shifts toward epic/燃 as BOSS scale increases. The first 5 chapters set the comedy bar — chapters 6-11 will lag without explicit countermeasures. Solution: inject at least one \"破坏气氛\" gag per middle chapter (比目鱼 trying to communicate with海神, 吴薯片 selling merchandise mid-apocalypse, 锅 exploding at the worst possible moment). Never let three consecutive chapters go full-serious.

## Cover Images in PDFs

When adding cover images to a markdown-generated PDF:
- The standard md2pdf script may not handle large images well
- Write a custom Python script that generates HTML with `<img>` tags, then uses WeasyPrint directly
- Use `@page { size: A4; margin: 0; }` for cover pages
- Set `max-width: 210mm; max-height: 297mm` for images to fill A4 without overflow
- Install PyPDF2 as a fallback for text extraction: `pip install PyPDF2 --break-system-packages`

**Full A4 portrait layout guide:** See `references/a4-pdf-layout-guide.md` for the complete WeasyPrint-based PDF generation pipeline — CSS parameters (13pt body, 10pt caption, 20pt chapter titles), image compression for <50MB PDFs, cover page handling, and verified script patterns from the《受着呗》production run.

## English Graded Reader Production

When Oxford Bookworms-style English readers are needed for 佳乐 (pure English, not Chinese+English hybrid), use the separate production pipeline documented in `references/english-graded-reader-production.md`. This covers the Bookworms 4-part structure (Before Read → Chapters → After Read → Glossary) with zero-out-of-curriculum vocabulary calibration.

## Related Skills

- `chinese-pdf-generation`: For rendering the novel as A4 PDF. See `references/novel-layout.md` for continuous-print CSS (no forced page breaks, 10.5pt serif, ✦ scene breaks).
- `kanban-video-orchestrator`: For multi-agent video production if animating the story.
- `docx-print-author`: For generating print-ready DOCX from English graded reader manuscripts.
- HTML trailer pattern: Self-contained animated HTML page (CSS + canvas particles + auto-advancing shots) as book trailer. See `references/trailer-storyboard-pattern.md`.
- PPTX storyboard pattern: Generate .pptx from scene data via OfficeCLI batch JSON. Preferred format for presenting to readers (kai哥's preference). See `references/officecli-storyboard-ppt.md`.
- Storyboard illustration pattern: 20-scene bilingual prompts (Chinese + English AI image-gen prompt) + style guide. See `references/trailer-storyboard-pattern.md`.
- V3 rewrite pattern: Reader-feedback-driven overhaul protocol for when the target reader rejects the story. See `references/v3-rewrite-pattern.md`.
- `references/shuangwen-comedy-engine.md`: 爽文+爆笑儿童小说创作引擎——主角嘴硬脑慌、围观震惊系统、BOSS心理崩溃、传闻链、商业化周边。
- `references/absurdist-spice.md`: 无厘头 3% 技法——不影响情节的荒诞小料（笔记本自己写字、薯片品牌每章换、锅炸出随机小鱼）。密度 8-12 处/40K 字，仅用于过渡和胜利后。\n- `references/external-diagnostic-pattern.md`: 外部诊断报告处理模式——当用户提供类似\"建议.MD\"的成分分析时，如何提取百分比、映射到具体操作、按影响排序。\n- `references/illustration-workflow.md`: 插画插入工作流——占位符格式、命名规范表、自动匹配脚本。适用于用户提供图片后批量嵌入PDF/DOCX。\n- `references/officecli-storyboard-ppt.md`: OfficeCLI生成故事板PPT——batch JSON格式、slide属性、字体的全部参数。\n- `references/weakness-shift-pattern.md`: 主角弱点重定向——当用户反馈\"佳乐短板是X不是Y\"时，如何在全书范围内精确替换而不改变其他设定。"\n- `references/rumor-chain-engine.md`: "自从"传闻链喜剧——每章一个离谱社会后果，从恐慌→生态→法则升级。
- `references/expansion-research-workflow.md`
- `references/readability-review-5th-grade.md`: 五年级可读性四维审查（P1词汇/P2句式/P3逻辑/P4幽默），含Python扫描脚本和输出模板。
- `writing-plans`: For structured implementation planning
- `test-driven-development`: The multi-phase revision maps to RED-GREEN-REFACTOR
