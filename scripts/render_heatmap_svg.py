from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from xml.sax.saxutils import escape

IN = Path("data/contributions.json")
OUT = Path("contrib-heatmap.svg")
W, H = 900, 200
CELL, GAP = 11, 4
GRID_X, GRID_Y = 42, 44

# Level 0 remains semantically "no contribution", but uses a subtle green tint.
PALETTE = ["#102018", "#0e4429", "#006d32", "#26a641", "#39d353"]
PULSE = ["#1c5a3b", "#238653", "#2db968", "#48e07c", "#7dff9b"]


def main():
    data = json.loads(IN.read_text(encoding="utf-8"))
    days = sorted(data["days"], key=lambda d: d["date"])
    first = date.fromisoformat(days[0]["date"])
    sunday_index = (first.weekday() + 1) % 7

    cells = []
    for i, d in enumerate(days):
        pos = sunday_index + i
        col, row = divmod(pos, 7)
        x = GRID_X + col * (CELL + GAP)
        y = GRID_Y + row * (CELL + GAP)
        level = max(0, min(4, int(d.get("level", 0))))
        delay = (col * 0.045) + (row * 0.07)
        base = PALETTE[level]
        hot = PULSE[level]
        title = f'{d["count"]} public contributions on {d["date"]}'
        cells.append(
            f'<rect class="cell level-{level}" x="{x}" y="{y}" '
            f'width="{CELL}" height="{CELL}" rx="2" '
            f'style="--delay:{delay:.2f}s;--base:{base};--hot:{hot}" fill="{base}">'
            f'<title>{escape(title)}</title></rect>'
        )

    footer = (
        f'{data.get("total", 0):,} public contributions · '
        f'current streak {data.get("current_streak", 0)}d · '
        f'longest {data.get("longest_streak", 0)}d'
    )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<style>
  text {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }}

  .cell {{
    opacity: 0;
    transform-box: fill-box;
    transform-origin: center;
    animation:
      boot .35s ease-out var(--delay) forwards,
      terminalPulse 5.2s ease-in-out calc(var(--delay) + .4s) infinite;
  }}

  .level-1, .level-2, .level-3, .level-4 {{
    filter: drop-shadow(0 0 2px rgba(57,211,83,.28));
  }}

  @keyframes boot {{
    from {{ opacity:0; transform:scale(.45) translateY(-4px); }}
    to {{ opacity:1; transform:scale(1) translateY(0); }}
  }}

  @keyframes terminalPulse {{
    0%, 18%, 100% {{ fill:var(--base); }}
    8% {{ fill:var(--hot); }}
    12% {{ fill:#39d353; }}
  }}

  .scan {{ animation:scan 3.8s linear infinite; }}
  @keyframes scan {{
    0% {{ transform:translateX(-120px); opacity:0; }}
    10% {{ opacity:.28; }}
    90% {{ opacity:.28; }}
    100% {{ transform:translateX(850px); opacity:0; }}
  }}

  .status {{ animation:blink 1.2s steps(2,end) infinite; }}
  @keyframes blink {{ 50% {{ opacity:.35; }} }}
</style>

<defs>
  <linearGradient id="scanGlow" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="#39d353" stop-opacity="0"/>
    <stop offset="50%" stop-color="#39d353" stop-opacity=".9"/>
    <stop offset="100%" stop-color="#39d353" stop-opacity="0"/>
  </linearGradient>
</defs>

<rect width="100%" height="100%" rx="14" fill="#0d1117" stroke="#30363d"/>
<circle class="status" cx="842" cy="22" r="4" fill="#39d353"/>
<text x="28" y="26" fill="#8b949e" font-size="12">Pedrssa / public contributions · live</text>

<g>
{''.join(cells)}
<rect class="scan" x="34" y="38" width="84" height="116" fill="url(#scanGlow)" opacity="0"/>
</g>

<text x="28" y="181" fill="#8b949e" font-size="11">{escape(footer)}</text>
</svg>'''
    OUT.write_text(svg, encoding="utf-8")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
