#!/usr/bin/env python3
"""Rasteriza titulos handwritten en naranja #FF9A00 sobre fondo transparente."""
from PIL import Image, ImageDraw, ImageFont
import os

ORANGE = (255, 154, 0, 255)
FONT_PATH = os.path.join(os.path.dirname(__file__), "fonts", "PatrickHand-Regular.ttf")
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "assets", "titles")
os.makedirs(OUT_DIR, exist_ok=True)

SCALE = 3          # supersampling para bordes suaves
BASE_SIZE = 64     # tamanio logico de la font

titles = {
    "about":    "// about me",
    "stack":    "my toolbox",
    "work":     "where i've built things",
    "projects": "stuff i've made",
    "quantum":  "0 | 1  quantum side quest",
    "stats":    "the numbers",
    "connect":  "say hi!",
}

def render(text, filename):
    size = BASE_SIZE * SCALE
    font = ImageFont.truetype(FONT_PATH, size)
    tmp = Image.new("RGBA", (10, 10), (0, 0, 0, 0))
    d = ImageDraw.Draw(tmp)
    bbox = d.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    pad = int(size * 0.25)
    img = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.text((pad - bbox[0], pad - bbox[1]), text, font=font, fill=ORANGE)
    # downscale para antialiasing
    final = img.resize(
        (img.width // SCALE, img.height // SCALE), Image.LANCZOS
    )
    out = os.path.join(OUT_DIR, filename)
    final.save(out)
    print(f"{filename}: {final.width}x{final.height}")

for key, text in titles.items():
    render(text, f"t-{key}.png")

print("done")
