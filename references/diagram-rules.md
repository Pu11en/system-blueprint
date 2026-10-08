# Diagram rules

Borrowed from three professional traditions. Each answers a different question, so a good
system design usually needs two of them.

| Style | Answers | Use it for |
| --- | --- | --- |
| **Service blueprint** (Nielsen Norman Group) | What happens at each stage, from what the person sees down to what is hidden? | The whole system on one page |
| **BPMN flow** (business process modelling) | What happens at every yes/no point, including timeouts, retries and dead ends? | One important journey per diagram |
| **C4 container diagram** (Simon Brown) | What are the parts, and what travels between them? | A parts map when there are many services |

## Rules every diagram follows (from C4)

- A **title** that says what the diagram shows and its scope.
- A **key** explaining every colour and shape.
- **Label every arrow** with what travels along it ("webhook event", "score + reply"),
  never vague words like "uses".
- Each element says **what it does**, not just its name ("Send DM via Messaging API").
- Same colours mean the same thing across all diagrams of a system.

## Service blueprint

- **Columns** = phases in time order, with a time row ("seconds", "within 24 h").
- **Lanes**, top to bottom: the person's actions; what they see (frontstage); the system;
  the AI; support and data.
- **Line of interaction** (dashed) under the person; **line of visibility** (solid) under
  what they see; **line of internal support** (dashed) above support.
- The person's lane has arrows from phase to phase, so the eye reads the journey first.
- Vertical arrows are hand-offs between lanes, each labelled.
- A **problems row** at the bottom, numbered; the numbers match the design log.

## BPMN-style flow

- The **normal path is one straight horizontal line**, start on the left, good end on the
  right. Someone should understand the happy case by reading only that line.
- **Decisions are diamonds** phrased as yes/no questions; the arrow continuing the normal
  path is labelled with the answer that continues ("no" for "API error?").
- **Failures branch below** and each one ends in one of three ways: rejoins the main line,
  loops back to retry, or a **red dead end** saying what the person experiences.
- **Interruptions come from above** (a restart, a human replying first) as dashed red
  events pointing into the step they affect.
- Dashed = rare or side path.

## Colours (fill / stroke)

| Meaning | Fill | Stroke |
| --- | --- | --- |
| Person / start | `#fed7aa` | `#c2410c` |
| What they see / good end | `#a7f3d0` | `#047857` |
| System step | `#93c5fd` | `#1e3a5f` |
| AI step | `#ddd6fe` | `#6d28d9` |
| Storage / support | `#dbeafe` | `#1e40af` |
| Decision | `#fef3c7` | `#b45309` |
| Failure / problem | `#fecaca` | `#b91c1c` |

## Writing the boxes

- Two short lines per box (about 26 characters each). Use `\n` in the spec to break lines.
- Verb first for actions ("Queue and retry in 1 minute").
- Real names and numbers beat placeholders ("200 a day", "24-hour window").

## Check the picture

Render, then look for: text overflowing a box, labels sitting on lines, arrows crossing
through boxes, branches overlapping, anything cut off at the edges. Fix the spec (shorter
text, fewer branches per diagram, split into two flows) and render again.
