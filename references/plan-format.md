# Plan format

The plan is one JSON file; `scripts/plan.py` draws both pictures from it. Grow it level by
level: parts first (the simple version), then each part's `steps` (the full system). See
`examples/instagram-plan.json` for a complete plan.

```json
{
  "title": "…", "subtitle": "…", "goal": "every comment gets the guide within a minute",
  "who": {"coach": {"label": "Coach"}, "online": {"label": "Instagram", "fill": "#fed7aa", "stroke": "#c2410c"}},
  "bands": [
    {"name": "Coach's side", "parts": [
      {"id": "coach", "name": "Coach", "who": "coach", "sub": "takes over hot leads",
       "steps": [{"text": "Gets a Slack alert"}, {"text": "Replies in the chat", "guess": 1}]}
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
- `goal`: one line in the owner's words, with a real number; shown under the title.
- `status` on parts, steps and links: `built` (default, solid), `next` (dashed), `later`
  (grey, dotted). Steps take their part's status unless they set their own.
- `guess` on a part or step: the number of the question that settles it (1, 2, 3 ...);
  the box turns yellow and keeps its status's line style. One number may cover several
  boxes. (`"status": "guess"` from older plans still works.)
- `changed: true` on a part, step or link: thick outline, "changed since last time".
  Remove it next round.
- `links`: arrows between parts. Lower band to higher or back runs through the gap above
  the receiving band; parts in one band get room for the label between them.
- `questions`: optional; a big list beside the simple version.
- Optional: `width` (default 1160), `simple_heading`, `full_heading`.
- `scripts/plan.py` prints each guess, how many questions are left, size warnings, and any
  layout problem (overlaps, arrows through boxes or crossing, labels on boxes). Fix the
  plan until there are none.
