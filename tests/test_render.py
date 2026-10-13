import openpyxl

from excel_drills.arena_sheet import render_arena, render_extra
from excel_drills.checks import Filled, Pick, Recall, Spill, Value
from excel_drills.keysheet import KeySheet
from excel_drills.model import Arena, Formula
from excel_drills.refs import resolve
from excel_drills.writer import Book


def _text(cell):
    """openpyxl returns dynamic-array formulas as ArrayFormula objects; give their formula text."""
    return getattr(cell.value, "text", cell.value)


def test_key_sheet_layout(tmp_path):
    book = Book(tmp_path / "k.xlsx", title="t", subject="s", keywords="k")
    book.sheet("Start")                      # XlsxWriter never hides the first (active) sheet; Key is always last
    key = KeySheet(book, book.sheet("Key"))
    res = lambda t: resolve(t, {}, "Arena")
    n1 = key.add("A W1", "hint one", Recall(("CTRL+A", "=SUM")), res)
    n2 = key.add("A T1", "hint two", Pick(("A", "B", "C"), "B"), res)
    n3 = key.add("A C1", "hint three", Value("F6", 10, "=«@C6»*«@D6»"), res)
    n4 = key.add("A C2", "h", Filled(("C6", "C7"), (1, 2), ("=«@B6»", "=«@B7»")), res)
    n5 = key.add("A C3", "h", Spill("K6", ((1,), (2,)), "=SEQUENCE(2)"), res)
    book.close()
    assert n1 == {"hint": "Key!$B$2", "keyrow": "Key!$E$2:$F$2", "opts": "Key!$E$2:$F$2"}
    assert n2["key"] == "Key!$C$3" and n2["opts"] == "Key!$E$3:$G$3"
    assert n3["key"] == "Key!$C$4"
    assert n4["key1"] == "Key!$E$5" and n4["key2"] == "Key!$F$5"
    assert n5["spill"] == "Key!$E$2001"
    ws = openpyxl.load_workbook(tmp_path / "k.xlsx")["Key"]
    assert ws.sheet_state == "veryHidden"
    assert ws["F2"].value == "=SUM" and ws["F2"].data_type == "s"       # text, never a formula
    assert _text(ws["C4"]).startswith("=") and "Arena" in _text(ws["C4"])


def test_arena_render(tmp_path):
    book = Book(tmp_path / "a.xlsx", title="t", subject="s", keywords="k")
    stage = book.sheet("S1-1 Warp Zones")
    ws = book.sheet("S1-1 Arena")
    arena = Arena(cells={"B5": "HEAD", "B6": 1, "C6": Formula("=B6*2", 2), "D9": "=not a formula"},
                  pass_code="QUASAR", inputs=("F6:F7",), headers=("B5",), number_formats={"B6": "0.0"},
                  validations={"F7": ("Bronze", "Gold")}, names={"TREASURE": "B6"})
    render_arena(book, ws, arena, title="ARENA ▸ S1-1 WARP ZONES", back_sheet=stage.name)
    render_extra(book, book.sheet("Rename Me"), "Rename this sheet to Vault.")
    book.close()
    wb = openpyxl.load_workbook(tmp_path / "a.xlsx")
    a = wb["S1-1 Arena"]
    assert a["A1"].value == "ARENA ▸ S1-1 WARP ZONES" and a["B3"].value == "QUASAR"
    assert a["D9"].data_type == "s" and _text(a["C6"]).startswith("=")
    assert not a.protection.sheet
    assert a["F6"].fill.fgColor.rgb.endswith("FFF4CC")
    assert "TREASURE" in wb.defined_names
    assert wb["Rename Me"]["A1"].value == "RENAME ME"
