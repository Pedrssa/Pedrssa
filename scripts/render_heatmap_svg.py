from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from xml.sax.saxutils import escape

IN = Path("data/contributions.json")
OUT = Path("contrib-heatmap.svg")

W, H = 860, 190
CELL, GAP = 10, 4
GRID_X, GRID_Y = 48, 42

# GitHub-like ramp. Empty days remain neutral; only real activity is green.
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
        color = PALETTE[level]
        delay = min(1.85, (col * 0.028) + (row * 0.052))
        title = f'{d["count"]} visible contributions on {d["date"]}'

        # Final state is always visible. SMIL only animates the one-time entrance,
        # so GitHub still has a clean static fallback if animation is unavailable.
        cells.append(
            f'<g>'
            f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" '
            f'fill="{color}" stroke="#21262d" stroke-width="0.35">'
            f'<title>{escape(title)}</title>'
            f'<animate attributeName="opacity" from="0" to="1" dur="0.36s" '
            f'begin="{delay:.3f}s" fill="freeze"/>'
            f'<animateTransform attributeName="transform" type="translate" '
            f'from="0 -8" to="0 0" dur="0.36s" begin="{delay:.3f}s" '
            f'fill="freeze" additive="sum"/>'
            f'</rect>'
            f'</g>'
        )

    total = data.get("total", 0)
    current = data.get("current_streak", 0)
    longest = data.get("longest_streak", 0)
    footer = f'{total:,} visible contributions · current streak {current}d · longest {longest}d'

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<style>
  text {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }}
</style>

<rect width="100%" height="100%" rx="14" fill="#0d1117" stroke="#30363d"/>
<text x="28" y="25" fill="#8b949e" font-size="12">Pedrssa / contributions</text>

<g>
{''.join(cells)}
</g>

<g transform="translate(675 18)">
  <text x="0" y="8" fill="#8b949e" font-size="9">Less</text>
  <rect x="30" y="0" width="9" height="9" rx="2" fill="#161b22"/>
  <rect x="43" y="0" width="9" height="9" rx="2" fill="#0e4429"/>
  <rect x="56" y="0" width="9" height="9" rx="2" fill="#006d32"/>
  <rect x="69" y="0" width="9" height="9" rx="2" fill="#26a641"/>
  <rect x="82" y="0" width="9" height="9" rx="2" fill="#39d353"/>
  <text x="97" y="8" fill="#8b949e" font-size="9">More</text>
</g>

<text x="28" y="172" fill="#8b949e" font-size="11">{escape(footer)}</text>
</svg>'''

    OUT.write_text(svg, encoding="utf-8")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
