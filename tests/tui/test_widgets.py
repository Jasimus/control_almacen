"""Tests for tui.widgets and tui.app — widget layer and app wiring."""

import pytest
from unittest.mock import MagicMock, patch, call
import urwid

from tui.widgets import (
    HeaderWidget,
    InputWidget,
    StatusWidget,
    HistoryWidget,
    make_header,
    make_footer,
    make_body,
)
from tui.app import ControlAlmacenApp, TITLE, PROMPTS
from tui.states import State


# ---------------------------------------------------------------------------
# HeaderWidget
# ---------------------------------------------------------------------------

class TestHeaderWidget:
    def test_creates_text_with_title_and_user(self):
        hw = HeaderWidget("MY APP", "alice")
        text = hw.widget.base_widget
        assert "MY APP" in text.get_text()[0]
        assert "alice" in text.get_text()[0]

    def test_widget_is_attrmap(self):
        hw = HeaderWidget("T", "u")
        assert isinstance(hw.widget, urwid.AttrMap)

    def test_make_header_returns_attrmap(self):
        widget = make_header("TITLE", "bob")
        assert isinstance(widget, urwid.AttrMap)


# ---------------------------------------------------------------------------
# InputWidget
# ---------------------------------------------------------------------------

class TestInputWidget:
    def test_default_caption(self):
        iw = InputWidget()
        assert iw.widget.caption == "> "

    def test_custom_caption(self):
        iw = InputWidget(caption="UBICACIÓN: ")
        assert iw.widget.caption == "UBICACIÓN: "

    def test_get_text_empty(self):
        iw = InputWidget()
        assert iw.get_text() == ""

    def test_get_text_after_edit(self):
        iw = InputWidget()
        iw.widget.set_edit_text("ABC123")
        assert iw.get_text() == "ABC123"

    def test_set_caption(self):
        iw = InputWidget(caption="OLD: ")
        iw.set_caption("NEW: ")
        assert iw.widget.caption == "NEW: "

    def test_clear(self):
        iw = InputWidget()
        iw.widget.set_edit_text("something")
        iw.clear()
        assert iw.get_text() == ""


# ---------------------------------------------------------------------------
# StatusWidget
# ---------------------------------------------------------------------------

class TestStatusWidget:
    def test_initial_text_empty(self):
        sw = StatusWidget()
        text = sw.widget.base_widget.get_text()[0]
        assert text == ""

    def test_update_shows_state(self):
        sw = StatusWidget()
        sw.update("Scan Location", 5)
        text = sw.widget.base_widget.get_text()[0]
        assert "Scan Location" in text
        assert "5" in text

    def test_update_with_error(self):
        sw = StatusWidget()
        sw.update("Scan Rolls", 3, error="Invalid format")
        text = sw.widget.base_widget.get_text()[0]
        assert "Invalid format" in text
        assert "⚠" in text

    def test_update_without_error(self):
        sw = StatusWidget()
        sw.update("Scan Location", 0, error=None)
        text = sw.widget.base_widget.get_text()[0]
        assert "⚠" not in text

    def test_make_footer_returns_status_widget(self):
        sw = make_footer()
        assert isinstance(sw, StatusWidget)


# ---------------------------------------------------------------------------
# HistoryWidget
# ---------------------------------------------------------------------------

class TestHistoryWidget:
    def test_initially_empty(self):
        hw = HistoryWidget()
        assert len(hw.widget.body) == 0

    def test_add_item(self):
        hw = HistoryWidget()
        hw.add_item("ITEM-001")
        assert len(hw.widget.body) == 1
        text = hw.widget.body[0].get_text()[0]
        assert "ITEM-001" in text

    def test_add_multiple_items(self):
        hw = HistoryWidget()
        hw.add_item("A")
        hw.add_item("B")
        hw.add_item("C")
        assert len(hw.widget.body) == 3

    def test_clear(self):
        hw = HistoryWidget()
        hw.add_item("A")
        hw.add_item("B")
        hw.clear()
        assert len(hw.widget.body) == 0


# ---------------------------------------------------------------------------
# make_body
# ---------------------------------------------------------------------------

class TestMakeBody:
    def test_returns_tuple_of_three(self):
        body, input_w, history_w = make_body("> ", "status", [])
        assert isinstance(body, urwid.Pile)
        assert isinstance(input_w, InputWidget)
        assert isinstance(history_w, HistoryWidget)

    def test_initial_items_populated(self):
        _, _, history_w = make_body("> ", "", ["X", "Y"])
        assert len(history_w.widget.body) == 2


# ---------------------------------------------------------------------------
# ControlAlmacenApp — unit tests (no urwid.MainLoop)
# ---------------------------------------------------------------------------

