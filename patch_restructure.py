#!/usr/bin/env python3
"""Build build_restructured_report.py from build_final_report.py.

Restructure (user direction, 2026-11-25):
- No Appendix A or B. All appendix content moves into headings 1-9.
- Query screenshots go in Query Results under each query, INSTEAD of
  writing the SQL out as text (each screenshot already shows the SQL
  followed by its result).
- Implementation figures (schema.sql, table list, keys, validation) move
  into Implementation Summary; the analytics view screenshot moves into
  Analytics-Ready Output.
- All figure captions are plain human wording: no "Figure A/B",
  no "SCREENSHOT", no "evidence screenshot".
- Team Contributions rewritten: Yuhui Xu first half, Deepthi second half.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "build_final_report.py"
DST = ROOT / "build_restructured_report.py"

text = SRC.read_text(encoding="utf-8")


def replace_once(old, new):
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"PATCH FAILED: found {count} occurrences of:\n{old[:140]}")
    text = text.replace(old, new)


# 1. Delete both appendix function definitions.
start = text.index("def add_query_appendix(document):")
end = text.index("def build_document():")
text = text[:start] + text[end:]

# 2. Delete the appendix calls.
replace_once(
    "    add_query_appendix(doc)\n    add_screenshot_appendix(doc)\n",
    "",
)

# 3. Implementation Summary: creation figures after the first paragraph,
# validation figure after the validation paragraph.
replace_once(
    '''        "the one-to-many and bridge relationships during loading; the composite NoteKeyword key prevents "
        "duplicate links between a note and a keyword."
    )''',
    '''        "the one-to-many and bridge relationships during loading; the composite NoteKeyword key prevents "
        "duplicate links between a note and a keyword."
    )
    doc.add_picture(str(EVIDENCE / "vscode_schema.png"), width=Inches(6.5))
    caption = doc.add_paragraph("Table definitions in schema.sql.")
    caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_picture(str(EVIDENCE / "shot1.png"), width=Inches(6.5))
    caption = doc.add_paragraph("Tables created in PostgreSQL.")
    caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_picture(str(EVIDENCE / "shot2.png"), width=Inches(6.5))
    caption = doc.add_paragraph("ClinicalNote - columns, keys, and constraints.")
    caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_picture(str(EVIDENCE / "shot3.png"), width=Inches(6.5))
    caption = doc.add_paragraph("NoteKeyword - bridge table keys.")
    caption.alignment = WD_ALIGN_PARAGRAPH.CENTER''',
)
# validation figure: after the validation paragraph.
replace_once(
    '''    doc.add_paragraph(
        "Post-load validation confirmed 120 ClinicalNote rows, 120 matching NoteText rows, 12 specialty "
        "labels, seven note types, 1,077 keywords, 1,324 bridge rows, and 779 sections. All imports succeeded "
        "with foreign-key constraints enabled; validate.sql repeats the checks and prints table row counts. "
        "The three document-type groupings are intentionally categorized separately from the nine clinical "
        "specialties."
    )''',
    '''    doc.add_paragraph(
        "Post-load validation confirmed 120 ClinicalNote rows, 120 matching NoteText rows, 12 specialty "
        "labels, seven note types, 1,077 keywords, 1,324 bridge rows, and 779 sections. All imports succeeded "
        "with foreign-key constraints enabled; validate.sql repeats the checks and prints table row counts. "
        "The three document-type groupings are intentionally categorized separately from the nine clinical "
        "specialties."
    )
    doc.add_picture(str(EVIDENCE / "shot4.png"), width=Inches(6.5))
    caption = doc.add_paragraph("Row counts and validation checks.")
    caption.alignment = WD_ALIGN_PARAGRAPH.CENTER''',
)

# 4. Query Results: screenshot under each query instead of written-out SQL.
# Anchors are the exact closing lines of each query paragraph (Q2 and Q4
# are f-strings, so the Export text sits mid-line there).
QUERY_SHOTS = [
    (
        '''        "Export: query1_specialty_note_counts.csv."
    )''',
        "shot5.png", "Query 1 result.",
    ),
    (
        '''        f"{q2_low['average_words']} words. Export: query2_average_words_by_specialty.csv."
    )''',
        "shot6.png", "Query 2 result.",
    ),
    (
        '''        "Export: query3_top_keywords.csv."
    )''',
        "shot7.png", "Query 3 result.",
    ),
    (
        '''        f"the longest is {longest['recount_words']} words. Export: query4_long_transcriptions.csv."
    )''',
        "shot8.png", "Query 4 result.",
    ),
    (
        '''        "Export: query5_note_types_by_specialty.csv."
    )''',
        "shot9.png", "Query 5 result.",
    ),
]
for anchor, image, caption_text in QUERY_SHOTS:
    replace_once(
        anchor,
        anchor
        + f'\n    doc.add_picture(str(EVIDENCE / "{image}"), width=Inches(6.5))'
        + f'\n    caption = doc.add_paragraph("{caption_text}")'
        + "\n    caption.alignment = WD_ALIGN_PARAGRAPH.CENTER",
    )

# 5. Analytics-Ready Output: view screenshot after the Figure 2 caption.
replace_once(
    '''    doc.add_picture(str(CHART_PATH), width=Inches(6.35))
    caption = doc.add_paragraph("Figure 2. Average recounted transcription words by clinical specialty.")
    caption.alignment = WD_ALIGN_PARAGRAPH.CENTER''',
    '''    doc.add_picture(str(CHART_PATH), width=Inches(6.35))
    caption = doc.add_paragraph("Figure 2. Average recounted transcription words by clinical specialty.")
    caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_picture(str(EVIDENCE / "shot10.png"), width=Inches(6.5))
    caption = doc.add_paragraph("Specialty summary from the analytics-ready view.")
    caption.alignment = WD_ALIGN_PARAGRAPH.CENTER''',
)

# 6. Team Contributions: Yuhui first half, Deepthi second half.
replace_once(
    '''    doc.add_heading("Team Contributions", level=1)
    doc.add_paragraph(
        "The names below are taken from the Week 2 paper. These are draft Week 5 contribution notes based on "
        "the responsibilities recorded there; both team members should revise them to describe the work each "
        "actually completed for this implementation."
    )
    doc.add_heading("Deepthi Venmanasseril Jainlal", level=2)
    doc.add_paragraph(
        "Draft contribution: Built on prior responsibility for profiling, analytical questions, data "
        "classification, and table design. For this assignment, describe the specific data-preparation and "
        "cleaning checks completed, the query or analytics interpretation contributed, and the report sections "
        "written or reviewed. Confirm or edit this draft before submission."
    )
    doc.add_heading("Yuhui Xu", level=2)
    doc.add_paragraph(
        "Draft contribution: Built on prior responsibility for keys, relationships, the ERD, data quality, "
        "and ethics. For this assignment, describe the specific PostgreSQL schema, key/relationship, validation, "
        "query-testing, and limitations work completed. Confirm or edit this draft before submission."
    )''',
    '''    doc.add_heading("Team Contributions", level=1)
    doc.add_paragraph(
        "The work was split into two halves: Yuhui Xu completed the first half of the assignment, and "
        "Deepthi Venmanasseril Jainlal completed the second half."
    )
    doc.add_heading("Yuhui Xu", level=2)
    doc.add_paragraph(
        "First half - design and implementation. Yuhui Xu revised the database design and the ERD, built "
        "the PostgreSQL tables with primary and foreign keys, and loaded and validated the data (Sections 1-3, "
        "including the table creation and row-count checks)."
    )
    doc.add_heading("Deepthi Venmanasseril Jainlal", level=2)
    doc.add_paragraph(
        "Second half - queries, analytics, and the report. Deepthi Venmanasseril Jainlal wrote the five "
        "analytical SQL queries and explained their results, built the analytics-ready specialty view and "
        "exported table, assessed the limitations, and assembled the final report with the terminal output "
        "(Sections 4-6, plus Conclusion and References)."
    )''',
)

DST.write_text(text, encoding="utf-8")
print(f"wrote {DST}")
bad = [w for w in ("Appendix", "SCREENSHOT", "evidence screenshot", "evidence_screenshots")
       if w in text]
if bad:
    print(f"WARNING: leftover wording: {bad}", file=sys.stderr)
    sys.exit(1)
print("patch checks passed: no Appendix / SCREENSHOT / evidence-screenshot wording left")
