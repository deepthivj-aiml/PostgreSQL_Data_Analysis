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
from PIL import Image as PILImage


def add_image(document, path, max_width=6.5, max_height=7.8):
    """Add an image scaled to fit the page, keeping its caption with it."""
    with PILImage.open(path) as image:
        width_px, height_px = image.size
    width = min(max_width, max_height * width_px / height_px)
    paragraph = document.add_paragraph()
    paragraph.paragraph_format.keep_with_next = True
    paragraph.add_run().add_picture(str(path), width=Inches(width))
    return paragraph


def add_sql_block(document, sql):
    """Add a query's SQL as a single-spaced monospace block. The rubric lists the SQL query and the
    screenshot or exported result as separate items, so the SQL appears here as text as well as in the
    terminal screenshot that follows."""
    paragraph = document.add_paragraph()
    paragraph.paragraph_format.line_spacing = 1
    paragraph.paragraph_format.space_after = Pt(6)
    paragraph.paragraph_format.space_before = Pt(0)
    lines = sql.strip().splitlines()
    for index, line in enumerate(lines):
        run = paragraph.add_run(line)
        run.font.name = "Consolas"
        run.font.size = Pt(10)
        if index < len(lines) - 1:
            run.add_break()
    return paragraph


def read_query_sql():
    """Extract the five analytical queries from queries.sql, in order, so the text in the report always
    matches the SQL that was actually run."""
    text = (ROOT / "queries.sql").read_text(encoding="utf-8")
    blocks = re.findall(r"-- Query \d:.*?\n(.*?)(?=\n-- Query|\n-- Analytics|\Z)", text, re.S)
    return [block.strip() for block in blocks]


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


