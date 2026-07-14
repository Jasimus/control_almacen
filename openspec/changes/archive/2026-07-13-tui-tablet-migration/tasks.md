# Tasks: TUI Tablet Migration

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 700–800 |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | PR 1 → PR 2 → PR 3 → PR 4 |
| Delivery strategy | auto-chain |
| Chain strategy | stacked-to-main |

Decision needed before apply: No
Chained PRs recommended: Yes
Chain strategy: stacked-to-main
400-line budget risk: High

### Suggested Work Units

| Unit | Goal | Likely PR | Focused test command | Runtime harness | Rollback boundary |
|------|------|-----------|----------------------|-----------------|-------------------|
| 1 | Foundation: package, states, excel store | PR 1 | `pytest tests/tui/test_states.py tests/tui/test_excel.py -v` | N/A — pure logic, no urwid main loop | Revert `tui/` dir; `main.py` unchanged |
| 2 | Widget layer + app wiring | PR 2 | `pytest tests/tui/test_widgets.py -v` + manual `python main.py testuser` | Manual scan flow on terminal | Revert `tui/widgets.py`, `tui/app.py`; `tui/states.py` + `tui/excel.py` intact |
| 3 | Entry point + dependency swap | PR 3 | `python main.py testuser` (urwid launches) + `pytest tests/` | Full manual flow with scanner | Revert `main.py`, `pyproject.toml`; TUI modules stay |
| 4 | Build + cleanup | PR 4 | `make termux-build` (or manual pyinstaller) | Binary compiles and runs on Termux | Revert `build.spec`, `Makefile`, `build_termux.sh`; delete `colors.py` last |

## Phase 1: Foundation

- [x] 1.1 Create `tui/__init__.py` (empty package marker)
- [x] 1.2 Create `tui/states.py`: `State` enum (SCAN_LOCATION, SCAN_ROLLS, CONFIRM_BATCH, SESSION_SUMMARY) + `transition(state, input_text) → (new_state, error|None)` using dispatch dict
- [x] 1.3 Write `tests/tui/test_states.py`: verify each valid transition path + invalid-input stays in same state
- [x] 1.4 Create `tui/excel.py`: `ExcelStore` class with `load_existing_rolls() → set[str]`, `append_location(ubic)`, `append_articulos(articulos)` using openpyxl directly
- [x] 1.5 Write `tests/tui/test_excel.py`: temp-file tests for load, append, duplicate detection

## Phase 2: Widget Layer

- [x] 2.1 Create `tui/widgets.py`: `make_header()`, `make_footer()`, `make_body(status_msg, scan_items)` widget builders returning urwid widgets
- [x] 2.2 Create `tui/app.py`: `App` class with FSM dispatch, urwid `MainLoop`, `on_input()` Enter callback, widget update on transition
- [x] 2.3 Wire `App.__init__` to accept `ExcelStore` and user; `App.run()` starts `urwid.MainLoop`
- [x] 2.4 Write `tests/tui/test_widgets.py`: verify widget tree structure and update behavior

## Phase 3: Integration

- [x] 3.1 Rewrite `main.py`: thin entry — parse `sys.argv[1]` as user, create `ExcelStore`, create `App`, call `app.run()`. Remove all `print()`/`input()`/`os.system("clear")`
- [x] 3.2 Update `pyproject.toml`: add `urwid>=2.6` to dependencies, remove `pandas>=3.0.3`
- [x] 3.3 Run full `pytest tests/` — all existing domain tests + new tui tests pass

## Phase 4: Build & Cleanup

- [x] 4.1 Update `build.spec`: replace pandas/numpy hiddenimports with urwid + `tui.*`; add `--exclude-module pandas`
- [x] 4.2 Update `Makefile`: add `termux-build` target calling `build_termux.sh`
- [x] 4.3 Create `build_termux.sh`: install deps, run pyinstaller, fallback to `python main.py` if binary fails
- [x] 4.4 Delete `colors.py`
- [x] 4.5 Verify: `python main.py testuser` launches urwid TUI; `make termux-build` succeeds (or documented fallback)
