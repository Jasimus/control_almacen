import pytest
from validation import (
    validate_location,
    validate_roll,
    ERROR_MSG_LOCATION,
    ERROR_MSG_ROLL,
    LOCATION_RE,
    ROLL_RE,
)


class TestValidateLocation:
    @pytest.mark.parametrize("code", [
        'DPA1A14702',
        'DEP1A14702',
        'DEP2B08150',
        'ABC1234567',
        'XYZ9876543',
        'A1B2C3D4E5',
    ])
    def test_valid_locations(self, code):
        """Test that valid location codes are accepted."""
        assert validate_location(code) is True

    @pytest.mark.parametrize("code", [
        'dpa1a14702',   # lowercase
        'DPA1A1470',    # 9 chars
        'DPA1A147023',  # 11 chars
        '',             # empty
        'DPA1A1470!',   # special char
        'DPA1A1470 ',   # trailing space
        'DEP1A14702!',  # special char
        None,           # None input
    ])
    def test_invalid_locations(self, code):
        """Test that invalid location codes are rejected."""
        if code is None:
            assert validate_location(code) is False
        else:
            assert validate_location(code) is False

    def test_exactly_10_chars(self):
        """Test boundary: exactly 10 alphanumeric chars."""
        assert validate_location('A' * 10) is True
        assert validate_location('A' * 9) is False
        assert validate_location('A' * 11) is False


class TestValidateRoll:
    @pytest.mark.parametrize("code", [
        'ABC1234',
        'abc1234',
        'AbCd123',
        '1234567',
        'Aa1Bb2C',
    ])
    def test_valid_rolls(self, code):
        """Test that valid roll codes are accepted."""
        assert validate_roll(code) is True

    @pytest.mark.parametrize("code", [
        'AB1234',     # 6 chars
        'AB123456',   # 8 chars
        '',           # empty
        'ABC123!',    # special char
        'ABC12345',   # too long
        None,         # None
    ])
    def test_invalid_rolls(self, code):
        """Test that invalid roll codes are rejected."""
        if code is None:
            assert validate_roll(code) is False
        else:
            assert validate_roll(code) is False

    def test_exactly_7_chars(self):
        """Test boundary: exactly 7 alphanumeric chars."""
        assert validate_roll('A' * 7) is True
        assert validate_roll('A' * 6) is False
        assert validate_roll('A' * 8) is False


class TestErrorMessages:
    def test_location_error_message(self):
        """Test that location error message is in Spanish."""
        assert 'UBICACIÓN' in ERROR_MSG_LOCATION
        assert 'REINTENTE' in ERROR_MSG_LOCATION

    def test_roll_error_message(self):
        """Test that roll error message is in Spanish."""
        assert 'ARTICULO' in ERROR_MSG_ROLL
        assert 'REINTENTE' in ERROR_MSG_ROLL