class TestControlAlmacenApp:
    def _make_app(self):
        """Create an app with a mocked ExcelStore."""
        mock_store = MagicMock()
        return ControlAlmacenApp(store=mock_store, user="testuser")

    def test_initial_state(self):
        app = self._make_app()
        assert app.state == State.SCAN_LOCATION
        assert app.user == "testuser"

    def test_initial_batch_empty(self):
        app = self._make_app()
        assert app.current_batch == []
        assert app.session_items == []

    def test_header_shows_title_and_user(self):
        app = self._make_app()
        text = app._header.widget.base_widget.get_text()[0]
        assert TITLE in text
        assert "testuser" in text

    def test_footer_updates_on_state_change(self):
        app = self._make_app()
        app.state = State.SCAN_ROLLS
        app._update_ui()
        text = app._footer.widget.base_widget.get_text()[0]
        assert "Scan Rolls" in text

    def test_input_caption_changes_per_state(self):
        app = self._make_app()
        assert app._input.widget.caption == PROMPTS[State.SCAN_LOCATION]
        app.state = State.SCAN_ROLLS
        app._input.set_caption(PROMPTS[State.SCAN_ROLLS])
        assert app._input.widget.caption == PROMPTS[State.SCAN_ROLLS]

    def test_on_key_f4_raises_exit(self):
        app = self._make_app()
        with pytest.raises(urwid.ExitMainLoop):
            app._on_key("f4")

    def test_on_key_escape_clears_input(self):
        app = self._make_app()
        app._input.widget.set_edit_text("abc")
        app._on_key("escape")
        assert app._input.get_text() == ""

    def test_on_key_f1_transitions_to_scan_location(self):
        app = self._make_app()
        app.state = State.SCAN_ROLLS
        app._on_key("f1")
        assert app.state == State.SCAN_LOCATION

    def test_on_key_enter_triggers_process_input(self):
        app = self._make_app()
        app._input.widget.set_edit_text("DPA1A14702")
        app._on_key("enter")
        # Should transition to SCAN_ROLLS
        assert app.state == State.SCAN_ROLLS

    def test_process_input_invalid_shows_error(self):
        app = self._make_app()
        app._input.widget.set_edit_text("bad")
        app._on_key("enter")
        assert app.last_error is not None
        assert app.state == State.SCAN_LOCATION

    def test_process_input_empty_does_nothing(self):
        app = self._make_app()
        app._on_key("enter")
        assert app.state == State.SCAN_LOCATION
        assert app.last_error is None

    def test_location_scan_stores_location(self):
        app = self._make_app()
        app._input.widget.set_edit_text("DPA1A14702")
        app._on_key("enter")
        assert app.current_location == "DPA1A14702"
        app.store.append_ubicacion.assert_called_once()

    def test_roll_scan_adds_to_batch(self):
        app = self._make_app()
        # First scan a location
        app._input.widget.set_edit_text("DPA1A14702")
        app._on_key("enter")
        assert app.state == State.SCAN_ROLLS

        # Now scan a roll
        app._input.widget.set_edit_text("ABC123456")
        app._on_key("enter")
        assert "ABC123456" in app.current_batch
        assert "ABC123456" in app.session_items

    def test_confirm_batch_saves_to_excel(self):
        app = self._make_app()
        # Scan location
        app._input.widget.set_edit_text("DPA1A14702")
        app._on_key("enter")
        # Scan a roll
        app._input.widget.set_edit_text("ABC123456")
        app._on_key("enter")
        # Press 0 to go to confirm
        app._input.widget.set_edit_text("0")
        app._on_key("enter")
        assert app.state == State.CONFIRM_BATCH
        # Confirm batch
        app._input.widget.set_edit_text("0")
        app._on_key("enter")
        assert app.state == State.SCAN_LOCATION
        app.store.append_articulos.assert_called_once()

    def test_f4_exits_app(self):
        app = self._make_app()
        with pytest.raises(urwid.ExitMainLoop):
            app._on_key("f4")

    def test_f2_goes_to_session_summary(self):
        app = self._make_app()
        app._on_key("f2")
        assert app.state == State.SESSION_SUMMARY

    def test_status_text_updates_on_state(self):
        app = self._make_app()
        app._update_ui()
        text = app._status_text.get_text()[0]
        assert "ubicación" in text.lower() or "UBICACIÓN" in text

    def test_history_grows_with_scans(self):
        app = self._make_app()
        app._input.widget.set_edit_text("DPA1A14702")
        app._on_key("enter")
        app._input.widget.set_edit_text("ABC123456")
        app._on_key("enter")
        assert len(app._history.widget.body) == 1

    def test_error_cleared_on_valid_input(self):
        app = self._make_app()
        # Trigger error
        app._input.widget.set_edit_text("bad")
        app._on_key("enter")
        assert app.last_error is not None
        # Valid input clears error
        app._input.widget.set_edit_text("DPA1A14702")
        app._on_key("enter")
        assert app.last_error is None

    def test_multiple_rolls_in_batch(self):
        app = self._make_app()
        app._input.widget.set_edit_text("DPA1A14702")
        app._on_key("enter")
        for roll in ["ABC123456", "DEF789012", "GHI345678"]:
            app._input.widget.set_edit_text(roll)
            app._on_key("enter")
        assert len(app.current_batch) == 3
        assert len(app.session_items) == 3
