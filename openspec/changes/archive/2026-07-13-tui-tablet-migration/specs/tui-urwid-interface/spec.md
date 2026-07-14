# TUI urwid Interface Specification

## Purpose

Defines the urwid-based terminal user interface for warehouse control on Android tablets via Termux. Replaces the CLI flicker-prone interface with a stable, flicker-free TUI optimized for Bluetooth barcode scanner input.

## Requirements

### Requirement: State Machine Architecture

The system SHALL implement a finite state machine with four states: SCAN_LOCATION, SCAN_ROLLS, CONFIRM_BATCH, SESSION_SUMMARY.

#### Scenario: Location scan transitions to roll scan

- GIVEN the system is in SCAN_LOCATION state
- WHEN a valid 10-character location code is scanned
- THEN the system transitions to SCAN_ROLLS state
- AND the location is registered in the current batch

#### Scenario: Roll scan adds to batch

- GIVEN the system is in SCAN_ROLLS state
- WHEN a valid 9-character roll code is scanned
- AND the roll is not a duplicate in session or existing in system
- THEN the roll is added to the current batch
- AND the scanned items list updates in real-time

#### Scenario: Confirm batch saves and resets

- GIVEN the system is in CONFIRM_BATCH state
- WHEN the user confirms the batch
- THEN the batch is saved to Excel
- AND the system transitions to SCAN_LOCATION state
- AND the session history is preserved

#### Scenario: Session summary shows all scans

- GIVEN the system is in SESSION_SUMMARY state
- WHEN the session ends
- THEN all scanned items across locations are displayed
- AND the user can exit the application

### Requirement: Widget Tree Layout

The system SHALL render a urwid Frame with header, body (Pile of status text, Edit input, ListBox), and footer.

#### Scenario: Persistent header display

- GIVEN the application is running
- WHEN the TUI is rendered
- THEN the header shows "SISTEMA DE CONTROL DE ALMACÉN"
- AND the header remains visible across state transitions

#### Scenario: Edit widget captures scanner input

- GIVEN the system is in SCAN_LOCATION or SCAN_ROLLS state
- WHEN the Bluetooth scanner sends keystrokes
- THEN the Edit widget captures each character
- AND Enter key triggers state transition callback

#### Scenario: Scrollable scan history

- GIVEN the system is in SCAN_ROLLS state
- WHEN rolls are scanned
- THEN the ListBox shows all scanned rolls for current location
- AND the list scrolls automatically to show newest items

### Requirement: Keyboard Navigation

The system SHALL support keyboard shortcuts: F1-F4 for state navigation, Tab for focus, Enter for confirm, Escape for cancel.

#### Scenario: F1 returns to location scan

- GIVEN the system is in any state
- WHEN F1 is pressed
- THEN the system transitions to SCAN_LOCATION state
- AND any unsaved batch is discarded

#### Scenario: Escape cancels current input

- GIVEN the system is in SCAN_LOCATION or SCAN_ROLLS state
- WHEN Escape is pressed
- THEN the current input is cleared
- AND the system remains in the same state

### Requirement: Error Display

The system SHALL display validation errors and duplicate warnings in the footer area.

#### Scenario: Invalid location code

- GIVEN the system is in SCAN_LOCATION state
- WHEN an invalid location code is scanned
- THEN an error message appears in the footer
- AND the input field is cleared
- AND the system remains in SCAN_LOCATION state

#### Scenario: Duplicate roll warning

- GIVEN the system is in SCAN_ROLLS state
- WHEN a roll code already scanned in session is entered
- THEN a warning message appears in the footer
- AND the roll is not added to the batch
- AND the input field is cleared

### Requirement: Color Palette

The system SHALL use a standard color palette with distinct colors for header, input, success, error, and warning states.

#### Scenario: Palette application

- GIVEN the TUI is rendered
- WHEN different states are active
- THEN the header uses a distinct color
- AND the input field uses a different color
- AND success messages use green
- AND error messages use red
- AND warnings use yellow