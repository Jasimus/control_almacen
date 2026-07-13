import re
import pytest
from rel_ubic import ProdUbic


class TestProdUbic:
    def test_creation(self):
        """Test basic object creation with correct fields."""
        p = ProdUbic('testuser', 'DPA1A14702', 'ABC1234')
        assert p.id_usuario == 'testuser'
        assert p.id_ubic == 'DPA1A14702'
        assert p.id_lote == 'ABC1234'

    def test_fecha_hora_format(self):
        """Test that fecha_hora matches YYYY-MM-DD HH:MM:SS format."""
        p = ProdUbic('user', 'loc', 'lot')
        assert len(p.fecha_hora) == 19
        assert re.match(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$', p.fecha_hora)

    def test_fecha_hora_is_set(self):
        """Test that fecha_hora is populated on creation."""
        p = ProdUbic('user', 'loc', 'lot')
        assert p.fecha_hora is not None
        assert p.fecha_hora != ''

    def test_str_representation(self):
        """Test string representation includes all fields."""
        p = ProdUbic('user', 'loc', 'lot')
        s = str(p)
        assert 'user' in s
        assert 'loc' in s
        assert 'lot' in s
        assert p.fecha_hora in s

    def test_dict_conversion(self):
        """Test __dict__ includes fecha_hora for DataFrame creation."""
        p = ProdUbic('user', 'loc', 'lot')
        d = p.__dict__
        assert 'id_usuario' in d
        assert 'id_ubic' in d
        assert 'id_lote' in d
        assert 'fecha_hora' in d
