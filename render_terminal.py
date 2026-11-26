#!/usr/bin/env python3
"""Render a captured terminal transcript as a terminal screenshot (PNG).

Usage: python3 render_terminal.py <input.txt> <title> <output.png>
The input must be the real output of a terminal/psql session. Lines are
rendered verbatim (no wrapping) in DejaVu Sans Mono on a dark background,
with no window title bar and no window controls: the figure caption in the
report labels the image, and the transcript itself starts with the shell
prompt (working directory) and the command that was typed, so the reader
can see where the command ran and what produced the output. The <title>
argument is accepted for compatibility and ignored.
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
FONT_BOLD_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
FONT_SIZE = 15
LINE_HEIGHT = 22
PAD_X = 16
PAD_TOP = 14
PAD_BOTTOM = 16

BG = (30, 30, 30)
TEXT = (212, 212, 212)
COMMAND = (255, 255, 255)
PROMPT = (120, 220, 120)


def main():
    src, title, out = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3])
    lines = src.read_text(encoding="utf-8", errors="replace").rstrip("\n").split("\n")
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    bold = ImageFont.truetype(FONT_BOLD_PATH, FONT_SIZE)
    # measure with the widest glyph estimate: use getlength per line
    max_w = max((font.getlength(ln) for ln in lines), default=0)
    width = int(max_w) + PAD_X * 2
    width = max(width, 480)
    height = PAD_TOP + len(lines) * LINE_HEIGHT + PAD_BOTTOM

    img = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(img)

    y = PAD_TOP
    for ln in lines:
        if "$ " in ln or ln.startswith("> "):
            draw.text((PAD_X, y), ln, font=bold, fill=COMMAND)
        elif ln.startswith("week5_mtsamples=#") or ln.startswith("week5_mtsamples-#"):
            draw.text((PAD_X, y), ln, font=bold, fill=PROMPT)
        else:
            draw.text((PAD_X, y), ln, font=font, fill=TEXT)
        y += LINE_HEIGHT

    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out)
    print(f"wrote {out} ({width}x{height}, {len(lines)} lines)")


if __name__ == "__main__":
    main()
