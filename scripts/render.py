# /// script
# requires-python = ">=3.10"
# dependencies = ["playwright>=1.40"]
# ///
"""Render a .excalidraw file to PNG so you can look at it before showing anyone.

    uv run render.py diagram.excalidraw [out.png]

First run only: uv run --with playwright playwright install chromium
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

# Pinned: the unpinned esm.sh build has pulled in a missing dependency before.
LIB = "https://esm.sh/@excalidraw/excalidraw@0.18.0?bundle&deps=@braintree/sanitize-url@6.0.4"
PAGE = f"""<!doctype html><html><head><meta charset="utf-8"></head>
<body style="margin:0;background:#fff"><div id="out"></div>
<script type="module">
import {{ exportToSvg }} from "{LIB}";
window.render = async (scene) => {{
  const svg = await exportToSvg({{
    elements: scene.elements,
    appState: {{ ...scene.appState, exportBackground: true, exportPadding: 40 }},
    files: scene.files || {{}},
  }});
  document.getElementById("out").appendChild(svg);
  const r = svg.getBoundingClientRect();
  return [Math.ceil(r.width), Math.ceil(r.height)];
}};
window.ready = true;
</script></body></html>"""


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    src = Path(sys.argv[1])
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else src.with_suffix(".png")
    scene = json.loads(src.read_text())
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(device_scale_factor=2)
        page.set_content(PAGE)
        page.wait_for_function("window.ready === true", timeout=120_000)
        w, h = page.evaluate("scene => window.render(scene)", scene)
        page.set_viewport_size({"width": w, "height": h})
        page.locator("#out svg").screenshot(path=str(out))
        browser.close()
    print(out)


if __name__ == "__main__":
    main()
