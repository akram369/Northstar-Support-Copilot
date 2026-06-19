# CSV Data Imports

## File requirements
CSV imports support UTF-8 files up to 100 MB and 250,000 rows. The first row must contain unique column names. Dates should use ISO 8601 (`YYYY-MM-DD`) and decimal values must use a period. Empty required identifiers cause row-level rejection.

## Diagnosing failures
The import results page provides a downloadable error CSV containing the row number, field, and validation reason. A completely rejected file usually indicates an unsupported encoding, missing header row, or malformed quoting. Re-save the file as UTF-8 CSV and validate that embedded commas are enclosed in double quotes.

## Duplicate handling
Imports match existing records by external ID. Selecting **Update existing** changes matching records; selecting **Create only** skips them. Test a representative 20-row sample before importing a large production file.

