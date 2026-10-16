#!/usr/bin/env python3
"""Titulos grandes del header: nombre + tagline."""
from PIL import Image, ImageDraw, ImageFont
import os

ORANGE = (255, 154, 0, 255)
FONT_PATH = os.path.join(os.path.dirname(__file__), "fonts", "PatrickHand-Regular.ttf")
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "assets", "titles")
os.makedirs(OUT_DIR, exist_ok=True)
SCALE = 3

def render(text, filename, base_size):
    size = base_size * SCALE
    font = ImageFont.truetype(FONT_PATH, size)
    tmp = Image.new("RGBA", (10, 10), (0, 0, 0, 0))
    d = ImageDraw.Draw(tmp)
    bbox = d.textbbox((0, 0), text, font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    pad = int(size * 0.2)
    img = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.text((pad - bbox[0], pad - bbox[1]), text, font=font, fill=ORANGE)
    final = img.resize((img.width // SCALE, img.height // SCALE), Image.LANCZOS)
    final.save(os.path.join(OUT_DIR, filename))
    print(f"{filename}: {final.width}x{final.height}")

render("hi, i'm Qchu", "h-name.png", 92)
render("i build things from scratch", "h-tagline.png", 44)
print("done")
