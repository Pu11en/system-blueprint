---
name: system-blueprint
description: Plan a system in pictures instead of documents, level by level, until there are no holes. Starts with the simple version (the whole system as one map, every part placed by who owns it), then goes deeper one level at a time in the same top-to-bottom picture, marks every assumption as a numbered yellow guess asked one at a time, shows what is built, next and later, and runs hole-finding rounds until it is ready to build. Use when someone wants to plan, think through, map, audit or redesign a workflow, automation, agent system, bot, business process or any system with several people or tools, or says a plan "feels vague", "I don't understand it" or "I keep missing things".
---

# System Blueprint: plan in pictures, level by level

Planning with a picture beats planning with a document: the owner sees the whole system,
points at what is wrong, and understands more each round. This skill is the process that
worked when a non-technical owner planned a real two-person system end to end: little at a
time, each level more detailed as they understand, until nothing is missing.

**The core idea: the levels follow understanding.** At the start nobody has all the
answers, and that is expected. Draw what is known now; mark what is not known as numbered
questions. Each answer fills in the picture, and the next level is drawn only once the
current one is understood. So a level is not a fixed amount of detail: it is how far the
owner and the agent understand the system so far. By the last level the whole flow is
clear from beginning to end, with no holes left.

**The picture is the plan.** Chat carries one question at a time. Notes are for the agent
(`<name>-plan.json` plus a short notes file of decisions and open questions); the owner
should never need to read them. The tool that draws the picture matters less than the
process below.

## The process

### 0. Read what exists first

Read the code, notes and the owner's own records (emails, chats, earlier answers). Never
ask what you can look up, and never propose a test or a task for the owner before checking
there. Give the owner no homework (searches, tests, things to collect); do it yourself.

Write the **goal** in one line, in the owner's words, with a real number ("every comment
gets the guide within a minute"). It goes at the top of the picture. If the owner names a
solution instead, ask once: "so that what happens?"

### 1. The simple version (Level 1)

