#!/usr/bin/env python3
"""Wrap each character/button PNG into a self-contained animated SVG.

GitHub renders CSS @keyframes inside an SVG loaded via <img>, so this gives a
subtle 'floaty' bob plus a gentle scale 'breath' (the closest thing to a
hover-grow that a sandboxed README allows). Each asset gets its own duration
and phase so they don't bob in lockstep.
"""
import base64
import os
from PIL import Image

ROOT = os.path.dirname(__file__)
ASSETS = os.path.join(ROOT, "..", "assets")
OUT = os.path.join(ASSETS, "anim")
os.makedirs(OUT, exist_ok=True)

# name -> (float_amplitude_px, duration_s, delay_s, breath_scale)
TARGETS = {
    "qchudev-hi":        (7, 4.0, 0.0, 1.035),
    "qchudev-sat":       (6, 4.6, 0.4, 1.030),
    "qchudev-toolbox":   (6, 4.3, 0.8, 1.030),
    "qchudev-t-posing":  (7, 3.8, 0.2, 1.040),
    "quantum-mechanics-symbols": (5, 5.0, 0.0, 1.030),
    "text-globe":        (5, 4.8, 0.3, 1.020),
    "click-me-button":   (5, 3.4, 0.0, 1.050),
}

SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{alt}">
  <style>
    @keyframes floaty-{key} {{
      0%   {{ transform: translateY(0px)        scale(1); }}
      50%  {{ transform: translateY(-{amp}px)   scale({breath}); }}
      100% {{ transform: translateY(0px)        scale(1); }}
    }}
    .fl-{key} {{
      transform-box: fill-box;
      transform-origin: 50% 90%;
      animation: floaty-{key} {dur}s ease-in-out {delay}s infinite;
      will-change: transform;
    }}
  </style>
  <image class="fl-{key}" width="{w}" height="{h}" xlink:href="data:image/png;base64,{b64}"
         xmlns:xlink="http://www.w3.org/1999/xlink" />
</svg>
"""


def build(name, amp, dur, delay, breath):
    src = os.path.join(ASSETS, name + ".png")
    im = Image.open(src)
    w, h = im.size
    # pad the viewBox a touch so the float/scale never clips
    pad = amp + 4
    with open(src, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    key = name.replace("-", "").replace("_", "")
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="{-pad} {-pad} {w + 2 * pad} {h + 2 * pad}" '
        f'width="{w}" height="{h}" role="img" aria-label="{name}">\n'
        "  <style>\n"
        f"    @keyframes floaty-{key} {{\n"
        "      0%   { transform: translateY(0px)      scale(1); }\n"
        f"      50%  {{ transform: translateY(-{amp}px) scale({breath}); }}\n"
        "      100% { transform: translateY(0px)      scale(1); }\n"
        "    }\n"
        f"    .fl-{key} {{ transform-box: fill-box; transform-origin: 50% 85%;\n"
        f"      animation: floaty-{key} {dur}s ease-in-out {delay}s infinite; will-change: transform; }}\n"
        "  </style>\n"
        f'  <image class="fl-{key}" width="{w}" height="{h}" '
        f'xlink:href="data:image/png;base64,{b64}" '
        'xmlns:xlink="http://www.w3.org/1999/xlink" />\n'
        "</svg>\n"
    )
    out = os.path.join(OUT, name + "-float.svg")
    with open(out, "w") as f:
        f.write(svg)
    print(f"{name}-float.svg  ({w}x{h}, amp={amp}, {dur}s)")


for name, (amp, dur, delay, breath) in TARGETS.items():
    build(name, amp, dur, delay, breath)
print("done")
