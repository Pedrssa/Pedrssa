from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path("info-card.svg")
ROWS = [
    ("user", "Pedrssa"),
    ("name", "Pedro Henrique Martins"),
    ("focus", "software · automation · product"),
    ("building", "Delta · tools · experiments"),
    ("github", "github.com/Pedrssa"),
]


def main():
    lines = []
    y = 82
    for i, (key, value) in enumerate(ROWS):
        delay = 0.25 + i * 0.16
        lines.append(
            f'<g style="animation:line .45s ease {delay:.2f}s both">'
            f'<text x="30" y="{y}" fill="#58a6ff" font-weight="700">{escape(key):>8}</text>'
            f'<text x="128" y="{y}" fill="#c9d1d9">: {escape(value)}</text></g>'
        )
        y += 31

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="490" height="265" viewBox="0 0 490 265">
<style>
  text {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size:14px; }}
  @keyframes line {{ from {{ opacity:0; transform:translateX(-8px); }} to {{ opacity:1; transform:translateX(0); }} }}
</style>
<rect width="489" height="264" x=".5" y=".5" rx="14" fill="#0d1117" stroke="#30363d"/>
<circle cx="22" cy="22" r="5" fill="#ff5f56"/><circle cx="40" cy="22" r="5" fill="#ffbd2e"/><circle cx="58" cy="22" r="5" fill="#27c93f"/>
<text x="82" y="27" fill="#8b949e" font-size="12">pedrssa@github:~</text>
<text x="30" y="54" fill="#3fb950">$ neofetch --profile</text>
{''.join(lines)}
</svg>'''
    OUT.write_text(svg, encoding="utf-8")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
