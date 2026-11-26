#!/usr/bin/env python3
"""Remove the References section (user direction, 2026-11-25).

Also removes the one in-text citation that pointed at it, so no
citation is left dangling.
"""
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


# 1. Delete the References section (page break + heading + list + loop).
start = text.index('    doc.add_page_break()\n    doc.add_heading("References", level=1)')
end = text.index("    doc.save(DOCX_PATH)")
text = text[:start] + text[end:]

# 2. Drop the in-text citation that pointed at the removed list.
replace_once(
    '"on reparsing comma-separated spreadsheet cells (Boyle, 2018; Coronel & Morris, 2019)."',
    '"on reparsing comma-separated spreadsheet cells."',
)

DST.write_text(text, encoding="utf-8")
print(f"patched {DST}")
bad = [w for w in ("References", "Boyle", "Coronel") if w in text]
if bad:
    print(f"WARNING: leftover wording: {bad}", file=sys.stderr)
    sys.exit(1)
print("patch checks passed: no References / Boyle / Coronel wording left")
