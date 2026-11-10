#!/usr/bin/env python3
"""
Convert a portrait photo into a high-resolution, monochrome ASCII portrait SVG:
- Isolates subject from black/dark background
- Bilateral smoothing keeps skin texture clean (avoids noisy ASCII dots on skin)
- Difference of Gaussians (DoG) sharpens glasses, eyes, mustache, and hair lines
- Renders 180 cols x 96 rows with staggered row-by-row typing animation
"""
import html
import os
import sys
import cv2
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")

DEFAULT_INPUT = os.path.join(ROOT, "photo.jpg")
DEFAULT_OUTPUT = os.path.join(ROOT, "portrait.svg")

INP = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_INPUT
OUT = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_OUTPUT

COLS = int(os.environ.get("COLS", 180))
ART_W_TARGET = 800
CELL_W = ART_W_TARGET / COLS
CELL_H = CELL_W * 15 / 8
ROWS = round(COLS * 8 / 15)   # 96 rows
RAMP = " .`:-=+*cs#%@"        # bright(sparse) -> dark(dense)
WHITE_FLOOR = 0.82

def process_photo(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Input image not found: {path}")

    im = Image.open(path).convert("RGB")
    w, h = im.size

    # Detect subject bounding box
    gray_full = cv2.cvtColor(np.array(im), cv2.COLOR_RGB2GRAY)
    mask_full = gray_full > 20
    ys, xs = np.where(mask_full)

    if len(ys) > 0 and len(xs) > 0:
        # Center horizontally on subject
        cx = int((xs.min() + xs.max()) / 2)
        top_y = max(0, ys.min() - 10)
        # Head & shoulders box (roughly square to match 800x800 aspect)
        crop_size = min(w, int((ys.max() - top_y) * 0.78))
        x0 = max(0, cx - crop_size // 2)
        x1 = min(w, x0 + crop_size)
        y0 = top_y
        y1 = min(h, y0 + crop_size)
        im = im.crop((x0, y0, x1, y1))

    rgb = np.array(im)
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)

    # Subject mask (background is black)
    mask = gray > 18
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask.astype(np.uint8), cv2.MORPH_CLOSE, kernel).astype(bool)

    # 1. Bilateral filter: smooth skin, preserve edges
    smooth = gray
    for _ in range(2):
        smooth = cv2.bilateralFilter(smooth, 7, 30, 7)

    # 2. Tone stretch over face subject
    if np.any(mask):
        lo, hi = np.percentile(smooth[mask], [4, 92])
        tone = np.clip((smooth.astype(np.float32) - lo) / max(1.0, (hi - lo)), 0, 1)
    else:
        tone = smooth.astype(np.float32) / 255.0

    # 3. Difference of Gaussians (DoG) for crisp glasses, eyes, mustache, teeth
    fine = cv2.GaussianBlur(smooth, (0, 0), 1.2).astype(np.float32)
    coarse = cv2.GaussianBlur(smooth, (0, 0), 5.0).astype(np.float32)
    dog = np.clip((coarse - fine) / 30.0, 0, 1)

    LINE_WEIGHT = 0.58
    out = np.clip(tone - LINE_WEIGHT * dog, 0, 1) * 255.0
    out[~mask] = 255.0  # background to pure white (blank in ASCII)

    prepped = Image.fromarray(out.astype(np.uint8))
    resized = prepped.resize((COLS, ROWS), Image.LANCZOS)
    px = resized.load()

    rows_txt = []
    for y in range(ROWS):
        chars = []
        for x in range(COLS):
            lum = px[x, y] / 255.0
            lum = pow(lum, 1.15)
            if lum >= WHITE_FLOOR:
                chars.append(" ")
            else:
                idx = int((1.0 - lum) * (len(RAMP) - 1) + 0.5)
                idx = max(0, min(len(RAMP) - 1, idx))
                chars.append(RAMP[idx])
        rows_txt.append("".join(chars))

    return rows_txt

def build_svg(rows_txt):
    art_w = COLS * CELL_W
    art_h = ROWS * CELL_H
    pad = 20
    canvas_w = art_w + pad * 2
    canvas_h = art_h + pad * 2
    font_size = CELL_H * 0.88

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w:.1f}" height="{canvas_h:.1f}" '
        f'viewBox="0 0 {canvas_w:.1f} {canvas_h:.1f}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
        '<style>',
        '.f{opacity:0;animation:fade .35s ease-out both}',
        '@keyframes fade{from{opacity:0}to{opacity:1}}',
        '@media (prefers-reduced-motion: reduce){.f{animation:none!important;opacity:1!important}}',
        '</style>',
        f'<rect width="{canvas_w:.1f}" height="{canvas_h:.1f}" fill="none"/>'
    ]

    for ry, line in enumerate(rows_txt):
        y = pad + ry * CELL_H + CELL_H * 0.74
        delay = 0.25 + ry * 0.018
        safe = html.escape(line)
        parts.append(
            f'<text class="f" style="animation-delay:{delay:.3f}s" xml:space="preserve" '
            f'x="{pad}" y="{y:.1f}" fill="#111111" font-size="{font_size:.1f}" '
            f'textLength="{art_w:.1f}" lengthAdjust="spacing">{safe}</text>'
        )

    parts.append('</svg>')
    return "".join(parts)

if __name__ == "__main__":
    print(f"Processing {INP} -> {OUT}...")
    rows = process_photo(INP)
    svg_data = build_svg(rows)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(svg_data)
    print(f"Successfully generated {OUT}: {len(svg_data)//1024} KB with {len(rows)} rows.")
