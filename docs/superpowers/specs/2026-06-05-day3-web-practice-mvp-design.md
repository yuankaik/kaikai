# Day3 Web Practice MVP Design

## Goal

Build a local, self-contained web companion for the current Day3 practice. It should let us try the computer-side experience without replacing the printable PDF.

## Scope

This MVP renders the existing `practice spec` into one HTML file. It does not require a server, login, database, internet, or account. The PDF remains the official printable version for tonight.

## Product Shape

The web page has two modes on one page:

- 船长练习：large question cards, answer boxes, complete buttons, and a small Ace Angler-style ocean visual.
- 大副提交：classroom radar, Feynman Boss prompt, audio file placeholders, and the same no-extra-questions rule.

## Data Flow

```text
practice/specs/Day3-海王龙的逆向追踪.json
  -> rendering/day_web.py
  -> practice/web/Day3-海王龙的逆向追踪.html
```

The HTML embeds the spec data at generation time, so it can open directly from disk.

## Guardrails

- Do not replace PDF for now.
- Do not add distracting animations during question answering.
- Do not reveal answers by default.
- Keep all progress and fish coin displays read-only.
- Use local browser storage only for temporary answer text and completed-card state.

## Success Criteria

- The HTML shows Day3 title, Switch2 progress, all question IDs, Feynman prompt, classroom radar, and大副 actions.
- The generated page can be opened directly from the filesystem.
- The existing PDF generation and tests continue to pass.
