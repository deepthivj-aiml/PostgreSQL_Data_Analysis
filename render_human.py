#!/usr/bin/env python3
"""Re-render the captured terminal sections as human-titled screenshots.

Reads evidence/raw/shotN.txt (the verbatim psql transcript for each
section) and renders it with render_terminal.py, but with:
- the "SCREENSHOT N - ..." marker line removed (its title becomes the
  window title instead),
- the trailing "\\prompt" line ("Capture ..., then press Enter to
  continue:") removed,
- a plain human window title, e.g. "Query 1 - notes by specialty label".
The terminal output itself is unchanged and verbatim.
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "evidence" / "raw"

TITLES = {
    1: "Tables created in PostgreSQL",
    2: "ClinicalNote - columns, keys, and constraints",
    3: "NoteKeyword - bridge table keys",
    4: "Row counts and validation checks",
    5: "Query 1 - notes by specialty label",
    6: "Query 2 - average transcription length by clinical specialty",
    7: "Query 3 - top 20 keywords",
    8: "Query 4 - notes over 500 words",
    9: "Query 5 - note type counts by specialty label",
    10: "Analytics-ready view - specialty summary",
}


def clean(n, text):
    lines = text.split("\n")
    # drop the SCREENSHOT marker line (first line, or wherever it sits)
    lines = [ln for ln in lines if not re.match(r"SCREENSHOT \d+ - ", ln)]
    # drop the trailing \prompt echo line
    lines = [ln for ln in lines if not re.match(r"Capture .*press Enter to (continue|finish):", ln)]
    # drop a trailing "Evidence output sequence complete." line
    lines = [ln for ln in lines if ln.strip() != "Evidence output sequence complete."]
    while lines and lines[0].strip() == "":
        lines.pop(0)
    while lines and lines[-1].strip() == "":
        lines.pop()
    return "\n".join(lines) + "\n"


def main():
    for n in range(1, 11):
        src = RAW / f"shot{n}.txt"
        cleaned = RAW / f"shot{n}_human.txt"
        cleaned.write_text(clean(1, src.read_text(encoding="utf-8")), encoding="utf-8")
        out = ROOT / "evidence" / f"shot{n}.png"
        subprocess.run(
            [sys.executable, str(ROOT / "render_terminal.py"),
             str(cleaned), TITLES[n], str(out)],
            check=True,
        )
    print("all 10 screenshots re-rendered with human titles")

    # Split the validation screenshot in two so each half fits on a page:
    # part 1 = the validation checks (DO block), part 2 = the row counts.
    lines4 = (RAW / "shot4_human.txt").read_text(encoding="utf-8").split("\n")
    cut = next(i for i, ln in enumerate(lines4) if ln.startswith("SELECT 'medical_specialty'"))
    (RAW / "shot4a_human.txt").write_text("\n".join(lines4[:cut]).strip() + "\n", encoding="utf-8")
    (RAW / "shot4b_human.txt").write_text("\n".join(lines4[cut:]).strip() + "\n", encoding="utf-8")
    for suffix, title in (("4a", "Validation checks"), ("4b", "Row counts")):
        subprocess.run(
            [sys.executable, str(ROOT / "render_terminal.py"),
             str(RAW / f"shot{suffix}_human.txt"), title,
             str(ROOT / "evidence" / f"shot{suffix}.png")],
            check=True,
        )
    print("validation screenshot split into shot4a / shot4b")


if __name__ == "__main__":
    main()
