# Design: Control Almacen Improvements

## Technical Approach

Incremental refactor of a CLI barcode scanner for warehouse roll registration. The system validates location (10-char) and roll (7-char) codes via Bluetooth scanner input, writes to a single Excel workbook, and must run offline on tablets. Changes are additive: fix bugs first, then layer validation, traceability, cross-session uniqueness, tests, and PyInstaller packaging. The architecture stays flat (no packages) — modules are added alongside existing files, not restructured.

## Architecture Decisions

| Decision | Choice | Alternatives | Rationale |
|----------|--------|--------------|-----------|
| Module layout | Flat files at root | `src/` package, `app/` subdirs | Current codebase is 4 flat files. Adding a package structure for 2 new modules is over-engineering. Keep flat until there's a real need. |
| Validation location | `validation.py` module | Inline in main.py, class methods | Centralizes regex patterns, single source of truth. Easier to test. |
| Cross-session cache | `set` loaded at startup from Excel | SQLite, pickle, JSON cache | File is the source of truth. A set gives O(1) lookup. No extra dependency. SQLite adds complexity for ~12K rows that already live in Excel. |
| Datetime storage | String `YYYY-MM-DD HH:MM:SS` | openpyxl datetime, epoch | String is human-readable in Excel, no timezone headaches, no serialization issues across platforms. |
| Test structure | `tests/` at root with pytest | `unittest` in each module | Spec requires pytest. Separate test dir keeps production code clean. |
| Build tool | PyInstaller `--onefile` | Nuitka, cx_Freeze | Spec requires PyInstaller. `--onefile` simplest for tablet distribution. |

## Data Flow

```
User (CLI)
  │
  ├─ arg[1] = username
  │
  ▼
main.py
  │
  ├─ load_workbook("deposito.xlsx")          ← Excel I/O
  │     └─ if FileNotFoundError → create empty workbook
  │
  ├─ load_existing_rolls()                    ← NEW: cross-session
  │     └─ read articulos.sheet → set of id_lote
  │
  ▼
[Location Loop]
  │  input("Escanee ubicación")
  │
  ├─ validate_location(input)                 ← NEW: regex ^[A-Z]{4}\d{6}$
  │     └─ FAIL → show error, retry
  │
  ├─ Ubic(input)                              ← FIX: ubic = input (not "DPA")
  │     └─ write to ubicacion sheet
  │
  ▼
[Roll Loop]
  │  input("Escanee rollo")
  │
  ├─ validate_roll(input)                     ← NEW: regex ^[A-Za-z0-9]{7}$
  │     └─ FAIL → show error, retry
  │
  ├─ check duplicate (session set ∪ loaded set)
  │     └─ FAIL → show error, retry
  │
  ├─ ProdUbic(user, ubic.id, roll)           ← MODIFY: add fecha_hora
  │     └─ append to session rolls, write to articulos sheet
  │
  └─ input("0") → return to location loop
```

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `main.py` | Modify | Fix import (`typing.List`), fix hardcoded ubic, add startup roll loading, integrate validation, add fecha_hora to writes |
| `ubic.py` | Modify | Fix `ubic = id` instead of hardcoded `"DPA"` |
| `rel_ubic.py` | Modify | Add `fecha_hora` field with `datetime.now().strftime()` |
| `validation.py` | Create | `validate_location(code) -> bool`, `validate_roll(code) -> bool` — regex patterns |
| `colors.py` | No change | Already correct |
| `pyproject.toml` | Modify | Add `pytest` to dev dependencies |
| `tests/__init__.py` | Create | Empty, marks tests as package |
| `tests/test_ubic.py` | Create | Ubic parsing, field extraction, ubic derivation |
| `tests/test_rel_ubic.py` | Create | ProdUbic creation, fecha_hora format |
| `tests/test_validation.py` | Create | Regex patterns — valid/invalid cases per spec |
| `Makefile` | Create | `build` target wrapping PyInstaller command |
| `build.spec` | Create | PyInstaller spec with hidden imports for pandas/openpyxl |

## Interfaces / Contracts

```python
# validation.py
import re

LOCATION_RE = re.compile(r'^[A-Z]{4}\d{6}$')  # 4 uppercase letters + 6 digits
ROLL_RE = re.compile(r'^[A-Za-z0-9]{7}$')      # 7 alphanumeric chars

def validate_location(code: str) -> bool:
    return bool(LOCATION_RE.match(code))

def validate_roll(code: str) -> bool:
    return bool(ROLL_RE.match(code))
```

```python
# rel_ubic.py (modified)
from datetime import datetime

class ProdUbic:
    def __init__(self, id_usuario: str, id_ubic: str, id_lote: str):
        self.id_usuario = id_usuario
        self.id_ubic = id_ubic
        self.id_lote = id_lote
        self.fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
```

```python
# main.py (cross-session loading — startup section)
def load_existing_rolls(file_path: str) -> set[str]:
    """Load all id_lote values from existing articulos sheet."""
    try:
        df = pd.read_excel(file_path, sheet_name='articulos', engine='openpyxl')
        if 'id_lote' in df.columns:
            return set(df['id_lote'].dropna().astype(str))
    except Exception:
        pass
    return set()
```

## Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Unit — `test_validation.py` | Regex patterns: valid/invalid locations and rolls | Direct function calls, parametrized cases from spec scenarios |
| Unit — `test_ubic.py` | Field parsing, ubic derivation from input | Instantiate `Ubic`, assert all 5 fields |
| Unit — `test_rel_ubic.py` | Object creation, fecha_hora format | Instantiate `ProdUbic`, check format with regex `^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$` |
| Unit — `test_main.py` | `load_existing_rolls()` with mock Excel | Create temp xlsx with `openpyxl`, verify set size and contents |
| Integration | Full loop with temp file | Mock `input()` calls, verify Excel output has correct columns including `fecha_hora` |

**Mock strategy**: For `load_existing_rolls`, create real temp `.xlsx` files (not mocking pandas) — this tests the actual openpyxl integration. For CLI loop testing, mock `input()` and `sys.argv`.

## Threat Matrix

N/A — no routing, shell commands, subprocesses, VCS/PR automation, executable-file classification, or process-integration boundary. The `os.system("clear")` call is cosmetic screen clearing, not a security boundary.

## Migration / Rollout

**Existing Excel files**: No migration required. The `fecha_hora` column is additive — new rows include it, old rows remain untouched. When `load_existing_rolls()` reads an old file without `fecha_hora`, the column absence is handled by the `if 'id_lote' in df.columns` guard. The `ubic` column in the `ubicacion` sheet will now store the full input instead of `"DPA"`, but this is a correction, not a format change — old rows keep their `"DPA"` values.

**Backward compatibility**: The Excel format is forward-compatible. New files get `fecha_hora`. Old files work without it. No schema migration needed.

## Open Questions

- [ ] Should the `ubic` field in existing `ubicacion` rows be backfilled? (Current design: no — old rows keep `"DPA"`, new rows get full input)
- [ ] Is the location regex `^[A-Z]{4}\d{6}$` correct? The PRD shows `DEP1A14702` where `DEP1` is 3 letters + 1 digit, but the spec says 4 uppercase letters. Which is the actual format?
