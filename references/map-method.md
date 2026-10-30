# Planning a system in pictures, with the person who owns it

How to run a design session so a non-technical owner understands every part, finds the
holes themselves, and can present the result to someone else. Learned over two days of
planning a real two-person system (an owner, a partner and their AI assistants sharing one
Drive folder) with its owner, October 2026. Each rule below fixed something that made the
owner say "I don't understand", "I'm confused" or "this is too noisy".

## The drawing

- **A map, not a chain.** A whole system (several people, bots or places passing things
  back and forth) is one map: every part placed by who owns it, in bands top to bottom
  (the owner's side, the shared middle, the other side, where things end up, such as
  online). A step-by-step chain was "too linear" and "only covers a part of the whole
  system". Use `scripts/diagram.py map`.
- **One drawing, read top to bottom.** The simple version on top, the full system under
  it. No pages, no cards, nothing side by side, no separate pictures per level.
- **The simple version first.** Every part, a few words each, arrows labelled with what
  travels (2 to 4 words). Shape it with the owner until they agree, then go deeper.
- **Going deeper grows the same map.** The next level is the same map with each part's
  steps inside it, in order. Draw it under the last level; once the owner approves it,
  remove the level above, except the simple version, which stays on top. The deepest
  approved level is "the full system".
- **Show what gets built, and when.** Draw the future design, not only what exists. Solid:
  built and working. Dashed: the next build. Grey (grey fill, dotted line, grey words):
  later, not in this build. Ask which parts go in the next build; don't guess.
- **Guesses are yellow and numbered.** Anything about how the system works for the people
  in it that the owner has not said is a guess: yellow, with a number matching the order
  you ask about it. When one decision covers several boxes, they share a number; say how
  many questions are left, not how many boxes. Technical choices (how to build it) stay
  yours.
- **Questions only someone else can answer** sit beside the simple version in big text.
  Answer what you can yourself first, from their own emails and records, and never ask
  how they run their own tools.
- **Keep the look once it works.** When the owner says a picture needs "a little more"
  but cannot say what, do not build new looks: ask one yes-or-no question about one small
  change and change only that. Three alternative looks on real content got "none of them
  ... go back to what we had". What finally worked: filled boxes with centred words,
  tidy columns running top to bottom, plain white parts and room between them.
- **Fit the screen.** Text 16 px or more; about 1160 wide, so it opens near 100% and the
  owner scrolls down rather than zooming.

## Designing the parts

- **One place per kind of thing, so an AI never has to think.** When a bot or AI decides
  what to do with something, make the answer obvious from where it is: one folder (or
  queue, or table) per kind of thing, each with one job. Write a table: place, what is
  in it, who puts it in, what happens next, and whether the owner is in the loop.
- **Name places by what is in them and what they are for**, so the name makes sense alone
  in a message or a log: "Video rules", not "Rules"; never "files", "assets" or "misc".
  Things with the same next step share a place. Add a catch-all that makes the system ask
  the owner, then teach the guide.
- **Only busy things get their own place.** Rare or static things live inside a related,
  busier one (a logo inside "Video rules").
- **Stores stay tidy by design, never with a clean-up job.** Each place holds only what
  waits for its next step; whoever finishes a step moves the thing on at once; one writer
  moves things and keeps a log of each move, so status shows at a glance.
- **Interruptions are rare.** Only what needs the owner pings them; the rest goes in one
  daily summary.

## The session

- Ask one question at a time, in chat, with your proposed answer. Questions and guesses
  go in chat; the drawing shows only the system.
- Check the owner's own records (emails, notes, earlier answers) before asking them or
  proposing a test for them.
- Rebuild and re-check the drawing after every change, and give its link every time.
  Before a layout change, compare every label before and after so nothing is lost.
- Anything made for someone else to see (an email, a guide, a presentation) never
  includes what the owner said about that person.
- **A story or analogy** (to present the idea) is one picture that tells the whole story,
  like a painting: never cards, panels or a storyboard. Fact-check every claim in it first
  and confirm each part of the analogy with the owner, one question at a time.
- When the owner asks "is planning done?", list what is still open and what the build can
  start without. Then write a short build plan from the full system: each box is one
  piece to build, each arrow a hand-off.
