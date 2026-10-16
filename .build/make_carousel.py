#!/usr/bin/env python3
"""Left-traveling animated carousel of real games (from CV/content/projs/games).

Self-contained animated SVG: a strip of hand-drawn-style cards (orange marker
outline + Patrick Hand title + engine/role tag) that scrolls leftward forever.
The card row is duplicated so the loop is seamless. The Patrick Hand font is
embedded via @font-face (base64) so the marker look survives on GitHub, which
renders CSS @keyframes inside <img>-loaded SVGs.
"""
import base64
import os

ROOT = os.path.dirname(__file__)
ASSETS = os.path.join(ROOT, "..", "assets")
OUT = os.path.join(ASSETS, "anim")
FONT = os.path.join(ROOT, "fonts", "PatrickHand-Regular.ttf")
os.makedirs(OUT, exist_ok=True)

ORANGE = "#FF9A00"

# Real games pulled from CV/content/projs/games/projects (+ short tag)
GAMES = [
    ("Stack the Little Guys", "Godot"),
    ("EGG5", "Unity - co-op"),
    ("SmolSlime Game", "Unity"),
    ("SCP Run or Die", "Unity"),
    ("Little Dress Fighters", "Unity - 2D"),
    ("Crazy Wizard", "Unity"),
    ("Billage", "Unity - 3D"),
    ("Bar de Enfermitos", "Unity - Photon"),
    ("Enuma Project", "Unity - WebGL"),
    ("Feliz San Valentin", "Unity"),
    ("Boss-Fighting Co-op", "Unity"),
    ("Deynum's Jam Game", "Unity - jam"),
    ("SCP Mini Run", "Unity"),
]

CARD_W = 230
CARD_H = 118
GAP = 24
PITCH = CARD_W + GAP
PAD = 20                      # top/bottom padding inside the viewBox
VIEW_H = CARD_H + PAD * 2
STRIP_W = PITCH * len(GAMES)  # width of one full set of cards
VIEW_W = 920                  # visible window width
DUR = max(28, len(GAMES) * 3) # seconds for one full loop

with open(FONT, "rb") as f:
    font_b64 = base64.b64encode(f.read()).decode("ascii")


def card(x, title, tag, idx):
    # tiny deterministic jitter so each outline feels hand-drawn
    j = (idx * 7) % 5 - 2
    rx = 16 + (idx % 3)
    cx = x + CARD_W / 2
    # wrap long titles into two lines on space nearest the middle
    words = title.split(" ")
    if len(title) > 14 and len(words) > 1:
        mid = len(words) // 2
        l1, l2 = " ".join(words[:mid]), " ".join(words[mid:])
    else:
        l1, l2 = title, ""
    ty = PAD + 46 if l2 else PAD + 54
    parts = [
        f'<rect x="{x}" y="{PAD + j}" width="{CARD_W}" height="{CARD_H}" rx="{rx}" '
        f'fill="#FFFFFF" stroke="{ORANGE}" stroke-width="4" stroke-linejoin="round"/>',
        # little pin dot (hand-drawn accent)
        f'<circle cx="{x + 18}" cy="{PAD + 20 + j}" r="5" fill="{ORANGE}"/>',
        f'<text x="{cx}" y="{ty + j}" text-anchor="middle" class="t-title">{_esc(l1)}</text>',
    ]
    if l2:
        parts.append(
            f'<text x="{cx}" y="{ty + 34 + j}" text-anchor="middle" class="t-title">{_esc(l2)}</text>'
        )
    parts.append(
        f'<text x="{cx}" y="{PAD + CARD_H - 16 + j}" text-anchor="middle" class="t-tag">{_esc(tag)}</text>'
    )
    return "\n    ".join(parts)


def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


cards_once = "\n    ".join(
    card(i * PITCH, t, tag, i) for i, (t, tag) in enumerate(GAMES)
)
# second copy shifted by one strip width -> seamless wrap
cards_twice = cards_once + "\n    " + "\n    ".join(
    card(STRIP_W + i * PITCH, t, tag, i) for i, (t, tag) in enumerate(GAMES)
)

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     viewBox="0 0 {VIEW_W} {VIEW_H}" width="{VIEW_W}" height="{VIEW_H}" role="img"
     aria-label="Unity and Godot game prototypes carousel">
  <defs>
    <style>
      @font-face {{
        font-family: 'PatrickHand';
        src: url(data:font/ttf;base64,{font_b64}) format('truetype');
      }}
      .t-title {{ font-family: 'PatrickHand', cursive; font-size: 24px; fill: {ORANGE}; }}
      .t-tag   {{ font-family: 'PatrickHand', cursive; font-size: 16px; fill: #9a6a1f; }}
      @keyframes travel-left {{
        0%   {{ transform: translateX(0); }}
        100% {{ transform: translateX(-{STRIP_W}px); }}
      }}
      .track {{ animation: travel-left {DUR}s linear infinite; will-change: transform; }}
    </style>
    <clipPath id="win"><rect x="0" y="0" width="{VIEW_W}" height="{VIEW_H}"/></clipPath>
  </defs>
  <g clip-path="url(#win)">
    <g class="track">
    {cards_twice}
    </g>
  </g>
</svg>
'''

out = os.path.join(OUT, "games-carousel.svg")
with open(out, "w") as f:
    f.write(svg)
print(f"games-carousel.svg  ({VIEW_W}x{VIEW_H}, {len(GAMES)} games, loop {DUR}s, strip {STRIP_W}px)")
