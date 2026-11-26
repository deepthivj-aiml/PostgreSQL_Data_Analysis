#!/usr/bin/env bash
# Capture the 10 labeled terminal-evidence sections from the live database.
# Runs evidence_screenshots.sql once, non-interactively (empty answers to
# every \prompt), echoes each query, and splits the transcript at the
# SCREENSHOT markers into evidence/raw/shotN.txt files.
# Run from the project folder after the pipeline has loaded the database.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p evidence/raw

export COLUMNS=120
printf '\n\n\n\n\n\n\n\n\n\n\n\n' | sudo -u postgres psql -X -d week5_mtsamples \
    -v ON_ERROR_STOP=1 -e -f evidence_screenshots.sql \
    > evidence/raw/full_transcript.txt 2>&1

python3 - << 'PY'
import re
from pathlib import Path

text = Path("evidence/raw/full_transcript.txt").read_text(encoding="utf-8", errors="replace")
# Markers 2-10 follow a \prompt on the same line (no newline after the
# prompt), so match anywhere, not just at line starts. Text before a
# marker (the prompt line) stays with the previous section.
parts = re.split(r"SCREENSHOT (\d+) - ", text)
preamble = parts[0]
out = {}
for i in range(1, len(parts) - 1, 2):
    n = int(parts[i])
    body = f"SCREENSHOT {n} - " + parts[i + 1]
    if n == 1:
        body = preamble.rstrip() + "\n" + body
    out[n] = body.rstrip() + "\n"
for n, body in out.items():
    Path(f"evidence/raw/shot{n}.txt").write_text(body, encoding="utf-8")
    print(f"shot{n}: {len(body.splitlines())} lines")
print("sections:", sorted(out))
PY

for n in 1 2 3 4 5 6 7 8 9 10; do
    python3 render_terminal.py "evidence/raw/shot${n}.txt" \
        "Terminal — psql week5_mtsamples (evidence screenshot ${n})" \
        "evidence/shot${n}.png"
done
ls -lh evidence/*.png
