# Week 5 PostgreSQL implementation

This folder contains the PostgreSQL schema, data preparation/import scripts, validation checks, five analytical queries, exported results, an ERD, and the implementation report.

## Run on Windows

1. Install PostgreSQL and create an empty database, for example:

   ```powershell
   createdb -h localhost -p 5432 -U postgres week5_mtsamples
   ```

2. From this folder, run the project (the default psql path is PostgreSQL 18):

   ```powershell
   .\run_project.ps1 -Database week5_mtsamples -Username postgres
   ```

   If PostgreSQL is installed elsewhere, pass its client path with `-PsqlPath`. The script reads `MIS550_Week2_Normalized_Preview.xlsx` from the parent folder. It expects a fresh database/schema; create a new database for a clean rerun.

3. Open `Week5_Query_Results_Tables.xlsx` to browse the query results as filterable Excel tables. CSV exports remain in `results\` for Tableau, Power BI, or other tools.

## Files

- `schema.sql`: eight related tables, constraints, indexes, and analytics views.
- `MIS550_Week2_Normalized_Preview.xlsx`: source workbook used by the data preparation script.
- `prepare_data.py`: exports normalized worksheets from the source workbook in this folder to UTF-8 CSV and removes specialty-label keyword relationships.
- `load_data.sql`: imports each CSV with PostgreSQL `\copy`.
- `validate.sql`: checks assignment minimums, text coverage, category-keyword separation, and row counts.
- `queries.sql`: five analytical queries and exported result datasets.
- `evidence_screenshots.sql`: reruns labeled table, validation, query, and analytics outputs, pausing for manual screenshots.
- `Week5_Query_Results_Tables.xlsx`: all query results in separate, filterable Excel tables.
- `Week5_Assignment4_APA_Report_Terminal_Evidence.docx`: APA-styled report with query screenshot placeholders instead of Word tables.

## Capture terminal evidence

After running the project, open PowerShell in this folder and run:

```powershell
& 'C:\Program Files\PostgreSQL\18\bin\psql.exe' -h localhost -p 5432 -U postgres -d week5_mtsamples -v ON_ERROR_STOP=1 -f .\evidence_screenshots.sql
```

Replace `postgres` and `week5_mtsamples` if you used a different database role or database. At each prompt, capture the visible terminal output with `Win+Shift+S`, paste/save it, return to the terminal, and press Enter. Appendix A contains the five query screenshot placeholders; Appendix B maps the remaining evidence points to screenshots 1–4 and 10. Verify the draft team contribution notes before submitting.

The sample is curated and balanced, and transcription text has not been reviewed for de-identification. Do not treat it as representative clinical or patient-care data. Confirm the contribution notes and make any necessary corrections before submission.
