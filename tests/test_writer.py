import datetime as dt

import openpyxl
import pytest

from excel_drills.writer import BUILD_DATE, Book, row_height


@pytest.fixture
def book(tmp_path):
    b = Book(tmp_path / "t.xlsx", title="T", subject="S", keywords="k")
    yield b


def test_formula_guards(book):
    ws = book.sheet("A")
    with pytest.raises(TypeError):
        book.formula(ws, "A1", "=1=1", True)
    with pytest.raises(ValueError):
        book.formula(ws, "A1", "=_xlfn.XLOOKUP(1,A2:A3,B2:B3)", 0)
    with pytest.raises(ValueError):
        book.formula(ws, "A1", "=«ans»", "")
    with pytest.raises(ValueError):
        book.formula(ws, "A1", "SUM(A2:A3)", 0)
    with pytest.raises(ValueError):
        book.formula(ws, "A1", "=SUM(A2:A3)", None)
    with pytest.raises(ValueError):
        book.formula(ws, "A1", "=SUM(B2#)", 0)
    with pytest.raises(ValueError):
        book.formula(ws, "A1", '=IF(B2="","use XLOOKUP(","")', "")
    book.formula(ws, "A1", '=SUM(ANCHORARRAY(B2))&"#1"', 0)
    book.formula(ws, "A2", "=SUM(A3:A4)", 0, volatile=True)
    assert book.formulas[-1].sheet == "A" and book.formulas[-1].volatile
    book.close()


def test_sheet_name_rules(book):
    book.sheet("Start")
    for bad in ("", "x" * 32, "a/b", "History", "start", "'q"):
        with pytest.raises(ValueError):
            book.sheet(bad)
    book.close()


def test_text_never_becomes_formula_and_properties(tmp_path):
    b = Book(tmp_path / "p.xlsx", title="My Title", subject="Sub", keywords="kw")
    ws = b.sheet("A")
    b.text(ws, "A1", "=SUMIFS")
    b.put(ws, "A2", 3.5)
    b.put(ws, "A3", dt.date(2026, 3, 15), b.fmt("arena", num_format="d-mmm-yy"))
    b.close()
    wb = openpyxl.load_workbook(tmp_path / "p.xlsx")
    assert wb["A"]["A1"].value == "=SUMIFS" and wb["A"]["A1"].data_type == "s"
    assert wb["A"]["A2"].value == 3.5
    assert wb["A"]["A3"].value == dt.datetime(2026, 3, 15)
    props = wb.properties
    assert props.creator == "excel-drills" and props.title == "My Title"
    assert props.created == BUILD_DATE and props.lastModifiedBy == "excel-drills"


def test_row_height_grows_with_text():
    assert row_height(("short", 58)) == pytest.approx(19.75)
    assert row_height(("x" * 200, 58)) > row_height(("x" * 60, 58))
    assert row_height(("a\nb\nc", 58)) == pytest.approx(3 * 15.75 + 4)
