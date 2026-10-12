# Running Threads Rule: Grievances Must Persist

> When the user expresses a personal grievance through the protagonist (teacher complaints, school frustrations, parental pressure), that thread must run through the ENTIRE book, not just Chapter 1.

## The Rule

A grievance introduced in the opening MUST appear every 2-3 chapters throughout. When you delegate bulk chapters to subagents, they WILL drop this thread unless you explicitly list it in their context. This is not a subagent quality issue — it's a context-preservation issue. Subagents see skill instructions, not the emotional thread of the conversation.

## Pre-Writing Checklist

Before dispatching subagents for bulk chapter writing, list every running thread in their context:

```
PERSISTENT THREADS TO MAINTAIN:
- Teacher complaints (李老登/李晶): Every 2-3 chapters, compare some deep-sea absurdity to her teaching
- [Other running gags: catchphrase, specific character quirks, etc.]
- Each callback must use a DIFFERENT angle — never repeat the same comparison
```

## Post-Writing Verification

After subagents complete bulk chapters:

```bash
# Count grievance mentions per chapter
grep -nc "李老登\|teacher\|罚抄\|家长会" output-file.md

# Find chapters with zero hits
grep -n "^## 第" output-file.md  # list chapter positions
# Cross-reference with grep results above
```

**Zero-hit chapters need a 1-2 sentence callback** inserted at a natural comparison point:
- A frustrating deep-sea event → compare to classroom frustration
- An artifact or note → compare to homework/assignments
- A character's behavior → compare to teacher behavior

## Callback Angle Map (Example from 深海钓徒)

| Chapter | Comparison Angle |
|---------|-----------------|
| 1 | Opening: full character intro (骂人, 罚抄, 家长会) |
| 2 | Goldie's protection racket vs parent meetings — "至少明码标价" |
| 3 | Upgrading through combat vs "努力" homework |
| 4 | Squid can't count vs teacher's broken logic |
| 5 | Fake market goods vs "为了你们好" |
| 6 | Old man's 3-word note vs teacher's 135-word homework |
| 7 | Volcano = teacher's office; "压力就是动力" |
| 9 | Dragon of failed writing vs teacher who only criticizes, never teaches |
| 10 | Deep sea has clear rules; classroom has fuzzy rules |
| 11 | Rival becomes ally vs teacher's "competition only" policy |
| 12 | Standing in awe vs standing as punishment |
| 13 | Listening to light vs "hearing" teacher's repetition |
| 14 | Punishment copying vs truly writing a name |
| 15 | 4.5 years of Li vs 7 days of the old man |
| 16 | Classroom window vs aquarium glass — one shows walls, one shows worlds |
| 17 | Thesis: "填鸭 vs 走出来; 抄答案 vs 走到答案那里" |

Each angle is different. The reader never feels "here's that teacher complaint again" — it feels like the protagonist's worldview expanding through contrast.

## The Final Chapter Thesis

The last callback is not a joke — it's the thesis statement. It ties the grievance to the story's theme. In 深海钓徒:

> "李老登的语文课教了四年半。教会他的东西用一根手指就能数完。深海教了他七天。教会他的东西整个深海都装不下。区别不在时间长短——在一个是填鸭，一个是走出来的。李老登会把答案写在黑板上让你抄。深海不写答案——深海让你自己走到答案那里。走到的时候你已经不需要答案了。你就是答案。"
