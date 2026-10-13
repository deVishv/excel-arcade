"""Every workbook in real Excel: no errors, honest cached values, every challenge, every puzzle, a playthrough."""
from __future__ import annotations

import pytest

from excel_drills.checks import Find, find_key
from excel_drills.content import FINAL, WORLDS
from excel_drills.course import Course
from excel_drills.model import Fixture
from excel_drills.refs import resolve, split_ref
from excel_drills.world_builder import build_world
from tests.demo_content import DEMO
from tests.excel.actions import LIGHT, apply, restore, rng, snapshot, truth
from tests.excel.harness import is_error, read, read_cell, same, unexpected_spills

pytestmark = pytest.mark.excel
CODES = ["D1", *[w.code for w in WORLDS]]
ODD_ANSWERS = ["   ", "$B$5", "=SUM(", "Ctrl+*", "'=1/0", 12345]


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    out = tmp_path_factory.mktemp("excel")
    real = Course(WORLDS, FINAL)
    cache = {}

    def get(code):
        if code not in cache:
            if code == "D1":
                cache[code] = build_world(Course((DEMO,)), DEMO, out)
            else:
                cache[code] = build_world(real, next(w for w in WORLDS if w.code == code), out)
        return cache[code]

    return get


def _ok(value) -> bool:
    return isinstance(value, str) and value.startswith("✔")


def _open_gate(wb, sheet) -> None:
    """Tests only: open a Boss gate directly instead of solving every stage first."""
    name, addr = split_ref(sheet.gate)
    ws = wb.Worksheets(name)
    ws.Unprotect()
    ws.Range(addr).Value2 = "OPEN"


def _fresh_result(excel, b, sheet, pc, fixtures):
    with excel.open(b.path) as wb:
        if sheet.gate:
            _open_gate(wb, sheet)
        for fx in fixtures:
            apply(wb, fx, pc.names, pc.arena_sheet)
        excel.calc()
        return read(wb, pc.result)


def _exercise(excel, wb, b, sheet, pc) -> list[str]:
    ch, out = pc.challenge, []
    where = f"{pc.sheet} {pc.label} ({ch.id})"
    blank, want = read(wb, pc.result), ch.check.formula().blank
    if not same(blank, want):
        out.append(f"{where} blank: {blank!r} != {want!r}")
    attempts = [("solve", ch.solve, True)] + [(f"wrong{i}", w, False) for i, w in enumerate(ch.wrong, 1)]
    for label, fixtures, want_ok in attempts:
        if all(fx.action in LIGHT for fx in fixtures):
            saved = snapshot(wb, fixtures, pc.names, pc.arena_sheet)
            for fx in fixtures:
                apply(wb, fx, pc.names, pc.arena_sheet)
            excel.calc()
            got = read(wb, pc.result)
            restore(saved)
            excel.calc()
        else:
            got = _fresh_result(excel, b, sheet, pc, fixtures)
        if is_error(got):
            out.append(f"{where} {label}: Excel error {got}")
        elif _ok(got) != want_ok:
            out.append(f"{where} {label}: {got!r}")
    return out


@pytest.mark.parametrize("code", CODES)
def test_no_error_values(code, built, excel):
    b = built(code)
    with excel.open(b.path) as wb:
        bad = [f"{f.sheet}!{f.cell}" for f in b.formulas
               if not f.error_ok and is_error(read_cell(wb, f.sheet, f.cell))]
    assert not bad, bad[:20]


@pytest.mark.parametrize("code", CODES)
def test_no_unexpected_spills(code, built, excel):
    b = built(code)
    with excel.open(b.path) as wb:
        spills = unexpected_spills(wb, b.formulas)
    assert not spills, spills[:20]


@pytest.mark.parametrize("code", CODES)
def test_cached_values_match(code, built, excel):
    b = built(code)
    bad = []
    with excel.open(b.path) as wb:
        for f in b.formulas:
            if f.error_ok or f.volatile:
                continue
            got = read_cell(wb, f.sheet, f.cell)
            if not same(got, f.cached):
                bad.append(f"{f.sheet}!{f.cell}: cached {f.cached!r}, Excel {got!r}")
    assert not bad, "\n".join(bad[:30])


