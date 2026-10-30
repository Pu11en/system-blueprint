#!/usr/bin/env python3
"""Build .excalidraw diagrams from a JSON spec.

    python diagram.py map spec.json [out.excalidraw]
    python diagram.py blueprint spec.json [out.excalidraw]
    python diagram.py flow spec.json [out.excalidraw]

map: the whole system as one drawing read top to bottom: the simple version (every part,
  placed by who owns it), then the full system (the same map with each part's steps).
blueprint: a service blueprint (phases over time x lanes from visible to hidden).
flow: a BPMN-style flow (straight normal path, failure branches below, interrupts above).
See references/spec-format.md for the JSON fields. Standard library only.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

KINDS = {  # kind: (fill, stroke)
    "person": ("#fed7aa", "#c2410c"),
    "frontstage": ("#a7f3d0", "#047857"),
    "system": ("#93c5fd", "#1e3a5f"),
    "ai": ("#ddd6fe", "#6d28d9"),
    "support": ("#dbeafe", "#1e40af"),
    "decision": ("#fef3c7", "#b45309"),
    "error": ("#fecaca", "#b91c1c"),
    "note": ("#f1f5f9", "#64748b"),
    "end": ("#a7f3d0", "#047857"),
}
KIND_LABELS = {
    "person": "person", "frontstage": "what they see", "system": "system step",
    "ai": "AI step", "support": "storage / support", "decision": "yes/no check",
    "error": "failure / problem #", "note": "side note", "end": "good end",
}
TITLE, SUB, BODY, ONLIGHT, RED, NAVY = (
    "#1e40af", "#3b82f6", "#64748b", "#374151", "#b91c1c", "#1e3a5f")


class Canvas:
    """Collects Excalidraw elements; every element gets a readable string id."""

    def __init__(self) -> None:
        self.els: list[dict] = []
        self.by_id: dict[str, dict] = {}
        self.seed = 1000

    def _base(self, kind: str, eid: str, x: float, y: float, w: float, h: float) -> dict:
        self.seed += 1
        e = {
            "type": kind, "id": eid, "x": x, "y": y, "width": w, "height": h,
            "strokeColor": NAVY, "backgroundColor": "transparent", "fillStyle": "solid",
            "strokeWidth": 2, "strokeStyle": "solid", "roughness": 0, "opacity": 100,
            "angle": 0, "seed": self.seed, "version": 1, "versionNonce": self.seed * 7,
            "isDeleted": False, "groupIds": [], "boundElements": None, "link": None,
            "locked": False,
        }
        self.els.append(e)
        self.by_id[eid] = e
        return e

    @staticmethod
    def size(s: str, fs: int) -> tuple[float, float]:
        lines = s.split("\n")
        return max(len(line) for line in lines) * fs * 0.6, len(lines) * fs * 1.25

    def text(self, eid: str, x: float, y: float, s: str, fs: int = 16, color: str = BODY,
             container: str | None = None, align: str = "left") -> dict:
        w, h = self.size(s, fs)
        e = self._base("text", eid, x, y, w, h)
        e.update({
            "text": s, "originalText": s, "fontSize": fs, "fontFamily": 3,
            "textAlign": align, "verticalAlign": "middle" if container else "top",
            "strokeColor": color, "strokeWidth": 1, "containerId": container,
            "lineHeight": 1.25,
        })
        return e

    def shape(self, eid: str, x: float, y: float, w: float, h: float, label: str, kind: str,
              form: str = "rectangle", fs: int = 14, dashed: bool = False) -> dict:
        fill, stroke = KINDS[kind]
        e = self._base(form, eid, x, y, w, h)
        e.update({"strokeColor": stroke, "backgroundColor": fill})
        if form == "rectangle":
            e["roundness"] = {"type": 3}
        if dashed:
            e["strokeStyle"] = "dashed"
        if label:
            tw, th = self.size(label, fs)
            self.text(f"{eid}_t", x + (w - tw) / 2, y + (h - th) / 2, label, fs, ONLIGHT,
                      eid, "center")
            e["boundElements"] = [{"id": f"{eid}_t", "type": "text"}]
        return e

    def anchor(self, eid: str, side: str) -> tuple[float, float]:
        e = self.by_id[eid]
        x, y, w, h = e["x"], e["y"], e["width"], e["height"]
        return {"r": (x + w, y + h / 2), "l": (x, y + h / 2),
                "t": (x + w / 2, y), "b": (x + w / 2, y + h)}[side]

    def arrow(self, eid: str, src: str, dst: str, sides: str = "rl",
              via: list[tuple[float, float]] | None = None, label: str = "",
              color: str | None = None, dashed: bool = False, lx: float = 8,
              ly: float = -22) -> None:
        (x1, y1), (x2, y2) = self.anchor(src, sides[0]), self.anchor(dst, sides[1])
        pts = [(x1, y1), *(via or []), (x2, y2)]
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        e = self._base("arrow", eid, x1, y1, max(xs) - min(xs), max(ys) - min(ys))
        e.update({
            "strokeColor": color or self.by_id[src]["strokeColor"],
            "points": [[px - x1, py - y1] for px, py in pts],
            "startBinding": {"elementId": src, "focus": 0, "gap": 4},
            "endBinding": {"elementId": dst, "focus": 0, "gap": 4},
            "startArrowhead": None, "endArrowhead": "arrow",
        })
        if dashed:
            e["strokeStyle"] = "dashed"
        for end in (self.by_id[src], self.by_id[dst]):
            end["boundElements"] = (end["boundElements"] or []) + [{"id": eid, "type": "arrow"}]
        if label:
            mid = len(pts) // 2
            (ax, ay), (bx, by) = pts[mid - 1], pts[mid]
            self.text(f"{eid}_l", (ax + bx) / 2 + lx, (ay + by) / 2 + ly, label, 13, ONLIGHT)

    def line(self, eid: str, x: float, y: float, w: float, dashed: bool = False,
             width: int = 2) -> None:
        e = self._base("line", eid, x, y, w, 0)
        e.update({"points": [[0, 0], [w, 0]], "strokeWidth": width})
        if dashed:
            e["strokeStyle"] = "dashed"

    def flag(self, eid: str, x: float, y: float, n: object) -> None:
        self.shape(eid, x, y, 34, 34, str(n), "error", "ellipse", fs=15)

    def key(self, x: float, y: float, kinds: list[str], note: str = "") -> None:
        self.text("key_h", 40, y, "KEY", 16, SUB)
        for j, kind in enumerate(kinds):
            form = "diamond" if kind == "decision" else "rectangle"
            self.shape(f"key{j}", x + j * 280, y - 4, 32, 26, "", kind, form)
            self.text(f"keyt{j}", x + j * 280 + 42, y, KIND_LABELS[kind], 14, BODY)
        if note:
            self.text("key_note", x, y + 40, note, 13, BODY)

    def header(self, spec: dict) -> None:
        self.text("title", 40, 24, spec["title"], 30, TITLE)
        if spec.get("subtitle"):
            self.text("subtitle", 40, 66, spec["subtitle"], 16, BODY)

    def doc(self) -> dict:
        return {"type": "excalidraw", "version": 2, "source": "https://excalidraw.com",
                "elements": self.els,
                "appState": {"viewBackgroundColor": "#ffffff", "gridSize": None}, "files": {}}


def build_blueprint(spec: dict) -> Canvas:
    cv = Canvas()
    cv.header(spec)
    x0, col, box_w = 300, spec.get("column_width", 420), spec.get("column_width", 420) - 60
    lane_h, gap = spec.get("lane_height", 100), 60
    phases, lanes = spec["phases"], spec["lanes"]
    width = x0 + len(phases) * col - 40

    for i, ph in enumerate(phases):
        cv.text(f"ph{i}", x0 + i * col, 120, ph["name"], 19, TITLE)
        if ph.get("time"):
            cv.text(f"tm{i}", x0 + i * col, 160, ph["time"], 15, BODY)
    if any(ph.get("time") for ph in phases):
        cv.text("time_h", 40, 160, "TIME", 16, SUB)

    lane_y: dict[str, float] = {}
    y = 230
    for lane in lanes:
        lane_y[lane["key"]] = y
        cv.text(f"lane_{lane['key']}", 40, y + 22, lane["label"], 16, TITLE)
        for i, ph in enumerate(phases):
            cell = ph.get("cells", {}).get(lane["key"])
            if cell:
                cv.shape(f"{lane['key']}{i}", x0 + i * col, y, box_w, lane_h, cell,
                         lane["kind"])
        line = lane.get("line_below")
        if line:
            ly = y + lane_h + gap / 2
            style = line.get("style", "dashed")
            cv.line(f"line_{lane['key']}", 40, ly, width, dashed=style == "dashed",
                    width=3 if style == "solid" else 2)
            cv.text(f"line_{lane['key']}_t", 40, ly - 20, line["label"], 12, BODY)
        y += lane_h + gap

    order = [lane["key"] for lane in lanes]
    first = order[0]
    if spec.get("connect_first_lane", True):
        for i in range(len(phases) - 1):
            a, b = f"{first}{i}", f"{first}{i + 1}"
            if a in cv.by_id and b in cv.by_id:
                cv.arrow(f"next{i}", a, b, "rl")
    for n, h in enumerate(spec.get("handoffs", [])):
        a, b = f"{h['from']}{h['phase']}", f"{h['to']}{h['phase']}"
        i, j = order.index(h["from"]), order.index(h["to"])
        between = order[min(i, j) + 1:max(i, j)]
        if any(f"{k}{h['phase']}" in cv.by_id for k in between):
            # A box sits in the way: run down the gutter to the right of the column.
            (_, ay), (_, by) = cv.anchor(a, "r"), cv.anchor(b, "r")
            gx = x0 + h["phase"] * col + box_w + 22
            cv.arrow(f"hand{n}", a, b, "rr", via=[(gx, ay), (gx, by)],
                     dashed=h.get("dashed", False))
            if h.get("label"):  # in the empty gap between lanes, just inside the gutter
                lw, _ = cv.size(h["label"], 13)
                gap_y = ay + lane_h / 2 + 8 if i < j else ay - lane_h / 2 - 26
                cv.text(f"hand{n}_l", gx - lw - 8, gap_y, h["label"], 13, ONLIGHT)
            continue
        cv.arrow(f"hand{n}", a, b, "bt" if i < j else "tb", label=h.get("label", ""),
                 lx=10, ly=4, dashed=h.get("dashed", False))

    if spec.get("problems"):
        cv.text("pain_h", 40, y + 10, "PROBLEMS", 16, RED)
        for n, p in enumerate(spec["problems"]):
            px = x0 + p["phase"] * col
            cv.flag(f"pf{n}", px, y + 5, p.get("n", n + 1))
            cv.text(f"pt{n}", px + 44, y + 5, p["text"], 14, RED)
        y += 90
    kinds = list(dict.fromkeys(lane["kind"] for lane in lanes))
    if spec.get("problems"):
        kinds.append("error")
    cv.key(x0, y + 20, kinds, "Arrow labels say what travels between steps. "
           "Boxes in one column happen at the same stage.")
    return cv


def build_flow(spec: dict) -> Canvas:
    cv = Canvas()
    cv.header(spec)
    mid = 390
    sizes = {"start": (140, 80), "end": (160, 80), "decision": (180, 130),
             "step": (210, 90), "fail": (210, 100), "note": (210, 90)}
    main, index = spec["main"], {}
    x = 40
    for i, node in enumerate(main):
        t = node.get("type", "step")
        w, h = sizes[t]
        kind = {"start": "person", "end": "end", "decision": "decision"}.get(
            t, node.get("kind", "system"))
        form = "ellipse" if t in ("start", "end") else "diamond" if t == "decision" else "rectangle"
        cv.shape(node["id"], x, mid - h / 2, w, h, node["text"], kind, form, fs=13)
        index[node["id"]] = i
        x += w + 70
    cv.text("happy", 40, mid - 130, "NORMAL PATH", 16, SUB)
    for i in range(len(main) - 1):
        a = main[i]
        cv.arrow(f"main{i}", a["id"], main[i + 1]["id"], "rl", label=a.get("next_label", ""),
                 color=NAVY, lx=-10)

    branches = spec.get("branches", [])
    if branches:
        cv.text("side", 40, mid + 150, "WHEN SOMETHING\nGOES WRONG", 16, RED)
    depth_at: dict[int, int] = {}
    low = mid + 170
    for n, br in enumerate(sorted(branches, key=lambda b: index[b["from"]])):
        s = index[br["from"]]
        depth = depth_at.get(s - 1, 0) + 1 if depth_at.get(s - 1, 0) < 3 else 1
        depth_at[s] = depth
        t = br.get("type", "step")
        w, h = sizes[t]
        src = cv.by_id[br["from"]]
        bx, by = src["x"] + src["width"] / 2 - w / 2, low + (depth - 1) * 150
        kind = {"fail": "error", "note": "note"}.get(t, br.get("kind", "system"))
        form = "ellipse" if t == "fail" else "rectangle"
        bid = br.get("id", f"br{n}")
        cv.shape(bid, bx, by, w, h, br["text"], kind, form, fs=13,
                 dashed=br.get("dashed", False))
        color = RED if t in ("fail", "note") else "#b45309"
        cv.arrow(f"{bid}_in", br["from"], bid, "bt", label=br.get("label", ""), lx=8,
                 ly=-8 if depth == 1 else -30, color=color, dashed=br.get("dashed", False))
        if "to" in br:
            tgt = cv.by_id[br["to"]]
            ti, cy = index[br["to"]], by + h / 2
            if ti == s + 1:  # rejoin the main line just before the next node
                gx = tgt["x"] - 25
                cv.arrow(f"{bid}_out", bid, br["to"], "rl", via=[(gx, cy), (gx, mid)],
                         color=NAVY, dashed=t == "fail")
            elif ti > s:  # skip ahead: come up under the target
                tx = tgt["x"] + tgt["width"] / 2
                cv.arrow(f"{bid}_out", bid, br["to"], "rb", via=[(tx, cy)], color=NAVY,
                         dashed=t == "fail")
            else:  # loop back
                tx = tgt["x"] + tgt["width"] / 2
                cv.arrow(f"{bid}_out", bid, br["to"], "lb", via=[(tx, cy)], color=NAVY,
                         dashed=t == "fail")

    for n, ev in enumerate(spec.get("interrupts", [])):
        tgt = cv.by_id[ev["into"]]
        ex = tgt["x"] + tgt["width"] / 2 - 125
        cv.shape(f"ev{n}", ex, mid - 240, 250, 70, ev["text"], "error", "ellipse", fs=13,
                 dashed=True)
        if ev.get("note"):
            cv.text(f"ev{n}_n", ex + 270, mid - 232, ev["note"], 13, BODY)
        cv.arrow(f"ev{n}_a", f"ev{n}", ev["into"], "bt", label=ev.get("label", ""), lx=8,
                 ly=-10, color=RED, dashed=True)

    for n, p in enumerate(spec.get("problems", [])):
        node = cv.by_id[p["on"]]
        cv.flag(f"pf{n}", node["x"] + node["width"] - 10, node["y"] - 20, p["n"])

    deepest = max(depth_at.values(), default=0)
    kinds = ["person", "decision", "system", "ai", "support", "end", "error"]
    used = {e.get("backgroundColor") for e in cv.els}
    kinds = [k for k in kinds if KINDS[k][0] in used]
    cv.key(200, low + max(deepest, 1) * 150 + 40, kinds,
           "Dashed = rare or side path. Red circles with numbers = known problems.")
    return cv


# ---- map ---------------------------------------------------------------------------------
# Tested over two days of planning a real two-person system with its non-technical owner.
# What worked: one drawing, top to bottom; every part placed by who owns it; the simple
# version first, the full system under it; built / next build / later visibly different;
# guesses yellow with the number of the question that settles them. See map-method.md.

WHO_PALETTE = [("#dbeafe", "#2563eb"), ("#ddd6fe", "#6d28d9"), ("#dcfce7", "#16a34a"),
               ("#fed7aa", "#c2410c"), ("#e2e8f0", "#475569"), ("#fce7f3", "#be185d")]
LATER = ("#f1f5f9", "#94a3b8")  # fill, line and words: not in this build
GUESS = ("#fef9c3", "#ca8a04")  # a guess, settled by the numbered question
INK = "#1e1e1e"
CW = 0.6  # Cascadia Code: every character is 0.6 em wide


def wrap(text: str, fs: int, width: float) -> str:
    """Break words into lines that fit width; existing line breaks are kept."""
    out = []
    for para in text.split("\n"):
        line = ""
        for word in para.split():
            trial = f"{line} {word}".strip()
            if line and len(trial) * fs * CW > width:
                out.append(line)
                line = word
            else:
                line = trial
        out.append(line)
    return "\n".join(out)


def build_map(spec: dict) -> Canvas:
    cv = Canvas()
    W = spec.get("width", 1160)
    who = {}
    for n, (key, w) in enumerate(spec.get("who", {}).items()):
        fill, stroke = WHO_PALETTE[n % len(WHO_PALETTE)]
        who[key] = (w.get("fill", fill), w.get("stroke", stroke), w.get("label", key))
    guesses: dict[int, list[str]] = {}

    def look(status: str, w: str) -> tuple[str, str, str, str]:
        """fill, stroke, words, stroke style for a box of this status, done by w."""
        fill, stroke, _ = who[w]
        if status == "later":
            return LATER[0], LATER[1], LATER[1], "dotted"
        if status == "guess":
            return GUESS[0], GUESS[1], INK, "solid"
        return fill, stroke, INK, "dashed" if status == "next" else "solid"

    def box(eid, x, y, w, h, text, fs, fill, stroke, color, style, align="center",
            valign="middle", pad=12):
        e = cv._base("rectangle", eid, x, y, w, h)
        e.update({"strokeColor": stroke, "backgroundColor": fill, "strokeStyle": style,
                  "roundness": {"type": 3}})
        if text:
            tw, th = cv.size(text, fs)
            tx = x + (w - tw) / 2 if align == "center" else x + pad
            ty = y + (h - th) / 2 if valign == "middle" else y + pad
            t = cv.text(f"{eid}_t", tx, ty, text, fs, color, eid, align)
            t["verticalAlign"] = valign
            e["boundElements"] = [{"id": f"{eid}_t", "type": "text"}]
        return e

    def badge(eid, owner, n):
        e = cv.by_id[owner]
        cv.shape(eid, e["x"] + e["width"] - 30, e["y"] - 12, 34, 34, str(n), "decision",
                 "ellipse", fs=16)
        cv.by_id[eid].update({"backgroundColor": "#f59e0b", "strokeColor": GUESS[1]})

    # Header and key: the key says what every look means, so nothing needs explaining.
    cv.text("title", 40, 24, spec["title"], 30, TITLE)
    y = 70
    if spec.get("subtitle"):
        cv.text("subtitle", 40, y, spec["subtitle"], 16, BODY)
        y += 34
    kx = 40
    for k, (fill, stroke, label) in who.items():
        cv._base("rectangle", f"key_{k}", kx, y, 26, 22).update(
            {"strokeColor": stroke, "backgroundColor": fill, "roundness": {"type": 3}})
        t = cv.text(f"key_{k}_t", kx + 34, y + 1, label, 16, INK)
        kx += 34 + t["width"] + 30
    y += 34
    cv.text("key_status", 40, y, "Solid: built and working.  Dashed: the next build.  "
            "Grey: later, not in this build.", 16, BODY)
    y += 26
    cv.text("key_guess", 40, y, "Yellow: a guess. Its number is the question that settles it.",
            16, BODY)
    y += 60

    def level(prefix: str, heading: str, y: float, full: bool, width: float) -> float:
        cv.text(f"{prefix}head", 40, y, heading, 24, TITLE)
        y += 50
        parts: dict[str, dict] = {}
        band_of: dict[str, int] = {}
        for bi, band in enumerate(spec["bands"]):
            top = y
            ps = band["parts"]
            # Neighbours with an arrow between them get room for its label.
            gaps = []
            for left, right in zip(ps, ps[1:]):
                words = [ln.get("label", "") for ln in spec.get("links", [])
                         if {ln["from"], ln["to"]} == {left["id"], right["id"]}]
                gaps.append(max([40] + [cv.size(w, 16)[0] + 50 for w in words]))
            total = sum(p.get("weight", 1) for p in ps)
            free = width - 40 - sum(gaps)
            # Heights first: every part in a band is as tall as the tallest.
            plans = []
            for p in ps:
                pw = free * p.get("weight", 1) / total
                name = wrap(p["name"], 20, pw - 24)
                sub = wrap(p.get("sub", ""), 16, pw - 24) if p.get("sub") else ""
                head = cv.size(name, 20)[1] + (cv.size(sub, 16)[1] + 4 if sub else 0) + 24
                steps = []
                if full:
                    for st in p.get("steps", []):
                        txt = wrap(st["text"], 16, pw - 48)
                        steps.append((st, txt, cv.size(txt, 16)[1] + 20))
                h = head + sum(sh + 28 for _, _, sh in steps) + (8 if steps else 0)
                plans.append((p, pw, name, sub, head, steps, h))
            bh = max(pl[-1] for pl in plans)
            band_box = cv._base("rectangle", f"{prefix}band{bi}", 20, top, width, bh + 56)
            band_box.update({"strokeColor": "#e2e8f0", "backgroundColor": "#f8fafc",
                             "strokeWidth": 1})
            cv.text(f"{prefix}band{bi}_t", 36, top + 8, band["name"], 16, SUB)
            x = 40
            for n, (p, pw, name, sub, head, steps, h) in enumerate(plans):
                pid = prefix + p["id"]
                status = p.get("status", "built")
                fill, stroke, color, style = look(status, p["who"])
                if full and steps:
                    fill = "#ffffff" if status not in ("later", "guess") else fill
                label = name + (f"\n{sub}" if sub else "")
                e = box(pid, x, top + 40, pw, bh, label, 20 if not sub else 18, fill, stroke,
                        color, style, align="left" if full and steps else "center",
                        valign="top" if full and steps else "middle")
                if status == "guess":
                    guesses.setdefault(p["guess"], []).append(p["name"])
                    badge(f"{pid}_q", pid, p["guess"])
                sy = top + 40 + head
                prev = None
                for k, (st, txt, sh) in enumerate(steps):
                    sid = f"{pid}_s{k}"
                    sf, ss, sc, sst = look(st.get("status", status), st.get("who", p["who"]))
                    box(sid, x + 24, sy, pw - 48, sh, txt, 16, sf, ss, sc, sst)
                    if st.get("status") == "guess":
                        guesses.setdefault(st["guess"], []).append(st["text"])
                        badge(f"{sid}_q", sid, st["guess"])
                    if prev:
                        cv.arrow(f"{sid}_in", prev, sid, "bt", color=BODY)
                    prev, sy = sid, sy + sh + 28
                parts[p["id"]] = e
                band_of[p["id"]] = bi
                x += pw + (gaps[n] if n < len(gaps) else 0)
            y = top + bh + 56 + 70  # the gap holds the arrow labels

        # Links between parts: down (or up) through the gap above the receiving band.
        ends: dict[tuple[str, str], list[int]] = {}
        links = spec.get("links", [])
        for n, ln in enumerate(links):
            a, b = band_of[ln["from"]], band_of[ln["to"]]
            sa, sb = ("b", "t") if a < b else ("t", "b") if a > b else ("r", "l")
            ends.setdefault((ln["from"], sa), []).append(n)
            ends.setdefault((ln["to"], sb), []).append(n)

        def spot(pid: str, side: str, n: int) -> tuple[float, float]:
            e, group = parts[pid], ends[(pid, side)]
            # spread several arrows along one side, ordered by where they go
            f = (group.index(n) + 1) / (len(group) + 1)
            if side in "tb":
                return e["x"] + e["width"] * f, e["y"] + (e["height"] if side == "b" else 0)
            return e["x"] + (e["width"] if side == "r" else 0), e["y"] + e["height"] * f

        for (pid, side), group in ends.items():  # order by the other end's position
            def other_x(n, pid=pid):
                ln = links[n]
                o = parts[ln["to"] if ln["from"] == pid else ln["from"]]
                return o["x"] + o["width"] / 2
            group.sort(key=other_x)

        for n, ln in enumerate(links):
            a, b = band_of[ln["from"]], band_of[ln["to"]]
            sa, sb = ("b", "t") if a < b else ("t", "b") if a > b else ("r", "l")
            (x1, y1), (x2, y2) = spot(ln["from"], sa, n), spot(ln["to"], sb, n)
            if sa == "r" or abs(x1 - x2) < 2:
                pts = [(x1, y1), (x2, y2)]
            else:  # elbow in the gap next to the receiving band
                tgt = parts[ln["to"]]
                my = tgt["y"] - 60 if a < b else tgt["y"] + tgt["height"] + 46
                pts = [(x1, y1), (x1, my), (x2, my), (x2, y2)]
            status = ln.get("status", "built")
            color = LATER[1] if status == "later" else NAVY
            aid = f"{prefix}link{n}"
            e = cv._base("arrow", aid, x1, y1, abs(x2 - x1), abs(y2 - y1))
            e.update({"strokeColor": color, "points": [[px - x1, py - y1] for px, py in pts],
                      "strokeStyle": {"next": "dashed", "later": "dotted"}.get(status, "solid"),
                      "startBinding": {"elementId": prefix + ln["from"], "focus": 0, "gap": 4},
                      "endBinding": {"elementId": prefix + ln["to"], "focus": 0, "gap": 4},
                      "startArrowhead": None, "endArrowhead": "arrow", "roundness": None})
            for pid in (ln["from"], ln["to"]):
                parts[pid]["boundElements"] = (parts[pid]["boundElements"] or []) + [
                    {"id": aid, "type": "arrow"}]
            if ln.get("label"):
                # Excalidraw puts an arrow's label on the middle of its line
                k = len(pts) // 2
                (ax, ay), (bx, by) = (pts[k], pts[k]) if len(pts) % 2 else (pts[k - 1], pts[k])
                tw, th = cv.size(ln["label"], 16)
                t = cv.text(f"{aid}_t", (ax + bx) / 2 - tw / 2, (ay + by) / 2 - th / 2,
                            ln["label"], 16, color if status == "later" else INK, aid, "center")
                e["boundElements"] = [{"id": t["id"], "type": "text"}]

        # A band name an arrow runs through moves to the band's right end.
        def crossed(t):
            for a in cv.els:
                if a["type"] != "arrow" or not a["id"].startswith(prefix + "link"):
                    continue
                pts = [(a["x"] + px, a["y"] + py) for px, py in a["points"]]
                for (ax, ay), (bx, by) in zip(pts, pts[1:]):
                    if (min(ax, bx) < t["x"] + t["width"] and max(ax, bx) > t["x"]
                            and min(ay, by) < t["y"] + t["height"] and max(ay, by) > t["y"]):
                        return True
            return False

        for bi in range(len(spec["bands"])):
            t = cv.by_id[f"{prefix}band{bi}_t"]
            if crossed(t):
                t["x"], t["textAlign"] = 20 + width - 16 - t["width"], "right"
                if crossed(t):
                    print(f"layout: an arrow runs through band name {spec['bands'][bi]['name']!r}")
        return y

    q = spec.get("questions")
    simple_w = W - 380 if q else W
    top = y
    y = level("s_", spec.get("simple_heading", "The simple version"), y, False, simple_w)
    if q:  # questions only someone else can answer, big, beside the simple version
        qx = simple_w + 40
        cv.text("q_head", qx, top + 50, wrap(q["title"], 24, W - qx), 24, RED)
        qy = top + 50 + cv.size(wrap(q["title"], 24, W - qx), 24)[1] + 20
        for n, item in enumerate(q["items"], 1):
            t = cv.text(f"q{n}", qx, qy, wrap(f"{n}. {item}", 22, W - qx), 22, INK)
            qy += t["height"] + 18
        y = max(y, qy + 40)
    y += 20
    level("f_", spec.get("full_heading", "The full system, step by step"), y, True, W)

    left = sorted(guesses)
    if left and left != list(range(1, len(left) + 1)):
        print(f"warning: guess numbers should run 1..{len(left)}, got {left}")
    for n in left:
        print(f"guess {n}: {' / '.join(dict.fromkeys(guesses[n]))}")
    print(f"{len(left)} question(s) left")
    for problem in check(cv.els):
        print("layout:", problem)
    return cv


def check(els: list[dict]) -> list[str]:
    """Boxes that overlap and arrows that run through boxes they don't connect."""
    boxes = [e for e in els if e["type"] in ("rectangle", "ellipse", "diamond")
             and "band" not in e["id"] and not e["id"].startswith("key")]

    def inside(a, b):
        return (b["x"] <= a["x"] and b["y"] <= a["y"] and a["x"] + a["width"] <= b["x"] + b["width"]
                and a["y"] + a["height"] <= b["y"] + b["height"])

    def hit(a, b):
        return not (a["x"] + a["width"] <= b["x"] or b["x"] + b["width"] <= a["x"]
                    or a["y"] + a["height"] <= b["y"] or b["y"] + b["height"] <= a["y"])

    out = []
    for i, a in enumerate(boxes):
        for b in boxes[i + 1:]:
            if hit(a, b) and not inside(a, b) and not inside(b, a) and not (
                    a["id"].endswith("_q") or b["id"].endswith("_q")):
                out.append(f"{a['id']} overlaps {b['id']}")
    for e in els:
        if e["type"] != "arrow":
            continue
        own = {e["startBinding"]["elementId"], e["endBinding"]["elementId"]}
        pts = [(e["x"] + px, e["y"] + py) for px, py in e["points"]]
        for b in boxes:
            if b["id"] in own or any(b["id"].startswith(o + "_") for o in own):
                continue
            if any(o.startswith(b["id"] + "_") for o in own):
                continue  # a step's arrow inside its own part
            x0, y0, x1, y1 = b["x"] + 3, b["y"] + 3, b["x"] + b["width"] - 3, b["y"] + b["height"] - 3
            for (ax, ay), (bx, by) in zip(pts, pts[1:]):
                if (min(ax, bx) < x1 and max(ax, bx) > x0 and min(ay, by) < y1
                        and max(ay, by) > y0):
                    out.append(f"arrow {e['id']} runs through {b['id']}")
                    break
    for t in els:  # arrow labels must sit in open space
        if t["type"] != "text" or not str(t.get("containerId", "")).count("link"):
            continue
        for b in boxes:
            if hit(t, b):
                out.append(f"label {t['id']} sits on {b['id']}")
    return out


def main() -> None:
    if len(sys.argv) < 3 or sys.argv[1] not in ("map", "blueprint", "flow"):
        sys.exit(__doc__)
    spec_path = Path(sys.argv[2])
    out = Path(sys.argv[3]) if len(sys.argv) > 3 else spec_path.with_suffix(".excalidraw")
    spec = json.loads(spec_path.read_text())
    cv = {"map": build_map, "blueprint": build_blueprint, "flow": build_flow}[sys.argv[1]](spec)
    out.write_text(json.dumps(cv.doc(), indent=1))
    print(f"wrote {out} ({len(cv.els)} elements)")


if __name__ == "__main__":
    main()
