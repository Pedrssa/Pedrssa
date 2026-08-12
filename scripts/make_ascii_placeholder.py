from pathlib import Path

OUT = Path("pedrssa-ascii.svg")
ART = [
    "                 ........                 ",
    "             ..::::::::::::..             ",
    "          .:::------------::::.           ",
    "        .::---============---:::.         ",
    "       ::---==++++++++++++==---::.        ",
    "      ::--==+++**********+++==--::.       ",
    "     .:--==++***########***++==--:.       ",
    "     :--==++**###%%%%%%###**++==--:       ",
    "     :--==++**##%%%%%%%%##**++==--:       ",
    "     .:--==++**###%%%%###**++==--:.       ",
    "      ::--==+++***####***+++==--::.       ",
    "       .::---==++++++++++==---::.         ",
    "         .:::----====----:::.             ",
    "            ..::::::::..                  ",
    "                ....                      ",
    "                                          ",
    "          P E D R S S A                   ",
]


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main():
    rows = []
    y = 26
    for i, line in enumerate(ART):
        delay = i * 0.055
        rows.append(
            f'<text x="18" y="{y}" style="animation:type .6s steps(20,end) {delay:.2f}s both">{esc(line)}</text>'
        )
        y += 13

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="370" height="265" viewBox="0 0 370 265">
<style>
text{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:11px;white-space:pre;fill:#8b949e}}
@keyframes type{{from{{opacity:0}}to{{opacity:1}}}}
</style>
<rect width="369" height="264" x=".5" y=".5" rx="14" fill="#0d1117" stroke="#30363d"/>
{''.join(rows)}
</svg>'''
    OUT.write_text(svg, encoding="utf-8")


if __name__ == "__main__":
    main()
