"""The fixture actions and truth recipes do exactly what they say in real Excel."""
from __future__ import annotations

import pytest
import xlsxwriter

from excel_drills.model import Fixture
from tests.excel.actions import apply, truth
from tests.excel.harness import is_error

pytestmark = pytest.mark.excel
ROWS = [("Player", "Score"), ("Ida", 95), ("Bo", 90), ("Zircon", 25), ("Ann", 40)]


@pytest.fixture
def book(tmp_path):
    path = tmp_path / "actions.xlsx"
    wb = xlsxwriter.Workbook(path)
    ws = wb.add_worksheet("A")
    wb.add_worksheet("B")
    for i, row in enumerate(ROWS):
        ws.write_row(i, 0, row)
    ws.write_formula("D1", "=SUM(B2:B5)+F9", None, 250)
    ws.write("D2", 7)
    wb.close()
    return path


def _col(ws, rng):
    return [r[0] for r in ws.Range(rng).Value2]


def test_sort_keeps_the_header_and_honours_the_order(excel, book):
    with excel.open(book) as wb:
        ws = wb.Worksheets("A")
        apply(wb, Fixture("sort", "«@A1:B5»", "asc", ("A",)), {}, "A")
        assert _col(ws, "A1:A5") == ["Player", "Ann", "Bo", "Ida", "Zircon"]
        apply(wb, Fixture("sort", "«@A1:B5»", "desc", ("B",)), {}, "A")
        assert _col(ws, "B1:B5") == ["Score", 95, 90, 40, 25] and ws.Range("A2").Value2 == "Ida"


def test_sort_column_only_leaves_the_other_columns_behind(excel, book):
    with excel.open(book) as wb:
        ws = wb.Worksheets("A")
        apply(wb, Fixture("sort_column_only", "«@A2:A5»", "desc"), {}, "A")
        assert _col(ws, "A2:A5") == ["Zircon", "Ida", "Bo", "Ann"] and _col(ws, "B2:B5") == [95, 90, 25, 40]


def test_add_sheet_appends_at_the_end(excel, book):
    with excel.open(book) as wb:
        apply(wb, Fixture("add_sheet", ""), {}, "A")
        assert [s.Name for s in wb.Worksheets][:2] == ["A", "B"] and wb.Worksheets.Count == 3


def test_find_and_replace_ignore_excels_remembered_options(excel, book):
    with excel.open(book) as wb:
        ws = wb.Worksheets("A")
        ws.Cells.Find("zzz", ws.Range("A1"), -4123, 1, 1, 1, True)     # leave formulas / whole cell / match case on
        assert truth(wb, ("find_offset", "irco", 1), arena_sheet="A", stage_sheet="A") == 25
        ws.Range("A6").Value2, ws.Range("A7").Value2 = "tbd", "TBDX"
        apply(wb, Fixture("replace", "«@A6:A7»", ("TBD", "Pending")), {}, "A")
        assert _col(ws, "A6:A7") == ["Pending", "TBDX"]


def test_address_recipes(excel, book):
    with excel.open(book) as wb:
        assert truth(wb, ("nonformula_in", "D1:D2"), arena_sheet="A", stage_sheet="A") == "D2"
        assert truth(wb, ("formula_ref_outside", "D1", "B2:B5"), arena_sheet="A", stage_sheet="A") == "F9"


def test_paste_error_puts_an_error_value_in_a_text_cell(excel, book):
    with excel.open(book) as wb:
        ws = wb.Worksheets("A")
        ws.Range("G1").NumberFormat = "@"
        apply(wb, Fixture("paste_error", "«@G1»", "=NA()"), {}, "A")
        assert is_error(ws.Range("G1").Value2) and not ws.Range("G1").HasFormula
