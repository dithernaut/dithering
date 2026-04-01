# didder cheat sheet

How to reproduce results from `dither.py` using [didder](https://github.com/makeworld-the-better-one/didder).

## Basic mapping

```bash
# dither.py
uv run dither.py input.jpg --palette pico --algorithm bayer --order 2 --width 200 --scale 4

# didder equivalent
magick input.jpg -resize 200x tmp.png && \
didder --palette "141B1E 133940 B56D70 FFCCAA" -i tmp.png -o output.png bayer 2x2 && \
magick output.png -filter point -resize 800x output.png
```

didder doesn't have resize or scale built in, so use ImageMagick before/after.

## Palettes

didder takes hex colors (no `#` prefix) as a space-separated list via `--palette`.

| dither.py `--palette` | didder `--palette` |
|---|---|
| `bw` | `"000000 FFFFFF"` |
| `3tone` | `"000000 808080 FFFFFF"` |
| `4tone` | `"000000 555555 AAAAAA FFFFFF"` |
| `6tone` | `"000000 333333 666666 999999 CCCCCC FFFFFF"` |
| `8tone` | `"000000 242424 494949 6D6D6D 929292 B6B6B6 DBDBDB FFFFFF"` |
| `cga` | `"000000 55FFFF FF55FF FFFFFF"` |
| `gameboy` | `"0F380F 306230 8BAC0F 9BBC0F"` |
| `sepia` | `"36210E 78502C BD9B69 F0DCB4"` |
| `nord` | `"2E3440 3B4252 88C0D0 8FBCBB D8DEE9 ECEFF4"` |
| `warmth` | `"1E0A00 78280A C8641E F0B450 FFE6A0 FFFAE6"` |
| `ocean` | `"050A1E 0F3250 1E648C 50AABe A0D7DC E6F5FA"` |
| `pico` | `"141B1E 133940 B56D70 FFCCAA"` |
| `dithernaut` | `"171F41 2F7077 FB6C76 FAEDE3"` |
| custom `#rrggbb,...` | Just strip the `#` and space-separate |

## Algorithms

| dither.py `--algorithm` | didder command |
|---|---|
| `bayer` (order 2) | `bayer 2x2` |
| `bayer` (order 4) | `bayer 4x4` |
| `bayer` (order 8) | `bayer 8x8` |
| `floyd-steinberg` | `edm FloydSteinberg` |
| `atkinson` | `edm Atkinson` |
| `jarvis-judice-ninke` | `edm JarvisJudiceNinke` |
| `stucki` | `edm Stucki` |
| `burkes` | `edm Burkes` |
| `sierra3` | `edm Sierra3` |
| `sierra2` | `edm Sierra2` |
| `sierra-2-4a` | `edm SierraLite` |
| `cluster-dot` | no equivalent in didder |
| `yliluoma` | no equivalent in didder |

## Resize and scale (using ImageMagick)

didder only does dithering. Use `magick` for resize/scale:

```bash
# Resize before dithering (--width 200)
magick input.jpg -resize 200x resized.png

# Scale up after dithering (--scale 4) — nearest neighbor to keep crisp pixels
magick dithered.png -filter point -resize 400% scaled.png
```

## Tint

didder has no tint option. Use ImageMagick:

```bash
# --tint "#e9633b"
magick dithered.png -colorspace Gray -fill "#e9633b" -tint 100 tinted.png
```

## Full example

Reproduce this:
```bash
uv run dither.py example-images/example-1.jpg --palette pico --algorithm bayer --order 2 --width 200 --scale 4
```

With didder + magick:
```bash
magick example-images/example-1.jpg -resize 200x /tmp/resized.png
didder --palette "141B1E 133940 B56D70 FFCCAA" -i /tmp/resized.png -o /tmp/dithered.png bayer 2x2
magick /tmp/dithered.png -filter point -resize 400% example-images/example-1_dithered.png
```
