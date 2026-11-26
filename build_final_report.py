import csv
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
DOCX_PATH = ROOT / "Week5_Assignment4_Final.docx"
EVIDENCE = ROOT / "evidence"
ERD_PATH = ROOT / "Week5_PostgreSQL_ERD.png"
CHART_PATH = ROOT / "Week5_Specialty_Average_Word_Count.png"


def read_csv(name):
    with (RESULTS / name).open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def make_erd():
    fig, ax = plt.subplots(figsize=(13, 7.2))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    nodes = {
        "MedicalSpecialty": (0.04, 0.72, 0.25, 0.18,
                             "MedicalSpecialty\nPK specialty_id\nUQ specialty_name\nspecialty_category"),
        "NoteType": (0.04, 0.41, 0.25, 0.17,
                     "NoteType\nPK note_type_id\nUQ note_type_name\nis_inferred"),
        "DataSource": (0.04, 0.12, 0.25, 0.17,
                       "DataSource\nPK source_id\nsource_name, source_url"),
        "ClinicalNote": (0.38, 0.40, 0.28, 0.27,
                         "ClinicalNote\nPK note_id; UQ source_row_id\nFK specialty_id, note_type_id\nFK source_id; sample metadata"),
        "NoteText": (0.73, 0.75, 0.25, 0.16,
                     "NoteText\nPK/FK note_id\ntranscription, lengths\ndeid_status"),
        "NoteSection": (0.73, 0.52, 0.25, 0.15,
                        "NoteSection\nPK section_id; FK note_id\nsection_order, header, text"),
        "NoteKeyword": (0.72, 0.25, 0.27, 0.16,
                        "NoteKeyword\nPK/FK note_id, keyword_id\nkeyword_position"),
        "Keyword": (0.72, 0.04, 0.27, 0.15,
                    "Keyword\nPK keyword_id\nUQ keyword_term"),
    }

    edges = [
        ("MedicalSpecialty", "ClinicalNote", "1 : many"),
        ("NoteType", "ClinicalNote", "1 : many"),
        ("DataSource", "ClinicalNote", "1 : many"),
        ("ClinicalNote", "NoteText", "1 : 1"),
        ("ClinicalNote", "NoteSection", "1 : many"),
        ("ClinicalNote", "NoteKeyword", "1 : many"),
        ("Keyword", "NoteKeyword", "1 : many"),
    ]

    def anchor(node, toward):
        x, y, w, h, _ = nodes[node]
        tx, ty, tw, th, _ = nodes[toward]
        cx, cy = x + w / 2, y + h / 2
        tcx, tcy = tx + tw / 2, ty + th / 2
        dx, dy = tcx - cx, tcy - cy
        if abs(dx) / w > abs(dy) / h:
            return (x + w if dx > 0 else x, cy)
        return (cx, y + h if dy > 0 else y)

    for source, target, label in edges:
        start = anchor(source, target)
        end = anchor(target, source)
        ax.annotate("", xy=end, xytext=start,
                    arrowprops={"arrowstyle": "->", "color": "#566573",
                                "linewidth": 1.3, "shrinkA": 1, "shrinkB": 1})
        mx, my = (start[0] + end[0]) / 2, (start[1] + end[1]) / 2
        ax.text(mx, my + 0.018, label, fontsize=8, ha="center",
                color="#34495e", bbox={"facecolor": "white", "edgecolor": "none", "pad": 1})

    for name, (x, y, w, h, text) in nodes.items():
        color = "#d6eaf8" if name == "ClinicalNote" else (
            "#e8f6f3" if name in ("NoteKeyword", "Keyword") else "#f7f9f9"
        )
        box = FancyBboxPatch((x, y), w, h,
                             boxstyle="round,pad=0.008,rounding_size=0.012",
                             linewidth=1.1, edgecolor="#2c3e50", facecolor=color)
        ax.add_patch(box)
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
                fontsize=8.6, family="DejaVu Sans", linespacing=1.3)

    ax.set_title("PostgreSQL relational schema", fontsize=15, weight="bold", pad=12)
    fig.tight_layout()
    fig.savefig(ERD_PATH, dpi=220, bbox_inches="tight")
    plt.close(fig)


