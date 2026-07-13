# Cross-Session Uniqueness Specification

## Purpose

Prevent duplicate roll registrations across sessions by checking existing Excel data on startup.

## Requirements

### Requirement: Load Existing Roll IDs on Startup

The system SHALL read all existing `id_lote` values from the `articulos` sheet into an in-memory set when the application starts.

#### Scenario: Startup loads rolls from existing file

- GIVEN a `deposito.xlsx` with 150 rolls in the `articulos` sheet
- WHEN the application starts
- THEN the system SHALL have a set of 150 `id_lote` values in memory

#### Scenario: Startup with empty articulos sheet

- GIVEN a `deposito.xlsx` with an empty `articulos` sheet
- WHEN the application starts
- THEN the duplicate set SHALL be empty

#### Scenario: Startup with no Excel file

- GIVEN no `deposito.xlsx` exists
- WHEN the application starts and creates a new file
- THEN the duplicate set SHALL be empty

### Requirement: Reject Duplicate Rolls Across Sessions

The system SHALL reject a roll if its `id_lote` already exists in the loaded set or the current session's list.

#### Scenario: Roll from previous session is rejected

- GIVEN the loaded set contains `"ABC1234"` from a prior session
- WHEN the user inputs `"ABC1234"`
- THEN the system SHALL display `"NO PUEDE INGRESAR EL MISMO ARTICULO. REINTENTE."`
- AND the roll SHALL NOT be added to the current session

#### Scenario: Roll from current session is rejected

- GIVEN the user has already registered `"XYZ9999"` in this session
- WHEN the user inputs `"XYZ9999"` again
- THEN the system SHALL display the duplicate rejection message

#### Scenario: New roll is accepted

- GIVEN the loaded set contains `"ABC1234"` but not `"DEF5678"`
- WHEN the user inputs `"DEF5678"`
- THEN the roll SHALL be accepted and added to the current session

### Requirement: Duplicate Set Refresh Per Location

The system SHALL clear the current session's roll list when moving to a new location, but the startup-loaded set persists for the entire session.

#### Scenario: Moving to new location clears session list

- GIVEN the user registered 3 rolls at location `"DPA1A14702"`
- WHEN the user scans a new location `"DPA1A14703"`
- THEN the session roll list for the new location starts empty
- AND the 3 previously registered rolls remain in the startup set (preventing cross-location duplicates within the same session)
