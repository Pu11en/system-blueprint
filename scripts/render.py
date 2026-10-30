# /// script
# requires-python = ">=3.10"
# dependencies = ["playwright>=1.40"]
# ///
"""Render a picture to PNG so you can look at it before showing anyone.

    uv run render.py plan.excalidraw [out.png]   # the whole drawing
    uv run render.py plan.md [out.png]           # its first Mermaid picture

First run only: uv run --with playwright playwright install chromium
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

# Pinned: the unpinned esm.sh build has pulled in a missing dependency before.
EXCALIDRAW = "https://esm.sh/@excalidraw/excalidraw@0.18.0?bundle&deps=@braintree/sanitize-url@6.0.4"
MERMAID = "https://esm.sh/mermaid@11.4.1"
PAGE = f"""<!doctype html><html><head><meta charset="utf-8"></head>
<body style="margin:0;background:#fff"><div id="out"></div>
<script type="module">
window.excalidraw = async (scene) => {{
  const {{ exportToSvg }} = await import("{EXCALIDRAW}");
  const svg = await exportToSvg({{
    elements: scene.elements,
    appState: {{ ...scene.appState, exportBackground: true, exportPadding: 40 }},
    files: scene.files || {{}},
  }});
  document.getElementById("out").appendChild(svg);
}};
window.mermaid = async (text) => {{
  const mermaid = (await import("{MERMAID}")).default;
  mermaid.initialize({{ startOnLoad: false }});
  const {{ svg }} = await mermaid.render("picture", text);
  document.getElementById("out").innerHTML = svg;
}};
window.ready = true;
</script></body></html>"""


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    src = Path(sys.argv[1])
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else src.with_suffix(".png")
    if src.suffix == ".md":
        blocks = re.findall(r"```mermaid\n(.*?)```", src.read_text(), re.S)
        if not blocks:
            sys.exit(f"no Mermaid picture in {src}")
        kind, data = "mermaid", blocks[0]
    else:
        kind, data = "excalidraw", json.loads(src.read_text())
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(device_scale_factor=2, viewport={"width": 1400, "height": 900})
        page.set_content(PAGE)
        page.wait_for_function("window.ready === true", timeout=120_000)
        page.evaluate(f"data => window.{kind}(data)", data)
        page.locator("#out svg").screenshot(path=str(out))
        browser.close()
    print(out)


if __name__ == "__main__":
    main()