def make_chart():
    rows = read_csv("query2_average_words_by_specialty.csv")
    rows.sort(key=lambda row: float(row["average_words"]))
    labels = [row["specialty_name"] for row in rows]
    values = [float(row["average_words"]) for row in rows]
    fig, ax = plt.subplots(figsize=(9, 4.8))
    bars = ax.barh(labels, values, color="#2471a3")
    ax.bar_label(bars, fmt="%.1f", padding=4, fontsize=8)
    ax.set_xlabel("Average transcription length (recounted words)")
    ax.set_title("Average transcription length by clinical specialty")
    ax.set_xlim(0, max(values) * 1.18)
    ax.grid(axis="x", linestyle=":", alpha=0.4)
    ax.spines[["top", "right", "left"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(CHART_PATH, dpi=200, bbox_inches="tight")
    plt.close(fig)


def set_page_number(paragraph):
    paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = paragraph.add_run()
    field = OxmlElement("w:fldSimple")
    field.set(qn("w:instr"), "PAGE")
    run._r.addnext(field)


def add_query_appendix(document):
    query_blocks = []
    current_title = None
    current_lines = []
    for line in (ROOT / "queries.sql").read_text(encoding="utf-8").splitlines():
        match = re.match(r"-- Query \d+: (.*)", line)
        if match:
            if current_title:
                query_blocks.append((current_title, "\n".join(current_lines).strip()))
            current_title = match.group(1)
            current_lines = []
        elif current_title and line.startswith("-- Analytics-ready output"):
            query_blocks.append((current_title, "\n".join(current_lines).strip()))
            current_title = None
            current_lines = []
        elif current_title:
            current_lines.append(line)
    if current_title:
        query_blocks.append((current_title, "\n".join(current_lines).strip()))

    files = [
        "query1_specialty_note_counts.csv",
        "query2_average_words_by_specialty.csv",
        "query3_top_keywords.csv",
        "query4_long_transcriptions.csv",
        "query5_note_types_by_specialty.csv",
    ]
    explanations = [
        "All 12 source specialty labels have 10 notes. The three document-type groupings are shown separately rather than treated as clinical specialties.",
        "Orthopedic has the highest average among the nine clinical-specialty labels (485.4 words); Radiology has the lowest (263.7).",
        "MRI is the most frequent cleaned keyword (7 notes). Specialty labels were removed from the keyword bridge before this query.",
        "There are 26 records over 500 recounted words; the longest is 845 words. These are sample transcription lengths, not clinical acuity measures.",
        "The output shows the inferred note-type distribution by source label and can be filtered or pivoted for document-mix analysis.",
    ]

    document.add_page_break()
    document.add_heading("Appendix A", level=1)
    document.add_paragraph("Executed SQL queries and complete exported results").alignment = (
        WD_ALIGN_PARAGRAPH.CENTER
    )
    document.add_paragraph(
        "Each query's question, executable SQL, result meaning, and terminal screenshot from the live run are below. "
        "The matching CSV exports and Excel workbook provide the complete results. The labeled outputs were "
        "captured with evidence_screenshots.sql."
    )
    for number, (title, sql) in enumerate(query_blocks):
        document.add_heading(f"Query {number + 1}. {title}", level=2)
        code = document.add_paragraph()
        code.paragraph_format.left_indent = Inches(0.18)
        code.paragraph_format.space_after = Pt(4)
        run = code.add_run(sql)
        run.font.name = "Consolas"
        run.font.size = Pt(7.5)
        document.add_paragraph(f"Result file: results\\{files[number]}")
        document.add_paragraph(explanations[number])
        caption = document.add_paragraph(
            f"Figure A{number + 1}. Query {number + 1} terminal output."
        )
        caption.paragraph_format.keep_with_next = True
        document.add_picture(str(EVIDENCE / f"shot{number + 5}.png"), width=Inches(6.5))
        if number in (1, 3):
            document.add_page_break()


def add_screenshot_appendix(document):
    evidence = [
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
    ]

    document.add_page_break()
    document.add_heading("Appendix B", level=1)
    title = document.add_paragraph("Screenshot workflow and evidence")
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    document.add_paragraph(
        "All screenshots in this appendix were captured from the live PostgreSQL run on this machine with "
        "evidence_screenshots.sql. Appendix A contains a separate screenshot for each query output."
    )
    document.add_paragraph(
        "Workflow used: the project was run once in a fresh PostgreSQL database; then evidence_screenshots.sql "
        "was run and each labeled section was rendered as a terminal screenshot. The report, ERD, SQL script, and "
        "exported workbook are also submission artifacts, not just screenshots."
    )
    for requirement, instruction, caption, images in evidence:
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
                note.paragraph_format.space_after = Pt(8)


def build_document():
    analytics = read_csv("analytics_ready_specialty.csv")
    clinical = [row for row in analytics if row["specialty_category"] == "Clinical specialty"]
    query2 = read_csv("query2_average_words_by_specialty.csv")
    query3 = read_csv("query3_top_keywords.csv")
    query4 = read_csv("query4_long_transcriptions.csv")
    q2_top = max(query2, key=lambda row: float(row["average_words"]))
    q2_low = min(query2, key=lambda row: float(row["average_words"]))
    top_keyword = query3[0]
    longest = max(query4, key=lambda row: int(row["recount_words"]))

    doc = Document()
    section = doc.sections[0]
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)
    styles = doc.styles
    styles["Normal"].font.name = "Times New Roman"
    styles["Normal"].font.size = Pt(12)
    styles["Normal"].paragraph_format.space_after = Pt(0)
    styles["Normal"].paragraph_format.line_spacing = 2
    for style_name in ("Heading 1", "Heading 2", "Heading 3"):
        styles[style_name].font.name = "Times New Roman"
        styles[style_name].font.color.rgb = None
    styles["Heading 1"].font.size = Pt(12)
    styles["Heading 1"].font.bold = True
    styles["Heading 1"].paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    styles["Heading 1"].paragraph_format.keep_with_next = True
    styles["Heading 1"].paragraph_format.space_before = Pt(0)
    styles["Heading 1"].paragraph_format.space_after = Pt(0)
    styles["Heading 2"].font.size = Pt(12)
    styles["Heading 2"].font.bold = True
    styles["Heading 2"].paragraph_format.keep_with_next = True
    styles["Heading 2"].paragraph_format.space_before = Pt(0)
    styles["Heading 2"].paragraph_format.space_after = Pt(0)
    set_page_number(section.header.paragraphs[0])

    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.paragraph_format.space_before = Pt(48)
    run = title.add_run("Week 5 Assignment 4\nPostgreSQL Database Implementation")
    run.bold = True
    run.font.name = "Times New Roman"
    run.font.size = Pt(12)
    for line in (
        "MTSamples Medical Transcription Dataset",
        "",
        "[Team Name]",
        "Deepthi Venmanasseril Jainlal and Yuhui Xu",
        "MIS 550: Big Data Analytics",
        "[Instructor Name]",
        "November 25, 2026",
    ):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run(line)
    doc.add_page_break()

    body_title = doc.add_paragraph()
    body_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    body_title.paragraph_format.space_after = Pt(0)
    body_title.paragraph_format.line_spacing = 2
    body_title_run = body_title.add_run(
        "Week 5 Assignment 4: PostgreSQL Database Implementation"
    )
    body_title_run.bold = True
    body_title_run.font.name = "Times New Roman"
    body_title_run.font.size = Pt(12)
    doc.add_heading("Introduction", level=1)
    doc.add_paragraph(
        "This implementation turns the Week 2 flat MTSamples subset into a PostgreSQL relational database "
        "for repeatable querying and analytics. The design keeps note metadata, category lookups, keywords, "
        "and transcription text in related tables so that category counts and keyword analysis do not depend "
        "on reparsing comma-separated spreadsheet cells (Boyle, 2018; Coronel & Morris, 2019)."
    )
    doc.add_heading("Database Design Summary", level=1)
    doc.add_heading("Revised design", level=2)
    doc.add_paragraph(
        "The implementation carries forward the Week 2 normalized design and builds eight tables: "
        "MedicalSpecialty, NoteType, DataSource, ClinicalNote, NoteText, Keyword, NoteKeyword, and NoteSection. "
        "ClinicalNote is the central entity. Specialty, note type, and source each have one-to-many relationships "
        "to notes; NoteText has a one-to-one relationship; NoteSection has a one-to-many relationship. "
        "NoteKeyword resolves the many-to-many relationship between notes and keywords."
    )
    doc.add_paragraph(
        "Two adjustments were made for implementation. First, specialty labels that actually describe document "
        "formats are marked as “Document-type grouping,” preserving source values without presenting them as "
        "clinical specialties. Second, keyword associations matching a specialty label were removed from the "
        "keyword bridge to prevent category names from inflating keyword frequencies. Source row identifiers "
        "remain unique for lineage, and transcription text stays separate with a full-text search index."
    )
    doc.add_picture(str(ERD_PATH), width=Inches(6.7))
    caption = doc.add_paragraph("Figure 1. Implemented PostgreSQL schema and relationship cardinalities.")
    caption.alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_page_break()
    doc.add_heading("Implementation Summary", level=1)
    doc.add_paragraph(
        "The database was implemented and executed in PostgreSQL 16.15. schema.sql creates the schema, "
        "typed tables, primary and foreign keys, uniqueness and range checks, supporting indexes, and two "
        "analytics views. load_data.sql imports the staged CSV files with psql \\copy. The foreign keys enforce "
        "the one-to-many and bridge relationships during loading; the composite NoteKeyword key prevents "
        "duplicate links between a note and a keyword."
    )
    doc.add_paragraph(
        "The source was the Week 2 normalized preview workbook, itself derived from Student_Flat_Dataset. "
        "The database load contains 120 notes, 12 source specialty labels (nine clinical specialties and three "
        "document-type groupings), seven inferred note types, one source record, 1,077 cleaned keywords, "
        "1,324 note-keyword links, and 779 extracted note sections. The 120 NoteText records remain separate "
        "from note metadata. Thirteen extracted sections had no body text; those missing values are retained "
        "as NULL instead of being replaced with invented content."
    )
    doc.add_paragraph(
        "The existing normalized workbook supplied split and standardized lookups, parsed sections, and "
        "word-count metadata. During preparation, the load script removed 121 specialty-label keyword links "
        "and renumbered the remaining keyword keys consistently. The original source word count is retained "
        "in ClinicalNote; analytics use recount_words and character_length from NoteText to make the chosen "
        "counting measure explicit. The de-identification status remains “Not reviewed”; this sample database "
        "is not represented as a de-identified clinical system."
    )
    doc.add_paragraph(
        "Post-load validation confirmed 120 ClinicalNote rows, 120 matching NoteText rows, 12 specialty "
        "labels, seven note types, 1,077 keywords, 1,324 bridge rows, and 779 sections. All imports succeeded "
        "with foreign-key constraints enabled; validate.sql repeats the checks and prints table row counts. "
        "The three document-type groupings are intentionally categorized separately from the nine clinical "
        "specialties."
    )

    doc.add_page_break()
    doc.add_heading("Query Results", level=1)
    doc.add_paragraph(
        "Five SQL queries were run. The complete SQL is in queries.sql, and each result is exported as a CSV "
        "in results. Together, they demonstrate joins, grouping, aggregate functions, filters, and outputs "
        "that can be used for operational review or visualization."
    )
    doc.add_heading("Query 1: Notes by specialty label", level=2)
    doc.add_paragraph(
        "Question: How many sampled notes are recorded under each label and category? "
        "Result: All 12 labels contain 10 notes; the three document-type groupings are not clinical specialties. "
        "Export: query1_specialty_note_counts.csv."
    )
    doc.add_heading("Query 2: Average transcription length", level=2)
    doc.add_paragraph(
        f"Question: What is the average transcription length by clinical specialty? Result: {q2_top['specialty_name']} "
        f"is highest at {q2_top['average_words']} words and {q2_low['specialty_name']} is lowest at "
        f"{q2_low['average_words']} words. Export: query2_average_words_by_specialty.csv."
    )
    doc.add_heading("Query 3: Most frequent keywords", level=2)
    doc.add_paragraph(
        f"Question: Which cleaned keywords occur in the most distinct notes? Result: “{top_keyword['keyword_term']}” "
        f"appears in {top_keyword['note_frequency']} notes. Specialty labels were removed from the keyword bridge. "
        "Export: query3_top_keywords.csv."
    )
    doc.add_heading("Query 4: Long transcriptions", level=2)
    doc.add_paragraph(
        f"Question: Which notes exceed 500 recounted words? Result: {len(query4)} records meet the threshold; "
        f"the longest is {longest['recount_words']} words. Export: query4_long_transcriptions.csv."
    )
    doc.add_heading("Query 5: Note type by specialty label", level=2)
    doc.add_paragraph(
        "Question: How are inferred note types distributed across specialty labels? The query returns 32 "
        "non-empty label/type combinations, useful for examining document mix. "
        "Export: query5_note_types_by_specialty.csv."
    )
    doc.add_paragraph(
        "The first query confirms that the provided subset was balanced, not a natural measure of service "
        "volume. The second identifies length differences between labels but does not imply differences in "
        "care quality. The keyword query is more interpretable after category-label terms are excluded. The "
        "note-type cross-tab shows that some source labels correspond entirely to document types, reinforcing "
        "the need to preserve the category distinction."
    )

    doc.add_page_break()
    doc.add_heading("Analytics-Ready Output", level=1)
    doc.add_paragraph(
        "The view v_specialty_analytics joins specialty labels to notes and transcription measurements. "
        "Its exported table contains specialty name and category, note count, average/shortest/longest "
        "recounted transcription words, and average transcription characters. It is suitable for a bar chart "
        "of mean transcription length by clinical specialty, with note count available as a tooltip or filter."
    )
    doc.add_picture(str(CHART_PATH), width=Inches(6.35))
    caption = doc.add_paragraph("Figure 2. Average recounted transcription words by clinical specialty.")
    caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph(
        f"In this sample, {q2_top['specialty_name']} averages {q2_top['average_words']} words and "
        f"{q2_low['specialty_name']} averages {q2_low['average_words']}. Since each clinical-specialty label "
        "has ten records, the visualization compares this curated subset rather than workload or population "
        "prevalence. A manager could use the output to identify where documentation-length review may be "
        "useful, then validate findings with representative operational data."
    )
    doc.add_paragraph(
        "Database-backed output is more reliable than querying the flat spreadsheet alone because the foreign "
        "keys constrain category references, unique keys prevent duplicate lookup values, keyword associations "
        "are atomic, and each metric has a documented source. The same view can be rerun after controlled "
        "loads, while the spreadsheet would require repeated string parsing and manual joins."
    )

    doc.add_page_break()
    doc.add_heading("Limitations", level=1)
    doc.add_paragraph(
        "This is a small curated teaching subset of public transcription examples, not a representative "
        "clinical population. Every source label has ten notes, so frequency comparisons cannot estimate "
        "real demand. The source specialty field mixes clinical specialties with document types, one label "
        "is abbreviated, inferred note types have not been clinically validated, and repeated transcriptions "
        "may affect counts. Keyword quality remains uneven even after category-label associations are removed. "
        "Word counts depend on the whitespace recount rule and should not be treated as clinical measures."
    )
    doc.add_paragraph(
        "Narrative text may contain identifiers or sensitive details. The records are marked “Not reviewed” "
        "for de-identification; access should therefore remain limited to the assignment team, and the text "
        "should not be used for patient care or external analytics. A production system would require a "
        "documented de-identification review, access controls, audit logging, retention rules, and validation "
        "against authoritative source data."
    )
    doc.add_heading("Team Contributions", level=1)
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
    )

    doc.add_heading("Conclusion", level=1)
    doc.add_paragraph(
        "The team converted its Week 2 normalized design into an executable PostgreSQL database, loaded "
        "representative data, enforced relationships, ran five analytical queries, and produced a reusable "
        "analytics view."
    )

    doc.add_page_break()
    doc.add_heading("References", level=1)
    references = [
        "Boyle, T. (2018). Medical transcriptions [Data set]. Kaggle. https://www.kaggle.com/tboyle10/medicaltranscriptions",
        "Coronel, C., & Morris, S. (2019). Database systems: Design, implementation, and management (13th ed.). Cengage Learning.",
        "MTSamples. (n.d.). Transcribed medical transcription sample reports and examples. https://www.mtsamples.com",
        "PostgreSQL Global Development Group. (2026). PostgreSQL 16 documentation. https://www.postgresql.org/docs/16/",
    ]
    for reference in references:
        paragraph = doc.add_paragraph(reference)
        paragraph.paragraph_format.left_indent = Inches(0.5)
        paragraph.paragraph_format.first_line_indent = Inches(-0.5)

    add_query_appendix(doc)
    add_screenshot_appendix(doc)
    doc.save(DOCX_PATH)
    print(f"Created {DOCX_PATH}")


if __name__ == "__main__":
    make_erd()
    make_chart()
    build_document()
