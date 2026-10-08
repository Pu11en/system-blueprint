#!/usr/bin/env python3
"""Build .excalidraw diagrams from a JSON spec.

    python diagram.py blueprint spec.json [out.excalidraw]
    python diagram.py flow spec.json [out.excalidraw]

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


def main() -> None:
    if len(sys.argv) < 3 or sys.argv[1] not in ("blueprint", "flow"):
        sys.exit(__doc__)
    spec_path = Path(sys.argv[2])
    out = Path(sys.argv[3]) if len(sys.argv) > 3 else spec_path.with_suffix(".excalidraw")
    spec = json.loads(spec_path.read_text())
    cv = build_blueprint(spec) if sys.argv[1] == "blueprint" else build_flow(spec)
    out.write_text(json.dumps(cv.doc(), indent=1))
    print(f"wrote {out} ({len(cv.els)} elements)")


if __name__ == "__main__":
    main()
