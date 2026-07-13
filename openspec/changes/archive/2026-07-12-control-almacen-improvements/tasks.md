# Tasks: Warehouse Barcode Scanning Improvements

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~210 |
| 400-line budget risk | Low |
| Chained PRs recommended | No |
| Suggested split | Single PR |
| Delivery strategy | single-pr |
| Chain strategy | size-exception |

Decision needed before apply: Yes
Chained PRs recommended: No
Chain strategy: size-exception
400-line budget risk: Low

### Suggested Work Units

| Unit | Goal | Likely PR | Focused test command | Runtime harness | Rollback boundary |
|------|------|-----------|----------------------|-----------------|-------------------|
| 1 | Full change | PR 1 | `uv run pytest tests/ -v` | `uv run main.py testuser` | All files are additive; revert PR to rollback |

## Phase 1: Bug Fixes

- [x] 1.1 Fix `main.py:1` — replace `from ast import List` with `from typing import List`
- [x] 1.2 Fix `ubic.py:9` — replace `self.ubic = "DPA"` with `self.ubic = id`
- [x] 1.3 Verify: `uv run python -c "from ubic import Ubic; u = Ubic('DPA1A14702'); assert u.ubic == 'DPA1A14702'"`

## Phase 2: Validation Module

- [x] 2.1 Create `validation.py` with `validate_ubicacion(loc: str) -> bool` using regex `^[A-Z]{4}\d{6}$`
- [x] 2.2 Add `validate_articulo(art: str) -> bool` using regex `^[A-Za-z0-9]{7}$`
- [x] 2.3 Add error messages: `"EL FORMATO NO COINCIDE CON EL DE LA UBICACIÓN. REINTENTE"` and `"EL ARTICULO NO CUMPLE CON EL FORMATO. REINTENTE."`
- [x] 2.4 Update `main.py:42-44` — replace `len(ubicacion_input) != 10` with `not validate_ubicacion(ubicacion_input)`
- [x] 2.5 Update `main.py:83-85` — replace `len(articulo_input) != 7` with `not validate_articulo(articulo_input)`
- [x] 2.6 Verify: `uv run python -c "from validation import validate_ubicacion; assert validate_ubicacion('DPA1A14702'); assert not validate_ubicacion('dpa1a14702')"`

## Phase 3: Cross-Session Uniqueness

- [x] 3.1 Add `load_existing_rolls(file: str) -> set` function in `main.py` — reads `id_lote` column from `articulos` sheet into a `set`
- [x] 3.2 Call `load_existing_rolls()` after `load_workbook()` succeeds (before the main loop)
- [x] 3.3 Update duplicate check in `main.py:89-93` — check against both `existing_rolls` set AND `articulos` session list
- [x] 3.4 Add new rolls to `existing_rolls` set after appending to session list
- [x] 3.5 Verify: create test Excel with existing roll, confirm rejection on startup

## Phase 4: Fecha/Hora Tracking

- [x] 4.1 Add `fecha_hora` field to `ProdUbic.__init__` in `rel_ubic.py` — populated with `datetime.now().strftime("%Y-%m-%d %H:%M:%S")`
- [x] 4.2 Add `from datetime import datetime` import to `rel_ubic.py`
- [x] 4.3 Update `main.py:29` — add `'fecha_hora'` to `df_articulos` columns list
- [x] 4.4 Update `__str__` in `rel_ubic.py` to include `fecha_hora`
- [x] 4.5 Verify: `uv run python -c "from rel_ubic import ProdUbic; p = ProdUbic('u','loc','lot'); assert len(p.fecha_hora) == 19"`

## Phase 5: Tests

- [x] 5.1 Create `tests/` directory with `__init__.py`
- [x] 5.2 Create `tests/test_ubic.py` — test `Ubic` parsing: field extraction, `ubic` derived from input
- [x] 5.3 Create `tests/test_rel_ubic.py` — test `ProdUbic` creation, `fecha_hora` format
- [x] 5.4 Create `tests/test_validation.py` — test valid/invalid locations and rolls per spec scenarios
- [x] 5.5 Add `pytest` to `[dependency-groups] dev` in `pyproject.toml`
- [x] 5.6 Verify: `uv run pytest tests/ -v` — all tests pass

## Phase 6: Build Configuration

- [x] 6.1 Create `build.spec` — PyInstaller spec with `--onefile`, hidden imports for `pandas`, `openpyxl`
- [x] 6.2 Create `Makefile` with `build` target: `pyinstaller build.spec`
- [x] 6.3 Verify: `make build && ./dist/main` runs without errors
