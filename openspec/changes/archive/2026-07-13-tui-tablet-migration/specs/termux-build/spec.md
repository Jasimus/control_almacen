# Termux Build Specification

## Purpose

Defines the PyInstaller build process for creating ARM binaries on Termux, including fallback launcher script for environments where compilation fails.

## Requirements

### Requirement: PyInstaller Build Configuration

The system SHALL provide a build.spec file that compiles the application for aarch64 architecture on Termux.

#### Scenario: Successful ARM binary compilation

- GIVEN the build.spec file is configured for aarch64
- WHEN `pyinstaller build.spec` is run on Termux
- THEN a binary is created in the dist directory
- AND the binary includes all required hiddenimports (urwid, openpyxl)
- AND the binary excludes pandas dependencies

#### Scenario: Hiddenimports configuration

- GIVEN the build.spec file
- WHEN the binary is compiled
- THEN urwid and its dependencies are included
- AND openpyxl and its dependencies are included
- AND pandas and its dependencies are excluded

### Requirement: Launcher Script Fallback

The system SHALL provide a shell script that runs the application via Python if the binary fails.

#### Scenario: Binary execution failure

- GIVEN the compiled binary exists but fails to execute
- WHEN the launcher script is run
- THEN it falls back to `python main.py`
- AND the application starts normally

#### Scenario: Binary execution success

- GIVEN the compiled binary exists and works
- WHEN the launcher script is run
- THEN it executes the binary directly
- AND the application starts normally

### Requirement: Build Instructions

The system SHALL document the build process for Termux environments.

#### Scenario: Fresh Termux setup

- GIVEN a fresh Termux installation on an Android tablet
- WHEN the build instructions are followed
- Then the application is compiled and ready to run
- AND all dependencies are installed

#### Scenario: Build with existing dependencies

- GIVEN a Termux environment with Python and pip installed
- WHEN the build script is run
- THEN only missing dependencies are installed
- AND the build completes successfully

### Requirement: Binary Size Optimization

The system SHALL minimize binary size through module exclusion and compression.

#### Scenario: Size reduction through exclusion

- GIVEN the build.spec file
- WHEN the binary is compiled
- THEN pandas and unused modules are excluded
- AND the binary size is reduced by approximately 50MB

#### Scenario: UPX compression

- GIVEN UPX is available in the Termux environment
- WHEN the binary is compiled
- THEN UPX compression is applied
- AND the binary size is further reduced