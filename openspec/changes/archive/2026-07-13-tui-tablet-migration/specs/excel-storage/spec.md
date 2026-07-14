# Excel Storage Delta Specification

## Purpose

Describes the change from pandas DataFrame-based Excel operations to direct openpyxl read/write/append operations for the warehouse control system.

## ADDED Requirements

### Requirement: Direct openpyxl Operations

The system SHALL use openpyxl directly for Excel operations without pandas DataFrame intermediaries.

#### Scenario: Load existing workbook

- GIVEN an Excel file exists with ubicacion and articulos sheets
- WHEN the application starts
- THEN openpyxl load_workbook is used to open the file
- AND the workbook is kept open for subsequent operations

#### Scenario: Append location data

- GIVEN a valid location code is scanned
- WHEN the location is registered
- Then openpyxl worksheet append adds the location data to the ubicacion sheet
- AND the workbook is saved after each append

#### Scenario: Append roll data

- GIVEN a batch of rolls is confirmed
- WHEN the batch is saved
- THEN openpyxl worksheet append adds each roll to the articulos sheet
- AND the workbook is saved after the batch

### Requirement: Session History Tracking

The system SHALL maintain a session-wide history of all scanned items across locations.

#### Scenario: Track all scanned rolls

- GIVEN the application is running
- WHEN rolls are scanned across multiple locations
- THEN all rolls are tracked in memory
- AND the session summary shows all scanned rolls

#### Scenario: Check for duplicate rolls in session

- GIVEN rolls have been scanned in the current session
- WHEN a new roll is scanned
- THEN the system checks if the roll exists in session history
- AND rejects duplicates with a warning message

## MODIFIED Requirements

### Requirement: Excel File Initialization

The system SHALL initialize Excel files with proper sheet structure when creating new files.

(Previously: Used pandas DataFrame to create empty sheets)

#### Scenario: Create new workbook with sheets

- GIVEN no Excel file exists for the current session
- WHEN the application starts
- THEN a new workbook is created with ubicacion and articulos sheets
- AND each sheet has appropriate column headers

#### Scenario: Load existing workbook

- GIVEN an Excel file exists from a previous session
- WHEN the application starts
- THEN the workbook is loaded preserving existing data
- AND the application can append new data to existing sheets

### Requirement: Roll Uniqueness Validation

The system SHALL validate roll uniqueness against both session history and existing system data.

(Previously: Only checked against existing system data)

#### Scenario: Reject duplicate roll in session

- GIVEN a roll was scanned earlier in the session
- WHEN the same roll is scanned again
- THEN the system rejects it with a duplicate warning
- AND the roll is not added to the batch

#### Scenario: Reject existing system roll

- GIVEN a roll exists in the Excel file from previous sessions
- WHEN the roll is scanned
- THEN the system rejects it with an existing system warning
- AND the roll is not added to the batch