# Million-Word Expansion Research Workflow

When scaling a children's novel from ~40K to 1M+ words, use parallel subagent research
followed by synthesis rounds. This workflow was validated on 字海钓徒 (38K→1M plan).

## Phase 1: Benchmark Research (3 parallel subagents)

Split 20 benchmark works into 3 thematic groups. Each subagent researches 6-7 works,
produces a structured analysis file with specific techniques applicable to the target novel.

| Group | Focus | Output |
|-------|-------|--------|
| A | Humor techniques, character archetypes, pacing | `research-groupA-humor.md` |
| B | Power systems, world-building, upgrade mechanics | `research-groupB-power.md` |
| C | Team dynamics, adventure structure, emotional beats | `research-groupC-adventure.md` |

**Key instruction for subagents:** "For each work, identify (1) the core technique,
(2) how the author executes it across chapters, (3) how to adapt it to our novel."

**Pitfall: web search may be blocked.** Subagents should fall back to training
knowledge with a note in the output. The analysis quality from training data is
sufficient for creative planning.

## Phase 2: Synthesis & Blueprint (2 parallel subagents)

| Subagent | Input | Output |
|----------|-------|--------|
| A | All 3 research files + current novel MD | `expansion-blueprint.md` — 8-volume structure, chapter outlines, character arcs, humor system, educational integration |
| B | Research files + current novel MD | `world-system.md` — cosmology, cultivation stages, equipment trees, factions, bestiary, game mechanics |

**Blueprint requirements:** volume-by-volume breakdown, power progression per volume,
companion arc per volume, 15-20 chapter summaries per volume. Target 1500+ lines.

**World system requirements:** 12+ cultivation stages with breakthrough conditions,
5-tier equipment evolution for each key item, faction system with leaders/goals,
bestiary with types and mechanics. Target 1500+ lines.

## Phase 3: Samples & Schedule (2 parallel subagents, may need chunking)

| Subagent | Input | Output |
|----------|-------|--------|
| A | Blueprint + world system + original novel | `sample-chapters-1-3.md` — first 3 expanded chapters (~9K words total) matching original voice |
| B | Blueprint (Vol 1-4) | `chapter-schedule-vol1-4.md` — detailed chapter tables |

**Chunking strategy for timeouts:** If a 600s subagent times out, split into smaller batches:
- Vol 1-2 instead of Vol 1-4
- Vol 3-4 as a separate subagent
- Vol 5-8 as another subagent

Each chunked subagent gets only the relevant sections of the blueprint (read partial
file with offset/limit to keep input tokens manageable).

## Phase 4: Master Summary (1 subagent)

Read ALL output files. Create `project-master-summary.md` with:
- Project overview table
- Core principles (what stays from original)
- One-paragraph per volume
- Character arc roadmap
- Top 3 borrowed techniques
- Writing roadmap with time estimates
- Complete file manifest

Keep under 500 lines. The reader (parent/author) should understand the full plan in 5 minutes.

## Chapter Sample Writing Rules

When writing expanded sample chapters:

1. **Voice matching is critical.** Read the full original novel first. Copy:
   - Paragraph rhythm (short punchy paragraphs, frequent line breaks)
   - Dialogue style (bilingual Chinese/English, fish speak English)
   - Internal monologue (deadpan, self-deprecating, 白小纯-style)
   - Scene break markers (---)

2. **Expansion, not replacement.** Keep iconic scenes (first fall into Word Sea,
   fish chorus "New boy!", Goldie's snack obsession). Expand with:
   - More classroom/school context
   - More sensory detail in transitions
   - More minor character moments
   - Foreshadowing for later volumes (glimpse of deep water, shadow, ancient thing)

3. **Each chapter needs:** 2+ funny moments, 1 heartfelt moment, 1 English word/phrase
   naturally embedded, a mini-arc (setup→complication→hook), a hook ending.

## Verified Time Estimates

| Phase | Subagents | Typical duration |
|-------|-----------|-----------------|
| Research (3 parallel) | 3 | 6-7 minutes |
| Blueprint + World (2 parallel) | 2 | 7-8 minutes |
| Samples + Schedule (2 parallel, chunked) | 2-3 batches | 15-20 minutes |
| Master Summary | 1 | 2 minutes |
| **Total** | | **30-40 minutes** |

The 8-hour estimate is for actual novel writing, not the planning phase.
Planning is 30-40 minutes with parallel subagents.
