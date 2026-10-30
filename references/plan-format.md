# Plan format

The plan is one JSON file; `scripts/plan.py` draws both pictures from it. Grow it level by
level: parts first (the simple version), then each part's `steps` (the full system). See
`examples/instagram-plan.json` for a complete plan.

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
- `scripts/plan.py` prints each guess and how many questions are left, plus any layout problem
  (overlaps, arrows through boxes, labels on boxes). Fix the plan until there are none.
