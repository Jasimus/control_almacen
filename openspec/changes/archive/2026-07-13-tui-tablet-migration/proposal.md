# Proposal: TUI Tablet Migration

## Intent

Migrate the CLI warehouse control system from `input()/print()` to an urwid TUI for Android tablets via Termux. The current CLI flickers on slow tablets, lacks persistent status display, and cannot show scanned items in real-time. urwid provides a stable, flicker-free interface that handles Bluetooth barcode scanner input natively (scanner acts as keyboard).

## Scope

### In Scope
- Rewrite `main.py` UI layer using urwid widgets (Frame, Edit, ListBox, Text, AttrMap)
- Replace nested while loops with state machine (SCAN_LOCATION → SCAN_ROLLS → CONFIRM_BATCH)
- Remove `pandas` dependency — use `openpyxl` directly for Excel writes
- Add urwid to `pyproject.toml` and `build.spec` hiddenimports
- Add Termux build target to Makefile
- Persistent header (system title) and footer (keyboard shortcuts/status)
- Real-time scrollable list of scanned rolls per location

### Out of Scope
- Touch/gesture navigation (scanner-first workflow)
- Database migration (Excel remains the data store)
- Changes to domain logic (`ubic.py`, `rel_ubic.py`, `validation.py`)
- Multi-tablet sync or networking
- Custom Termux:GUI plugin integration

## Capabilities

### New Capabilities
- `tui-urwid-interface`: urwid-based TUI with header, input field, scrollable scan list, footer status bar, and state machine navigation

### Modified Capabilities
- `build`: Remove pandas hiddenimports, add urwid hiddenimports, add Termux build target

## Approach

1. **State machine architecture**: Replace nested `while` loops with explicit states and transitions. Each state maps to a urwid view (location prompt, roll prompt, batch review).
2. **Widget tree**: `Frame(header, Pile([status_text, Edit_input, ListBox_scans]), footer)` with AttrMap for color palette.
3. **Scanner integration**: urwid's `Edit` widget captures scanner keystrokes natively. Enter key triggers state transitions via callback.
4. **pandas removal**: Replace `DataFrame.to_excel()` with direct `openpyxl` worksheet append. Reduces binary size ~50MB.
5. **Termux compilation**: Document on-tablet `pyinstaller` build with known `_bootlocale` and lib path workarounds.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `main.py` | Major rewrite | UI layer replaced with urwid; business logic preserved |
| `colors.py` | Removed | urwid palette system replaces ANSI codes |
| `pyproject.toml` | Modified | Add urwid, remove pandas |
| `build.spec` | Modified | Update hiddenimports for urwid, remove pandas |
| `Makefile` | Modified | Add `termux-build` target |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| PyInstaller on Termux has known bugs | High | Test compilation early; fallback to `python main.py` launcher script |
| Binary size 80-120MB | Medium | UPX compression; `--exclude-module` for unused pandas internals |
| Touch navigation limited | Low | Scanner-first design; on-screen numbered shortcuts |
| Validation regex mismatch (9 vs 7 chars) | Low | Not a blocker; note for future cleanup |

## Rollback Plan

Revert `main.py` to previous CLI version. Remove urwid from `pyproject.toml` and `build.spec`. Restore `colors.py`. Domain files are unchanged — no rollback needed there.

## Dependencies

- urwid library (pip install)
- Termux environment on target tablets
- PyInstaller with Termux workarounds

## Success Criteria

- [ ] Application launches in urwid TUI mode on Termux
- [ ] Bluetooth scanner input captured correctly in Edit widget
- [ ] Scanned rolls appear in real-time scrollable list
- [ ] State machine transitions work (location → rolls → confirm → location)
- [ ] Excel writes succeed without pandas
- [ ] Binary compiles on Termux (or launcher script works)
- [ ] All existing tests pass (domain logic unchanged)

## Proposal Question Round

These questions aim to uncover business rules and edge cases before finalizing:

1. **How many tablets will run this?** Affects distribution strategy — single-device manual copy vs. scripted multi-device deployment.

2. **Should the app auto-save periodically or only on explicit confirm?** Current flow saves per batch on location change. Auto-save could prevent data loss on crash but complicates the "undo last scan" flow.

3. **What happens if the Excel file gets corrupted?** Should the app create a backup before each write? Or is manual recovery acceptable?

4. **Should the TUI show a history of scanned items across locations, or only the current location?** Affects ListBox scope and memory usage.

5. **Any accessibility needs?** Font size, high-contrast mode, or color-blind-friendly palette for the warehouse environment?
