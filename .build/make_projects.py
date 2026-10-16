#!/usr/bin/env python3
"""Projects as one borderless composed SVG (2x2 hand-drawn cards).

Replaces the HTML table (which GitHub frames with grey borders) with a single
<img>-friendly SVG: four marker-style cards, each with an embedded Lucide icon,
a Patrick Hand title, a short description and a stack line. A very subtle float
keeps it alive.
"""
import base64
import os
import textwrap
from PIL import ImageFont

ROOT = os.path.dirname(__file__)
ASSETS = os.path.join(ROOT, "..", "assets")
ICONS = os.path.join(ASSETS, "icons")
OUT = os.path.join(ASSETS, "anim", "projects.svg")
FONT_PATH = os.path.join(ROOT, "fonts", "PatrickHand-Regular.ttf")
ORANGE = "#FF9A00"
INK = "#4a4a4a"
STACKC = "#9a6a1f"

CARDS = [
    ("clapperboard", "Animine",
     "A 3D animation & visualization engine from scratch: a custom scene DSL + parser, keyframes (easing, Catmull-Rom), hierarchical transforms and hot-reload.",
     "C++17 - OpenGL - GLSL - GLM - CMake"),
    ("brain", "Brab",
     "A neural-network library and API built from scratch: training, persistence and inference.",
     "Rust"),
    ("cat", "SmolPet",
     "A desktop virtual pet with my own ECS engine: fixed-timestep physics, particles, an FSM and a transparent always-on-top window via Win32.",
     "Python - Pygame - Win32 API"),
    ("dice-5", "Game Dev",
     "Years of Unity / Godot prototypes and game-jam entries - gameplay, animation and asset design. See the reel below.",
     "C# - Unity - Godot"),
]

CARD_W, CARD_H = 540, 232
GAP = 28
PAD = 10
COLS = 2
TITLE_SZ = 34
DESC_SZ = 22
STACK_SZ = 20
ICON = 40


def b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def wrap(text, font, max_w):
    words, line, out = text.split(" "), "", []
    for w in words:
        trial = (line + " " + w).strip()
        if font.getlength(trial) <= max_w or not line:
            line = trial
        else:
            out.append(line); line = w
    if line:
        out.append(line)
    return out


def main():
    font_b64 = b64(FONT_PATH)
    desc_font = ImageFont.truetype(FONT_PATH, DESC_SZ)

    cols_w = COLS * CARD_W + (COLS - 1) * GAP
    rows = (len(CARDS) + COLS - 1) // COLS
    W = PAD * 2 + cols_w
    H = PAD * 2 + rows * CARD_H + (rows - 1) * GAP

    icon_defs, nodes, styles = [], [], []
    styles.append(
        "@font-face{font-family:'PatrickHand';"
        f"src:url(data:font/ttf;base64,{font_b64}) format('truetype');}}"
    )
    styles.append(".ti{font-family:'PatrickHand',cursive;fill:%s;}" % ORANGE)
    styles.append(".de{font-family:'PatrickHand',cursive;fill:%s;}" % INK)
    styles.append(".st{font-family:'PatrickHand',cursive;fill:%s;}" % STACKC)
    styles.append("@keyframes cardbob{0%{transform:translateY(0)}50%{transform:translateY(-4px)}100%{transform:translateY(0)}}")

    for i, (icon, title, desc, stack) in enumerate(CARDS):
        r, c = divmod(i, COLS)
        x = PAD + c * (CARD_W + GAP)
        y = PAD + r * (CARD_H + GAP)
        rx = 20 + (i % 3)
        key = f"c{i}"
        dur = 4.0 + i * 0.4
        delay = i * 0.3

        ib = b64(os.path.join(ICONS, icon + ".png"))
        icon_defs.append(
            f'<image id="pi{i}" width="{ICON}" height="{ICON}" '
            f'xlink:href="data:image/png;base64,{ib}" />'
        )

        tx = x + 34
        # title + icon row
        parts = [
            f'<rect x="{x}" y="{y}" width="{CARD_W}" height="{CARD_H}" rx="{rx}" '
            f'fill="#FFFFFF" stroke="{ORANGE}" stroke-width="4" stroke-linejoin="round"/>',
            f'<use href="#pi{i}" xlink:href="#pi{i}" x="{tx}" y="{y + 26}"/>',
            f'<text x="{tx + ICON + 14}" y="{y + 54}" class="ti" font-size="{TITLE_SZ}">{esc(title)}</text>',
        ]
        # description (wrapped)
        dy = y + 96
        for ln in wrap(desc, desc_font, CARD_W - 68):
            parts.append(f'<text x="{tx}" y="{dy}" class="de" font-size="{DESC_SZ}">{esc(ln)}</text>')
            dy += DESC_SZ + 6
        # stack pinned near bottom
        parts.append(
            f'<text x="{tx}" y="{y + CARD_H - 20}" class="st" font-size="{STACK_SZ}">{esc(stack)}</text>'
        )
        inner = "\n      ".join(parts)
        nodes.append(
            f'<g style="animation:cardbob {dur}s ease-in-out {delay}s infinite;'
            f'transform-box:fill-box;transform-origin:center">\n      {inner}\n    </g>'
        )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Projects">
  <style>
    {"".join(chr(10) + "    " + s for s in styles)}
  </style>
  <defs>
    {"".join(chr(10) + "    " + d for d in icon_defs)}
  </defs>
  {"".join(chr(10) + "  " + n for n in nodes)}
</svg>
'''
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"projects.svg  ({W}x{H}, {len(CARDS)} cards)")


if __name__ == "__main__":
    main()
