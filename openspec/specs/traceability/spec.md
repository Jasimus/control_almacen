# Traceability Specification

## Purpose

Add datetime tracking to every roll registration for audit and traceability.

## Requirements

### Requirement: Fecha/Hora Column in Articulos Sheet

The system SHALL include a `fecha_hora` column in the `articulos` Excel sheet as the rightmost column.

#### Scenario: New Excel file includes fecha_hora header

- GIVEN no `deposito.xlsx` exists
- WHEN the system creates a new workbook
- THEN the `articulos` sheet columns SHALL be `['id_usuario', 'id_ubicacion', 'id_lote', 'fecha_hora']`

#### Scenario: Existing Excel file without fecha_hora is compatible

- GIVEN a `deposito.xlsx` exists without a `fecha_hora` column
- WHEN the system appends new rows
- THEN the new rows SHALL include the `fecha_hora` value
- AND existing rows remain untouched

### Requirement: Datetime Capture at Registration

The system SHALL populate `fecha_hora` with the local datetime at the moment the roll is registered.

#### Scenario: Timestamp reflects registration time

- GIVEN a user registers roll `"ABC1234"` at 14:30:05 on 2026-07-12
- WHEN the `ProdUbic` object is created
- THEN `fecha_hora` SHALL be `"2026-07-12 14:30:05"` (ISO-like format, space-separated)

#### Scenario: Multiple rolls in same session get distinct timestamps

- GIVEN two rolls are registered 3 seconds apart
- WHEN both are written to Excel
- THEN their `fecha_hora` values SHALL differ by at least 1 second

### Requirement: DateTime Format in Excel

The system SHALL store `fecha_hora` as a string in `YYYY-MM-DD HH:MM:SS` format.

#### Scenario: Excel stores readable datetime string

- GIVEN a roll is registered
- WHEN the row is written to the `articulos` sheet
- THEN `fecha_hora` SHALL be a human-readable string, not a numeric serial