@pytest.mark.parametrize("code", CODES)
def test_every_challenge_blank_solve_wrong(code, built, excel):
    b = built(code)
    problems = []
    for sheet in b.sheets:
        with excel.open(b.path) as wb:
            if sheet.gate:
                _open_gate(wb, sheet)
                excel.calc()
            for pc in sheet.challenges:
                problems += _exercise(excel, wb, b, sheet, pc)
    assert not problems, "\n".join(problems)


@pytest.mark.parametrize("code", CODES)
def test_find_puzzles_are_solved_by_excel_itself(code, built, excel):
    b = built(code)
    bad = []
    with excel.open(b.path) as wb:
        for sheet in b.sheets:
            for pc in sheet.challenges:
                check = pc.challenge.check
                if not (isinstance(check, Find) and check.verify):
                    continue
                got = truth(wb, check.verify, arena_sheet=pc.arena_sheet, stage_sheet=pc.sheet)
                if isinstance(check.answer, str):
                    ok = find_key(str(got)) == find_key(check.answer)
                else:
                    ok = isinstance(got, (int, float)) and abs(got - check.answer) <= 1e-9 * max(1, abs(check.answer))
                if not ok:
                    bad.append(f"{pc.sheet} {pc.label}: Excel gives {got!r}, authored answer {check.answer!r}")
    assert not bad, "\n".join(bad)


@pytest.mark.parametrize("code", CODES)
def test_full_playthrough(code, built, excel):
    b = built(code)
    stages = [s for s in b.sheets if not s.gate]
    boss = next(s for s in b.sheets if s.gate)
    with excel.open(b.path) as wb:
        for sheet in stages:
            for pc in sheet.challenges:
                for fx in pc.challenge.solve:
                    apply(wb, fx, pc.names, pc.arena_sheet)
        excel.calc()
        assert read(wb, boss.gate) == "OPEN"
        assert read(wb, b.hub["next"]) == "the Boss"
        for pc in boss.challenges:
            for fx in pc.challenge.solve:
                apply(wb, fx, pc.names, pc.arena_sheet)
        excel.xl.CalculateFull()
        not_ok = [(pc.sheet, pc.label, read(wb, pc.result)) for s in b.sheets for pc in s.challenges
                  if not _ok(read(wb, pc.result))]
        assert not not_ok, not_ok
        spills = unexpected_spills(wb, b.formulas)
        assert not spills, spills[:20]
        for s in stages:
            assert read(wb, b.hub[f"status:{s.code}"]) == "PERFECT"
        assert read(wb, b.hub["status:BOSS"]) == "DEFEATED"
        assert read(wb, b.hub["next"]) == "All clear! Aim for rank S"     # found in review: stuck on "the Boss"
        assert read(wb, b.hub["rank"]) == "A"                      # 100% but no time stamped yet
        sheet_name, _ = split_ref(boss.time_cell)
        bws = wb.Worksheets(sheet_name)
        bws.Range("C6").Value2 = 0.5
        bws.Range("C7").Value2 = 0.5 + (boss.par - 1) / 1440
        excel.calc()
        assert read(wb, b.hub["rank"]) == "S"


ALTERNATIVES = [   # equally right formulas a learner knows from the course (found in review)
    ("F3", "F3-B.M1", '=COUNTIFS(D6:D25,"North")'),
    ("F3", "F3-B.M7", '=COUNTIF(G6:G25,">="&K6)'),
    ("F4", "F4-B.M8", "=VLOOKUP(I30,L6:M9,2,TRUE)"),
    ("F5", "F5-B.M4", '=RIGHT(B9,LEN(B9)-SEARCH(" ",B9))'),
    ("F6", "F6-B.M6", "=DATE(YEAR(B7),MONTH(B7)+1,0)"),
    ("F7", "F7-B.M6", "=ROWS(UNIQUE(F6:F25))"),
]


@pytest.mark.parametrize("code, mission, alt", ALTERNATIVES, ids=[a[1] for a in ALTERNATIVES])
def test_equally_right_alternatives_are_accepted(code, mission, alt, built, excel):
    b = built(code)
    sheet, pc = next((s, pc) for s in b.sheets for pc in s.challenges if pc.challenge.id == mission)
    got = _fresh_result(excel, b, sheet, pc, [Fixture("formula", f"«@{pc.challenge.arena_cell}»", alt)])
    assert _ok(got), got


