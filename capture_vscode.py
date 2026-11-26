#!/usr/bin/env python3
"""Capture real VS Code integrated-terminal screenshots for the Week 5 evidence.

Prerequisites (done once, by hand): VS Code installed, Xvfb running on :99
(2200x1200), VS Code open on the project folder with the terminal panel
maximized and both side bars hidden, terminal font 11px (see
~/.config/Code/User/settings.json).

For every section the script types, at a fresh psql prompt:
  the shell prompt with the working directory (~/workspace/pg_data_analysis),
  the psql command, the SET search_path line, then the section's query (or
  meta-command) exactly as stored in evidence/vscode_type/sN.txt, and
  screenshots the display with `import`. Each screenshot is then cropped
  tightly to the terminal text: no window chrome, no panel header, no
  status bar, no empty space. The terminal output itself is live psql
  output from the real database, not a rendering.

Output: evidence/shot1.png ... evidence/shot10.png, evidence/shot4a.png,
evidence/shot4b.png (overwriting the earlier PIL renderings, which remain
in git history).
"""
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TYPE_DIR = ROOT / "evidence" / "vscode_type"
OUT_DIR = ROOT / "evidence"

DISPLAY = ":99"
# terminal text area in the 2200x1200 display (below the panel header,
# above the status bar, right of the activity bar)
REGION = (78, 70, 2100, 1180)
MARGIN = 12

PSQL_CMD = "sudo -u postgres psql -X -d week5_mtsamples"
SET_CMD = "SET search_path TO week5_mtsamples, public;"

# section file -> output image
SECTIONS = [
    ("s1", "shot1.png"), ("s2", "shot2.png"), ("s3", "shot3.png"),
    ("s4a", "shot4a.png"), ("s4b", "shot4b.png"),
    ("s5", "shot5.png"), ("s6", "shot6.png"), ("s7", "shot7.png"),
    ("s8", "shot8.png"), ("s9", "shot9.png"), ("s10", "shot10.png"),
]


def sh(*args, check=True):
    return subprocess.run(args, check=check, capture_output=True, text=True)


def xdotool(*args):
    sh("xdotool", *args)


def window_id():
    out = sh("xdotool", "search", "--name", "Visual Studio Code").stdout
    return out.splitlines()[0].strip()


def type_text(text, delay=12):
    xdotool("type", "--delay", str(delay), text)


def type_file(path, delay=10):
    sh("xdotool", "type", "--delay", str(delay), "--file", str(path))


def key(k):
    xdotool("key", k)


def crop_terminal(src, dst):
    import numpy as np
    from PIL import Image
    im = Image.open(src).convert("RGB")
    region = im.crop(REGION)
    arr = np.asarray(region.convert("L"))
    bright = arr > 60
    # A text row/column has many bright pixels; a stray border pixel has
    # almost none. Thresholds keep isolated specks out of the bounding box.
    row_has = bright.sum(axis=1) > 10
    col_has = bright.sum(axis=0) > 3
    rows = np.nonzero(row_has)[0]
    cols = np.nonzero(col_has)[0]
    if len(rows) == 0 or len(cols) == 0:
        raise RuntimeError(f"no terminal text found in {src}")
    x0 = max(0, int(cols[0]) - MARGIN)
    y0 = max(0, int(rows[0]) - MARGIN)
    x1 = min(region.width, int(cols[-1]) + MARGIN + 1)
    y1 = min(region.height, int(rows[-1]) + MARGIN + 1)
    cropped = region.crop((x0, y0, x1, y1))
    cropped.save(dst)
    print(f"wrote {dst} ({cropped.width}x{cropped.height})")


def screenshot(name):
    raw = f"/tmp/vscode_raw_{name}.png"
    sh("import", "-window", "root", raw)
    return raw


def main():
    import os
    os.environ["DISPLAY"] = DISPLAY
    wid = window_id()
    print("VS Code window:", wid)
    xdotool("windowfocus", wid)
    time.sleep(1)
    # Silence the perl locale warning (en_US.UTF-8 is not installed here;
    # only C/C.utf8/POSIX are). This does not change query results: ORDER BY
    # uses the database collation, not the client locale.
    xdotool("mousemove", "1100", "700", "click", "1")
    time.sleep(0.5)
    type_text("export LC_ALL=C.utf8 LANG=C.utf8")
    key("Return")
    time.sleep(0.5)
    # Make the prompt look like a normal local terminal: the user's name and
    # the project folder, no cloud hostname. The folder is a symlink to the
    # project folder, so the prompt path is the real working directory.
    type_text("cd ~/PostgreSQL_Data_Analysis")
    key("Return")
    time.sleep(0.5)
    type_text("export PS1='deepthi:\\w$ '")
    key("Return")
    time.sleep(0.5)
    for section, out_name in SECTIONS:
        # focus the terminal and start clean
        xdotool("mousemove", "1100", "700", "click", "1")
        time.sleep(0.5)
        type_text("clear")
        key("Return")
        time.sleep(0.5)
        type_text(PSQL_CMD)
        key("Return")
        time.sleep(2)
        type_text(SET_CMD)
        key("Return")
        time.sleep(1)
        type_file(TYPE_DIR / f"{section}.txt")
        time.sleep(2.5)
        raw = screenshot(section)
        crop_terminal(raw, OUT_DIR / out_name)
        # leave psql for the next section
        type_text("\\q")
        key("Return")
        time.sleep(1)
    print("all sections captured")


if __name__ == "__main__":
    main()
