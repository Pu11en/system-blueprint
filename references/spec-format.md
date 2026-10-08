# Spec format

Both diagram types are plain JSON. `\n` breaks a line inside a box. See `examples/` for
complete working specs.

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
