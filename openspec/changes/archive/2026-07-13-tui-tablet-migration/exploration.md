# Exploration: TUI Tablet Migration

## Current State

The system is a Python 3.13 CLI application (~350 lines total across 4 source files) for warehouse inventory control. It runs on Android tablets via Termux with Bluetooth barcode scanners.

**Architecture:**
- `main.py` (244 lines) — Monolithic main loop using `input()`/`print()` with ANSI color codes. Handles: user login (argv), Excel file creation, location scanning loop, roll scanning loop, duplicate/uniqueness validation, Excel append writes.
- `ubic.py` (9 lines) — `Ubic` class: parses 10-char location codes into depo/pasillo/columna/nivel fields.
- `rel_ubic.py` (16 lines) — `ProdUbic` class: stores user, location, roll code, timestamp.
- `validation.py` (22 lines) — Regex validators for location (10 chars, uppercase alphanumeric) and roll (9 chars, alphanumeric — note: PRD says 7 but regex says 9).
- `colors.py` (7 lines) — ANSI escape code constants (GREEN, RED, YELLOW, etc.).
- `pyproject.toml` — Dependencies: openpyxl, pandas, pyinstaller. Python >=3.13.
- `build.spec` / `main.spec` — PyInstaller specs for standalone binary.
- `Makefile` — `make build`, `make test`, `make clean`.
- `tests/` — 3 test files: validation (92 lines), ubic (43 lines), rel_ubic (42 lines).

**Flow:** User → argv login → [LOOP: scan location (10 chars) → [LOOP: scan roll (7 chars)] → save batch to Excel] → exit. Scanner input arrives as keyboard keystrokes + Enter.

**Key constraints:**
- Bluetooth scanner acts as keyboard input (types characters then sends Enter)
- No mouse/touch interaction currently
- Excel file is the only data store (no database)
- Binary must be distributable to tablets (PyInstaller)
- Offline operation required

## Affected Areas

- `main.py` — The ONLY file that needs major restructuring. All UI logic (print_header, print_success, print_error, print_info, print_separator, input prompts, clear_screen) must be replaced with urwid widgets. The core business logic (Excel writes, validation calls, object creation) stays.
- `colors.py` — Becomes unnecessary (urwid has its own palette system). Can be removed or kept as fallback.
- `pyproject.toml` — Must add `urwid` as dependency.
- `build.spec` — Must add `urwid` to hiddenimports.
- `tests/` — Currently tests only domain logic (validation, Ubic, ProdUbic). No UI tests exist. Should remain untouched unless we add integration tests.
- `ubic.py`, `rel_ubic.py`, `validation.py` — NO CHANGES needed. These are pure domain logic with no UI coupling. This is a good sign — clean separation already exists.

## Approaches

### 1. urwid TUI (User's request)

**Pros:**
- Pure Python, installs cleanly via pip in Termux (no native deps)
- Mature library (since 2004, 3k+ GitHub stars, Python 3.9–3.14)
- Rich widget set: Edit (for scanner input), Button, ListBox, Frame, Pile, Columns, Text
- Built-in curses display backend works in Termux's terminal
- Mouse event support (mouse_event method on widgets) — if terminal sends touch-as-mouse
- Automatic screen refresh, no manual clear_screen needed
- Lightweight — adds ~200KB to binary, not MB
- Active maintenance (latest release 2024)

**Cons:**
- Touch input in Termux is keyboard-only by default. Touch taps do NOT translate to mouse events in standard Termux terminal. User would rely entirely on scanner + on-screen virtual buttons (which urwid can render but require keyboard shortcuts to activate).
- Learning curve for urwid widget tree (Pile, Columns, Frame, AttrMap)
- Slightly more complex event loop (MainLoop with callbacks vs linear input() calls)
- No built-in "toast" or "snackbar" notifications — must implement manually

**Effort:** Medium (~2–3 days for a working prototype, ~1 week for polished)

### 2. curses (stdlib)

**Pros:**
- Zero extra dependencies (in Python stdlib)
- Works everywhere Python works, including Termux
- No binary size increase

