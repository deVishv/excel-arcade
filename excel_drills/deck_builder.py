"""Review Deck: one Leitner flashcard per move in the course, scheduled by box and date with plain formulas."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from pathlib import Path

from . import theme as T
from .checks import Recall, q
from .course import Course
from .keysheet import KeySheet
from .refs import resolve, sheet_ref
from .writer import Book, row_height

DECK_FILE = "00 Review Deck.xlsx"
INTERVALS = (1, 3, 7, 14, 30)
COLUMNS = {"A": 7, "B": 8, "C": 22, "D": 52, "E": 24, "F": 20, "G": 11, "H": 8, "I": 15, "J": 15, "K": 14}
HEADERS = ("Card", "World", "Stage", "Prompt", "Your answer", "Result", "Suggested box", "Box", "Last reviewed",
           "Next due", "Status")
HOW_IT_WORKS = (
    "Every card lives in a box from 1 to 5. Box 1 cards come back tomorrow; Box 5 cards wait a month.",
    "Intervals: Box 1 → 1 day · Box 2 → 3 days · Box 3 → 7 days · Box 4 → 14 days · Box 5 → 30 days.",
    "Right answer: the card moves up a box. Missed it: back to Box 1. NEW cards haven't been reviewed yet.",
    "Start with the cards from worlds you have played; leave the rest as NEW until you get there.",
)
ROUTINE = (
    "1 · Open the Deck sheet, select the Status header (K4), press Alt+↓ and keep only DUE (plus any NEW cards).",
    "2 · Type each answer in the yellow Your answer cell and check the Result.",
    "3 · Set Box to the Suggested box (select the Box cell, press Alt+↓, pick the number).",
    "4 · Select Last reviewed and press Ctrl+; to stamp today's date.",
    "5 · Clear your answers (select them, press Delete), then clear the filter (Alt+↓ → Select All).",
    "6 · Come back tomorrow: a little every day is how it sticks.",
)


@dataclass(frozen=True)
class Card:
    row: int
    item_id: str


@dataclass
class BuiltDeck:
    path: Path
    formulas: list
    cards: list[Card]
    start: dict[str, str]
    sheets: list = field(default_factory=list)


def _status(r: int) -> str:
    return (f'=IF(H{r}="","NEW",IF(J{r}="","DUE",IF(J{r}<=TODAY(),"DUE",'
            f'"in "&(J{r}-TODAY())&IF(J{r}-TODAY()=1," day"," days"))))')


def _write_deck(book: Book, ws, key: KeySheet, course: Course) -> list[Card]:
    f = book.fmt
    for col, width in COLUMNS.items():
        ws.set_column(f"{col}:{col}", width)
    book.text(ws, "A1", "REVIEW DECK ▸ ALL CARDS", f("title"))
    for col in "BCDEFGHIJK":
        ws.write_blank(f"{col}1", None, f("title_fill"))
    ws.set_row(0, 34)
    book.text(ws, "A2", "Answer the DUE cards, move each to its Suggested box, and stamp the date with Ctrl+;.",
              f("subtitle"))
    for col, label in zip("ABCDEFGHIJK", HEADERS):
        book.text(ws, f"{col}4", label, f("th"))
    cards, r = [], 5
    choose = ",".join(str(d) for d in INTERVALS)
    for n, (item_id, item) in enumerate(course.items.items(), 1):
        names = {"ans": sheet_ref(ws.name, f"E{r}")}
        check = Recall(course.accepted(item_id))

        def res(template: str, names=names) -> str:
            return resolve(template, names, None)

        names.update(key.add(f"Deck {n}", item.hint, check, res))
        book.put(ws, f"A{r}", n, f("body_center"))
        book.text(ws, f"B{r}", course.world_of[item_id], f("body_center"))
        book.text(ws, f"C{r}", course.origin[item_id], f("body"))
        book.text(ws, f"D{r}", item.prompt, f("body"))
        ws.write_blank(f"E{r}", None, f("input", num_format="@"))
        ws.data_validation(f"E{r}", {"validate": "any", "input_title": "Type your answer",
                                     "input_message": "Keys joined with +, like Ctrl+Shift+L, or a function name."})
        book.formula(ws, f"F{r}", res(check.formula().template), "", f("result"))
        book.formula(ws, f"G{r}", f'=IF(F{r}="","",IF(LEFT(F{r},1)="✔",MIN(IF(H{r}="",1,H{r})+1,5),1))', "",
                     f("calc_center"))
        ws.write_blank(f"H{r}", None, f("input"))
        ws.data_validation(f"H{r}", {"validate": "list", "source": [1, 2, 3, 4, 5], "input_title": "Box 1-5",
                                     "input_message": "Press Alt+Down and pick the Suggested box."})
        ws.write_blank(f"I{r}", None, f("input_date"))
        ws.data_validation(f"I{r}", {"validate": "date", "criteria": ">=", "value": dt.date(2020, 1, 1),
                                     "input_title": "Stamp the date", "input_message": "Press Ctrl+; for today's date."})
        book.formula(ws, f"J{r}", f'=IF(OR(H{r}="",I{r}=""),"",IFERROR(I{r}+CHOOSE(H{r},{choose}),""))', "",
                     f("calc_date"))
        book.formula(ws, f"K{r}", _status(r), "NEW", f("calc_center"))
        ws.set_row(r - 1, row_height((item.prompt, COLUMNS["D"]), (course.origin[item_id], COLUMNS["C"])))
        cards.append(Card(r, item_id))
        r += 1
    last = r - 1
    ws.autofilter(f"A4:K{last}")
    ws.freeze_panes(4, 0)
    ws.conditional_format(f"F5:F{last}", {"type": "formula", "criteria": '=LEFT($F5,1)="✔"', "format": book.fmt.cf("ok")})
    ws.conditional_format(f"F5:F{last}", {"type": "formula", "criteria": '=LEFT($F5,1)="✘"', "format": book.fmt.cf("bad")})
    ws.conditional_format(f"K5:K{last}", {"type": "formula", "criteria": '=$K5="DUE"', "format": book.fmt.cf("bad")})
    ws.protect("", {"autofilter": True, "select_locked_cells": True, "select_unlocked_cells": True,
                    "format_columns": True, "format_rows": True})
    return cards


def _band(book: Book, ws, row: int, text: str) -> None:
    book.text(ws, f"A{row}", text, book.fmt("band"))
    for col in "BCDEFGH":
        ws.write_blank(f"{col}{row}", None, book.fmt("band"))


def _write_start(book: Book, ws, last: int, total: int) -> dict[str, str]:
    f = book.fmt
    ws.set_column("A:A", 30)
    ws.set_column("B:B", 14)
    ws.set_column("C:H", 12)
    ws.hide_gridlines(2)
    book.text(ws, "A1", "REVIEW DECK ▸ YOUR DAILY 10 MINUTES", f("title"))
    for col in "BCDEFGH":
        ws.write_blank(f"{col}1", None, f("title_fill"))
    ws.set_row(0, 34)
    book.text(ws, "A2", "Every move from the course on a flashcard. A little every day beats cramming.", f("subtitle"))
    status, box = f"Deck!$K$5:$K${last}", f"Deck!$H$5:$H${last}"
    _band(book, ws, 4, "TODAY")
    rows = (("Cards due today", f'=COUNTIF({status},"DUE")', 0), ("New cards", f'=COUNTIF({status},"NEW")', total),
            ("Mastered (Box 5)", f"=COUNTIF({box},5)", 0))
    refs = {}
    for i, (label, formula, cached) in enumerate(rows, 5):
        book.text(ws, f"A{i}", label, f("label"))
        book.formula(ws, f"B{i}", formula, cached, f("calc_bold"))
    refs.update(due=sheet_ref(ws.name, "B5"), new=sheet_ref(ws.name, "B6"), mastered=sheet_ref(ws.name, "B7"))
    book.text(ws, "A8", "Mastery", f("label"))
    book.formula(ws, "B8", f'=TEXT(B7/{total},"0%")', "0%", f("calc_bold"))
    refs["mastery"] = sheet_ref(ws.name, "B8")
    _band(book, ws, 10, "CARDS PER BOX")
    book.text(ws, "A11", "Box", f("th"))
    book.text(ws, "B11", "Cards", f("th"))
    labels = ["New", "Box 1", "Box 2", "Box 3", "Box 4", "Box 5"]
    for i, label in enumerate(labels, 12):
        book.text(ws, f"A{i}", label, f("body"))
        formula = f'=COUNTIF({status},"NEW")' if label == "New" else f"=COUNTIF({box},{label[-1]})"
        book.formula(ws, f"B{i}", formula, total if label == "New" else 0, f("calc_center"))
    chart = book.wb.add_chart({"type": "column"})
    chart.add_series({"name": "Cards", "categories": f"=Start!$A$12:$A$17", "values": f"=Start!$B$12:$B$17",
                      "fill": {"color": T.NAVY}, "data_labels": {"value": True}})
    chart.set_title({"name": "Cards per box"})
    chart.set_legend({"none": True})
    ws.insert_chart("D4", chart, {"description": "Column chart: how many cards are New and how many sit in "
                                                  "Boxes 1 to 5.", "x_scale": 1.1, "y_scale": 0.9})
    _band(book, ws, 20, "HOW IT WORKS")
    for i, line in enumerate(HOW_IT_WORKS, 21):
        book.text(ws, f"A{i}", line, f("body_nowrap"))
    _band(book, ws, 26, "DAILY ROUTINE")
    for i, line in enumerate(ROUTINE, 27):
        book.text(ws, f"A{i}", line, f("body_nowrap"))
    ws.protect("", {"select_locked_cells": True, "select_unlocked_cells": True, "objects": False})
    return refs


def build_deck(course: Course, out_dir: Path) -> BuiltDeck:
    book = Book(Path(out_dir) / DECK_FILE, title="Review Deck",
                subject="Excel practice: spaced-repetition flashcards for every move in the course",
                keywords="Excel, practice, review, spaced repetition, Leitner")
    start = book.sheet("Start", T.TAB_COLORS["DECK"])
    deck = book.sheet("Deck", T.TAB_COLORS["DECK"])
    key = KeySheet(book, book.sheet("Key"))
    cards = _write_deck(book, deck, key, course)
    refs = _write_start(book, start, cards[-1].row, len(cards))
    start.activate()
    book.close()
    return BuiltDeck(book.path, book.formulas, cards, refs)
