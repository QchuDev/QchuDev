#!/usr/bin/env python3
"""Recolorea iconos Lucide a #FF9A00 con trazo grueso (look marcador) y
los rasteriza a PNG transparente de alta resolucion para GitHub."""
import os, glob, subprocess, re, shutil

ROOT = os.path.dirname(__file__)
SRC = os.path.join(ROOT, "icons-src")
OUT = os.path.join(ROOT, "..", "assets", "icons")
os.makedirs(OUT, exist_ok=True)

ORANGE = "#FF9A00"
STROKE = "2.6"      # mas grueso que el 2 default -> sensacion marcador
RENDER_PX = 96      # alta resolucion; luego se escala por height en HTML
CHROME = "/usr/bin/chromium"

def tint(svg: str) -> str:
    svg = svg.replace('stroke="currentColor"', f'stroke="{ORANGE}"')
    svg = re.sub(r'stroke-width="[0-9.]+"', f'stroke-width="{STROKE}"', svg)
    svg = re.sub(r'\bwidth="24"', f'width="{RENDER_PX}"', svg)
    svg = re.sub(r'\bheight="24"', f'height="{RENDER_PX}"', svg)
    return svg

tmp = os.path.join(ROOT, "_tint_tmp")
os.makedirs(tmp, exist_ok=True)
names = []
for path in sorted(glob.glob(os.path.join(SRC, "*.svg"))):
    name = os.path.splitext(os.path.basename(path))[0]
    with open(path) as f:
        svg = tint(f.read())
    tp = os.path.join(tmp, name + ".svg")
    with open(tp, "w") as f:
        f.write(svg)
    outp = os.path.join(OUT, name + ".png")
    subprocess.run([
        CHROME, "--headless", "--no-sandbox", "--disable-gpu",
        "--hide-scrollbars", "--default-background-color=00000000",
        f"--force-device-scale-factor=2",
        f"--window-size={RENDER_PX},{RENDER_PX}",
        f"--screenshot={outp}", "file://" + os.path.abspath(tp),
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    names.append(name)
    print("rendered", name + ".png")

shutil.rmtree(tmp)
print("done:", ", ".join(names))
