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

# Resting colors preserve the real contribution level.
# Even level 0 is visibly green-tinted so the calendar never looks empty.
PALETTE = ["#123322", "#0e4429", "#006d32", "#26a641", "#39d353"]
PULSE = ["#1f6f47", "#23935b", "#2fc56f", "#55e889", "#8cffad"]


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
        base = PALETTE[level]
        hot = PULSE[level]
        delay = ((col * 0.11) + (row * 0.19)) % 6.4
        title = f'{d["count"]} public contributions on {d["date"]}'

        # Native SVG <animate> is additive. If animation is blocked, the
        # explicit fill below remains visible as a green static fallback.
        cells.append(
            f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" '
            f'fill="{base}" stroke="#1f5136" stroke-width="0.35">'
            f'<title>{escape(title)}</title>'
            f'<animate attributeName="fill" '
            f'values="{base};{hot};#39d353;{hot};{base}" '
            f'keyTimes="0;0.28;0.42;0.58;1" '
            f'dur="6.4s" begin="{delay:.2f}s" repeatCount="indefinite"/>'
            f'</rect>'
        )

    footer = (
        f'{data.get("total", 0):,} public contributions · '
        f'current streak {data.get("current_streak", 0)}d · '
        f'longest {data.get("longest_streak", 0)}d'
    )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<style>
  text {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }}
  .live {{ animation: blink 1.2s steps(2,end) infinite; }}
  @keyframes blink {{ 50% {{ opacity:.35; }} }}
</style>

<defs>
  <filter id="softGlow" x="-30%" y="-30%" width="160%" height="160%">
    <feGaussianBlur stdDeviation="1.5" result="blur"/>
    <feMerge>
      <feMergeNode in="blur"/>
      <feMergeNode in="SourceGraphic"/>
    </feMerge>
  </filter>
</defs>

<rect width="100%" height="100%" rx="14" fill="#0d1117" stroke="#30363d"/>

<circle class="live" cx="858" cy="22" r="4" fill="#39d353" filter="url(#softGlow)">
  <animate attributeName="opacity" values="1;.3;1" dur="1.2s" repeatCount="indefinite"/>
</circle>
<text x="28" y="26" fill="#8b949e" font-size="12">Pedrssa / public contributions · green pulse</text>

<g filter="url(#softGlow)">
{''.join(cells)}
</g>

<text x="28" y="181" fill="#8b949e" font-size="11">{escape(footer)}</text>
<text x="665" y="181" fill="#39d353" font-size="10">animation = decorative · brightness = real level</text>
</svg>'''

    OUT.write_text(svg, encoding="utf-8")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
