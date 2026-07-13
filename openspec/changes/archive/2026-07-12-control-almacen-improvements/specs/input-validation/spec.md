# Input Validation Specification

## Purpose

Validate location and roll code formats using regex patterns, replacing pure length checks.

## Requirements

### Requirement: Location Format Validation

The system SHALL validate location input against the pattern `^[A-Z]{4}\d{2}\d{2}\d{2}$` (4 uppercase letters + 6 digits).

#### Scenario: Valid location accepted

- GIVEN the user inputs `"DPA1A14702"`
- WHEN the system validates the location format
- THEN validation passes
- AND the input proceeds to `Ubic` parsing

#### Scenario: Lowercase letters rejected

- GIVEN the user inputs `"dpa1a14702"`
- WHEN the system validates the location format
- THEN validation fails
- AND the message `"EL FORMATO NO COINCIDE CON EL DE LA UBICACIÓN. REINTENTE"` is displayed

#### Scenario: Special characters rejected

- GIVEN the user inputs `"DPA1A147-2"`
- WHEN the system validates the location format
- THEN validation fails

#### Scenario: Wrong length rejected

- GIVEN the user inputs `"DPA1A147"`
- WHEN the system validates the location format
- THEN validation fails

### Requirement: Roll Code Format Validation

The system SHALL validate roll input against the pattern `^[A-Za-z0-9]{7}$` (7 alphanumeric characters).

#### Scenario: Valid alphanumeric roll accepted

- GIVEN the user inputs `"ABC1234"`
- WHEN the system validates the roll format
- THEN validation passes

#### Scenario: Roll with special characters rejected

- GIVEN the user inputs `"ABC-234"`
- WHEN the system validates the roll format
- THEN validation fails
- AND the message `"EL ARTICULO NO CUMPLE CON EL FORMATO. REINTENTE."` is displayed

#### Scenario: Roll with wrong length rejected

- GIVEN the user inputs `"ABC123"`
- WHEN the system validates the roll format
- THEN validation fails

### Requirement: Exit Command Bypasses Validation

The system SHALL accept `"0"` as an exit command without applying format validation.

#### Scenario: Exit command during location scan

- GIVEN the user is at the location input prompt
- WHEN the user inputs `"0"`
- THEN the session ends without validation error

#### Scenario: Exit command during roll scan

- GIVEN the user is at the roll input prompt
- WHEN the user inputs `"0"`
- THEN the review menu is displayed without validation error
