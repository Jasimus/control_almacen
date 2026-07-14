"""Tests for tui.excel — ExcelStore direct openpyxl I/O."""

import os
import tempfile
import pytest
from tui.excel import ExcelStore
from ubic import Ubic
from rel_ubic import ProdUbic


@pytest.fixture
def tmp_xlsx(tmp_path):
    """Return path to a temporary .xlsx file."""
    return str(tmp_path / "test.xlsx")


class TestExcelStoreInit:
    def test_creates_new_file_with_sheets(self, tmp_xlsx):
        store = ExcelStore(tmp_xlsx)
        assert os.path.exists(tmp_xlsx)
        assert "ubicacion" in store.wb.sheetnames
        assert "articulos" in store.wb.sheetnames

    def test_ubicacion_headers(self, tmp_xlsx):
        store = ExcelStore(tmp_xlsx)
        sheet = store.wb["ubicacion"]
        headers = [cell.value for cell in sheet[1]]
        assert headers == ["id", "depo", "pasillo", "columna", "nivel", "ubic"]

    def test_articulos_headers(self, tmp_xlsx):
        store = ExcelStore(tmp_xlsx)
        sheet = store.wb["articulos"]
        headers = [cell.value for cell in sheet[1]]
        assert headers == ["id_usuario", "id_ubicacion", "id_lote", "fecha_hora"]

    def test_loads_existing_file(self, tmp_xlsx):
        store1 = ExcelStore(tmp_xlsx)
        store1.append_ubicacion(Ubic("DPA1A14702"))

        store2 = ExcelStore(tmp_xlsx)
        sheet = store2.wb["ubicacion"]
        assert sheet.max_row == 2  # header + 1 data row


class TestAppendUbicacion:
    def test_appends_one_row(self, tmp_xlsx):
        store = ExcelStore(tmp_xlsx)
        ubic = Ubic("DPA1A14702")
        store.append_ubicacion(ubic)

        sheet = store.wb["ubicacion"]
        assert sheet.max_row == 2
        row_values = [cell.value for cell in sheet[2]]
        assert row_values == ["DPA1A14702", "DPA1", "A1", "47", "02", "DPA1A14702"]

    def test_appends_multiple_rows(self, tmp_xlsx):
        store = ExcelStore(tmp_xlsx)
        store.append_ubicacion(Ubic("DPA1A14702"))
        store.append_ubicacion(Ubic("DEP2B08150"))

        sheet = store.wb["ubicacion"]
        assert sheet.max_row == 3

    def test_persists_to_disk(self, tmp_xlsx):
        store = ExcelStore(tmp_xlsx)
        store.append_ubicacion(Ubic("DPA1A14702"))
        del store

        store2 = ExcelStore(tmp_xlsx)
        sheet = store2.wb["ubicacion"]
        assert sheet.max_row == 2


class TestAppendArticulos:
    def test_appends_batch(self, tmp_xlsx):
        store = ExcelStore(tmp_xlsx)
        ubic = Ubic("DPA1A14702")
        articulos = [
            ProdUbic("user1", ubic.id, "LOTE001"),
            ProdUbic("user1", ubic.id, "LOTE002"),
        ]
        store.append_articulos(articulos)

        sheet = store.wb["articulos"]
        assert sheet.max_row == 3  # header + 2 data rows

    def test_appends_empty_list(self, tmp_xlsx):
        store = ExcelStore(tmp_xlsx)
        store.append_articulos([])

        sheet = store.wb["articulos"]
        assert sheet.max_row == 1  # header only

    def test_persists_to_disk(self, tmp_xlsx):
        store = ExcelStore(tmp_xlsx)
        ubic = Ubic("DPA1A14702")
        articulos = [ProdUbic("user1", ubic.id, "LOTE001")]
        store.append_articulos(articulos)
        del store

        store2 = ExcelStore(tmp_xlsx)
        sheet = store2.wb["articulos"]
        assert sheet.max_row == 2


class TestLoadExistingRolls:
    def test_empty_sheet_returns_empty_set(self, tmp_xlsx):
        store = ExcelStore(tmp_xlsx)
        rolls = store.load_existing_rolls()
        assert rolls == set()

    def test_returns_all_roll_ids(self, tmp_xlsx):
        store = ExcelStore(tmp_xlsx)
        ubic = Ubic("DPA1A14702")
        articulos = [
            ProdUbic("user1", ubic.id, "LOTE001"),
            ProdUbic("user1", ubic.id, "LOTE002"),
        ]
        store.append_articulos(articulos)

        rolls = store.load_existing_rolls()
        assert rolls == {"LOTE001", "LOTE002"}

    def test_duplicates_collapsed(self, tmp_xlsx):
        store = ExcelStore(tmp_xlsx)
        ubic = Ubic("DPA1A14702")
        articulos = [
            ProdUbic("user1", ubic.id, "LOTE001"),
            ProdUbic("user1", ubic.id, "LOTE001"),
        ]
        store.append_articulos(articulos)

        rolls = store.load_existing_rolls()
        assert rolls == {"LOTE001"}


class TestFileNotFoundGraceful:
    def test_nonexistent_dir_raises(self):
        with pytest.raises(Exception):
            ExcelStore("/nonexistent/path/file.xlsx")
