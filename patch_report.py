#!/usr/bin/env python3
"""Build build_final_report.py from build_report.py.

Patches, all verified against the live run on this machine:
- output file -> Week5_Assignment4_Final.docx
- PostgreSQL 18.7 -> 16.15 (the version actually installed and run here),
  including the documentation reference (18 -> 16)
- Appendix A: real terminal screenshots (evidence/shot5..shot9) replace the
  [PASTE SCREENSHOT ...] placeholders
- Appendix B: real screenshots replace the placeholders; the two page
  renders (report title page, contributions section) are pasted only when
  the PNGs exist (two-pass build), otherwise a note is left in place.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "build_report.py"
DST = ROOT / "build_final_report.py"

text = SRC.read_text(encoding="utf-8")


def replace_once(old, new):
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"PATCH FAILED: found {count} occurrences of:\n{old[:120]}")
    text = text.replace(old, new)


# 1. Output file
replace_once(
    'DOCX_PATH = ROOT / "Week5_Assignment4_APA_Report_Terminal_Evidence.docx"',
    'DOCX_PATH = ROOT / "Week5_Assignment4_Final.docx"\nEVIDENCE = ROOT / "evidence"',
)

# 2. PostgreSQL version actually run here
replace_once(
    '"The database was implemented and executed in PostgreSQL 18.7. schema.sql creates',
    '"The database was implemented and executed in PostgreSQL 16.15. schema.sql creates',
)
replace_once(
    '"PostgreSQL Global Development Group. (2026). PostgreSQL 18 documentation. https://www.postgresql.org/docs/18/"',
    '"PostgreSQL Global Development Group. (2026). PostgreSQL 16 documentation. https://www.postgresql.org/docs/16/"',
)

# 3. Appendix A intro
replace_once(
    '''        "Each query's question, executable SQL, result meaning, and terminal screenshot placeholder are below. "
        "The matching CSV exports and Excel workbook provide the complete results. Capture the labeled outputs "
        "with evidence_screenshots.sql and paste each image into its corresponding placeholder."''',
    '''        "Each query's question, executable SQL, result meaning, and terminal screenshot from the live run are below. "
        "The matching CSV exports and Excel workbook provide the complete results. The labeled outputs were "
        "captured with evidence_screenshots.sql."''',
)

# 4. Appendix A: paste the real screenshot instead of the placeholder
replace_once(
    '''        caption = document.add_paragraph(
            f"Figure A{number + 1}. Query {number + 1} terminal output."
        )
        caption.paragraph_format.keep_with_next = True
        placeholder = document.add_paragraph(
            f"[PASTE SCREENSHOT {number + 5} FROM evidence_screenshots.sql HERE.]"
        )
        placeholder.paragraph_format.left_indent = Inches(0.25)''',
    '''        caption = document.add_paragraph(
            f"Figure A{number + 1}. Query {number + 1} terminal output."
        )
        caption.paragraph_format.keep_with_next = True
        document.add_picture(str(EVIDENCE / f"shot{number + 5}.png"), width=Inches(6.5))''',
)

# 5. Appendix B intros
replace_once(
    '''        "Use this checklist to add terminal screenshots to the report. Do not submit a screenshot with "
        "truncated rows; maximize the VS Code terminal panel and capture multiple images for a result that "
        "does not fit on screen. Appendix A contains a separate placeholder for each query output."''',
    '''        "All screenshots in this appendix were captured from the live PostgreSQL run on this machine with "
        "evidence_screenshots.sql. Appendix A contains a separate screenshot for each query output."''',
)
replace_once(
    '''        "Workflow: run the project once in a fresh PostgreSQL database; then run the evidence_screenshots.sql "
        "script below. At each prompt, use Win+Shift+S to capture the terminal output, paste or save the image, "
        "return to the terminal, and press Enter to continue. Replace each placeholder below with the matching "
        "image. The report, ERD, SQL script, and exported workbook are also submission artifacts, not just screenshots."''',
    '''        "Workflow used: the project was run once in a fresh PostgreSQL database; then evidence_screenshots.sql "
        "was run and each labeled section was rendered as a terminal screenshot. The report, ERD, SQL script, and "
        "exported workbook are also submission artifacts, not just screenshots."''',
)

# 6. Appendix B evidence list -> (requirement, instruction, caption, [images])
old_list_start = text.index("    evidence = [")
old_list_end = text.index("    ]", old_list_start) + len("    ]")
new_list = '''    evidence = [
        ("Report", "Title page of this APA implementation report, captured from the built document.",
         "Figure B1. APA implementation report.", [EVIDENCE / "report_title.png"]),
        ("Revised ERD", "The implemented schema diagram (Figure 1).",
         "Figure B2. Revised PostgreSQL entity-relationship diagram.", [ERD_PATH]),
        ("SQL implementation", "schema.sql shown in the VS Code editor, with the CREATE TABLE and key definitions.",
         "Figure B3. PostgreSQL table definitions and constraints.", [EVIDENCE / "vscode_schema.png"]),
        ("Table creation", "SCREENSHOT 1 from evidence_screenshots.sql: the PostgreSQL table list.",
         "Figure B4. Tables created in PostgreSQL.", [EVIDENCE / "shot1.png"]),
        ("Keys and relationships", "SCREENSHOTS 2 and 3: ClinicalNote and NoteKeyword definitions.",
         "Figure B5. Primary keys, foreign keys, and bridge-table relationship.",
         [EVIDENCE / "shot2.png", EVIDENCE / "shot3.png"]),
        ("Loaded data and validation", "SCREENSHOT 4: row counts and validation checks.",
         "Figure B6. Loaded table row counts and integrity checks.", [EVIDENCE / "shot4.png"]),
        ("Five SQL queries", "SCREENSHOTS 5-9; the matching query images are in Appendix A as Figures A1-A5.",
         "Figures A1-A5. Executed SQL query results.", []),
        ("Analytics-ready output", "SCREENSHOT 10: v_specialty_analytics and the exported CSV.",
         "Figure B12. Analytics-ready specialty output.", [EVIDENCE / "shot10.png"]),
        ("Individual contributions", "The completed Team Contributions section of this report.",
         "Figure B13. Completed team contribution notes.", [EVIDENCE / "contributions.png"]),
    ]'''
text = text[:old_list_start] + new_list + text[old_list_end:]

# 7. Appendix B loop: paste images when present
replace_once(
    '''    for requirement, instruction, caption in evidence:
        document.add_heading(requirement, level=2)
        document.add_paragraph(instruction)
        label = document.add_paragraph(caption)
        label.paragraph_format.keep_with_next = True
        placeholder = document.add_paragraph(
            "[PASTE THE MATCHING SCREENSHOT HERE; remove this instruction after inserting it.]"
        )
        placeholder.paragraph_format.left_indent = Inches(0.25)
        placeholder.paragraph_format.space_after = Pt(8)''',
    '''    for requirement, instruction, caption, images in evidence:
        document.add_heading(requirement, level=2)
        document.add_paragraph(instruction)
        label = document.add_paragraph(caption)
        label.paragraph_format.keep_with_next = True
        for image in images:
            if image is not None and Path(image).exists():
                document.add_picture(str(image), width=Inches(6.5))
            else:
                note = document.add_paragraph(
                    "[Screenshot not yet generated - rerun the evidence capture.]"
                )
                note.paragraph_format.left_indent = Inches(0.25)
                note.paragraph_format.space_after = Pt(8)''',
)

# 8. Appendix B subtitle: screenshots are pasted now, not placeholders
replace_once(
    '"Screenshot workflow and evidence placeholders"',
    '"Screenshot workflow and evidence"',
)

DST.write_text(text, encoding="utf-8")
print(f"wrote {DST}")
if "18.7" in text or "PostgreSQL 18" in text:
    print("WARNING: stale PostgreSQL 18 reference remains", file=sys.stderr)
    sys.exit(1)
if "PASTE SCREENSHOT" in text or "PASTE THE MATCHING SCREENSHOT" in text:
    print("WARNING: placeholder text remains", file=sys.stderr)
    sys.exit(1)
print("patch checks passed: no 18.7 / placeholder text left")
