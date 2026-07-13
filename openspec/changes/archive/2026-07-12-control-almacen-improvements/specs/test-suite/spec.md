# Test Suite Specification

## Purpose

Add pytest-based automated tests for core validation and parsing logic.

## Requirements

### Requirement: Test Framework Setup

The system SHALL use `pytest` as the test runner with tests in a `tests/` directory at the project root.

#### Scenario: Tests directory structure

- GIVEN the project root
- WHEN the test suite is set up
- THEN `tests/` SHALL contain `__init__.py`, `test_ubic.py`, `test_rel_ubic.py`, and `test_validation.py`

#### Scenario: pytest runs from project root

- GIVEN the project is set up with `uv` and `pytest` installed
- WHEN `uv run pytest` is executed
- THEN all tests SHALL execute and report pass/fail status

### Requirement: Ubic Parsing Tests

The system SHALL test `Ubic` class parsing and field extraction.

#### Scenario: Valid location parsed correctly

- GIVEN `Ubic("DPA1A14702")`
- WHEN fields are accessed
- THEN `ubic.id` SHALL be `"DPA1A14702"`
- AND `ubic.depo` SHALL be `"DPA1A"`
- AND `ubic.pasillo` SHALL be `"14"`
- AND `ubic.columna` SHALL be `"70"`
- AND `ubic.nivel` SHALL be `"02"`

#### Scenario: ubic field derives from input

- GIVEN `Ubic("DPB2B33501")`
- WHEN `ubic.ubic` is accessed
- THEN it SHALL equal `"DPB2B33501"`

### Requirement: ProdUbic Creation Tests

The system SHALL test `ProdUbic` object creation and field assignment.

#### Scenario: ProdUbic stores all fields

- GIVEN `ProdUbic("user1", "DPA1A14702", "ABC1234")`
- WHEN fields are accessed
- THEN `id_usuario` SHALL be `"user1"`
- AND `id_ubic` SHALL be `"DPA1A14702"`
- AND `id_lote` SHALL be `"ABC1234"`

#### Scenario: ProdUbic includes timestamp

- GIVEN a `ProdUbic` is created at a known time
- WHEN `fecha_hora` is accessed
- THEN it SHALL be a non-empty string in `YYYY-MM-DD HH:MM:SS` format

### Requirement: Format Validation Tests

The system SHALL test location and roll regex patterns.

#### Scenario: Valid location patterns pass

- GIVEN location inputs `"DPA1A14702"`, `"DPZ9Z99999"`, `"ABCD010101"`
- WHEN each is validated against the location regex
- THEN all SHALL pass

#### Scenario: Invalid location patterns fail

- GIVEN location inputs `"dpa1a14702"` (lowercase), `"DPA1A147-2"` (special char), `"DPA1A147"` (too short), `"DPA1A147020"` (too long)
- WHEN each is validated against the location regex
- THEN all SHALL fail

#### Scenario: Valid roll patterns pass

- GIVEN roll inputs `"ABC1234"`, `"abc1234"`, `"A1B2C3D"`, `"1234567"`
- WHEN each is validated against the roll regex
- THEN all SHALL pass

#### Scenario: Invalid roll patterns fail

- GIVEN roll inputs `"ABC-234"` (special char), `"ABC12"` (too short), `"ABC12345"` (too long)
- WHEN each is validated against the roll regex
- THEN all SHALL fail