def build_document():
    analytics = read_csv("analytics_ready_specialty.csv")
    query_sql = read_query_sql()
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
        "on reparsing comma-separated spreadsheet cells."
    )
    doc.add_heading("Database Design Summary", level=1)
    doc.add_heading("Revised design", level=2)
    doc.add_paragraph(
        "The implementation carries forward the Week 2 normalized design and builds eight tables: "
        "MedicalSpecialty, NoteType, DataSource, ClinicalNote, NoteText, Keyword, NoteKeyword, and NoteSection. "
        "ClinicalNote is the central entity. Specialty, note type, and source each have one-to-many relationships "
        "to notes; NoteText has a one-to-one relationship; NoteSection has a one-to-many relationship. "
        "NoteKeyword resolves the many-to-many relationship between notes and keywords. Separating the repeated "
        "labels and keywords into lookup and bridge tables keeps each fact in one place, so a category or keyword "
        "can be renamed without touching the note records."
    )
    doc.add_paragraph(
        "Two adjustments were made for implementation. First, specialty labels that actually describe document "
        "formats are marked as “Document-type grouping,” preserving source values without presenting them as "
        "clinical specialties. Second, keyword associations matching a specialty label were removed from the "
        "keyword bridge to prevent category names from inflating keyword frequencies. Source row identifiers "
        "remain unique for lineage, and transcription text stays separate with a full-text search index."
    )
    add_image(doc, ERD_PATH)
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
    add_image(doc, EVIDENCE / "vscode_schema_top.png")
    caption = doc.add_paragraph("Table definitions in schema.sql, part 1.")
    caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_image(doc, EVIDENCE / "vscode_schema_bottom.png")
    caption = doc.add_paragraph("Table definitions in schema.sql, part 2.")
    caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_image(doc, EVIDENCE / "shot1.png")
    caption = doc.add_paragraph("Tables created in PostgreSQL.")
    caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_image(doc, EVIDENCE / "shot2.png")
    caption = doc.add_paragraph("ClinicalNote - columns, keys, and constraints.")
    caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_image(doc, EVIDENCE / "shot3.png")
    caption = doc.add_paragraph("NoteKeyword - bridge table keys.")
    caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
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
        "counting measure explicit."
    )
    doc.add_paragraph(
        "Post-load validation confirmed 120 ClinicalNote rows, 120 matching NoteText rows, 12 specialty "
        "labels, seven note types, 1,077 keywords, 1,324 bridge rows, and 779 sections. All imports succeeded "
        "with foreign-key constraints enabled; validate.sql repeats the checks and prints table row counts."
    )
    add_image(doc, EVIDENCE / "shot4a.png")
    caption = doc.add_paragraph("Validation checks.")
    caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_image(doc, EVIDENCE / "shot4b.png")
    caption = doc.add_paragraph("Row counts.")
    caption.alignment = WD_ALIGN_PARAGRAPH.CENTER

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
    add_sql_block(doc, query_sql[0])
    add_image(doc, EVIDENCE / "shot5.png")
    caption = doc.add_paragraph("Query 1 result.")
    caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph(
        "What this means: the sample was built to be balanced, so this query is a check on the sample "
        "rather than a ranking — no specialty can look busier than another here. That balance is what "
        "makes the later comparisons fair: any difference in the other queries comes from the notes "
        "themselves, not from one specialty having more notes."
    )
    doc.add_heading("Query 2: Average transcription length", level=2)
    doc.add_paragraph(
        f"Question: What is the average transcription length by clinical specialty? Result: {q2_top['specialty_name']} "
        f"is highest at {q2_top['average_words']} words and {q2_low['specialty_name']} is lowest at "
        f"{q2_low['average_words']} words. Export: query2_average_words_by_specialty.csv."
    )
    add_sql_block(doc, query_sql[1])
    add_image(doc, EVIDENCE / "shot6.png")
    caption = doc.add_paragraph("Query 2 result.")
    caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph(
        "What this means: Orthopedic notes take the most documentation effort and Radiology the least, "
        "with about 222 words between them. A team planning review time, or reading the Figure 2 chart, "
        "should expect longer text from Orthopedic. It says nothing about care quality — only that the "
        "documentation is longer."
    )
    doc.add_heading("Query 3: Most frequent keywords", level=2)
    doc.add_paragraph(
        f"Question: Which cleaned keywords occur in the most distinct notes? Result: “{top_keyword['keyword_term']}” "
        f"appears in {top_keyword['note_frequency']} notes. Specialty labels were removed from the keyword bridge. "
        "Export: query3_top_keywords.csv."
    )
    add_sql_block(doc, query_sql[2])
    add_image(doc, EVIDENCE / "shot7.png")
    caption = doc.add_paragraph("Query 3 result.")
    caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph(
        "What this means: no single keyword dominates the collection, so keyword search is useful but no "
        "one term will find most notes. MRI is the most useful single search term, appearing in 7 notes. "
        "Removing the specialty-label terms first is what makes this list interpretable — otherwise the "
        "labels themselves would have topped it."
    )
    doc.add_heading("Query 4: Long transcriptions", level=2)
    doc.add_paragraph(
        f"Question: Which notes exceed 500 recounted words? Result: {len(query4)} records meet the threshold; "
        f"the longest is {longest['recount_words']} words. Export: query4_long_transcriptions.csv."
    )
    add_sql_block(doc, query_sql[3])
    add_image(doc, EVIDENCE / "shot8.png")
    caption = doc.add_paragraph("Query 4 result.")
    caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph(
        "What this means: long notes are about one in five of the sample, so a review that prioritises "
        "long transcriptions only needs to look at 26 notes, not all 120. The 845-word note is the "
        "extreme case and the natural place to start that review."
    )
    doc.add_heading("Query 5: Note type by specialty label", level=2)
    doc.add_paragraph(
        "Question: How are inferred note types distributed across specialty labels? The query returns 32 "
        "non-empty label/type combinations, useful for examining document mix. "
        "Export: query5_note_types_by_specialty.csv."
    )
    add_sql_block(doc, query_sql[4])
    add_image(doc, EVIDENCE / "shot9.png")
    caption = doc.add_paragraph("Query 5 result.")
    caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph(
        "What this means: note type depends on specialty — no label uses all seven types, and most use "
        "only two or three. A dashboard should therefore show the type mix per specialty instead of one "
        "overall mix, and the three document-type labels confirm again that they are groupings, not "
        "clinical specialties."
    )
    doc.add_paragraph(
        "Each query above returns a table that can feed a chart. The most direct candidates are Query 1 "
        "(bars of note counts), Query 2 (the bar chart in Figure 2), and Query 5 (stacked bars of "
        "note-type mix by specialty)."
    )

    doc.add_page_break()
    doc.add_heading("Analytics-Ready Output", level=1)
    doc.add_paragraph(
        "The view v_specialty_analytics joins specialty labels to notes and transcription measurements. "
        "Its exported table contains specialty name and category, note count, average/shortest/longest "
        "recounted transcription words, and average transcription characters. It is suitable for a bar chart "
        "of mean transcription length by clinical specialty, with note count available as a tooltip or filter."
    )
    add_image(doc, CHART_PATH)
    caption = doc.add_paragraph("Figure 2. Average recounted transcription words by clinical specialty.")
    caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_image(doc, EVIDENCE / "shot10.png")
    caption = doc.add_paragraph("Specialty summary from the analytics-ready view.")
    caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph(
        f"In this sample, {q2_top['specialty_name']} averages {q2_top['average_words']} words and "
        f"{q2_low['specialty_name']} averages {q2_low['average_words']}. Since each clinical-specialty label "
        "has ten records, the visualization compares this curated subset rather than workload or population "
        "prevalence. A manager could use the output to identify where documentation-length review may be "
        "useful, then validate findings with representative operational data."
    )
    doc.add_paragraph(
        "What this means: charted as bars, the output shows at a glance that Orthopedic notes run longest "
        "and Radiology shortest, with every specialty on the same 10-note base, so the bars compare length "
        "rather than workload. That is the single headline the analytics-ready table is built to support."
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
    doc.add_page_break()
    doc.add_heading("Team Contributions", level=1)
    doc.add_paragraph(
        "The work was split by section: Yuhui Xu completed the Introduction, Database Design Summary, and "
        "Implementation Summary, and Deepthi Venmanasseril Jainlal completed the Query Results, "
        "Analytics-Ready Output, and Limitations."
    )
    doc.add_heading("Yuhui Xu", level=2)
    doc.add_paragraph(
        "Introduction, Database Design Summary, and Implementation Summary. Yuhui Xu revised the database "
        "design and the ERD, defining the eight tables, their primary and foreign keys, and the constraints "
        "that keep the specialty, note, keyword, and section records linked. She built the PostgreSQL tables, "
        "loaded the prepared data, and ran the validation checks, confirming the row count in every table "
        "(Sections 1-3)."
    )
    doc.add_heading("Deepthi Venmanasseril Jainlal", level=2)
    doc.add_paragraph(
        "Query Results, Analytics-Ready Output, and Limitations. Deepthi Venmanasseril Jainlal wrote the "
        "five analytical SQL queries and explained their results, built the analytics-ready specialty view "
        "and exported table, assessed the limitations, and assembled the final report with the terminal "
        "output (Sections 4-6). She also contributed to the implementation, including the PostgreSQL table "
        "definitions and data loading."
    )

    doc.save(DOCX_PATH)
    print(f"Created {DOCX_PATH}")


if __name__ == "__main__":
    make_erd()
    make_chart()
    build_document()
