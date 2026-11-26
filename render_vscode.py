#!/usr/bin/env python3
"""Render schema.sql as a VS Code editor screenshot (PNG).

Draws the real file content verbatim with line numbers and simple SQL
syntax highlighting in a VS Code dark-theme window. Used for Appendix B,
Figure B3, because the report is built on a headless machine with no GUI
to capture VS Code in.
"""
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "schema.sql"
OUT = ROOT / "evidence" / "vscode_schema.png"

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
SIZE = 13
LINE_H = 19
GUTTER_W = 52
PAD_X = 12
TAB_H = 36
TITLE_H = 30

BG = (30, 30, 30)
GUTTER_BG = (30, 30, 30)
GUTTER_FG = (133, 133, 133)
DEFAULT = (212, 212, 212)
KEYWORD = (86, 156, 214)
STRING = (206, 145, 120)
NUMBER = (181, 206, 168)
COMMENT = (106, 153, 85)
TYPE = (78, 201, 176)

KEYWORDS = {
    "CREATE", "SCHEMA", "SET", "TABLE", "PRIMARY", "KEY", "FOREIGN",
    "REFERENCES", "NOT", "NULL", "UNIQUE", "CHECK", "INDEX", "VIEW",
    "AS", "SELECT", "FROM", "WHERE", "GROUP", "BY", "LEFT", "JOIN",
    "ON", "AND", "OR", "IN", "CASCADE", "DELETE", "USING",
}
TYPES = {"smallint", "integer", "varchar", "text", "boolean"}

TOKEN_RE = re.compile(
    r"(?P<comment>--[^\n]*)"
    r"|(?P<string>'(?:[^']|'')*')"
    r"|(?P<number>\b\d+(?:\.\d+)?\b)"
    r"|(?P<word>[A-Za-z_][A-Za-z0-9_]*)"
    r"|(?P<other>.)",
    re.DOTALL,
)


def highlight(line):
    """Return a list of (text, color) segments for one line."""
    segments = []
    for m in TOKEN_RE.finditer(line):
        kind = m.lastgroup
        text = m.group()
        if kind == "comment":
            segments.append((text, COMMENT))
        elif kind == "string":
            segments.append((text, STRING))
        elif kind == "number":
            segments.append((text, NUMBER))
        elif kind == "word":
            if text.upper() in KEYWORDS:
                segments.append((text, KEYWORD))
            elif text.lower() in TYPES:
                segments.append((text, TYPE))
            else:
                segments.append((text, DEFAULT))
        else:
            segments.append((text, DEFAULT))
    return segments


def render(lines, start, end, out_path, title):
    """Render lines[start:end] (1-based, end exclusive) as one editor screenshot."""
    subset = lines[start - 1:end - 1]
    font = ImageFont.truetype(FONT, SIZE)
    bold = ImageFont.truetype(FONT_BOLD, SIZE)
    max_w = max((font.getlength(ln) for ln in subset), default=0)
    width = GUTTER_W + int(max_w) + PAD_X * 2
    height = TITLE_H + TAB_H + len(subset) * LINE_H + 12

    img = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, width, TITLE_H], fill=(60, 60, 60))
    draw.text((width // 2 - 180, 7), title,
              font=font, fill=(204, 204, 204))
    draw.rectangle([0, TITLE_H, width, TITLE_H + TAB_H], fill=(37, 37, 38))
    draw.rectangle([0, TITLE_H, 150, TITLE_H + TAB_H], fill=(30, 30, 30))
    draw.text((14, TITLE_H + 9), "schema.sql", font=font, fill=(255, 255, 255))
    draw.text((128, TITLE_H + 9), "×", font=font, fill=(150, 150, 150))

    y = TITLE_H + TAB_H + 6
    for i, line in enumerate(subset, start=start):
        draw.text((8, y), f"{i:>4}", font=font, fill=GUTTER_FG)
        x = GUTTER_W
        for text, color in highlight(line):
            draw.text((x, y), text, font=font, fill=color)
            x += font.getlength(text)
        y += LINE_H

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path)
    print(f"wrote {out_path} ({width}x{height}, {len(subset)} lines)")


def main():
    lines = SRC.read_text(encoding="utf-8").rstrip("\n").split("\n")
    total = len(lines)
    # Full file, plus two halves so each fits on a report page.
    render(lines, 1, total + 1, OUT, "schema.sql — PostgreSQL_Data_Analysis — Visual Studio Code")
    render(lines, 1, 47, ROOT / "evidence" / "vscode_schema_top.png",
           "schema.sql — PostgreSQL_Data_Analysis — Visual Studio Code")
    render(lines, 47, total + 1, ROOT / "evidence" / "vscode_schema_bottom.png",
           "schema.sql — PostgreSQL_Data_Analysis — Visual Studio Code")


if __name__ == "__main__":
    main()
