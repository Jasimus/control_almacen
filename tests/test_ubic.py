import pytest
from ubic import Ubic


class TestUbic:
    def test_basic_parsing(self):
        """Test basic field extraction from a valid location code."""
        u = Ubic('DPA1A14702')
        assert u.id == 'DPA1A14702'
        assert u.depo == 'DPA1'
        assert u.pasillo == 'A1'
        assert u.columna == '47'
        assert u.nivel == '02'

    def test_ubic_derived_from_input(self):
        """Test that ubic field stores the full input, not hardcoded value."""
        u = Ubic('DPA1A14702')
        assert u.ubic == 'DPA1A14702'

    def test_different_input(self):
        """Test parsing with different location codes."""
        u = Ubic('DEP2B08150')
        assert u.id == 'DEP2B08150'
        assert u.depo == 'DEP2'
        assert u.pasillo == 'B0'
        assert u.columna == '81'
        assert u.nivel == '50'

    def test_all_fields_present(self):
        """Test that all expected attributes exist."""
        u = Ubic('ABC1234567')
        assert hasattr(u, 'id')
        assert hasattr(u, 'depo')
        assert hasattr(u, 'pasillo')
        assert hasattr(u, 'columna')
        assert hasattr(u, 'nivel')
        assert hasattr(u, 'ubic')

    def test_ubic_not_hardcoded(self):
        """Verify ubic is not the old hardcoded 'DPA' value."""
        u = Ubic('XYZ1234567')
        assert u.ubic != 'DPA'
        assert u.ubic == 'XYZ1234567'
