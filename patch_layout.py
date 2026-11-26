#!/usr/bin/env python3
"""Layout fix for build_restructured_report.py.

Tall images overflowed the page and captions got stranded alone:
- schema.sql (94 lines) and the validation output (66 lines) are split in
  two, so each half fits on a page.
- Every figure now goes through add_image(), which caps the height at
  7.8 inches and keeps the image paragraph with its caption.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "build_restructured_report.py"
DST = SRC  # patch in place; build_restructured_report.py is generated

text = SRC.read_text(encoding="utf-8")


def replace_once(old, new):
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"PATCH FAILED: found {count} occurrences of:\n{old[:140]}")
    text = text.replace(old, new)


# 1. PIL import + add_image helper (inserted after the docx imports).
replace_once(
    "from docx.shared import Inches, Pt\n",
    "from docx.shared import Inches, Pt\n"
    "from PIL import Image as PILImage\n"
    "\n"
    "\n"
    "def add_image(document, path, max_width=6.5, max_height=7.8):\n"
    '    """Add an image scaled to fit the page, keeping its caption with it."""\n'
    "    with PILImage.open(path) as image:\n"
    "        width_px, height_px = image.size\n"
    "    width = min(max_width, max_height * width_px / height_px)\n"
    "    paragraph = document.add_paragraph()\n"
    "    paragraph.paragraph_format.keep_with_next = True\n"
    "    paragraph.add_run().add_picture(str(path), width=Inches(width))\n"
    "    return paragraph\n",
)

# 2. ERD and chart through the helper.
replace_once(
    '    doc.add_picture(str(ERD_PATH), width=Inches(6.7))',
    '    add_image(doc, ERD_PATH)',
)
replace_once(
    '    doc.add_picture(str(CHART_PATH), width=Inches(6.35))',
    '    add_image(doc, CHART_PATH)',
)

# 3. schema.sql in two halves.
replace_once(
    '''    doc.add_picture(str(EVIDENCE / "vscode_schema.png"), width=Inches(6.5))
    caption = doc.add_paragraph("Table definitions in schema.sql.")
    caption.alignment = WD_ALIGN_PARAGRAPH.CENTER''',
    '''    add_image(doc, EVIDENCE / "vscode_schema_top.png")
    caption = doc.add_paragraph("Table definitions in schema.sql, part 1.")
    caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_image(doc, EVIDENCE / "vscode_schema_bottom.png")
    caption = doc.add_paragraph("Table definitions in schema.sql, part 2.")
    caption.alignment = WD_ALIGN_PARAGRAPH.CENTER''',
)

# 4. Validation output in two halves.
replace_once(
    '''    doc.add_picture(str(EVIDENCE / "shot4.png"), width=Inches(6.5))
    caption = doc.add_paragraph("Row counts and validation checks.")
    caption.alignment = WD_ALIGN_PARAGRAPH.CENTER''',
    '''    add_image(doc, EVIDENCE / "shot4a.png")
    caption = doc.add_paragraph("Validation checks.")
    caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_image(doc, EVIDENCE / "shot4b.png")
    caption = doc.add_paragraph("Row counts.")
    caption.alignment = WD_ALIGN_PARAGRAPH.CENTER''',
)

# 5. All remaining terminal screenshots through the helper.
new_text, count = re.subn(
    r'doc\.add_picture\(str\(EVIDENCE / "(shot\d+\.png)"\), width=Inches\(6\.5\)\)',
    r'add_image(doc, EVIDENCE / "\1")',
    text,
)
if count != 9:
    raise SystemExit(f"PATCH FAILED: expected 9 remaining shot images, found {count}")
text = new_text

DST.write_text(text, encoding="utf-8")
print(f"patched {DST} (8 shot images routed through add_image)")
