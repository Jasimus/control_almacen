# Bug Fixes Specification

## Purpose

Fix two critical bugs that break runtime or produce incorrect data.

## Requirements

### Requirement: Fix Invalid Import

The system SHALL import `List` from `typing`, not from `ast`.

#### Scenario: Application starts without import error

- GIVEN the application is launched with a valid user argument
- WHEN `main.py` is loaded by the Python interpreter
- THEN no `ImportError` is raised
- AND the `List` type annotation is available for use

#### Scenario: Type annotation works correctly

- GIVEN the application is running
- WHEN a `List[ProdUbic]` annotation is evaluated
- THEN it behaves as a standard typing annotation (not an AST node)

### Requirement: Remove Hardcoded Ubic Value

The system SHALL derive the `ubic` field from the parsed location input, not from a hardcoded constant.

#### Scenario: Ubic field reflects parsed deposit code

- GIVEN a location input `"DPA1A14702"`
- WHEN `Ubic.__init__` parses the input
- THEN `ubic` SHALL equal `"DPA1A14702"` (the full original input)
- AND `depo` SHALL equal `"DPA1A"`
- AND `pasillo` SHALL equal `"14"`
- AND `columna` SHALL equal `"70"`
- AND `nivel` SHALL equal `"02"`

#### Scenario: Different deposit codes produce correct ubic

- GIVEN a location input `"DPB2B33501"`
- WHEN `Ubic.__init__` parses the input
- THEN `ubic` SHALL equal `"DPB2B33501"`
- AND `depo` SHALL equal `"DPB2"`
