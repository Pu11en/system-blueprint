# Spec format

All three diagram types are plain JSON. `\n` breaks a line inside a box. See `examples/` for
complete working specs.

## Map

```json
{
  "title": "…", "subtitle": "…",
  "who": {"coach": {"label": "Coach"}, "online": {"label": "Instagram", "fill": "#fed7aa", "stroke": "#c2410c"}},
  "bands": [
    {"name": "Coach's side", "parts": [
      {"id": "coach", "name": "Coach", "who": "coach", "sub": "takes over hot leads",
       "steps": [{"text": "Gets a Slack alert"}, {"text": "Replies in the chat", "status": "guess", "guess": 1}]}
    ]}
  ],
  "links": [{"from": "auto", "to": "coach", "label": "hot lead alert", "status": "next"}],
  "questions": {"title": "Questions only the coach can answer", "items": ["…"]}
}
```

- `who`: one entry per owner, in key order; colours come from a palette unless `fill` and
  `stroke` are given. Every part and step is coloured by its `who`.
- `bands`: top to bottom, one per side (owner's side, shared middle, other side, online).
  `parts` sit left to right; `weight` (default 1) makes a part wider.
- `status` on parts, steps and links: `built` (default, solid), `next` (dashed), `later`
  (grey, dotted), `guess` (yellow; needs `guess`: the question number, starting at 1).
  Steps take their part's status unless they set their own.
- `links`: arrows between parts. Lower band to higher or back runs through the gap above
  the receiving band; parts in one band get room for the label between them.
- `questions`: optional; a big list beside the simple version.
- Optional: `width` (default 1160), `simple_heading`, `full_heading`.
- The build prints each guess and how many questions are left, plus any layout problem
  (overlaps, arrows through boxes, labels on boxes). Fix the spec until there are none.

## Blueprint

```json
{
  "title": "…", "subtitle": "…",
  "lanes": [
    {"key": "fan", "label": "FOLLOWER\nwhat they do", "kind": "person",
     "line_below": {"label": "line of interaction", "style": "dashed"}}
  ],
  "phases": [
    {"name": "1. COMMENTS", "time": "seconds",
     "cells": {"fan": "Comments 'GUIDE'", "auto": "Webhook gets comment"}}
  ],
  "handoffs": [{"phase": 0, "from": "fan", "to": "ig", "label": "comment"}],
  "problems": [{"phase": 0, "n": 1, "text": "Duplicate DMs if…"}]
}
```

- `lanes[].kind`: `person`, `frontstage`, `system`, `ai`, `support` (or any colour kind).
- `lanes[].line_below`: optional; `style` is `dashed` or `solid`.
- `phases[].cells`: lane key → box text. Leave a lane out where nothing happens.
- `handoffs`: vertical arrows inside one phase (0-based). Direction comes from lane order.
  If a box sits between the two lanes, the arrow is routed down the gutter beside it.
- `problems[].phase`: which column the problem sits under.
- Optional: `column_width` (default 420), `lane_height` (100), `connect_first_lane`
  (true: arrows between phases in the first lane).

## Flow

```json
{
  "title": "…", "subtitle": "…",
  "main": [
    {"id": "start", "type": "start", "text": "Follower\ncomments"},
    {"id": "kw", "type": "decision", "text": "Says\n'GUIDE'?", "next_label": "yes"},
    {"id": "send", "type": "step", "kind": "system", "text": "Send DM"},
    {"id": "done", "type": "end", "text": "Human\ntakes over"}
  ],
  "branches": [
    {"from": "kw", "label": "no", "type": "fail", "text": "Ignore"},
    {"from": "send", "label": "error", "id": "retry", "text": "Retry in 1 min", "to": "send"}
  ],
  "interrupts": [{"into": "send", "text": "Human replies first", "note": "…", "label": "pause"}],
  "problems": [{"on": "send", "n": 2}]
}
```

- `main[].type`: `start`, `decision`, `step`, `end`. Steps take `kind` (`system`, `ai`,
  `support`). `next_label` labels the arrow to the next main node.
- `branches[].type`: `step` (default), `fail` (red dead end), `note`. `to` makes it
  rejoin: the next main node (enters from the left), a later node (comes up from below),
  or an earlier one (loops back). Leave `to` out for a dead end. `dashed: true` for rare paths.
- Consecutive branches are staggered in depth automatically so they don't collide.
- `interrupts`: dashed red events above the line pointing into a main node.
- `problems`: numbered red flags on main nodes; numbers should match the design log.