def test_replay_tip_clears_a_stage_on_its_protected_sheet(built, excel):
    """The hub's replay tip: select runs of yellow cells (Ctrl+click for more) and press Delete."""
    b = built("D1")
    typed = [pc for pc in b.sheets[0].challenges if pc.challenge.kind in ("RECALL", "PICK", "FIND", "SELF")]
    with excel.open(b.path) as wb:
        for pc in typed:
            for fx in pc.challenge.solve:
                apply(wb, fx, pc.names, pc.arena_sheet)
            apply(wb, Fixture("pick_hint", ""), pc.names, pc.arena_sheet)
        excel.calc()
        assert all(read(wb, pc.xp) == 5 for pc in typed)
        selection = rng(wb, typed[0].names["ans"])
        for pc in typed:
            for ref in (pc.names["ans"], pc.picker):
                selection = wb.Application.Union(selection, rng(wb, ref))
        selection.ClearContents()                       # what Delete does on that multi-run selection
        excel.calc()
        assert all(read(wb, pc.xp) == 0 and read(wb, pc.result) in ("", None) for pc in typed)


def test_date_stamp_stays_clear_the_next_day(built, excel):
    """A Ctrl+; date is a constant, so its ✔ must survive midnight (found in review)."""
    b = built("D1")
    pc = next(pc for s in b.sheets for pc in s.challenges if pc.challenge.id == "D1-1.M12")
    with excel.open(b.path) as wb:
        today = wb.Application.Evaluate("TODAY()")
        cell = rng(wb, resolve(pc.challenge.solve[0].target, pc.names, pc.arena_sheet))
        for value, want in ((today - 1, True), (today + 1, False), ("=TODAY()-1", False)):
            if isinstance(value, str):
                cell.Formula2 = value
            else:
                cell.Value2 = value
            excel.calc()
            assert _ok(read(wb, pc.result)) == want, value


def test_hint_costs_half_xp(built, excel):
    b = built("D1")
    pc = b.sheets[0].challenges[0]
    with excel.open(b.path) as wb:
        for fx in pc.challenge.solve:
            apply(wb, fx, pc.names, pc.arena_sheet)
        excel.calc()
        assert read(wb, pc.xp) == 10
        apply(wb, Fixture("pick_hint", ""), pc.names, pc.arena_sheet)
        excel.calc()
        assert read(wb, pc.xp) == 5
        assert read(wb, pc.result.replace("$D$", "$F$")) == pc.challenge.hint


@pytest.mark.parametrize("code", CODES)
def test_odd_inputs_never_error(code, built, excel):
    b = built(code)
    bad = []
    with excel.open(b.path) as wb:
        for sheet in b.sheets:
            if sheet.gate:
                _open_gate(wb, sheet)
            for pc in sheet.challenges:
                kind = pc.challenge.kind
                if kind in ("RECALL", "PICK", "FIND", "SELF"):
                    target = pc.names["ans"]
                    attempts = [Fixture("type", target, v) for v in ODD_ANSWERS]
                    errors = [Fixture("paste_error", target, "=1/0"), Fixture("paste_error", target, "=NA()")]
                elif kind == "FORMULA":
                    target = f"«@{pc.challenge.arena_cell}»"
                    attempts = [Fixture("type", target, "abc"), Fixture("type", target, 12345)]
                    errors = [Fixture("formula", target, "=1/0")]
                else:
                    continue
                for fx in attempts + errors:
                    saved = snapshot(wb, [fx], pc.names, pc.arena_sheet)
                    try:
                        apply(wb, fx, pc.names, pc.arena_sheet)
                    except Exception:
                        continue                    # Excel refused the entry outright
                    excel.calc()
                    if fx in errors and not is_error(rng(wb, resolve(fx.target, pc.names, pc.arena_sheet)).Value2):
                        bad.append(f"{pc.sheet} {pc.label}: {fx.value!r} left no error in the cell (guard untested)")
                    got = read(wb, pc.result)
                    restore(saved)
                    excel.calc()
                    if is_error(got):
                        bad.append(f"{pc.sheet} {pc.label} {fx.action} {fx.value!r}: {got}")
    assert not bad, "\n".join(bad)
