#!/usr/bin/env python3
"""
braille.py — convert a photo into Unicode braille art.

Usage:
    python braille.py IMAGE [options]

Example (what generated the README portrait):
    python braille.py me.jpg --crop 210 160 750 930 --cols 36 --contrast 1.35 --floor 70
"""
import argparse
from PIL import Image, ImageEnhance, ImageOps

# braille cell = 2 dots wide x 4 dots tall; (dx, dy) -> bit in the 0x2800 block
DOTS = [(0, 0, 0x01), (0, 1, 0x02), (0, 2, 0x04), (0, 3, 0x40),
        (1, 0, 0x08), (1, 1, 0x10), (1, 2, 0x20), (1, 3, 0x80)]


def to_braille(path, crop=None, cols=48, contrast=1.0, floor=0, threshold=None, invert=False):
    im = Image.open(path).convert("L")           # grayscale
    if crop:
        im = im.crop(crop)                       # (left, top, right, bottom)
    if contrast != 1.0:
        im = ImageEnhance.Contrast(im).enhance(contrast)
    if floor > 0:                                # crush near-blacks -> pure black
        im = im.point(lambda p: 0 if p < floor else p)  # keeps background empty
    if invert:
        im = ImageOps.invert(im)                 # for light-background photos: keeps the SUBJECT drawn, background empty

    # resize to the dot grid (2*cols wide, height rounded to a multiple of 4)
    dot_w = cols * 2
    dot_h = int(round(dot_w * im.height / im.width))
    dot_h -= dot_h % 4
    im = im.resize((dot_w, dot_h))

    if threshold is None:
        bw = im.convert("1")                     # Floyd–Steinberg dithering
    else:
        bw = im.point(lambda p: 255 if p > threshold else 0, mode="1")

    px = bw.load()
    lines = []
    for cy in range(0, bw.height, 4):
        row = []
        for cx in range(0, bw.width, 2):
            v = 0
            for dx, dy, bit in DOTS:
                if px[cx + dx, cy + dy]:         # white dot on
                    v |= bit
            row.append(chr(0x2800 + v))
        lines.append("".join(row).rstrip())
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="Convert a photo to Unicode braille art.")
    ap.add_argument("image", help="path to the source image")
    ap.add_argument("--crop", nargs=4, type=int, metavar=("L", "T", "R", "B"),
                    help="crop box in pixels (left top right bottom)")
    ap.add_argument("--cols", type=int, default=48, help="width in braille characters")
    ap.add_argument("--contrast", type=float, default=1.0, help="contrast multiplier")
    ap.add_argument("--floor", type=int, default=0,
                    help="pixels below this (0-255) become pure black — kills background speckle")
    ap.add_argument("--threshold", type=int, default=None,
                    help="hard cutoff instead of dithering (0-255)")
    ap.add_argument("--invert", action="store_true",
                    help="invert tones — use for light-background photos so the subject draws in dots, not the background")
    ap.add_argument("-o", "--out", help="write to file instead of stdout")
    args = ap.parse_args()

    art = to_braille(args.image, crop=tuple(args.crop) if args.crop else None,
                     cols=args.cols, contrast=args.contrast,
                     floor=args.floor, threshold=args.threshold, invert=args.invert)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(art)
    else:
        print(art)


if __name__ == "__main__":
    main()
