#!/usr/bin/env python3
"""
Dither Explorer — Try every dithering algorithm on an image.

Applies a variety of ordered and error-diffusion dithering algorithms
to an input image using different palettes, and outputs a comparison
grid plus individual images.

Usage:
    python3 dither_explorer.py input.jpg
    python3 dither_explorer.py input.jpg --outdir results
    python3 dither_explorer.py input.jpg --width 800
    python3 dither_explorer.py input.jpg --palette bw          # Pure black & white
    python3 dither_explorer.py input.jpg --palette gameboy      # Game Boy green
    python3 dither_explorer.py input.jpg --palette ocean        # Cool blue tones
    python3 dither_explorer.py input.jpg --palette '#ff0000,#000000,#0000ff'  # Custom!
    python3 dither_explorer.py input.jpg --tint "#e9633b"       # Apply color tint
    python3 dither_explorer.py --list-palettes                  # Show all presets
"""

import argparse
import os
import sys
import time

from PIL import Image, ImageDraw, ImageFont

import hitherdither

from palettes import PALETTES, parse_custom_palette
from dither import dither_image, apply_tint, DIFFUSION_ALGORITHMS, DISPLAY_NAMES

# ---------------------------------------------------------------------------
# Algorithm runs: (display_name, algorithm_key, order)
# ---------------------------------------------------------------------------
EXPLORER_RUNS = [
    ("Bayer (order 2)", "bayer", 2),
    ("Bayer (order 4)", "bayer", 4),
    ("Bayer (order 8)", "bayer", 8),
    ("Cluster Dot", "cluster-dot", 4),
    ("Yliluoma (order 8)", "yliluoma", 8),
] + [
    (DISPLAY_NAMES[alg], alg, 2) for alg in DIFFUSION_ALGORITHMS
]


def make_comparison_grid(images_with_labels, cols=4, thumb_width=400):
    """Create a grid image showing all dithered variants with labels."""
    n = len(images_with_labels)
    rows = (n + cols - 1) // cols

    sample = images_with_labels[0][1]
    aspect = sample.height / sample.width
    thumb_height = int(thumb_width * aspect)

    label_height = 36
    padding = 12
    cell_w = thumb_width + padding * 2
    cell_h = thumb_height + label_height + padding * 2

    grid = Image.new("RGB", (cols * cell_w, rows * cell_h), (30, 30, 30))
    draw = ImageDraw.Draw(grid)

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
    except OSError:
        font = ImageFont.load_default()

    for i, (label, img) in enumerate(images_with_labels):
        col = i % cols
        row = i // cols
        x = col * cell_w + padding
        y = row * cell_h + padding

        thumb = img.convert("RGB").resize((thumb_width, thumb_height), Image.Resampling.NEAREST)
        grid.paste(thumb, (x, y))

        text_y = y + thumb_height + 4
        draw.text((x + 4, text_y), label, fill=(220, 220, 220), font=font)

    return grid


