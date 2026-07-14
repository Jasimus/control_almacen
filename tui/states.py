"""State machine for the TUI warehouse control application.

Defines the four application states and transition logic using
an enum + dispatch dict pattern (Design Decision: A).
"""

from enum import Enum, auto
from typing import Optional


class State(Enum):
    """Application states for the TUI state machine."""

    SCAN_LOCATION = auto()
    SCAN_ROLLS = auto()
    CONFIRM_BATCH = auto()
    SESSION_SUMMARY = auto()


def transition(current: State, input_text: str) -> tuple[State, Optional[str]]:
    """Determine the next state based on current state and input.

    Args:
        current: The current application state.
        input_text: Raw input text (e.g. scanned barcode, user command).

    Returns:
        Tuple of (next_state, error_message). error_message is None on
        successful transitions, or a human-readable string on invalid input.
    """
    handlers = {
        State.SCAN_LOCATION: _handle_scan_location,
        State.SCAN_ROLLS: _handle_scan_rolls,
        State.CONFIRM_BATCH: _handle_confirm_batch,
        State.SESSION_SUMMARY: _handle_session_summary,
    }
    handler = handlers[current]
    return handler(input_text)


def _handle_scan_location(text: str) -> tuple[State, Optional[str]]:
    if text == "0":
        return State.SESSION_SUMMARY, None
    if len(text) == 10 and text.isalnum() and text.isupper():
        return State.SCAN_ROLLS, None
    return State.SCAN_LOCATION, "Formato de ubicación inválido. Reintente."


def _handle_scan_rolls(text: str) -> tuple[State, Optional[str]]:
    if text == "0":
        return State.CONFIRM_BATCH, None
    if len(text) == 9 and text.isalnum():
        return State.SCAN_ROLLS, None
    return State.SCAN_ROLLS, "Formato de artículo inválido. Reintente."


def _handle_confirm_batch(text: str) -> tuple[State, Optional[str]]:
    if text == "0":
        return State.SCAN_LOCATION, None
    if text == "1":
        return State.SCAN_ROLLS, None
    return State.CONFIRM_BATCH, "Opción inválida. Ingrese 0 para confirmar."


def _handle_session_summary(text: str) -> tuple[State, Optional[str]]:
    if text == "0":
        return State.SESSION_SUMMARY, None
    return State.SCAN_LOCATION, None
