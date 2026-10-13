import pytest

from excel_drills import theme as T
from excel_drills.checks import Condition, Filled, Find, SelfCheck, Spill, Value
from excel_drills.model import (Arena, Boss, Formula, Item, Stage, World, column, count_filled, do, filled,
                                find, formula, merge, row, self_check, spill, table, validate_world, Fixture)


def test_arena_helpers():
    assert column("B6", [1, 2, None, 4]) == {"B6": 1, "B7": 2, "B9": 4}
    assert row("F10", ["a", "b"]) == {"F10": "a", "G10": "b"}
    assert table("B5", ["H1", "H2"], [[1, 2], [3, None]]) == {"B5": "H1", "C5": "H2", "B6": 1, "C6": 2, "B7": 3}
    with pytest.raises(ValueError):
        merge({"B5": 1}, {"B5": 2})


def test_count_filled_includes_fixed_header_cells():
    arena = Arena(cells={"B6": 1, "B7": "x", "C6": Formula("=B6*2", 2)}, pass_code="P")
    assert count_filled(arena, "A1:C7") == 4 + 3      # A1 A2 A3 B3 + 3 data cells (D3 is outside)
    assert count_filled(arena, "B6:B7") == 2


def test_find_constructor():
    ch = find("X.M1", "Find it", "hint", "COMET", items=("X.a",), wrong=("STAR",), verify=("end", "B6", "down"))
    assert isinstance(ch.check, Find) and ch.check.verify == ("end", "B6", "down")
    assert ch.solve[0].value == "COMET" and ch.wrong[0][0].value == "STAR"


def test_formula_constructor_derives_key_formula_from_solution():
    ch = formula("X.M2", "Multiply", "hint", "F6", "=C6*D6", 10, items=("X.a",), wrong=("=C6+D6",), uses=("SUM",))
    assert isinstance(ch.check, Value)
    assert ch.check.expect_formula == "=«@C6»*«@D6»" and ch.arena_cell == "F6"
    assert ch.solve[0].action == "formula" and ch.solve[0].target == "«@F6»"
    let = formula("X.M9", "LET", "hint", "K6", "=LET(rev,H6:H9,SUM(rev))", 10, items=("X.a",), wrong=("=1",),
                  key="=SUM(H6:H9)")
    assert let.check.expect_formula == "=SUM(«@H6:H9»)" and let.solve[0].value == "=LET(rev,H6:H9,SUM(rev))"


def test_filled_constructor():
    ch = filled("X.M3", "Fill", "hint", "C6:C7", lambda c: f"=B{c[1:]}*$E$5", [1.6, 2.8], items=("X.a",),
                wrong_for=lambda c: f"=B{c[1:]}*E5", dollar=True)
    assert isinstance(ch.check, Filled) and ch.check.cells == ("C6", "C7")
    assert ch.check.expect_formulas == ("=«@B6»*«@E5»", "=«@B7»*«@E5»")
    assert [f.value for f in ch.solve] == ["=B6*$E$5", "=B7*$E$5"]
    indep = filled("X.M4", "Flag", "hint", "H6:H7", lambda c: f'=IF(F{c[1:]}>=1000,"Big","")', ["Big", ""],
                   items=("X.a",), wrong_for=lambda c: '=""', key_for=lambda c: f'=IF(VALUE(D{c[1:]})>=1000,"Big","")')
    assert indep.check.expect_formulas[0] == '=IF(VALUE(«@D6»)>=1000,"Big","")'


def test_spill_do_and_self_constructors():
    s = spill("X.M4", "Spill", "hint", "K6", "=SEQUENCE(2)", [[1], [2]], items=("X.a",), wrong=("=1",))
    assert isinstance(s.check, Spill) and s.check.expect == ((1,), (2,))
    d = do("X.M5", "Do", "hint", "«@B6»=1", solve=[Fixture("type", "«@B6»", 1)],
           wrong=[[Fixture("type", "«@B6»", 2)]], items=("X.a",), arena_cell="B6", f9=True)
    assert isinstance(d.check, Condition) and d.check.f9 and d.kind == "DO"
    sc = self_check("X.M6", "Self", "hint", items=("X.a",))
    assert isinstance(sc.check, SelfCheck) and sc.solve[0].value == T.DONE


def _world(**over):
    item = Item("W1.a", "shortcut", "Ctrl+A", "what", "tip", "prompt?", ("Ctrl+A",), "hint")
    arena = Arena(cells={"B6": 1}, pass_code="P")
    stage = Stage("W1-1", "One", "goal", (item,), (find("W1-1.M1", "p", "h", "X", items=("W1.a",), wrong=("Y",)),), arena)
    boss = Boss((find("W1-B.M1", "p", "h", "X", items=("W1.a",), wrong=("Y",)),), arena, 5)
    fields = dict(code="W1", track="S", order=1, title="T", tagline="t", file_name="f.xlsx", stages=(stage,), boss=boss)
    fields.update(over)
    return World(**fields)


def test_validate_world_ok_and_problems():
    assert validate_world(_world()) == []
    bad_arena = Arena(cells={"B2": 1}, pass_code="")
    w = _world(boss=Boss((), bad_arena, 5))
    problems = validate_world(w)
    assert any("pass code" in p for p in problems) and any("reserved" in p for p in problems)
    assert any("no missions" in p for p in problems)