def main():
    parser = argparse.ArgumentParser(
        description="Dither Explorer — apply many dithering algorithms to an image"
    )
    parser.add_argument("input", nargs="?", help="Input image path")
    parser.add_argument("--outdir", default="dithered_output", help="Output directory")
    parser.add_argument("--width", type=int, default=0,
                        help="Resize image to this width before dithering (0 = keep original)")
    palette_names = list(PALETTES.keys())
    parser.add_argument("--palette", default="6tone",
                        help=f"Preset name or custom hex colors. "
                             f"Presets: {', '.join(palette_names)} (default: 6tone). "
                             f"Custom: '#000000,#808080,#ffffff'")
    parser.add_argument("--tint", default=None,
                        help='Hex color to tint results, e.g. "#e9633b"')
    parser.add_argument("--threshold", type=int, nargs=3, default=[96, 96, 96],
                        help="Bayer threshold as 3 ints (default: 96 96 96)")
    parser.add_argument("--scale", "-s", type=int, default=1,
                        help="Scale factor for output (e.g. 4 = each pixel becomes 4x4) using nearest neighbor")
    parser.add_argument("--list-palettes", action="store_true",
                        help="Show all preset palettes and exit")
    args = parser.parse_args()

    if args.list_palettes:
        print("Available palettes:\n")
        for key, info in PALETTES.items():
            hex_colors = " ".join(f"#{r:02x}{g:02x}{b:02x}" for r, g, b in info["colors"])
            print(f"  {key:10s}  {info['name']}")
            print(f"             {hex_colors}\n")
        print("Custom:  --palette '#ff0000,#00ff00,#0000ff'")
        sys.exit(0)

    if not os.path.isfile(args.input or ""):
        print(f"Error: file not found: {args.input}")
        sys.exit(1)

    os.makedirs(args.outdir, exist_ok=True)

    # Load and prep image
    print(f"Loading {args.input}...")
    img = Image.open(args.input).convert("RGB")

    if args.width > 0 and img.width != args.width:
        ratio = args.width / img.width
        new_h = int(img.height * ratio)
        img = img.resize((args.width, new_h), Image.Resampling.LANCZOS)
        print(f"  Resized to {args.width}x{new_h}")

    # Save original for reference
    orig_path = os.path.join(args.outdir, "00_original.png")
    img.save(orig_path)
    orig_size = os.path.getsize(orig_path)

    # Set up palette
    if args.palette in PALETTES:
        pal_info = PALETTES[args.palette]
        pal_colors = pal_info["colors"]
        pal_name = pal_info["name"]
    else:
        pal_colors = parse_custom_palette(args.palette)
        pal_name = f"Custom ({len(pal_colors)} colors)"
    palette = hitherdither.palette.Palette(pal_colors)
    threshold = args.threshold
    print(f"  Palette: {pal_name} ({len(pal_colors)} colors)")

    # Run all algorithms
    results = [("Original", img)]

    for display_name, algorithm, order in EXPLORER_RUNS:
        print(f"  Dithering: {display_name}...", end=" ", flush=True)
        t0 = time.time()
        try:
            dithered = dither_image(img, palette, algorithm, order, threshold)
            dt = time.time() - t0
            print(f"({dt:.1f}s)")

            safe_name = display_name.lower().replace(" ", "_").replace("(", "").replace(")", "").replace("-", "_")
            out_path = os.path.join(args.outdir, f"{safe_name}.png")
            dithered_img = dithered.convert("RGB") if dithered.mode != "RGB" else dithered

            if args.tint:
                tinted = apply_tint(dithered_img, args.tint)
                if args.scale > 1:
                    scaled = (tinted.width * args.scale, tinted.height * args.scale)
                    tinted = tinted.resize(scaled, Image.Resampling.NEAREST)
                tint_path = os.path.join(args.outdir, f"{safe_name}_tinted.png")
                tinted.save(tint_path, optimize=True)

            if args.scale > 1:
                scaled = (dithered_img.width * args.scale, dithered_img.height * args.scale)
                dithered_img = dithered_img.resize(scaled, Image.Resampling.NEAREST)

            dithered_img.save(out_path, optimize=True)
            dith_size = os.path.getsize(out_path)
            ratio = dith_size / orig_size * 100

            label = f"{display_name} ({dith_size//1024}KB, {ratio:.0f}%)"
            results.append((label, dithered_img))

        except Exception as e:
            print(f"FAILED: {e}")
            continue

    # Build comparison grid
    print("Building comparison grid...")
    grid = make_comparison_grid(results, cols=4)
    grid_path = os.path.join(args.outdir, "comparison_grid.png")
    grid.save(grid_path, optimize=True)

    if args.tint:
        tinted_results = [(label, apply_tint(im, args.tint)) for label, im in results]
        tinted_grid = make_comparison_grid(tinted_results, cols=4)
        tinted_grid_path = os.path.join(args.outdir, "comparison_grid_tinted.png")
        tinted_grid.save(tinted_grid_path, optimize=True)
        print(f"  Tinted grid: {tinted_grid_path}")

    print(f"\nDone! {len(results)-1} dithered images saved to: {args.outdir}/")
    print(f"  Comparison grid: {grid_path}")
    print(f"\nFile sizes vs original ({orig_size//1024}KB):")
    for label, _ in results[1:]:
        print(f"  {label}")


if __name__ == "__main__":
    main()