Draw the whole system as one **map**: a row per side, top to bottom (the owner's side, the
shared middle, the other people's side, where things end up, such as online), every part
placed in its row, arrows labelled with what travels (2 to 4 words). Not a chain of steps:
a chain is "too linear" and covers only part of the system.

- Include what is not built yet. Plan the future system, not only today's.
- Few words per box, real names for people and places, colour by who does it.
- No limit on parts: show everything the system has, and never merge parts to fit a
  number. Keep the words big; 3 to 5 rows read best.
- Draw the real system from the first picture. A look tried on a small example tells you
  nothing: one that read fine at 8 boxes failed at 28.
- Show it beside the chat, give its link, and shape it with the owner until they agree.
- End the reply by offering to go deeper.

### 2. Ask about every assumption, one at a time

Anything about how the system works for the people in it that the owner has not said is a
**guess**: yellow on the picture, with a small number for the order you will ask about it.

- **Ask only what changes the plan.** Decide yourself, and say so once, when you can look
  it up, there is a normal default, both answers build the same thing, or it is easy to
  change later. Technical choices (how to build it) are always yours.
- **Ask the biggest question first:** the one that changes the most of the picture, or that
  would break the system if the guess is wrong. Small details last.
- **One question at a time**, naming the box ("question 3, the box 'Replies within an
  hour'"), with your proposed answer worded so "yes" accepts it and a one-line reason.
  The owner can answer in their own words, or "yes to all" for the numbered list.
- **Ask it alone.** A question at the end of a reply full of news gets skipped. Put news
  first, then the question by itself; end every reply with one line: "Still open: 3, 5".
- One decision covering several boxes gets one number; say how many questions are left,
  not how many boxes. Never bury guesses in a page of proposed answers.
- A pick from options is not approval: build it, show it, ask again.
- If a new answer contradicts an earlier one, say so at once. If the owner drops an idea
  they had themselves, just change the picture, with no "but you said".
- Propose structures that remove decisions without being asked (see "Stores" in
  `references/finding-holes.md`).

Update the picture after every answer, then ask the next one.

### 3. Go deeper, one level at a time

Draw the next level **under** the last one, in the same picture: the same map with every
part opened up, its steps inside it in order. One picture read top to bottom: no pages, no
cards, nothing side by side, no separate picture per level.

- Keep every name, row and order from the level above, word for word; each opened part's
  title is its Level 1 label. Never redo the layout from scratch: the owner's eye finds
  its way by what stays put.
- Open up only the parts that are built, in the next build, or hold a guess. Later parts
  stay simple boxes until they come closer.
- Mark what changed this round with a thick outline and one "Changed: ..." line in chat;
  clear it next round. Never fade the rest.
- End each round with one line of progress: "Level 2: 5 of 8 questions settled."

When the owner approves a deeper level, remove the one above it, except the simple version,
which stays on top. The picture ends as two parts: **the simple version** and **the full
system, step by step**. Go deeper again only where the owner wants more detail.

### 4. Say what gets built, and when

Solid: built and working. Dashed: the next build. Grey: later, not in this build. Ask the
owner which parts are in the next build; don't guess. Keep the later parts on the picture
so the next build leaves room for them; new ideas mid-session go straight to grey.

The next build must run from beginning to end: the solid and dashed parts together make one
unbroken path from what starts the system to its result, so the first build already works.
Then each build adds to something that works.

### 5. Find the holes, round after round

Run `references/finding-holes.md` over every part and arrow: what starts it, what comes in
and out, what fails, who takes over, what piles up, where each thing is stored. Each round:

- **Walk one real example** through the picture, step by step, then backwards from the
  result: does each step have what it needs?
- **Ask one pre-mortem question:** "Three months from now this went wrong. What happened?"
  Add your own list from research on how systems like this one usually break.
- **Get a fresh check:** give a helper that was not in the conversation only the plan and
  the picture, and ask it to list what it would have to guess to build this. Sort each
  item: already answered, your own call, or a question for the owner.

Every hole becomes a new guess on the picture or a question in chat. Repeat ("go through
everything again") until a round, including the fresh check, finds nothing new.

Questions only someone else can answer: answer them yourselves first from what you have,
never ask how they run their own tools, and list what remains in big text beside the simple
version.

### 6. Ready to build

When the owner asks if planning is done, say plainly what is still open, what the build can
start without, and what waits on someone else. A guess nobody can answer becomes a small
"try it and see" step in the build. Then write a short build plan from the full system:
each box is one piece to build, each arrow a hand-off. Build from the picture; if the build
must differ, change the picture first and say so.

During the build, keep using the same picture: a box turns solid only when it is shown to
work; anything missing stays dashed for the next build.

## How to work with the owner

- Go at their pace: little at a time, more detail only as they understand.
- A long spoken message holds many messages: answer each point in its own short bullet.
- When they are lost in logistics, reset in three lines and end with what, if anything,
  they need to do ("you don't need to do anything").
- Every label and fact must make sense on its own ("13 weeks" of what?). Avoid "X, not
  Y" wording; it reads as disagreeing with them.
- Keep the look once it works. If they say it needs "a little more" but cannot say what,
  don't make new looks: ask one yes-or-no question about one small change.
- When they say "I don't understand" or "I'm confused", find what caused it (a word, a
  number, a crowded part), fix the picture, and keep that fix for every later picture.
- Use their words, never yours: no jargon, no internal names ("test tab", "bot" when they
  say "my system"). Keep a short list of their words, and words to avoid, in the notes.
- Anything made for someone else to see (an email, a guide, a presentation) never includes
  what the owner said about that person. Show them the same simple version with the goal
  on top, open only their part, and ask them 3 questions at most.
- A story or analogy to present the idea is one picture, like a painting: never cards or
  panels. Fact-check every claim in it and confirm each part with the owner first.

## Drawing it

Write the plan as JSON (`references/plan-format.md`) and build both pictures from it:

```bash
python3 scripts/plan.py my-plan.json             # -> my-plan.excalidraw, my-plan.md
uv run scripts/render.py my-plan.excalidraw      # -> my-plan.png: look at it
```

- `my-plan.excalidraw`: the whole picture, the simple version then the full system. Open it
  in any Excalidraw (excalidraw.com or self-hosted), or show the PNG.
- `my-plan.md`: the simple version as Mermaid, for a chat or a board beside the chat that
  shows Mermaid, plus the questions. Mermaid can't keep the full system tidy (its automatic
  layout loses the row order and crosses arrows), so the full system is always the drawing.
- The build prints every numbered guess, how many questions are left, size warnings and
  any layout problem (overlaps, arrows through boxes or crossing each other). Fix the plan until there are none, render, and **look at the PNG** before
  showing it. First render only: `uv run --with playwright playwright install chromium`.

Any other drawing tool is fine if the picture follows `references/pictures.md`.

## Files

- `references/pictures.md`: how the pictures look, and what made an owner lost.
- `references/finding-holes.md`: the hole checklist, how to ask, how to design stores.
- `references/plan-format.md`: the plan's JSON fields.
- `scripts/plan.py`: plan JSON to Excalidraw drawing and Mermaid (standard library only).
- `scripts/render.py`: drawing or Mermaid to PNG via headless Chromium.
- `examples/`: an Instagram comment-to-DM system as a plan.
