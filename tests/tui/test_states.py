"""Tests for tui.states — state machine transitions."""

import pytest
from tui.states import State, transition


class TestStateEnum:
    def test_has_four_states(self):
        assert len(State) == 4

    def test_state_names(self):
        names = [s.name for s in State]
        assert "SCAN_LOCATION" in names
        assert "SCAN_ROLLS" in names
        assert "CONFIRM_BATCH" in names
        assert "SESSION_SUMMARY" in names


class TestTransitionScanLocation:
    def test_valid_location_to_scan_rolls(self):
        next_state, error = transition(State.SCAN_LOCATION, "DPA1A14702")
        assert next_state == State.SCAN_ROLLS
        assert error is None

    def test_zero_to_session_summary(self):
        next_state, error = transition(State.SCAN_LOCATION, "0")
        assert next_state == State.SESSION_SUMMARY
        assert error is None

    def test_invalid_lowercase_stays(self):
        next_state, error = transition(State.SCAN_LOCATION, "dpa1a14702")
        assert next_state == State.SCAN_LOCATION
        assert error is not None

    def test_invalid_length_stays(self):
        next_state, error = transition(State.SCAN_LOCATION, "DPA1A14")
        assert next_state == State.SCAN_LOCATION
        assert error is not None

    def test_invalid_special_char_stays(self):
        next_state, error = transition(State.SCAN_LOCATION, "DPA1A1470!")
        assert next_state == State.SCAN_LOCATION
        assert error is not None

    def test_empty_stays(self):
        next_state, error = transition(State.SCAN_LOCATION, "")
        assert next_state == State.SCAN_LOCATION
        assert error is not None


class TestTransitionScanRolls:
    def test_valid_roll_stays_in_scan_rolls(self):
        next_state, error = transition(State.SCAN_ROLLS, "ABC123456")
        assert next_state == State.SCAN_ROLLS
        assert error is None

    def test_zero_to_confirm_batch(self):
        next_state, error = transition(State.SCAN_ROLLS, "0")
        assert next_state == State.CONFIRM_BATCH
        assert error is None

    def test_invalid_length_stays(self):
        next_state, error = transition(State.SCAN_ROLLS, "ABC123")
        assert next_state == State.SCAN_ROLLS
        assert error is not None

    def test_invalid_special_char_stays(self):
        next_state, error = transition(State.SCAN_ROLLS, "ABC1234!")
        assert next_state == State.SCAN_ROLLS
        assert error is not None

    def test_empty_stays(self):
        next_state, error = transition(State.SCAN_ROLLS, "")
        assert next_state == State.SCAN_ROLLS
        assert error is not None


class TestTransitionConfirmBatch:
    def test_confirm_to_scan_location(self):
        next_state, error = transition(State.CONFIRM_BATCH, "0")
        assert next_state == State.SCAN_LOCATION
        assert error is None

    def test_add_more_to_scan_rolls(self):
        next_state, error = transition(State.CONFIRM_BATCH, "1")
        assert next_state == State.SCAN_ROLLS
        assert error is None

    def test_invalid_option_stays(self):
        next_state, error = transition(State.CONFIRM_BATCH, "2")
        assert next_state == State.CONFIRM_BATCH
        assert error is not None

    def test_empty_stays(self):
        next_state, error = transition(State.CONFIRM_BATCH, "")
        assert next_state == State.CONFIRM_BATCH
        assert error is not None


class TestTransitionSessionSummary:
    def test_exit_stays_in_summary(self):
        next_state, error = transition(State.SESSION_SUMMARY, "0")
        assert next_state == State.SESSION_SUMMARY
        assert error is None

    def test_any_input_returns_to_scan_location(self):
        next_state, error = transition(State.SESSION_SUMMARY, "any")
        assert next_state == State.SCAN_LOCATION
        assert error is None
