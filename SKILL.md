---
name: system-blueprint
description: Design an automation or business system so nothing is vague, then draw it the way professional system designers do. Interviews the user one question at a time with a fixed step checklist (trigger, input, action, tool, output, failure, human hand-off), keeps a design log with open questions, then produces an Excalidraw service blueprint (the whole system over time, from what people see to what is hidden) and BPMN-style flows (every failure path for one journey). Use when someone wants to plan, map, audit or redesign a workflow, automation, agent system, bot, funnel or internal process, or says their system "feels vague" or "I keep missing things".
---

# System Blueprint

Turn a fuzzy idea ("an Instagram system that handles posts, comments and DMs") or an
existing messy system into a design with no vague parts, and show it in pictures that
read like a professional's.

Two outputs, always:

1. **Design log** (`<name>-design.md`): every decision, every step card, every open question.
2. **Diagrams** (`.excalidraw` + `.png`): one **service blueprint** for the whole system and
   one **flow** per important journey. Open `.excalidraw` files at excalidraw.com or any
   self-hosted Excalidraw.

## Process

### 1. Find out what exists

If it is an existing system, read the code, docs and notes first; never ask the user what
you can look up. Write a short "how it works today" section in the design log with the
problems you found. If it is a new idea, skip to step 2.

### 2. Interview, one question at a time

Follow `references/interview.md`. The rules that matter most:

- **One question per message**, as lettered multiple choice (A/B/C) with your recommended
  answer and a one-line reason. The user can always answer in their own words.
- Plain language. Ask about the system's behaviour, not about code internals.
- Go **system level first** (goal, people, triggers, volume, tools, rules), then **step by
  step** along the main journey. Each step is done only when its **step card** is full.
- Anything still unknown becomes an open question `Q-<n>` in the log, not a guess.
- **Write the answer into the design log after every reply**, so a long session never
  loses work.
- Stop when every step card is full and no open question blocks building. Say so plainly.

### 3. Draw

Read `references/diagram-rules.md`, then write JSON specs and build with the scripts:

```bash
python3 scripts/diagram.py blueprint my-blueprint.json   # -> my-blueprint.excalidraw
python3 scripts/diagram.py flow my-flow.json             # -> my-flow.excalidraw
uv run scripts/render.py my-blueprint.excalidraw         # -> my-blueprint.png
```

Spec fields are in `references/spec-format.md`; working examples are in `examples/`.
First render only: `uv run --with playwright playwright install chromium`.

- **Blueprint**: phases left to right (with time), lanes top to bottom: the person, what
  they see, the system, the AI, support/data. Lines of interaction and visibility.
  Label every hand-off arrow with what travels. Problems row at the bottom.
- **Flow**: one journey. Normal path in a straight line; every yes/no check that can go
  wrong branches below; outside interruptions (restarts, a human stepping in) come from
  above. Every branch ends in a rejoin, a retry, or a clearly marked dead end.

### 4. Check before showing

Render to PNG and **look at it**. Fix overlapping text, arrows through boxes, labels on top
of lines, and anything cut off. Then check the content: every step card from the log
appears somewhere, every failure from the cards appears in a flow, and every problem has a
number that matches the log.

### 5. Hand over

Explain the result in a few plain sentences: what the system does, the biggest risks the
diagrams expose, and the next decision needed. Attach the PNGs; point to the `.excalidraw`
files for editing. Keep the design log as the source of truth and update diagrams when it
changes.

## Files

- `references/interview.md`: question order, the step card, systems checks, log format.
- `references/diagram-rules.md`: what professionals do (C4, service blueprint, BPMN) and
  the layout rules the scripts follow.
- `references/spec-format.md`: JSON fields for `blueprint` and `flow`.
- `scripts/diagram.py`: JSON spec to `.excalidraw` (standard library only).
- `scripts/render.py`: `.excalidraw` to PNG via headless Chromium (uv inline deps).
- `examples/`: an Instagram comment-to-DM system as blueprint and flow, specs and output.
