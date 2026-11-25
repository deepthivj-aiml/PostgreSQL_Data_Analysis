import csv
import re
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.table import Table, TableStyleInfo


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
OUTPUT = ROOT / "Week5_Query_Results_Tables.xlsx"

SHEETS = [
    ("Query 1 - Specialty Counts", "query1_specialty_note_counts.csv",
     "Counts notes by specialty label and category."),
    ("Query 2 - Average Length", "query2_average_words_by_specialty.csv",
     "Average transcription words for clinical specialties."),
    ("Query 3 - Top Keywords", "query3_top_keywords.csv",
     "Twenty most frequent cleaned keywords."),
    ("Query 4 - Long Notes", "query4_long_transcriptions.csv",
     "Notes with more than 500 recounted words."),
    ("Query 5 - Note Types", "query5_note_types_by_specialty.csv",
     "Inferred note type counts by source specialty label."),
    ("Analytics - Specialty", "analytics_ready_specialty.csv",
     "Dashboard-ready specialty metrics from the analytics view."),
    ("Specialty x Note Type", "specialty_note_type_counts.csv",
     "Full specialty and note type cross-tabulation."),
]


def parse_value(value):
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    if re.fullmatch(r"-?\d+\.\d+", value):
        return float(value)
    return value


def load_rows(filename):
    with (RESULTS / filename).open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.reader(stream)
        headers = next(reader)
        return headers, [[parse_value(value) for value in row] for row in reader]


def add_excel_table(worksheet, headers, rows, table_name):
    worksheet.append(headers)
    for row in rows:
        worksheet.append(row)

    reference = f"A1:{worksheet.cell(worksheet.max_row, worksheet.max_column).coordinate}"
    table = Table(displayName=table_name, ref=reference)
    table.tableStyleInfo = TableStyleInfo(
        name="TableStyleMedium2",
        showFirstColumn=False,
        showLastColumn=False,
        showRowStripes=True,
        showColumnStripes=False,
    )
    worksheet.add_table(table)
    worksheet.freeze_panes = "A2"
    worksheet.sheet_view.showGridLines = False

    for column in worksheet.columns:
        letter = column[0].column_letter
        width = min(max(len(str(cell.value or "")) for cell in column) + 2, 42)
        worksheet.column_dimensions[letter].width = max(width, 12)
        for cell in column:
            cell.alignment = Alignment(vertical="top", wrap_text=True)
    for cell in worksheet[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="1F4E78")


def main():
    workbook = Workbook()
    overview = workbook.active
    overview.title = "Start Here"
    overview_rows = []

    for index, (sheet_name, filename, description) in enumerate(SHEETS, start=1):
        headers, rows = load_rows(filename)
        worksheet = workbook.create_sheet(sheet_name)
        table_name = f"ResultTable{index}"
        add_excel_table(worksheet, headers, rows, table_name)
        overview_rows.append([sheet_name, description])

    add_excel_table(
        overview,
        ["Result sheet", "Contents"],
        overview_rows,
        "WorkbookGuide",
    )
    overview.freeze_panes = "A2"
    overview.sheet_view.showGridLines = False
    overview.column_dimensions["A"].width = 28
    overview.column_dimensions["B"].width = 65
    overview["A10"] = "Source"
    overview["B10"] = "PostgreSQL query exports in the results folder"
    overview["A11"] = "Tip"
    overview["B11"] = "Each result tab is an Excel table with filters; use the header arrows to sort or filter."
    for row in overview.iter_rows(min_row=10, max_row=11):
        for cell in row:
            cell.alignment = Alignment(vertical="top", wrap_text=True)
    workbook.save(OUTPUT)
    print(f"Created {OUTPUT}")


if __name__ == "__main__":
    main()
