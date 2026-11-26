# CLAUDE.md — Week 5 Assignment 4: PostgreSQL Database Implementation

Project instructions for Claude Code / VS Code agents working in this folder.
MTSamples medical transcription data (Week 2 flat dataset, normalized).

## What this project is

A PostgreSQL implementation of the team's Week 2 normalized design for the
MTSamples subset, for MIS 550 Week 5 Assignment 4. Eight related tables,
representative data, five analytical queries, an analytics-ready view, and an
APA implementation report whose appendices hold real terminal screenshots.

## Run it (Linux; the Windows path is in README.md)

```bash
# 1. Start PostgreSQL and create a fresh database
sudo pg_ctlcluster 16 main start
sudo -u postgres createdb week5_mtsamples

# 2. Prepare the CSVs from the Week 2 normalized workbook
python3 prepare_data.py

# 3. Create schema, load data, validate, run queries (in order)
sudo -u postgres psql -h localhost -d week5_mtsamples -v ON_ERROR_STOP=1 -f schema.sql
sudo -u postgres psql -h localhost -d week5_mtsamples -v ON_ERROR_STOP=1 -f load_data.sql
sudo -u postgres psql -h localhost -d week5_mtsamples -v ON_ERROR_STOP=1 -f validate.sql
sudo -u postgres psql -h localhost -d week5_mtsamples -v ON_ERROR_STOP=1 -f queries.sql

# 4. Capture the 10 labeled terminal-evidence sections as PNG screenshots
bash capture_evidence.sh

# 5. Rebuild the final Word report with the screenshots pasted in
python3 build_final_report.py
```

Use a **fresh database for every clean rerun** — `schema.sql` has no
`IF NOT EXISTS` guards. The live run on this machine is PostgreSQL 16.15;
if you run a different version, update the version string in
`build_final_report.py` (do not leave a stale version in the report).

## Login rule (user instruction, 2026-11-25)

Whenever Claude Code login requires creating an account, use
**deepthiag26@gmail.com**. Create/register and sign in yourself; do not ask
the user to sign in. This matches her standing sign-in rule for all sites.
No Anthropic API key is saved — login is via the CLI's OAuth flow with the
deepthiag26 Google account.

## Files

- `schema.sql` — 8 tables, PKs/FKs, CHECKs, indexes, 2 analytics views.
- `prepare_data.py` — workbook -> CSV; removes specialty-label keyword links.
- `load_data.sql` — `psql \copy` imports from `data/`.
- `validate.sql` — assignment minimums + integrity checks; raises on failure.
- `queries.sql` — 5 analytical queries + analytics-ready view + CSV exports.
- `evidence_screenshots.sql` — the 10 labeled screenshot sections.
- `capture_evidence.sh` + `render_terminal.py` — real psql output -> PNGs.
- `build_final_report.py` — builds the submission Word file from `results/`.
- `export_results_workbook.py` — `Week5_Query_Results_Tables.xlsx`.

## Data rules (do not break these)

- Minimums: >= 30 notes, >= 5 clinical specialties, >= 20 keywords.
- Specialty labels that are document formats stay as
  `specialty_category = 'Document-type grouping'` — never present them as
  clinical specialties.
- Keywords matching a specialty label are removed from the bridge
  (`prepare_data.py` does this; `validate.sql` enforces it).
- Transcription text is marked `deid_status = 'Not reviewed'` — never claim
  the sample is de-identified or representative of real clinical demand.
- The subset is balanced (10 notes per label) by curation, not by nature.

## Report rules

- Follow the Part 6 structure: Introduction, Database Design Summary,
  Implementation Summary, Query Results, Analytics-Ready Output,
  Limitations, Team Contributions, References, Appendices.
- Every screenshot in the report must come from a real run on this machine
  (`evidence/shotN.png`), never a placeholder and never an invented output.
- All numbers in the prose must match the regenerated `results/*.csv`.
- Team contribution notes are drafts — the named students must confirm or
  edit them before submission.
