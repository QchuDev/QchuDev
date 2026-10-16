#!/usr/bin/env python3
"""Scattered, floating tech-stack cloud as a self-contained animated SVG.

Instead of static, aligned shields, each tool logo is placed at a scattered
position with its own gentle float (bob + tiny drift + sway), so the stack
looks like it's floating around. Logos come from Simple Icons, recolored to the
brand orange (#FF9A00) and embedded as base64. GitHub plays CSS @keyframes in
<img>-loaded SVGs, so the whole cloud animates on the profile.
"""
import base64
import math
import os
import random
import re
import urllib.request

ROOT = os.path.dirname(__file__)
OUT = os.path.join(ROOT, "..", "assets", "anim", "stack-cloud.svg")
os.makedirs(os.path.dirname(OUT), exist_ok=True)

ORANGE = "FF9A00"

# (label, simpleicons slug, display size px) — order roughly big->small
TOOLS = [
    ("Java", "openjdk", 58), ("Python", "python", 58), ("C", "c", 50),
    ("C++", "cplusplus", 54), ("C#", "sharp", 50), ("TypeScript", "typescript", 52),
    ("Rust", "rust", 50), ("SQL", "mysql", 48),
    ("Spring", "spring", 48), ("React", "react", 52), ("Vite", "vite", 46),
    ("D3", "d3", 46), ("OpenGL", "opengl", 50), ("Node.js", "nodedotjs", 50),
    ("CMake", "cmake", 44), ("Unity", "unity", 50), ("PostgreSQL", "postgresql", 48),
    ("Git", "git", 48),
]

VIEW_W = 640
VIEW_H = 300


def fetch_logo(slug):
    url = f"https://cdn.simpleicons.org/{slug}/{ORANGE}"
    req = urllib.request.Request(url, headers={"User-Agent": "qchudev-readme"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read().decode("utf-8")


def scatter_positions(n, w, h, size_max, seed=11):
    """Poisson-ish scatter: reject points too close to already-placed ones."""
    rnd = random.Random(seed)
    pts = []
    min_d = 86
    tries = 0
    margin = 40
    while len(pts) < n and tries < 20000:
        tries += 1
        x = rnd.uniform(margin, w - margin)
        y = rnd.uniform(margin, h - margin)
        if all((x - px) ** 2 + (y - py) ** 2 > min_d ** 2 for px, py in pts):
            pts.append((x, y))
    # if we couldn't fit them all, relax and grid-fill the rest
    while len(pts) < n:
        pts.append((rnd.uniform(margin, w - margin), rnd.uniform(margin, h - margin)))
    rnd.shuffle(pts)
    return pts


def main():
    rnd = random.Random(5)
    pos = scatter_positions(len(TOOLS), VIEW_W, VIEW_H, 60)

    defs = []
    uses = []
    styles = []
    for i, (label, slug, size) in enumerate(TOOLS):
        try:
            raw = fetch_logo(slug)
        except Exception as e:  # noqa: BLE001
            print(f"  ! {slug} failed: {e}")
            continue
        b64 = base64.b64encode(raw.encode("utf-8")).decode("ascii")
        x, y = pos[i]
        # per-logo float params
        dur = round(rnd.uniform(3.2, 5.6), 2)
        delay = round(rnd.uniform(0, 2.4), 2)
        amp = round(rnd.uniform(5, 11), 1)
        sway = round(rnd.uniform(2, 6), 1)
        rot = round(rnd.uniform(-10, 10), 1)
        key = f"s{i}"
        half = size / 2
        defs.append(
            f'<image id="img{i}" width="{size}" height="{size}" '
            f'xlink:href="data:image/svg+xml;base64,{b64}" />'
        )
        # wrap in a <g> translated to pos; inner animates around its own center
        uses.append(
            f'<g transform="translate({x - half:.1f} {y - half:.1f})">'
            f'<g class="fl {key}" transform-origin="{half} {half}">'
            f'<use href="#img{i}" xlink:href="#img{i}" opacity="0.96"/></g></g>'
        )
        styles.append(
            f"@keyframes k{key}{{"
            f"0%{{transform:translate(0,0) rotate(0deg);}}"
            f"50%{{transform:translate({sway:.1f}px,-{amp:.1f}px) rotate({rot:.1f}deg);}}"
            f"100%{{transform:translate(0,0) rotate(0deg);}}}}"
            f".{key}{{animation:k{key} {dur}s ease-in-out {delay}s infinite;}}"
        )

    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'viewBox="0 0 {VIEW_W} {VIEW_H}" width="{VIEW_W}" height="{VIEW_H}" '
        'role="img" aria-label="Floating tech stack">\n'
        "  <style>\n"
        "    .fl{transform-box:fill-box;will-change:transform;}\n"
        "    " + "\n    ".join(styles) + "\n"
        "  </style>\n"
        "  <defs>\n    " + "\n    ".join(defs) + "\n  </defs>\n  "
        + "\n  ".join(uses)
        + "\n</svg>\n"
    )
    with open(OUT, "w") as f:
        f.write(svg)
    print(f"stack-cloud.svg  ({VIEW_W}x{VIEW_H}, {len(TOOLS)} logos)")


if __name__ == "__main__":
    main()
