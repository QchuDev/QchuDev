#!/usr/bin/env python3
"""Hand-drawn dot-grid contribution heatmap (dynamic).

Fetches the real GitHub contribution calendar for a user and renders it as a
grid of hand-drawn orange dots/blobs. Intensity is bucketed into 5 levels that
map to dot radius + opacity, so busy days are big bold blobs and quiet days are
faint specks -- a marker-sketch take on the usual heatmap.

Data source: grubersjoe/github-contributions-api (scrapes the public profile).
Falls back to a deterministic pseudo-pattern only if the network is unavailable,
so the build never breaks; the scheduled GitHub Action re-runs it with live data.

Usage: python3 make_heatmap.py [username]
"""
import json
import math
import os
import random
import sys
import urllib.request

USER = sys.argv[1] if len(sys.argv) > 1 else "QchuDev"
ORANGE = "#FF9A00"
ROOT = os.path.dirname(__file__)
OUT = os.path.join(ROOT, "..", "assets", "anim", "heatmap.svg")
os.makedirs(os.path.dirname(OUT), exist_ok=True)

CELL = 15          # grid pitch (px)
PAD = 18
WEEKS = 53
DAYS = 7
MONTH_H = 18       # space on top for month labels


def fetch_levels(user):
    """Return list of weeks; each week is a list of 7 ints (level 0..4)."""
    url = f"https://github-contributions-api.jogruber.de/v4/{user}?y=last"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "qchudev-readme"})
        with urllib.request.urlopen(req, timeout=20) as r:
            data = json.load(r)
        days = data["contributions"]            # list of {date, count, level}
        days = sorted(days, key=lambda d: d["date"])
        # pad to align so the last column ends today; group into weeks of 7
        levels = [int(d.get("level", 0)) for d in days]
        return levels, True
    except Exception as e:                       # noqa: BLE001
        sys.stderr.write(f"[heatmap] live fetch failed ({e}); using fallback\n")
        rnd = random.Random(42)
        return [rnd.choices([0, 1, 2, 3, 4], weights=[55, 18, 14, 8, 5])[0]
                for _ in range(WEEKS * DAYS)], False


def main():
    levels, live = fetch_levels(USER)
    # keep the most recent WEEKS*DAYS cells, newest last
    cells = levels[-(WEEKS * DAYS):]
    cells = [0] * (WEEKS * DAYS - len(cells)) + cells

    w = PAD * 2 + WEEKS * CELL
    h = PAD * 2 + MONTH_H + DAYS * CELL

    # radius + opacity per intensity bucket (0 = empty tiny speck)
    rad = {0: 2.0, 1: 3.4, 2: 4.4, 3: 5.4, 4: 6.3}
    opa = {0: 0.14, 1: 0.45, 2: 0.65, 3: 0.84, 4: 1.0}

    rnd = random.Random(7)
    dots = []
    i = 0
    for wk in range(WEEKS):
        for dy in range(DAYS):
            lv = cells[i]
            i += 1
            cx = PAD + wk * CELL + CELL / 2
            cy = PAD + MONTH_H + dy * CELL + CELL / 2
            # hand-drawn jitter
            jx = rnd.uniform(-1.3, 1.3)
            jy = rnd.uniform(-1.3, 1.3)
            r = rad[lv] * rnd.uniform(0.9, 1.08)
            o = opa[lv]
            # squish slightly for an inked-blob feel
            ry = r * rnd.uniform(0.86, 1.0)
            rot = rnd.uniform(-18, 18)
            delay = round((wk * DAYS + dy) * 0.012, 3)
            dots.append(
                f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{r:.1f}" ry="{ry:.1f}" '
                f'fill="{ORANGE}" opacity="{o}" class="pop" '
                f'transform="rotate({rot:.1f} {cx:.1f} {cy:.1f})" '
                f'style="animation-delay:{delay}s"/>'
            )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}"
     width="{w}" height="{h}" role="img" aria-label="Contribution heatmap for {USER}">
  <style>
    @keyframes pop {{
      0%   {{ transform: scale(0.2); }}
      60%  {{ transform: scale(1.12); }}
      100% {{ transform: scale(1); }}
    }}
    .pop {{ transform-box: fill-box; transform-origin: center;
           animation: pop 0.9s ease-out both; }}
  </style>
  <rect x="0" y="0" width="{w}" height="{h}" rx="14" fill="#FFFFFF"/>
  {"".join(chr(10) + "  " + d for d in dots)}
</svg>
'''
    with open(OUT, "w") as f:
        f.write(svg)
    print(f"heatmap.svg  ({w}x{h}, {WEEKS}x{DAYS} dots, live_data={live})")


if __name__ == "__main__":
    main()
