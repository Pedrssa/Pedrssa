# Profile automation

This repository powers the public GitHub profile for `Pedrssa`.

## Generated assets

- `contrib-heatmap.svg` — contribution activity visualization.
- `pedrssa-ascii.svg` — ASCII portrait used in the profile README.
- `info-card.svg` — terminal-style profile card.
- `data/contributions.json` — normalized contribution data used by the renderer.

## Update flow

The workflow in `.github/workflows/update-profile-art.yml` runs the profile-art pipeline:

1. install the Python dependencies from `scripts/requirements.txt`;
2. run `scripts/fetch_contributions.py`;
3. run `scripts/render_heatmap_svg.py`;
4. commit refreshed generated assets when they changed.

The workflow also rebases against the current `main` branch before publishing generated files, reducing conflicts when the profile README is edited at the same time.

## Privacy

The profile visualization exposes contribution activity only. Private repository names, source code and repository details are not published by this automation.

## Maintenance

Generated files should normally be refreshed through the workflow rather than edited manually. Source changes belong in `scripts/` or the workflow file so future runs remain reproducible.