**Cons:**
- Extremely low-level — you'd build every widget from scratch (text rendering, cursor movement, input handling)
- No built-in widgets (no Edit, Button, ListBox — all DIY)
- Tedious for anything beyond simple forms
- More bugs, more code, more maintenance
- Mouse support varies by terminal

**Effort:** High (~1–2 weeks, and the result would be less polished than urwid)

### 3. Textual (modern TUI framework)

**Pros:**
- Beautiful, modern API with CSS-like styling
- Rich widget set, reactive programming model
- Better developer experience than urwid

**Cons:**
- HEAVIER dependency tree (requires rich, typing_extensions, platformdirs, msgpack, etc.)
- ~5–10MB added to binary size
- Overkill for this simple scan-and-save workflow
- Newer, less battle-tested in constrained environments like Termux
- May have issues with Termux's limited terminal capabilities

**Effort:** Medium (similar to urwid but heavier runtime)

### 4. Keep CLI + optimize for touch (minimal change)

**Pros:**
- Zero migration risk
- No new dependencies
- Scanner input already works perfectly
- Can improve UX without rewriting: bigger prompts, color-coded status bar, persistent footer with shortcuts

**Cons:**
- No visual improvement (still linear scrolling text)
- User specifically requested TUI
- No way to show persistent status bar, scanned items count, or navigation hints
- clear_screen() calls cause flickering on slow tablets

**Effort:** Low (1 day of polish)

## Recommendation

**Go with urwid.** Here's why:

1. **The codebase is READY for this.** Domain logic (ubic.py, rel_ubic.py, validation.py) is completely decoupled from UI. The migration is purely in `main.py`.

2. **urwid fits the constraints.** Pure Python, lightweight, works in Termux, Python 3.13 compatible. Textual is too heavy; curses is too raw.

3. **Bluetooth scanner = keyboard input.** The scanner already types characters + Enter. urwid's `Edit` widget handles this natively. No special scanner integration needed.

4. **Touch limitation is acceptable.** Termux doesn't translate touch to mouse events in standard terminal mode, BUT the use case is scanner-driven, not touch-driven. Virtual buttons in the UI can be navigated with Tab/Enter or scanner shortcuts. If touch-as-mouse is ever needed, Termux:GUI plugin exists as an escape hatch.

5. **Proposed widget architecture:**
   ```
   urwid.Frame(
     header=urwid.AttrMap(urwid.Text("SISTEMA DE CONTROL DE ALMACEN"), 'header'),
     body=Pile([
       Text("UBICACION / ARTICULOS status"),
       Edit("INPUT: ", ""),
       ListBox(scanned_items),  # scrollable list of scanned rolls
     ]),
     footer=urwid.AttrMap(Text("[0] Salir  [ENTER] Confirmar"), 'footer')
   )
   ```

6. **State machine approach:** Replace the nested while loops with a simple state machine (SCAN_LOCATION → SCAN_ROLLS → CONFIRM_BATCH → back to SCAN_LOCATION). This is cleaner than the current spaghetti of nested loops with `input()` calls.

## Risks

- **PyInstaller on Termux:** Known issues exist (missing `_bootlocale` module, Termux lib path not found). Requires manual patching of PyInstaller. The `pyinstaller-in-termux` repo documents fixes but they're fragile across PyInstaller versions. **Mitigation:** Test compilation early, consider distributing as `python main.py` via Termux with a launcher script instead of compiled binary.
- **Cross-compilation not possible:** PyInstaller cannot cross-compile from x86 to aarch64. Must compile ON the tablet. **Mitigation:** Accept this, document the on-tablet build process.
- **Binary size:** pandas + openpyxl + urwid = potentially 80–120MB binary. **Mitigation:** Consider `--exclude-module` for unused pandas features, use UPX compression (already enabled in build.spec).
- **Touch navigation:** Without a keyboard (only scanner), navigating urwid widgets may be awkward. **Mitigation:** Design the UI to be scanner-first: auto-focus the input field, use Enter to confirm, use on-screen numbered shortcuts. The scanner IS the keyboard.
- **Validation regex mismatch:** `validation.py` says roll is 9 chars (`{9}$`) but PRD says 7 chars. `main.py` line 209 does `articulo_input[:-2]` suggesting the scanner sends 9 chars and the last 2 are stripped. This works but is fragile. **Not a blocker but worth noting.**
