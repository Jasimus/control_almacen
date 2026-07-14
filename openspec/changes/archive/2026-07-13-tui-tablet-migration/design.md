# Design: TUI Tablet Migration

## Technical Approach

Replace the nested `while` loops and `input()/print()` CLI in `main.py` with a finite state machine (FSM) powered by urwid. The scanner acts as a keyboard — `Edit` widgets capture keystrokes, Enter triggers transitions. Domain logic (`ubic.py`, `rel_ubic.py`, `validation.py`) stays untouched.

## Architecture Decisions

| Decision | Options | Tradeoff | Choice |
|----------|---------|----------|--------|
| **State machine style** | A) Enum + dispatch dict | B) Class per state | C) Single class with mode attr |
| | A: Flat, easy to reason | B: Polymorphic but heavier | C: Mutable state, harder to test |
| | A: One file, clear transitions | B: Good for complex per-state logic | C: State leaks between modes |
| **Decision** | | | **A — Enum + dispatch dict** |
| **Widget tree** | A) Frame(body) | B) Pile manually | |
| | A: urwid handles focus cycling | B: Manual focus management | |
| **Decision** | | | **A — Frame(header, body, footer)** |
| **Excel I/O** | A) openpyxl directly | B) keep pandas | |
| | A: ~50MB smaller binary, full control | B: DataFrame convenience, bigger binary | |
| **Decision** | | | **A — openpyxl directly** |
| **Session history** | A) List in App state | B) ListBox per state | |
| | A: Single source of truth, reused | B: Duplicated per state | |
| **Decision** | | | **A — List in App state** |

## Data Flow

```
Scanner keystrokes
       │
       ▼
┌──────────────┐
│  urwid main  │
│  loop        │
│  (run())     │
└──────┬───────┘
       │  Edit.get_text() on Enter
       ▼
┌──────────────┐    validate_*()
│  State       │─────────────────► OK / ERROR
│  Machine     │
│  (dispatch)  │
└──────┬───────┘
       │  on transition
       ▼
┌──────────────┐     ┌──────────────────┐
│  Update body │────►│  ListBox widget   │
│  widgets     │     │  (session rolls)  │
└──────┬───────┘     └──────────────────┘
       │  on CONFIRM_BATCH
       ▼
┌──────────────┐
│  openpyxl    │
│  append rows │──► deposito_YYYY-MM-DD_HHMM.xlsx
└──────────────┘
```

## Widget Tree

```
Frame
├─ Header: AttrMap(Text("SISTEMA DE CONTROL DE ALMACEN"), "header")
├─ Body: Pile
│   ├─ [0] AttrMap(Text(status_msg), "info")
│   ├─ [1] AttrMap(Edit(prompt, ""), "input")
│   └─ [2] ListBox(AttrMap Walker(session_items))
└─ Footer: AttrMap(Text("F1:Ubic  F2:Resumen  Esc:Limpiar  0:Salir"), "footer")
```

`status_msg` and `session_items` are updated by the App on each transition. The `Edit` widget is replaced (not cleared) on state change to reset prompt text.

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `tui/app.py` | Create | App class: FSM, urwid main loop, state dispatch, widget orchestration |
| `tui/states.py` | Create | State enum + transition logic (validate → next state or error) |
| `tui/widgets.py` | Create | Widget builders: make_header, make_footer, make_body, update helpers |
| `tui/excel.py` | Create | Direct openpyxl load/append/save — no pandas |
| `main.py` | Rewrite | Thin entry: parse args, create App, run. Remove all print/input/clear |
| `pyproject.toml` | Modify | Add `urwid>=2.6`, remove `pandas>=3.0.3` |
| `build.spec` | Modify | hiddenimports: remove pandas/numpy, add urwid/tui.*, add excludes |
| `Makefile` | Modify | Add `termux-build` target |
| `build_termux.sh` | Create | On-tablet build + launcher fallback script |
| `colors.py` | Delete | Replaced by urwid palette |

## Key Interfaces

```python
# tui/states.py
from enum import Enum, auto

class State(Enum):
    SCAN_LOCATION = auto()
    SCAN_ROLLS = auto()
    CONFIRM_BATCH = auto()
    SESSION_SUMMARY = auto()

# tui/excel.py
class ExcelStore:
    def __init__(self, filepath: str): ...
    def load_existing_rolls(self) -> set[str]: ...
    def append_location(self, ubic: Ubic) -> None: ...
    def append_articulos(self, articulos: list[ProdUbic]) -> None: ...

# tui/app.py
class App:
    def __init__(self, user: str, store: ExcelStore): ...
    def run(self) -> None:  # urwid.MainLoop.run()
    def transition(self, new_state: State) -> None: ...
    def on_input(self, widget, text: str) -> None:  # Enter callback
```

## Testing Strategy

| Layer | What | Approach |
|-------|------|----------|
| Unit | State transitions, validation reuse | pytest with mocked App; verify State enum output |
| Unit | Excel I/O (append, load) | openpyxl on temp files; verify row counts |
| Integration | Full scan flow | Mock scanner input as string list; assert final Excel content |
| E2E | Manual on Termux | Run `python main.py testuser`, scan real barcodes |

## Threat Matrix

| Boundary | Applicable? | Notes |
|----------|-------------|-------|
| Shell commands | N/A | `os.system("clear")` replaced by urwid — no shell calls remain |
| File I/O | Yes | Excel writes via openpyxl. Safe: append-only, no user-controlled paths beyond filename |
| Subprocess | N/A | No subprocess usage |
| VCS automation | N/A | No git operations |
| Executable classification | N/A | Single binary / script |
| Process integration | N/A | Standalone app |

## Migration / Rollout

No data migration. `colors.py` is deleted. `main.py` is a full rewrite — previous version preserved in git history. Rollback: revert to pre-migration commit.

## Open Questions

- [ ] Should the app auto-save on crash (signal handler) or rely on batch confirm?
- [ ] Should `validation.py` regex for rolls be corrected from 9 to 7 chars per the comment?
