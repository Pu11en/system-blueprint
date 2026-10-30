# Interview guide

The goal is a design with no vague parts. Vagueness hides in three places: steps nobody
described, failures nobody planned for, and hand-offs between people and machines. This
guide walks through all three in a fixed order so nothing gets skipped.

## How to ask

- One question per message. Lettered options (A, B, C, sometimes D), each one line.
- Put your recommendation first or mark it, with a one-line reason.
- Use the user's own words and real examples ("a follower comments 'GUIDE'"), not jargon.
- If the answer is in the files, the code or an earlier answer, don't ask; state it and move on.
- If the user says "I don't know", offer a sensible default, record it as an assumption,
  and keep going. If they say "I don't get it", explain with a concrete example first.
- After each answer, update the design log, then ask the next question.

## Order

### Part A — the whole system (5–8 questions)

1. **Goal**: what result should this system produce, and how will you know it works?
   (one measurable success sign, e.g. "every comment gets a DM within a minute")
2. **People**: who uses it, who is affected, who steps in when it can't cope?
3. **Triggers**: what starts it? (a message, a schedule, a webhook, a person clicking)
4. **Volume and timing**: how many per day, how fast must it respond, any time windows?
5. **Tools and accounts**: which apps, APIs, AI models, storage; what already exists?
6. **Rules and limits**: platform policies, rate limits, budget, privacy, legal.
7. **Scope**: what is deliberately out (so nobody builds it by accident)?

Then list the main journey as 4–7 phases in time order and confirm them with the user.
These become the blueprint's columns.

### Part B — step by step

Walk the main journey in order. For every step, fill a **step card**. Ask only for the
fields you can't fill yourself.

| Field | Question it answers | Example |
| --- | --- | --- |
| Trigger | What makes this step start? | New comment webhook arrives |
| Input | What exactly comes in? (real example) | `{"user": "@sam", "text": "GUIDE"}` |
| Action | What happens, in one sentence? | Check keyword and whether we DM'd Sam before |
| Done by | Which person, tool or AI does it? | n8n workflow |
| Output | What exactly comes out? (real example) | DM sent with the guide link |
| Stored | What is saved, where? | Contacts table: Sam, DM sent, time |
| Time / volume | How long, how often? | < 5 s, ~200 a day |
| Can fail by | What can go wrong? (list every way) | API rate limit; Sam blocked DMs |
| On failure | What happens for each failure? | Retry in 1 min, max 3, then alert |
| Human hand-off | When does a person take over, how do they know? | AI unsure → Slack alert with chat link |
| Visible to | What does the person see at this step? | "Check your DMs!" reply |

A step is finished when every field has a concrete answer or an open question.

### Part C — systems checks (ask once the steps are known)

These catch the problems that only show up when the whole thing runs for weeks.

- **Piles**: what can build up? (unanswered messages, retries, unpaid invoices) What
  drains it, and what happens if it grows faster than it drains?
- **Loops**: can the system trigger itself? (bot replying to its own reply, retry storms,
  two automations ping-ponging) What stops the loop?
- **Delays**: where does waiting change the outcome? (24-hour reply windows, slow
  approvals, cache delays)
- **Limits**: which rate limits, quotas, costs or capacity caps can be hit at peak volume?
- **Single points of failure**: if one tool, account or person is down, what stops?
- **Duplicates and order**: can the same event arrive twice or out of order? What
  prevents double actions?
- **Stopping**: how is the system paused, and how does a human take over cleanly?
- **Stores**: for every folder, queue or table: what is in it, who puts it in, what
  happens next, is the owner in the loop? One place per kind of thing, named by what is in
  it and what for; only busy things get their own place; whoever finishes a step moves
  the thing on, so it stays tidy without a clean-up job (see `map-method.md`).

Each answer either becomes a branch in a flow diagram or a numbered problem.

## Design log format

Keep one Markdown file, updated after every answer:

```markdown
# <System name> — design log

## Goal and success sign
## People, triggers, volume, tools, rules, out of scope
## Phases (blueprint columns)
## Step cards
### 1. <step name>
- Trigger: …
- Input: …
(all fields)
## Systems checks
## Stores (place, what is in it, who puts it in, what happens next, owner in the loop?)
## Decisions (date, decision, why)
## Open questions
- Q-1 (open): …
- Q-2 (resolved 2026-01-05): … → answer
## Problems (numbers match diagrams)
1. …
```

## When to stop

Stop interviewing when all step cards are full, every systems check has an answer, and
no open question blocks building. Tell the user that in one sentence, then draw.
