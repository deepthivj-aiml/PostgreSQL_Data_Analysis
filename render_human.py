#!/usr/bin/env python3
"""Re-render the captured terminal sections as plain terminal screenshots.

Reads evidence/raw/shotN.txt (the verbatim psql transcript for each
section) and renders it with render_terminal.py, but with:
- the "SCREENSHOT N - ..." marker line removed,
- the trailing "\\prompt" line ("Capture ..., then press Enter to
  continue:") removed,
- no window title bar and no window controls: the figure caption in the
  report labels each image,
- the shell prompt (working directory) and the command that was actually
  typed to produce the output added at the top of every screenshot, so
  the reader can see the terminal path and the query command.
The terminal output itself is unchanged and verbatim.
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "evidence" / "raw"

# The command that produced every section, as run from the project folder
# (see capture_evidence.sh). Shown at the top of each screenshot.
PROMPT_LINES = [
    "~/workspace/pg_data_analysis$ sudo -u postgres psql -X -d week5_mtsamples \\",
    ">   -v ON_ERROR_STOP=1 -e -f evidence_screenshots.sql",
]


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
    return "\n".join(PROMPT_LINES + lines) + "\n"


def main():
    for n in range(1, 11):
        src = RAW / f"shot{n}.txt"
        cleaned = RAW / f"shot{n}_human.txt"
        cleaned.write_text(clean(1, src.read_text(encoding="utf-8")), encoding="utf-8")
        out = ROOT / "evidence" / f"shot{n}.png"
        subprocess.run(
            [sys.executable, str(ROOT / "render_terminal.py"),
             str(cleaned), "", str(out)],
            check=True,
        )
    print("all 10 screenshots re-rendered without window chrome")

    # Split the validation screenshot in two so each half fits on a page:
    # part 1 = the validation checks (DO block), part 2 = the row counts.
    lines4 = (RAW / "shot4_human.txt").read_text(encoding="utf-8").split("\n")
    cut = next(i for i, ln in enumerate(lines4) if ln.startswith("SELECT 'medical_specialty'"))
    (RAW / "shot4a_human.txt").write_text("\n".join(lines4[:cut]).strip() + "\n", encoding="utf-8")
    (RAW / "shot4b_human.txt").write_text(
        "\n".join(PROMPT_LINES + lines4[cut:]).strip() + "\n", encoding="utf-8")
    for suffix in ("4a", "4b"):
        subprocess.run(
            [sys.executable, str(ROOT / "render_terminal.py"),
             str(RAW / f"shot{suffix}_human.txt"), "",
             str(ROOT / "evidence" / f"shot{suffix}.png")],
            check=True,
        )
    print("validation screenshot split into shot4a / shot4b")


if __name__ == "__main__":
    main()
