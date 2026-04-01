#!/usr/bin/env python3
"""
Dither — Apply a single dithering algorithm to an image.

Output is saved next to the input file.

Usage:
    python3 dither.py input.jpg
    python3 dither.py input.jpg --algorithm atkinson
    python3 dither.py input.jpg --algorithm bayer --order 8
    python3 dither.py input.jpg --palette gameboy --algorithm floyd-steinberg
    python3 dither.py input.jpg --tint "#e9633b"
    python3 dither.py --list-algorithms
    python3 dither.py --list-palettes
"""

import argparse
import os
import sys

import numpy as np
from PIL import Image

import hitherdither

from palettes import PALETTES, parse_custom_palette

# ---------------------------------------------------------------------------
# Available algorithms
# ---------------------------------------------------------------------------
ORDERED_ALGORITHMS = ["bayer", "cluster-dot", "yliluoma"]

DIFFUSION_ALGORITHMS = [
    "floyd-steinberg",
    "atkinson",
    "jarvis-judice-ninke",
    "stucki",
    "burkes",
    "sierra3",
    "sierra2",
    "sierra-2-4a",
]

ALL_ALGORITHMS = ORDERED_ALGORITHMS + DIFFUSION_ALGORITHMS

DISPLAY_NAMES = {
    "bayer": "Bayer",
    "cluster-dot": "Cluster Dot",
    "yliluoma": "Yliluoma",
    "floyd-steinberg": "Floyd-Steinberg",
    "atkinson": "Atkinson",
    "jarvis-judice-ninke": "Jarvis-Judice-Ninke",
    "stucki": "Stucki",
    "burkes": "Burkes",
    "sierra3": "Sierra 3-Row",
    "sierra2": "Sierra 2-Row",
    "sierra-2-4a": "Sierra Lite",
}


def dither_image(img, palette, algorithm, order, threshold):
    """Apply a dithering algorithm and return the result."""
    if algorithm == "bayer":
        return hitherdither.ordered.bayer.bayer_dithering(
            img, palette, threshold, order=order
        )
    elif algorithm == "cluster-dot":
        return hitherdither.ordered.cluster.cluster_dot_dithering(
            img, palette, threshold, order=order
        )
    elif algorithm == "yliluoma":
        return hitherdither.ordered.yliluoma.yliluomas_1_ordered_dithering(
            img, palette, order=order
        )
    else:
        # Error diffusion
        return hitherdither.diffusion.error_diffusion_dithering(
            img, palette, method=algorithm, order=order
        )


def apply_tint(img, hex_color):
    """Apply a color tint to an image."""
    r = int(hex_color[1:3], 16)
    g = int(hex_color[3:5], 16)
    b = int(hex_color[5:7], 16)

    arr = np.array(img.convert("RGB")).astype(np.float32)
    gray = np.mean(arr, axis=2, keepdims=True) / 255.0
    tinted = np.stack([gray[:, :, 0] * r, gray[:, :, 0] * g, gray[:, :, 0] * b], axis=2)
    return Image.fromarray(np.clip(tinted, 0, 255).astype(np.uint8))


def main():
    parser = argparse.ArgumentParser(
        description="Dither — apply a dithering algorithm to an image"
    )
    parser.add_argument("input", nargs="?", help="Input image path")
    parser.add_argument(
        "--algorithm", "-a",
        default="floyd-steinberg",
        choices=ALL_ALGORITHMS,
        help="Dithering algorithm (default: floyd-steinberg)",
    )
    parser.add_argument(
        "--order", "-o",
        type=int,
        default=4,
        help="Order for ordered dithering / error diffusion (default: 4)",
    )
    palette_names = list(PALETTES.keys())
    parser.add_argument(
        "--palette", "-p",
        default="6tone",
        help=f"Preset name or custom hex colors. "
             f"Presets: {', '.join(palette_names)} (default: 6tone). "
             f"Custom: '#000000,#808080,#ffffff'",
    )
    parser.add_argument(
        "--tint", "-t",
        default=None,
        help='Hex color to tint result, e.g. "#e9633b"',
    )
    parser.add_argument(
        "--threshold",
        type=int,
        nargs=3,
        default=[96, 96, 96],
        help="Threshold as 3 ints (default: 96 96 96)",
    )
    parser.add_argument(
        "--width", "-w",
        type=int,
        default=0,
        help="Resize to this width before dithering (0 = keep original)",
    )
    parser.add_argument(
        "--scale", "-s",
        type=int,
        default=1,
        help="Scale factor for output (e.g. 4 = each pixel becomes 4x4) using nearest neighbor",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output file path (default: <input>_dithered.png next to input)",
    )
    parser.add_argument(
        "--list-algorithms",
        action="store_true",
        help="Show all available algorithms and exit",
    )
    parser.add_argument(
        "--list-palettes",
        action="store_true",
        help="Show all preset palettes and exit",
    )
    args = parser.parse_args()

    if args.list_algorithms:
        print("Available algorithms:\n")
        print("  Ordered:")
        for a in ORDERED_ALGORITHMS:
            print(f"    {a:25s} {DISPLAY_NAMES[a]}")
        print("\n  Error diffusion:")
        for a in DIFFUSION_ALGORITHMS:
            print(f"    {a:25s} {DISPLAY_NAMES[a]}")
        sys.exit(0)

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

    # Load image
    img = Image.open(args.input).convert("RGB")

    if args.width > 0 and img.width != args.width:
        ratio = args.width / img.width
        new_h = int(img.height * ratio)
        img = img.resize((args.width, new_h), Image.Resampling.LANCZOS)
        print(f"Resized to {args.width}x{new_h}")

    # Set up palette
    if args.palette in PALETTES:
        pal_info = PALETTES[args.palette]
        pal_colors = pal_info["colors"]
        pal_name = pal_info["name"]
    else:
        pal_colors = parse_custom_palette(args.palette)
        pal_name = f"Custom ({len(pal_colors)} colors)"
    palette = hitherdither.palette.Palette(pal_colors)

    print(f"Algorithm: {DISPLAY_NAMES[args.algorithm]}, Palette: {pal_name}, Order: {args.order}")

    # Dither
    dithered = dither_image(img, palette, args.algorithm, args.order, args.threshold)
    dithered_img = dithered.convert("RGB") if dithered.mode != "RGB" else dithered

    if args.tint:
        dithered_img = apply_tint(dithered_img, args.tint)

    if args.scale > 1:
        new_size = (dithered_img.width * args.scale, dithered_img.height * args.scale)
        dithered_img = dithered_img.resize(new_size, Image.Resampling.NEAREST)

    # Output path: next to input file
    if args.output:
        out_path = args.output
    else:
        base, ext = os.path.splitext(args.input)
        out_path = f"{base}_dithered.png"

    dithered_img.save(out_path, optimize=True)
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()
