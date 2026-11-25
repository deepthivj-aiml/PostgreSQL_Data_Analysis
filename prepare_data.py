import csv
from pathlib import Path

from openpyxl import load_workbook


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "MIS550_Week2_Normalized_Preview.xlsx"
DATA_DIR = ROOT / "data"

TABLE_FILES = {
    "MedicalSpecialty": "MedicalSpecialty.csv",
    "NoteType": "NoteType.csv",
    "DataSource": "DataSource.csv",
    "ClinicalNote": "ClinicalNote.csv",
    "NoteText": "NoteText.csv",
    "Keyword": "Keyword.csv",
    "NoteKeyword": "NoteKeyword.csv",
    "NoteSection": "NoteSection.csv",
}


def main():
    if not SOURCE.exists():
        raise FileNotFoundError(f"Expected normalized Week 2 workbook: {SOURCE}")

    workbook = load_workbook(SOURCE, read_only=True, data_only=True)
    DATA_DIR.mkdir(exist_ok=True)
    sheets = {}
    for sheet_name in TABLE_FILES:
        if sheet_name not in workbook.sheetnames:
            raise ValueError(f"Required worksheet is missing: {sheet_name}")
        sheets[sheet_name] = list(workbook[sheet_name].iter_rows(values_only=True))

    specialty_names = {
        str(row[1]).strip().casefold()
        for row in sheets["MedicalSpecialty"][1:]
    }
    original_keywords = {
        int(row[0]): str(row[1]).strip()
        for row in sheets["Keyword"][1:]
    }
    keyword_id_map = {}
    cleaned_keywords = []
    for old_id, term in sorted(original_keywords.items()):
        if term.casefold() not in specialty_names:
            new_id = len(cleaned_keywords) + 1
            keyword_id_map[old_id] = new_id
            cleaned_keywords.append((new_id, term))

    keyword_header = sheets["Keyword"][0]
    bridge_header = sheets["NoteKeyword"][0]
    filtered_bridge = []
    removed_specialty_links = 0
    for row in sheets["NoteKeyword"][1:]:
        old_keyword_id = int(row[1])
        if old_keyword_id not in keyword_id_map:
            removed_specialty_links += 1
            continue
        filtered_bridge.append((row[0], keyword_id_map[old_keyword_id], row[2]))

    sheets["Keyword"] = [keyword_header, *cleaned_keywords]
    sheets["NoteKeyword"] = [bridge_header, *filtered_bridge]
    counts = {}

    for sheet_name, file_name in TABLE_FILES.items():
        output_path = DATA_DIR / file_name
        with output_path.open("w", newline="", encoding="utf-8-sig") as output:
            writer = csv.writer(output)
            for row in sheets[sheet_name]:
                writer.writerow(["" if value is None else value for value in row])
        counts[sheet_name] = len(sheets[sheet_name]) - 1

    if counts["ClinicalNote"] < 30:
        raise ValueError(f"Expected at least 30 notes; exported {counts['ClinicalNote']}")
    if counts["MedicalSpecialty"] < 5:
        raise ValueError(
            f"Expected at least 5 specialties; exported {counts['MedicalSpecialty']}"
        )
    if counts["Keyword"] < 20:
        raise ValueError(f"Expected at least 20 keywords; exported {counts['Keyword']}")

    for sheet_name, count in counts.items():
        print(f"{sheet_name}: {count} rows")
    print(f"Removed specialty-label keyword relationships: {removed_specialty_links}")


if __name__ == "__main__":
    main()
