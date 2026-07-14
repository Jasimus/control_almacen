"""Main urwid application for warehouse control.

Wires together the state machine, widgets, and Excel store into a
flicker-free TUI optimized for Bluetooth barcode scanner input.
"""

from typing import Optional
import urwid

from tui.states import State, transition
from tui.widgets import (
    HeaderWidget,
    InputWidget,
    StatusWidget,
    HistoryWidget,
    make_header,
    make_footer,
    make_body,
)
from tui.excel import ExcelStore


TITLE = "SISTEMA DE CONTROL DE ALMACÉN"

# Prompt text shown in the input field per state
PROMPTS = {
    State.SCAN_LOCATION: "UBICACIÓN: ",
    State.SCAN_ROLLS: "ARTÍCULO: ",
    State.CONFIRM_BATCH: "0. Guardar  /  1. Agregar más: ",
    State.SESSION_SUMMARY: "Presione ENTER para nueva ubicación: ",
}


class ControlAlmacenApp:
    """Main urwid application with FSM dispatch and widget orchestration.

    The app manages a Frame containing header, body (status + input + history),
    and footer. Scanner keystrokes are captured by the Edit widget; Enter
    triggers state transitions via the states.transition() function.
    """

    def __init__(self, store: ExcelStore, user: str) -> None:
        """Initialize the app.

        Args:
            store: ExcelStore for reading/writing workbook data.
            user: Current user identifier.
        """
        self.store = store
        self.user = user

        # Session state
        self.state = State.SCAN_LOCATION
        self.session_items: list[str] = []
        self.current_batch: list[str] = []
        self.current_location: Optional[str] = None
        self.last_error: Optional[str] = None

        # Build widget tree
        self._header = HeaderWidget(TITLE, user)
        self._footer = StatusWidget()
        self._input = InputWidget(caption=PROMPTS[self.state])
        self._history = HistoryWidget()
        self._status_text = urwid.Text("")
        self._status_attr = urwid.AttrMap(self._status_text, "info")

        body = urwid.Pile([
            ("pack", self._status_attr),
            ("pack", self._input.widget),
            ("weight", 1, self._history.widget),
        ])

        self._frame = urwid.Frame(
            body=body,
            header=self._header.widget,
            footer=self._footer.widget,
        )

        # Initial UI update
        self._update_ui()

    def run(self) -> None:
        """Start the urwid main loop."""
        palette = [
            ("header", "white", "dark blue"),
            ("footer", "white", "dark gray"),
            ("info", "light cyan", ""),
            ("error", "light red", ""),
            ("success", "light green", ""),
        ]
        self._loop = urwid.MainLoop(
            self._frame,
            palette=palette,
            unhandled_input=self._on_key,
        )
        self._loop.run()

    def _on_key(self, key: str) -> None:
        """Handle unhandled input (function keys, F4 exit)."""
        if key == "f4":
            raise urwid.ExitMainLoop()
        elif key == "f1":
            self._jump_to(State.SCAN_LOCATION)
        elif key == "f2":
            self._jump_to(State.SESSION_SUMMARY)
        elif key == "enter":
            self._process_input()
        elif key == "escape":
            self._input.clear()

    def _jump_to(self, target: State) -> None:
        """Force-jump to a target state (F1/F2 shortcuts).

        Clears any unsaved batch and resets input.
        """
        self.last_error = None
        self.current_batch = []
        self.current_location = None
        self.state = target
        self._input.clear()
        self._input.set_caption(PROMPTS[self.state])
        self._update_ui()

    def _process_input(self) -> None:
        """Read input text and trigger a state transition."""
        text = self._input.get_text().strip()
        if not text:
            return

        next_state, error = transition(self.state, text)

        if error:
            self.last_error = error
            self._input.clear()
            self._update_ui()
            return

        # Transition succeeded — clear error
        self.last_error = None

        # Side effects on transition
        self._on_transition(self.state, next_state, text)

        self.state = next_state
        self._input.clear()
        self._input.set_caption(PROMPTS[self.state])
        self._update_ui()

    def _on_transition(
        self, current: State, next_state: State, text: str
    ) -> None:
        """Execute side effects for a successful transition.

        Handles batch accumulation, Excel writes, and history tracking.
        """
        if current == State.SCAN_LOCATION and next_state == State.SCAN_ROLLS:
            # Valid location scanned — record it
            self.current_location = text
            self.current_batch = []
            from ubic import Ubic
            self.store.append_ubicacion(Ubic(text))

        elif current == State.SCAN_ROLLS and next_state == State.SCAN_ROLLS:
            # Valid roll scanned — add to batch
            self.current_batch.append(text)
            self.session_items.append(text)
            self._history.add_item(f"  {text}")

        elif current == State.SCAN_ROLLS and next_state == State.CONFIRM_BATCH:
            # User pressed 0 to review batch
            pass

        elif current == State.CONFIRM_BATCH and next_state == State.SCAN_LOCATION:
            # User confirmed batch — save to Excel
            if self.current_batch and self.current_location:
                from rel_ubic import ProdUbic
                articulos = [
                    ProdUbic(self.user, self.current_location, roll)
                    for roll in self.current_batch
                ]
                self.store.append_articulos(articulos)

        elif current == State.CONFIRM_BATCH and next_state == State.SCAN_ROLLS:
            # User chose to add more rolls
            pass

    def _update_ui(self) -> None:
        """Refresh all dynamic widgets to reflect current state."""
        state_label = self.state.name.replace("_", " ").title()

        if self.state == State.SCAN_LOCATION:
            self._status_text.set_text(
                f"Escaneé la ubicación (10 caracteres).  0=Salir"
            )
            self._footer.update(state_label, len(self.session_items), self.last_error)

        elif self.state == State.SCAN_ROLLS:
            self._status_text.set_text(
                f"UBICACIÓN: {self.current_location}  |  "
                f"Cargados: {len(self.current_batch)}  |  "
                f"0=Verificar"
            )
            self._footer.update(state_label, len(self.session_items), self.last_error)

        elif self.state == State.CONFIRM_BATCH:
            if self.current_batch:
                items = "\n".join(f"  [{i+1}] {r}" for i, r in enumerate(self.current_batch))
                self._status_text.set_text(
                    f"ARTÍCULOS EN ESTA UBICACIÓN ({len(self.current_batch)}):\n"
                    f"{items}\n"
                    f"0. Confirmar y guardar  |  1. Agregar más"
                )
            else:
                self._status_text.set_text("No hay artículos para confirmar.")
            self._footer.update(state_label, len(self.session_items), self.last_error)

        elif self.state == State.SESSION_SUMMARY:
            if self.session_items:
                items = "\n".join(f"  [{i+1}] {r}" for i, r in enumerate(self.session_items))
                self._status_text.set_text(
                    f"RESUMEN DE LA SESIÓN ({len(self.session_items)} artículos):\n"
                    f"{items}\n"
                    f"ENTER para nueva ubicación"
                )
            else:
                self._status_text.set_text("Sesión vacía. ENTER para comenzar.")
            self._footer.update(state_label, len(self.session_items), self.last_error)
