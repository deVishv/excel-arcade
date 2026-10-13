"""The Final Boss in real Excel: no errors, honest caches, every mission, puzzles, playthrough and certificate."""
import pytest

from excel_drills.checks import Find, find_key
from excel_drills.content import FINAL, WORLDS
from excel_drills.course import Course
from excel_drills.final_builder import TIMER, build_final
from excel_drills.refs import split_ref
from tests.excel.actions import apply, truth
from tests.excel.harness import is_error, read, read_cell, same
from tests.excel.test_worlds import _exercise, _ok

pytestmark = pytest.mark.excel


@pytest.fixture(scope="module")
def final_book(tmp_path_factory):
    return build_final(Course(WORLDS, FINAL), tmp_path_factory.mktemp("final"))


def test_final_no_errors_and_honest_cache(final_book, excel):
    with excel.open(final_book.path) as wb:
        for f in final_book.formulas:
            got = read_cell(wb, f.sheet, f.cell)
            if not f.error_ok:
                assert not is_error(got), f"{f.sheet}!{f.cell}"
            if not (f.error_ok or f.volatile):
                assert same(got, f.cached), f"{f.sheet}!{f.cell}: cached {f.cached!r}, Excel {got!r}"


def test_final_every_mission(final_book, excel):
    problems = []
    for sheet in final_book.sheets:
        with excel.open(final_book.path) as wb:
            for pc in sheet.challenges:
                problems += _exercise(excel, wb, final_book, sheet, pc)
    assert not problems, "\n".join(problems)


def test_final_find_puzzles(final_book, excel):
    with excel.open(final_book.path) as wb:
        for sheet in final_book.sheets:
            for pc in sheet.challenges:
                check = pc.challenge.check
                if isinstance(check, Find) and check.verify:
                    got = truth(wb, check.verify, arena_sheet=pc.arena_sheet, stage_sheet=pc.sheet)
                    assert find_key(str(got)) == find_key(str(check.answer)), pc.label


def test_final_playthrough_rank_and_certificate(final_book, excel):
    with excel.open(final_book.path) as wb:
        for sheet in final_book.sheets:
            for pc in sheet.challenges:
                for fx in pc.challenge.solve:
                    apply(wb, fx, pc.names, pc.arena_sheet)
        excel.xl.CalculateFull()
        bad = [(pc.label, read(wb, pc.result)) for s in final_book.sheets for pc in s.challenges
               if not _ok(read(wb, pc.result))]
        assert not bad, bad
        assert read(wb, final_book.hub["rank"]) == "A"
        start = wb.Worksheets("Start")
        start.Range(TIMER[0]).Value2 = 0.4
        start.Range(TIMER[1]).Value2 = 0.4 + 30 / 1440
        cert = wb.Worksheets("Certificate")
        cert.Range("C5").Value2 = "Ada"
        excel.calc()
        assert read(wb, final_book.hub["rank"]) == "S"
        assert cert.Range("B11").Value2 == "This certifies that Ada conquered the Excel Arcade with rank S."
