"""Shared palette definitions for dithering scripts."""

PALETTES = {
    "bw": {
        "name": "Black & White (1-bit)",
        "colors": [(0, 0, 0), (255, 255, 255)],
    },
    "3tone": {
        "name": "3-Tone Grayscale",
        "colors": [(0, 0, 0), (128, 128, 128), (255, 255, 255)],
    },
    "4tone": {
        "name": "4-Tone Grayscale",
        "colors": [(0, 0, 0), (85, 85, 85), (170, 170, 170), (255, 255, 255)],
    },
    "6tone": {
        "name": "6-Tone Grayscale",
        "colors": [
            (0, 0, 0),
            (51, 51, 51),
            (102, 102, 102),
            (153, 153, 153),
            (204, 204, 204),
            (255, 255, 255),
        ],
    },
    "8tone": {
        "name": "8-Tone Grayscale",
        "colors": [
            (0, 0, 0),
            (36, 36, 36),
            (73, 73, 73),
            (109, 109, 109),
            (146, 146, 146),
            (182, 182, 182),
            (219, 219, 219),
            (255, 255, 255),
        ],
    },
    "cga": {
        "name": "CGA (4-color)",
        "colors": [(0, 0, 0), (85, 255, 255), (255, 85, 255), (255, 255, 255)],
    },
    "gameboy": {
        "name": "Game Boy",
        "colors": [(15, 56, 15), (48, 98, 48), (139, 172, 15), (155, 188, 15)],
    },
    "sepia": {
        "name": "Sepia 4-Tone",
        "colors": [(54, 33, 18), (120, 80, 44), (189, 155, 105), (240, 220, 180)],
    },
    "nord": {
        "name": "Nord",
        "colors": [
            (46, 52, 64),
            (59, 66, 82),
            (136, 192, 208),
            (143, 188, 187),
            (216, 222, 233),
            (236, 239, 244),
        ],
    },
    "warmth": {
        "name": "Warm Tones",
        "colors": [
            (30, 10, 0),
            (120, 40, 10),
            (200, 100, 30),
            (240, 180, 80),
            (255, 230, 160),
            (255, 250, 230),
        ],
    },
    "ocean": {
        "name": "Ocean",
        "colors": [
            (5, 10, 30),
            (15, 50, 80),
            (30, 100, 140),
            (80, 170, 190),
            (160, 215, 220),
            (230, 245, 250),
        ],
    },
    "pico": {
      "name": "Pico Cherry",
      "colors": [(20, 27, 30), (19,57,64), (181, 109, 112), (255, 204, 170)]
    },
    "dithernaut": {
        "name": "Dithernaut",
        "colors": [
            (23, 31, 65),
            (47, 112, 119),
            (251, 108, 118),
            (254, 237, 227),
        ],
    }
}


def parse_custom_palette(spec):
    """Parse a custom palette string like '#ff0000,#00ff00,#0000ff' or 'rgb(255,0,0);rgb(0,255,0)'."""
    import re

    colors = []
    hex_colors = re.findall(r'#([0-9a-fA-F]{6})', spec)
    if hex_colors:
        for h in hex_colors:
            colors.append((int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)))
        return colors
    rgb_groups = re.findall(r'(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})', spec)
    if rgb_groups:
        for r, g, b in rgb_groups:
            colors.append((int(r), int(g), int(b)))
        return colors
    raise ValueError(f"Could not parse palette: {spec}\n"
                     f"  Use hex:  '#000000,#808080,#ffffff'\n"
                     f"  Or RGB:   '0,0,0  128,128,128  255,255,255'")
