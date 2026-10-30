#!/usr/bin/env python3
"""Turn a plan (JSON) into pictures: the simple version, then the full system.

    python3 plan.py plan.json   # -> plan.excalidraw and plan.md

plan.excalidraw: one drawing read top to bottom, the simple version then the full system.
plan.md: the simple version as Mermaid, for a chat or a board beside it, plus the questions.
Prints every numbered guess, how many questions are left, and layout problems (overlaps,
arrows through boxes, labels on boxes).
See references/plan-format.md for the JSON fields. Standard library only.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

KINDS = {"decision": ("#fef3c7", "#b45309")}  # kind: (fill, stroke)
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

    def doc(self) -> dict:
        return {"type": "excalidraw", "version": 2, "source": "https://excalidraw.com",
                "elements": self.els,
                "appState": {"viewBackgroundColor": "#ffffff", "gridSize": None}, "files": {}}


# ---- the plan as pictures ------------------------------------------------------------------
# Tested over two days of planning a real two-person system with its non-technical owner.
# What worked: one picture, top to bottom; every part placed by who owns it; the simple
# version first, the full system under it; built / next build / later visibly different;
# guesses yellow with the number of the question that settles them. See SKILL.md.

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

    def look(status: str, w: str, guess: bool = False) -> tuple[str, str, str, str]:
        """fill, stroke, words, stroke style. One look, one meaning: colour is who does it,
        line style is when it gets built, yellow is a guess."""
        fill, stroke, _ = who[w]
        style = {"next": "dashed", "later": "dotted"}.get(status, "solid")
        if guess:
            return GUESS[0], GUESS[1], INK, style
        if status == "later":
            return LATER[0], LATER[1], LATER[1], style
        return fill, stroke, INK, style

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
    if spec.get("goal"):  # what the system is for, in the owner's words
        t = cv.text("goal", 40, y, wrap("Goal: " + spec["goal"], 20, W - 80), 20, INK)
        y += t["height"] + 14
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
    if any(it.get("changed") for it in items(spec)):
        y += 26
        cv.text("key_changed", 40, y, "Thick outline: changed since last time.", 16, BODY)
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
                fill, stroke, color, style = look(status, p["who"], "guess" in p)
                if full and steps:
                    fill = "#ffffff" if status != "later" and "guess" not in p else fill
                label = name + (f"\n{sub}" if sub else "")
                e = box(pid, x, top + 40, pw, bh, label, 20 if not sub else 18, fill, stroke,
                        color, style, align="left" if full and steps else "center",
                        valign="top" if full and steps else "middle")
                if p.get("changed"):
                    e["strokeWidth"] = 4
                if "guess" in p:
                    badge(f"{pid}_q", pid, p["guess"])
                sy = top + 40 + head
                prev = None
                for k, (st, txt, sh) in enumerate(steps):
                    sid = f"{pid}_s{k}"
                    sf, ss, sc, sst = look(st.get("status", status), st.get("who", p["who"]),
                                           "guess" in st)
                    se = box(sid, x + 24, sy, pw - 48, sh, txt, 16, sf, ss, sc, sst)
                    if st.get("changed"):
                        se["strokeWidth"] = 4
                    if "guess" in st:
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
            if ln.get("changed"):
                e["strokeWidth"] = 4
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
    # arrows crossing each other: the layout fault that hurts reading most
    segs = []
    for e in els:
        if e["type"] == "arrow" and "link" in e["id"]:
            pts = [(e["x"] + px, e["y"] + py) for px, py in e["points"]]
            segs.append((e["id"], list(zip(pts, pts[1:]))))

    def side(a, b, c):
        v = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
        return 0 if abs(v) < 1e-9 else (1 if v > 0 else -1)

    def cross(p1, p2, p3, p4):
        return (side(p1, p2, p3) * side(p1, p2, p4) < 0
                and side(p3, p4, p1) * side(p3, p4, p2) < 0)

    for i, (ia, sa) in enumerate(segs):
        for ib, sb in segs[i + 1:]:
            if any(cross(p, q, r, t) for p, q in sa for r, t in sb):
                out.append(f"arrows cross: {ia} and {ib}")
    return out


def colours(spec: dict) -> dict[str, tuple[str, str, str]]:
    """who key -> (fill, stroke, label)."""
    out = {}
    for n, (key, w) in enumerate(spec.get("who", {}).items()):
        fill, stroke = WHO_PALETTE[n % len(WHO_PALETTE)]
        out[key] = (w.get("fill", fill), w.get("stroke", stroke), w.get("label", key))
    return out


def items(spec: dict):
    """Every part, step and link in the plan."""
    for band in spec["bands"]:
        for p in band["parts"]:
            yield p
            yield from p.get("steps", [])
    yield from spec.get("links", [])


def normalise(spec: dict) -> None:
    """Older plans wrote status "guess"; a guess is now its own field, so it can also be
    built, next or later."""
    for it in items(spec):
        if it.get("status") == "guess":
            del it["status"]


def guesses(spec: dict) -> dict[int, list[str]]:
    """Question number -> the boxes it settles."""
    out: dict[int, list[str]] = {}
    for it in items(spec):
        if "guess" in it and "from" not in it:
            out.setdefault(it["guess"], []).append(it.get("name") or it.get("text"))
    return dict(sorted(out.items()))


def size_warnings(spec: dict) -> list[str]:
    """Limits from diagram research: a view people can take in at once."""
    out = []
    parts = [p for band in spec["bands"] for p in band["parts"]]
    if len(spec["bands"]) > 5:
        out.append(f"{len(spec['bands'])} rows; keep it to 3 to 5")
    if len(parts) > 9:
        out.append(f"{len(parts)} parts in the simple version; keep it to 9 (5 to 7 is best),"
                   " merge parts rather than shrink text")
    for p in parts:
        if len(p.get("steps", [])) > 7:
            out.append(f"{p['name']!r} has {len(p['steps'])} steps; keep it to 7, split the part")
    boxes = len(parts) + sum(len(p.get("steps", [])) for p in parts)
    if boxes > 50:
        out.append(f"{boxes} boxes in the full system; about 50 is the most people follow")
    if len(spec.get("who", {})) > 5:
        out.append(f"{len(spec['who'])} owner colours; keep it to 5")
    return out


CIRCLED = "①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳"


def mermaid(spec: dict) -> str:
    """The simple version as a Mermaid flowchart: one row per band, top to bottom.

    Only the simple version: with every step inside, Mermaid's automatic layout loses the
    row order and crosses arrows, so the full system is the hand-placed drawing."""
    who = colours(spec)

    def label(text: str, item: dict) -> str:
        if "guess" in item:
            n = item["guess"]
            text = f"{CIRCLED[n - 1] if n <= len(CIRCLED) else n} {text}"
        return '"' + text.replace('"', "#quot;").replace("\n", "<br/>") + '"'

    def style(item: dict) -> str:
        status = item.get("status", "built")
        fill, stroke, _ = who[item["who"]]
        color = INK
        if "guess" in item:
            fill, stroke = GUESS
        elif status == "later":
            fill, stroke, color = LATER[0], LATER[1], LATER[1]
        dash = {"next": ",stroke-dasharray:6 4", "later": ",stroke-dasharray:2 3"}.get(status, "")
        width = 4 if item.get("changed") else 2
        return f"fill:{fill},stroke:{stroke},color:{color},stroke-width:{width}px{dash}"

    lines, styles = ["flowchart TD"], []
    for bi, band in enumerate(spec["bands"]):
        lines.append(f'  subgraph band{bi}["{band["name"]}"]')
        for p in band["parts"]:
            name = p["name"] + (f"<br/>{p['sub']}" if p.get("sub") else "")
            lines.append(f"    {p['id']}[{label(name, p)}]")
            styles.append(f"  style {p['id']} {style(p)}")
        lines.append("  end")
        styles.append(f"  style band{bi} fill:#f8fafc,stroke:#e2e8f0")
    hops = 0  # Mermaid numbers every link in the order it is written
    if len(spec["bands"]) > 1:  # keeps the rows in order, top to bottom
        lines.append("  " + " ~~~ ".join(f"band{bi}" for bi in range(len(spec["bands"]))))
        hops = len(spec["bands"]) - 1
    for ln in spec.get("links", []):
        status = ln.get("status", "built")
        text = f'|"{ln["label"]}"|' if ln.get("label") else ""
        lines.append(f"  {ln['from']} {'-->' if status == 'built' else '-.->'}{text} {ln['to']}")
        css = [f"stroke:{LATER[1]},color:{LATER[1]}"] if status == "later" else []
        if ln.get("changed"):
            css.append("stroke-width:4px")
        if css:
            styles.append(f"  linkStyle {hops} {','.join(css)}")
        hops += 1
    return "\n".join(lines + styles)


def markdown(spec: dict, drawing: str) -> str:
    """The simple version for a chat or a board, the questions, and where the full system is."""
    who = colours(spec)
    parts = [f"# {spec['title']}", ""]
    if spec.get("goal"):
        parts += [f"Goal: {spec['goal']}", ""]
    parts += ["Colour = who does it: " + ", ".join(v[2] for v in who.values()) + ". "
              "Solid: built and working. Dashed: the next build. Grey: later, not in this build. "
              "Yellow with a number: a guess; the number is the question that settles it.", ""]
    parts += [f"## {spec.get('simple_heading', 'The simple version')}", "", "```mermaid",
              mermaid(spec), "```", ""]
    q = spec.get("questions")
    if q:
        parts += [f"## {q['title']}", ""] + [f"{n}. {item}" for n, item in
                                               enumerate(q["items"], 1)] + [""]
    parts += [f"## {spec.get('full_heading', 'The full system, step by step')}", "",
              f"In the drawing `{drawing}`, under the simple version.", ""]
    return "\n".join(parts)


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    spec_path = Path(sys.argv[1])
    spec = json.loads(spec_path.read_text())
    normalise(spec)
    for warning in size_warnings(spec):
        print("size:", warning)
    found = guesses(spec)
    if found and list(found) != list(range(1, len(found) + 1)):
        print(f"warning: guess numbers should run 1..{len(found)}, got {list(found)}")
    for n, boxes in found.items():
        print(f"guess {n}: {' / '.join(dict.fromkeys(boxes))}")
    print(f"{len(found)} question(s) left")
    out = spec_path.with_suffix(".excalidraw")
    cv = build_map(spec)
    out.write_text(json.dumps(cv.doc(), indent=1))
    print(f"wrote {out} ({len(cv.els)} elements)")
    md = spec_path.with_suffix(".md")
    md.write_text(markdown(spec, out.name))
    print(f"wrote {md}")

if __name__ == "__main__":
    main()
