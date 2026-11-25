param(
    [string]$PsqlPath = "C:\Program Files\PostgreSQL\18\bin\psql.exe",
    [string]$HostName = "localhost",
    [int]$Port = 5432,
    [string]$Database = "week5_mtsamples",
    [string]$Username = $env:USERNAME
)

$ErrorActionPreference = "Stop"
$ProjectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not (Test-Path $PsqlPath)) {
    throw "psql was not found at '$PsqlPath'. Supply its installed path with -PsqlPath."
}

Push-Location $ProjectDir
try {
    python .\prepare_data.py
    if ($LASTEXITCODE -ne 0) {
        throw "CSV preparation failed with exit code $LASTEXITCODE."
    }

    foreach ($SqlFile in @("schema.sql", "load_data.sql", "validate.sql", "queries.sql")) {
        & $PsqlPath -h $HostName -p $Port -U $Username -d $Database `
            -v ON_ERROR_STOP=1 -f $SqlFile
        if ($LASTEXITCODE -ne 0) {
            throw "$SqlFile failed with exit code $LASTEXITCODE."
        }
    }

    python .\build_report.py
    if ($LASTEXITCODE -ne 0) {
        throw "Report generation failed with exit code $LASTEXITCODE."
    }

    python .\export_results_workbook.py
    if ($LASTEXITCODE -ne 0) {
        throw "Excel results workbook generation failed with exit code $LASTEXITCODE."
    }
}
finally {
    Pop-Location
}
