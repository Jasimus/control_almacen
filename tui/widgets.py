"""Custom urwid widgets for the TUI warehouse control application.

Widget builders that create and update the UI components used by the
main application frame. Each widget is a self-contained urwid widget
with its own update methods.
"""

from typing import Optional
import urwid


class HeaderWidget:
    """Application title bar with user info.

    Displays 'SISTEMA DE CONTROL DE ALMACÉN' and the current user name.
    """

    def __init__(self, title: str, user: str) -> None:
        self._text = urwid.Text(
            f"{title}\nUsuario: {user}", align="center"
        )
        self._attr = urwid.AttrMap(self._text, "header")

    @property
    def widget(self) -> urwid.AttrMap:
        return self._attr


class InputWidget:
    """urwid.Edit wrapper for scanner input with a label.

    Wraps urwid.Edit with a caption that changes per state
    (e.g. 'UBICACIÓN:' or 'ARTÍCULO:').
    """

    def __init__(self, caption: str = "> ") -> None:
        self._edit = urwid.Edit(caption=caption, edit_text="")

    @property
    def widget(self) -> urwid.Edit:
        return self._edit

    def get_text(self) -> str:
        """Return the current edit text (without caption)."""
        return self._edit.edit_text

    def set_caption(self, caption: str) -> None:
        """Update the input caption (e.g. on state change)."""
        self._edit.set_caption(caption)

    def clear(self) -> None:
        """Clear the current input text."""
        self._edit.set_edit_text("")


class StatusWidget:
    """Footer showing current state, item count, errors.

    Renders a single-line bar at the bottom of the screen.
    """

    def __init__(self) -> None:
        self._text = urwid.Text("")
        self._attr = urwid.AttrMap(self._text, "footer")

    @property
    def widget(self) -> urwid.AttrMap:
        return self._attr

    def update(
        self, state_name: str, count: int, error: Optional[str] = None
    ) -> None:
        """Update footer text with current state and info.

        Args:
            state_name: Human-readable state name.
            count: Number of items scanned this session.
            error: Optional error/warning message to display.
        """
        parts = [f"Estado: {state_name}  |  Artículos: {count}"]
        if error:
            parts.append(f"  |  ⚠ {error}")
        self._text.set_text("".join(parts))


class HistoryWidget:
    """ListBox showing session-wide scanned items.

    Scrollable list that grows as items are scanned.
    """

    def __init__(self) -> None:
        self._walker = urwid.SimpleListWalker([])
        self._listbox = urwid.ListBox(self._walker)

    @property
    def widget(self) -> urwid.ListBox:
        return self._listbox

    def add_item(self, text: str) -> None:
        """Append an item to the history list."""
        self._walker.append(urwid.Text(text))
        # Auto-scroll to bottom
        self._listbox.set_focus(len(self._walker) - 1)

    def clear(self) -> None:
        """Remove all items from history."""
        del self._walker[:]


def make_header(title: str, user: str) -> urwid.AttrMap:
    """Build the header widget."""
    return HeaderWidget(title, user).widget


def make_footer() -> StatusWidget:
    """Build the footer widget. Returns the StatusWidget for updates."""
    return StatusWidget()


def make_body(
    prompt: str, status_msg: str, scan_items: list[str]
) -> tuple[urwid.Pile, InputWidget, HistoryWidget]:
    """Build the body widget: status line, input field, and history list.

    Args:
        prompt: Input field caption (e.g. 'UBICACIÓN: ').
        status_msg: Initial status line text.
        scan_items: Initial items to display in history.

    Returns:
        Tuple of (Pile widget, InputWidget, HistoryWidget) for the app
        to access input and history for updates.
    """
    status_text = urwid.Text(status_msg)
    status_attr = urwid.AttrMap(status_text, "info")

    input_w = InputWidget(caption=prompt)
    history_w = HistoryWidget()
    for item in scan_items:
        history_w.add_item(item)

    body = urwid.Pile([
        ("pack", status_attr),
        ("pack", input_w.widget),
        ("weight", 1, history_w.widget),
    ])

    return body, input_w, history_w
