#!/usr/bin/env python3
"""About section as one self-contained animated SVG (no table => no GitHub frame).

Layout: Qchu (sat.png) on the left, the text-globe speech bubble on the right.
Inside the bubble, phrases from about_phrases.json cycle with a crossfade.
Edit the JSON and re-run this script to change the phrases.

GitHub plays CSS @keyframes inside <img>-loaded SVGs, so the cycle animates on
the profile.
"""
import base64
import json
import os
from PIL import Image, ImageFont

ROOT = os.path.dirname(__file__)
ASSETS = os.path.join(ROOT, "..", "assets")
OUT = os.path.join(ASSETS, "anim", "about.svg")
FONT_PATH = os.path.join(ROOT, "fonts", "PatrickHand-Regular.ttf")
JSON_PATH = os.path.join(ROOT, "about_phrases.json")
ORANGE = "#FF9A00"
INK = "#C2740A"

# ---- canvas layout -------------------------------------------------------
VIEW_W, VIEW_H = 1180, 440
SAT_H = 360                      # displayed height of the sitting character
# text-globe placement/scale (globe native 1006x379)
GLOBE_NATIVE_W, GLOBE_NATIVE_H = 1006, 379
GLOBE_W = 820
GLOBE_SCALE = GLOBE_W / GLOBE_NATIVE_W
GLOBE_X = 350
GLOBE_Y = 24
# interior text box in GLOBE-LOCAL coords (before scale)
BOX = (90, 55, 915, 235)         # x0, y0, x1, y1 (rectangular body, above the tail)
FONT_SIZE = 44
LINE_H = 52


def b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


def wrap(text, font, max_w):
    """Wrap on spaces to fit max_w; respect explicit \\n."""
    out = []
    for hard in text.split("\n"):
        words = hard.split(" ")
        line = ""
        for w in words:
            trial = (line + " " + w).strip()
            if font.getlength(trial) <= max_w or not line:
                line = trial
            else:
                out.append(line)
                line = w
        out.append(line)
    return out


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main():
    cfg = json.load(open(JSON_PATH, encoding="utf-8"))
    phrases = cfg["phrases"]
    per = float(cfg.get("seconds_per_phrase", 3.0))
    k = len(phrases)
    total = round(per * k, 3)

    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    box_w = (BOX[2] - BOX[0])
    cx = (BOX[0] + BOX[2]) / 2
    cy = (BOX[1] + BOX[3]) / 2

    font_b64 = b64(FONT_PATH)
    sat_b64 = b64(os.path.join(ASSETS, "qchudev-sat.png"))
    globe_b64 = b64(os.path.join(ASSETS, "text-globe.png"))
    sat = Image.open(os.path.join(ASSETS, "qchudev-sat.png"))
    sat_w = int(sat.size[0] * SAT_H / sat.size[1])
    sat_y = VIEW_H - SAT_H - 10

    # fade timing: each phrase visible 'per' seconds, quick cross-fades
    fade = min(0.55, per * 0.22)   # seconds
    hold = per - fade
    p_fade = fade / total * 100
    p_hold = per / total * 100

    styles = [
        "@font-face{font-family:'PatrickHand';"
        f"src:url(data:font/ttf;base64,{font_b64}) format('truetype');}}",
        ".ph{font-family:'PatrickHand',cursive;fill:%s;}" % INK,
    ]
    # one keyframe set per phrase, delayed by i*per
    groups = []
    for i, text in enumerate(phrases):
        lines = wrap(text, font, box_w)
        n = len(lines)
        y0 = cy - (n - 1) * LINE_H / 2
        tspans = "".join(
            f'<text x="{cx:.1f}" y="{y0 + j * LINE_H:.1f}" text-anchor="middle" '
            f'dominant-baseline="middle" class="ph" font-size="{FONT_SIZE}">{esc(ln)}</text>'
            for j, ln in enumerate(lines)
        )
        key = f"cyc{i}"
        delay = round(i * per, 3)
        groups.append(
            f'<g class="{key}" opacity="0">{tspans}</g>'
        )
        # keyframes: fade in, hold, fade out, stay hidden the rest of the cycle
        styles.append(
            f"@keyframes {key}{{"
            f"0%{{opacity:0}}"
            f"{p_fade:.2f}%{{opacity:1}}"
            f"{p_hold:.2f}%{{opacity:1}}"
            f"{p_hold + p_fade:.2f}%{{opacity:0}}"
            f"100%{{opacity:0}}}}"
            f".{key}{{animation:{key} {total}s linear {delay}s infinite;}}"
        )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     viewBox="0 0 {VIEW_W} {VIEW_H}" width="{VIEW_W}" height="{VIEW_H}"
     role="img" aria-label="About Qchu: cycling phrases">
  <style>
    {"".join(chr(10) + "    " + s for s in styles)}
    @keyframes satbob {{0%{{transform:translateY(0)}}50%{{transform:translateY(-7px)}}100%{{transform:translateY(0)}}}}
    .sat {{transform-box:fill-box;transform-origin:50% 90%;animation:satbob 4.4s ease-in-out infinite;}}
  </style>

  <!-- character -->
  <image class="sat" x="20" y="{sat_y}" width="{sat_w}" height="{SAT_H}"
         xlink:href="data:image/png;base64,{sat_b64}" />

  <!-- speech bubble + cycling text (globe-local coords, scaled/translated) -->
  <g transform="translate({GLOBE_X} {GLOBE_Y}) scale({GLOBE_SCALE:.4f})">
    <image x="0" y="0" width="{GLOBE_NATIVE_W}" height="{GLOBE_NATIVE_H}"
           xlink:href="data:image/png;base64,{globe_b64}" />
    {"".join(chr(10) + "    " + g for g in groups)}
  </g>
</svg>
'''
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"about.svg  ({VIEW_W}x{VIEW_H}, {k} phrases, {per}s each, loop {total}s)")


if __name__ == "__main__":
    main()
