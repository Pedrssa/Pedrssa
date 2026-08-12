from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from xml.sax.saxutils import escape

IN = Path("data/contributions.json")
OUT = Path("contrib-heatmap.svg")
W, H = 860, 190
CELL, GAP = 11, 4
GRID_X, GRID_Y = 40, 38
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]


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
        delay = min(1.6, (col + row) * 0.018)
        title = f'{d["count"]} contributions on {d["date"]}'
        cells.append(
            f'<g style="animation:reveal .38s ease-out {delay:.3f}s both">'
            f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" fill="{PALETTE[level]}">'
            f'<title>{escape(title)}</title></rect></g>'
        )

    footer = (
        f'{data.get("total", 0):,} contributions · '
        f'current streak {data.get("current_streak", 0)}d · '
        f'longest {data.get("longest_streak", 0)}d'
    )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<style>
  text {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }}
  @keyframes reveal {{ from {{ opacity:0; transform:translateY(-8px); }} to {{ opacity:1; transform:translateY(0); }} }}
</style>
<rect width="100%" height="100%" rx="14" fill="#0d1117" stroke="#30363d"/>
<text x="28" y="24" fill="#8b949e" font-size="12">Pedrssa / contributions</text>
{''.join(cells)}
<text x="28" y="174" fill="#8b949e" font-size="11">{escape(footer)}</text>
</svg>'''
    OUT.write_text(svg, encoding="utf-8")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
