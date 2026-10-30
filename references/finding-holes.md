# Finding the holes

Holes hide in four places: steps nobody described, failures nobody planned for, hand-offs
between people and machines, and stores nobody keeps tidy. Run this over every part and
arrow of the picture. Answer what you can from the files and the owner's records; every
hole left becomes a numbered guess on the picture or a question in chat.

## How to ask

- One question per message, in plain words, with your proposed answer first and a one-line
  reason. Lettered options (A, B, C) help when the choices are clear.
- Use the owner's own words and a real example ("a follower comments GUIDE").
- Ask about how the system works for people, never about code. Technical choices are yours.
- "I don't know": propose a sensible default, mark it as a guess, keep going. "I don't get
  it": explain with a concrete example, then ask again.
- After each answer: update the plan, rebuild the picture, then ask the next question.
- Order: the question that changes the most of the picture, or would break the system if
  wrong, comes first. Don't number what you can decide yourself (see SKILL.md).

## Every step

| Check | Question it answers |
| --- | --- |
| Starts when | What makes this step happen? |
| Comes in | What exactly arrives? (a real example) |
| Does | What happens, in one sentence? |
| Done by | Which person, tool or AI? |
| Goes out | What exactly leaves, and to where? |
| Stored | What is saved, where? |
| How often | How long, how many, on what schedule? |
| Can fail by | Every way it can go wrong. |
| On failure | What happens for each one? |
| Person takes over | When, and how do they find out? |
| Seen by | Who sees what at this step? |

## The whole system, once the steps are known

- **Piles:** what can build up, what drains it, what if it grows faster?
- **Loops:** can the system trigger itself? What stops it?
- **Delays:** where does waiting change the outcome?
- **Limits:** rate limits, quotas, costs, capacity at the busiest time.
- **One point of failure:** if one tool, account or person is down, what stops?
- **Twice or out of order:** can the same thing arrive twice? What prevents a double action?
- **Stopping:** how is it paused, and how does a person take over cleanly?
- **Interruptions:** only what needs the owner pings them; the rest goes in one daily summary.
- **Research:** how do systems like this one usually break? Check sources, not memory.

## Stores: designed so an AI never has to think

Every folder, queue, inbox or table gets a row in the notes: what is in it, who puts it in,
what happens next, and whether the owner is in the loop.

- **One place per kind of thing, one job each**, so what to do with something is obvious
  from where it is. Things with the same next step share a place.
- **Name it by what is in it and what it is for**, so the name makes sense alone in a
  message or a log: "Video rules", not "Rules"; never "files", "assets" or "misc".
- **Only busy things get their own place.** Rare or static things live inside a related,
  busier one (a logo inside "Video rules").
- **Who picks the place**, usually the sender, by a short guide with examples; plus a
  catch-all that makes the system ask the owner, after which the guide is taught.
- **Tidy by design, never by a clean-up job.** Each place holds only what waits for its next
  step; whoever finishes a step moves the thing on at once; one writer moves things and logs
  each move, so status shows at a glance.

## Questions for someone else

Work out your own answers first from everything you have. Never ask how they run their own
tools. Keep only what would break the system without their answer, word it so it does not
sound risky, and list it beside the simple version.

## When to stop asking

Stop when what is left is cheaper to settle while building than in planning, and say so. A
guess nobody can answer becomes a small "try it and see" step in the build plan.

## Done

Planning is done when every step passes the table, every whole-system check has an answer,
no guess is left on the picture, and a hole-finding round finds nothing new. Say so in one
sentence, with what can be built now and what waits.
