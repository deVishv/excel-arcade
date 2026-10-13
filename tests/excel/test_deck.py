"""Review Deck in real Excel: answer checking, suggested box, next-due dates and DUE status relative to today."""
import pytest

from excel_drills.content import FINAL, WORLDS
from excel_drills.course import Course
from excel_drills.deck_builder import build_deck
from tests.excel.harness import is_error, read, read_cell, same, unexpected_spills

pytestmark = pytest.mark.excel


@pytest.fixture(scope="module")
def deck(tmp_path_factory):
    course = Course(WORLDS, FINAL)
    return course, build_deck(course, tmp_path_factory.mktemp("deck"))


def test_deck_opens_clean(deck, excel):
    _, built = deck
    with excel.open(built.path) as wb:
        for f in built.formulas:
            got = read_cell(wb, f.sheet, f.cell)
            assert not is_error(got), f"{f.sheet}!{f.cell}"
            if not f.volatile:
                assert same(got, f.cached), f"{f.sheet}!{f.cell}: cached {f.cached!r}, Excel {got!r}"
        spills = unexpected_spills(wb, built.formulas)
        assert not spills, spills[:20]


def test_suggested_box_stops_once_stamped_today(deck, excel):
    """After Box is set and the date stamped, re-checking must not promote the card again (found in review)."""
    course, built = deck
    card = built.cards[0]
    r = card.row
    with excel.open(built.path) as wb:
        ws = wb.Worksheets("Deck")
        today = wb.Application.Evaluate("TODAY()")
        ws.Range(f"E{r}").Value2 = course.items[card.item_id].answers[0]
        excel.calc()
        assert read_cell(wb, "Deck", f"G{r}") == 2
        ws.Range(f"H{r}").Value2 = 2
        ws.Range(f"I{r}").Value2 = today
        excel.calc()
        assert read_cell(wb, "Deck", f"G{r}") == "done today"


def test_deck_schedules_cards(deck, excel):
    course, built = deck
    card = built.cards[0]
    r = card.row
    with excel.open(built.path) as wb:
        ws = wb.Worksheets("Deck")
        today = wb.Application.Evaluate("TODAY()")
        ws.Range(f"E{r}").Value2 = course.items[card.item_id].answers[0]
        excel.calc()
        assert read_cell(wb, "Deck", f"F{r}").startswith("✔") and read_cell(wb, "Deck", f"G{r}") == 2
        ws.Range(f"H{r}").Value2 = 2
        ws.Range(f"I{r}").Value2 = today - 3
        excel.calc()
        assert read_cell(wb, "Deck", f"J{r}") == today and read_cell(wb, "Deck", f"K{r}") == "DUE"
        assert read(wb, built.start["due"]) == 1
        ws.Range(f"I{r}").Value2 = today
        excel.calc()
        assert read_cell(wb, "Deck", f"K{r}") == "in 3 days"
        ws.Range(f"H{r}").Value2 = 5
        excel.calc()
        assert read_cell(wb, "Deck", f"K{r}") == "in 30 days" and read(wb, built.start["mastered"]) == 1
        ws.Range(f"I{r}").Value2 = today - 31
        excel.calc()
        assert read_cell(wb, "Deck", f"K{r}") == "DUE"
        ws.Range(f"E{r}").Value2 = "Ctrl+Q"
        excel.calc()
        assert read_cell(wb, "Deck", f"F{r}").startswith("✘") and read_cell(wb, "Deck", f"G{r}") == 1
