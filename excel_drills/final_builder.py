"""The Final Boss workbook: Start (with a speedrun timer), three rounds + arenas, and a Certificate."""
from __future__ import annotations

from pathlib import Path

from . import theme as T
from .arena_sheet import render_arena
from .checks import q
from .course import Course
from .hub_sheet import render_hub
from .keysheet import KeySheet
from .refs import sheet_ref
from .stage_sheet import PROTECT, render_round
from .world_builder import BuiltWorkbook
from .writer import Book, row_height

TIMER = ("C40", "C41", "C42")                 # START, FINISH, TIME (minutes) on the Start sheet


def _timer(book: Book, ws, par: int) -> None:
    f = book.fmt
    start, finish, time = TIMER
    book.text(ws, "A39", "SPEEDRUN · stamp START before Round 1 and FINISH after Round 3", f("band"))
    for col in "BCDEF":
        ws.write_blank(f"{col}39", None, f("band"))
    stamp = {"validate": "any", "input_title": "Stamp the time", "input_message": "Press Ctrl+Shift+: to type the time."}
    book.text(ws, "B40", "START (Ctrl+Shift+:)", f("label"))
    ws.write_blank(start, None, f("input_time"))
    ws.data_validation(start, stamp)
    book.text(ws, "B41", "FINISH (Ctrl+Shift+:)", f("label"))
    ws.write_blank(finish, None, f("input_time"))
    ws.data_validation(finish, stamp)
    book.text(ws, "B42", "TIME", f("label"))
    book.formula(ws, time, f'=IF(OR({start}="",{finish}=""),"",ROUND(MOD({finish}-{start},1)*1440,0))', "",
                 f("calc_minutes"))
    book.text(ws, "B43", "PAR", f("label"))
    book.put(ws, "C43", par, f("calc_minutes"))


def _certificate(book: Book, ws, rank_ref: str) -> None:
    f = book.fmt
    for col, width in {"A": 4, "B": 40, "C": 44}.items():
        ws.set_column(f"{col}:{col}", width)
    ws.hide_gridlines(2)
    book.text(ws, "A1", "CERTIFICATE OF MASTERY", f("title"))
    for col in "BC":
        ws.write_blank(f"{col}1", None, f("title_fill"))
    ws.set_row(0, 34)
    book.text(ws, "A2", "Type your name, stamp the date with Ctrl+;, then print it with Ctrl+P.", f("subtitle"))
    book.text(ws, "B5", "Your name", f("label"))
    ws.write_blank("C5", None, f("input"))
    ws.data_validation("C5", {"validate": "any", "input_title": "Your name", "input_message": "Type your name."})
    book.text(ws, "B7", "Completed on (select C7, press Ctrl+;)", f("label"))
    ws.write_blank("C7", None, f("input_date"))
    book.text(ws, "B9", "Final rank", f("label"))
    book.formula(ws, "C9", f"={rank_ref}", "D", f("calc_bold"))
    blank_line = "This certifies that [your name] conquered the Excel Arcade with rank D."
    book.formula(ws, "B11", '="This certifies that "&IF(C5="","[your name]",C5)&'
                            '" conquered the Excel Arcade with rank "&C9&"."', blank_line, f("calc"))
    ws.set_row(10, row_height((blank_line + " " * 20, 40)))
    book.text(ws, "B13", "★ ★ ★   EXCEL ARCADE CHAMPION   ★ ★ ★", f("trophy"))
    ws.protect("", PROTECT)


def build_final(course: Course, out_dir: Path) -> BuiltWorkbook:
    final = course.final
    book = Book(Path(out_dir) / final.file_name, title="Final Boss · The Championship",
                subject="Excel practice: the whole course in one championship",
                keywords="Excel, practice, final, championship")
    hub_ws = book.sheet("Start", T.TAB_COLORS["HUB"])
    layout = [(rnd, book.sheet(f"{rnd.code} {rnd.name}", T.TAB_COLORS["FINAL"]), book.sheet(f"{rnd.code} Arena"))
              for rnd in final.rounds]
    cert_ws = book.sheet("Certificate", T.TAB_COLORS["FINAL"])
    key = KeySheet(book, book.sheet("Key"))
    extra = {"sheets": str(len(book.wb.worksheets()))}
    placed = []
    for i, (rnd, ws, aws) in enumerate(layout):
        render_arena(book, aws, rnd.arena, title=f"ARENA ▸ {rnd.code} {rnd.name.upper()}", back_sheet=ws.name)
        ids = [item_id for item_id in course.schedule.overflow if course.items[item_id].kind in rnd.recall_kinds]
        recalls = [course.recall(item_id, f"{rnd.code}.G{j}", flashback=True) for j, item_id in enumerate(ids, 1)]
        nxt = layout[i + 1][0] if i + 1 < len(layout) else None
        placed.append(render_round(book, ws, key, rnd, recalls=recalls, arena_sheet=aws.name,
                                   next_label=f"{nxt.code} {nxt.name}" if nxt else "Certificate", extra_names=extra))
    hub = render_hub(book, hub_ws, title="FINAL BOSS ▸ THE CHAMPIONSHIP",
                     tagline="Every shortcut and formula from the course in one championship. Beat par for rank S.",
                     sheets=placed, boss=None, timer_cell=sheet_ref("Start", TIMER[2]), par=final.par_minutes)
    _timer(book, hub_ws, final.par_minutes)
    _certificate(book, cert_ws, hub["rank"])
    hub_ws.activate()
    names = [ws.name for ws in book.wb.worksheets()]
    book.close()
    return BuiltWorkbook(book.path, book.formulas, placed, hub, names)
