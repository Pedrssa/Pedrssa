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

# GitHub-like contribution scale: empty days stay neutral; activity gets greener.
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
PULSE = [None, "#177143", "#00a84b", "#39d353", "#7dff9b"]


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
        title = f'{d["count"]} public contributions on {d["date"]}'

        if level == 0:
            cells.append(
                f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" '
                f'fill="{base}" stroke="#21262d" stroke-width="0.35">'
                f'<title>{escape(title)}</title></rect>'
            )
        else:
            hot = PULSE[level]
            delay = ((col * 0.17) + (row * 0.29)) % 5.6
            cells.append(
                f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" '
                f'fill="{base}" stroke="#238636" stroke-width="0.45">'
                f'<title>{escape(title)}</title>'
                f'<animate attributeName="fill" '
                f'values="{base};{hot};{base}" '
                f'keyTimes="0;0.5;1" dur="5.6s" begin="{delay:.2f}s" repeatCount="indefinite"/>'
                f'<animate attributeName="opacity" values="1;.78;1" dur="5.6s" '
                f'begin="{delay:.2f}s" repeatCount="indefinite"/>'
                f'</rect>'
            )

    footer = (
        f'{data.get("total", 0):,} public contributions · '
        f'current streak {data.get("current_streak", 0)}d · '
        f'longest {data.get("longest_streak", 0)}d'
    )

    grid_width = 53 * (CELL + GAP) - GAP
    grid_height = 7 * (CELL + GAP) - GAP

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<style>
  text {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }}
</style>

<defs>
  <filter id="activeGlow" x="-35%" y="-35%" width="170%" height="170%">
    <feGaussianBlur stdDeviation="0.8" result="blur"/>
    <feMerge>
      <feMergeNode in="blur"/>
      <feMergeNode in="SourceGraphic"/>
    </feMerge>
  </filter>

  <linearGradient id="scanBand" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="#39d353" stop-opacity="0"/>
    <stop offset="22%" stop-color="#39d353" stop-opacity="0.05"/>
    <stop offset="50%" stop-color="#39d353" stop-opacity="0.42"/>
    <stop offset="78%" stop-color="#39d353" stop-opacity="0.05"/>
    <stop offset="100%" stop-color="#39d353" stop-opacity="0"/>
  </linearGradient>

  <clipPath id="gridClip">
    <rect x="{GRID_X}" y="{GRID_Y}" width="{grid_width}" height="{grid_height}" rx="3"/>
  </clipPath>
</defs>

<rect width="100%" height="100%" rx="14" fill="#0d1117" stroke="#30363d"/>

<circle cx="858" cy="22" r="4" fill="#39d353">
  <animate attributeName="opacity" values="1;.25;1" dur="1.4s" repeatCount="indefinite"/>
</circle>
<text x="28" y="26" fill="#8b949e" font-size="12">Pedrssa / public contributions · live</text>

<g>
{''.join(cells)}
</g>

<!-- Decorative scan layer. It does not represent contribution data. -->
<g clip-path="url(#gridClip)" pointer-events="none">
  <rect x="-180" y="{GRID_Y - 2}" width="220" height="{grid_height + 4}" fill="url(#scanBand)" opacity="0.92">
    <animateTransform attributeName="transform" type="translate" from="0 0" to="1040 0" dur="4.8s" repeatCount="indefinite"/>
  </rect>
  <rect x="-340" y="{GRID_Y - 2}" width="140" height="{grid_height + 4}" fill="url(#scanBand)" opacity="0.46">
    <animateTransform attributeName="transform" type="translate" from="0 0" to="1200 0" dur="7.4s" repeatCount="indefinite"/>
  </rect>
</g>

<g transform="translate(690 18)">
  <text x="0" y="8" fill="#8b949e" font-size="9">less</text>
  <rect x="27" y="0" width="9" height="9" rx="2" fill="#161b22"/>
  <rect x="40" y="0" width="9" height="9" rx="2" fill="#0e4429"/>
  <rect x="53" y="0" width="9" height="9" rx="2" fill="#006d32"/>
  <rect x="66" y="0" width="9" height="9" rx="2" fill="#26a641"/>
  <rect x="79" y="0" width="9" height="9" rx="2" fill="#39d353"/>
  <text x="94" y="8" fill="#8b949e" font-size="9">more</text>
</g>

<text x="28" y="181" fill="#8b949e" font-size="11">{escape(footer)}</text>
<text x="603" y="181" fill="#8b949e" font-size="10">scan = animation · fixed green = real activity</text>
</svg>'''

    OUT.write_text(svg, encoding="utf-8")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
