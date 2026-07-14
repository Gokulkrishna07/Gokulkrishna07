#!/usr/bin/env python3
"""
braille_svg.py — render braille-art text (from braille.py) as a colored SVG card.

Usage:
    python braille_svg.py portrait.txt -o portrait.svg
"""
import argparse
import html

CARD_BG = "#0d1117"
BORDER = "#30363d"
GRAD_FROM = "#38BDF8"
GRAD_TO = "#8B5CF6"

FONT_SIZE = 15
LINE_HEIGHT = FONT_SIZE * 1.05
CHAR_WIDTH = FONT_SIZE * 0.62
PAD = 28


def build_svg(lines):
    cols = max(len(l) for l in lines)
    text_w = cols * CHAR_WIDTH
    text_h = len(lines) * LINE_HEIGHT
    width = text_w + PAD * 2
    height = text_h + PAD * 2

    rows = []
    for i, line in enumerate(lines):
        y = PAD + (i + 1) * LINE_HEIGHT - (LINE_HEIGHT - FONT_SIZE)
        rows.append(
            f'<text x="{PAD}" y="{y:.1f}" fill="url(#grad)">{html.escape(line)}</text>'
        )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height:.0f}" viewBox="0 0 {width:.0f} {height:.0f}">
  <defs>
    <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{GRAD_FROM}"/>
      <stop offset="100%" stop-color="{GRAD_TO}"/>
    </linearGradient>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="1.6" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>
  <rect x="0.5" y="0.5" width="{width - 1:.0f}" height="{height - 1:.0f}" rx="14" fill="{CARD_BG}" stroke="{BORDER}"/>
  <g font-family="Cascadia Code, Consolas, 'Segoe UI Symbol', monospace" font-size="{FONT_SIZE}" filter="url(#glow)">
    {''.join(rows)}
  </g>
</svg>
'''


def main():
    ap = argparse.ArgumentParser(description="Render braille-art text as a colored SVG card.")
    ap.add_argument("textfile", help="path to braille art .txt file")
    ap.add_argument("-o", "--out", required=True, help="output .svg path")
    args = ap.parse_args()

    with open(args.textfile, encoding="utf-8") as f:
        lines = f.read().splitlines()

    with open(args.out, "w", encoding="utf-8") as f:
        f.write(build_svg(lines))


if __name__ == "__main__":
    main()
