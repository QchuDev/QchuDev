#!/usr/bin/env python3
"""Header as one composed SVG: Qchu (hi) on the left, speech bubble up-right
with the title + subtitle inside it. Floaty bob on the character.
"""
import base64
import os
from PIL import Image, ImageFont

ROOT = os.path.dirname(__file__)
ASSETS = os.path.join(ROOT, "..", "assets")
OUT = os.path.join(ASSETS, "anim", "header.svg")
FONT_PATH = os.path.join(ROOT, "fonts", "PatrickHand-Regular.ttf")
ORANGE = "#FF9A00"
INK = "#C2740A"

TITLE = "hi, i'm Qchu"
SUBTITLE = "i build things from scratch"

VIEW_W, VIEW_H = 1180, 460
HI_H = 300                              # displayed height of the waving char
GLOBE_NATIVE_W, GLOBE_NATIVE_H = 1006, 379
GLOBE_W = 790
GLOBE_SCALE = GLOBE_W / GLOBE_NATIVE_W
GLOBE_X = 360                           # to the right of the character
GLOBE_Y = 0                             # a bit higher than the character
BOX = (90, 55, 915, 235)               # globe-local interior
TITLE_SZ = 76
SUB_SZ = 36


def b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main():
    font_b64 = b64(FONT_PATH)
    hi_b64 = b64(os.path.join(ASSETS, "qchudev-hi.png"))
    globe_b64 = b64(os.path.join(ASSETS, "text-globe.png"))
    hi = Image.open(os.path.join(ASSETS, "qchudev-hi.png"))
    hi_w = int(hi.size[0] * HI_H / hi.size[1])
    hi_y = VIEW_H - HI_H - 10

    cx = (BOX[0] + BOX[2]) / 2
    cy = (BOX[1] + BOX[3]) / 2

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     viewBox="0 0 {VIEW_W} {VIEW_H}" width="{VIEW_W}" height="{VIEW_H}"
     role="img" aria-label="hi, i'm Qchu — i build things from scratch">
  <style>
    @font-face {{ font-family:'PatrickHand'; src:url(data:font/ttf;base64,{font_b64}) format('truetype'); }}
    .title {{ font-family:'PatrickHand',cursive; fill:{ORANGE}; }}
    .sub   {{ font-family:'PatrickHand',cursive; fill:{INK}; }}
    @keyframes hibob {{ 0%{{transform:translateY(0)}} 50%{{transform:translateY(-8px)}} 100%{{transform:translateY(0)}} }}
    .hi {{ transform-box:fill-box; transform-origin:50% 85%; animation:hibob 4s ease-in-out infinite; }}
  </style>

  <image class="hi" x="20" y="{hi_y}" width="{hi_w}" height="{HI_H}"
         xlink:href="data:image/png;base64,{hi_b64}" />

  <g transform="translate({GLOBE_X} {GLOBE_Y}) scale({GLOBE_SCALE:.4f})">
    <image x="0" y="0" width="{GLOBE_NATIVE_W}" height="{GLOBE_NATIVE_H}"
           xlink:href="data:image/png;base64,{globe_b64}" />
    <text x="{cx:.1f}" y="{cy - 24:.1f}" text-anchor="middle" dominant-baseline="middle"
          class="title" font-size="{TITLE_SZ}">{esc(TITLE)}</text>
    <text x="{cx:.1f}" y="{cy + 44:.1f}" text-anchor="middle" dominant-baseline="middle"
          class="sub" font-size="{SUB_SZ}">{esc(SUBTITLE)}</text>
  </g>
</svg>
'''
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"header.svg  ({VIEW_W}x{VIEW_H})")


if __name__ == "__main__":
    main()
