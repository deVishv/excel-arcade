"""Start hub (stage select, score, rank, next up) and the Cheat Codes reference sheet."""
from __future__ import annotations

from xlsxwriter.utility import quote_sheetname

from .checks import q
from .model import Stage
from .refs import sheet_ref
from .stage_sheet import PROTECT, PlacedSheet, stars_formula
from .writer import Book, row_height

HOW_TO = (
    "1 · Each stage: read the BRIEFING, then answer WARM-UP, TRAINING and CHALLENGES.",
    "2 · Yellow cells are yours: type, pick from a list (Alt+↓), or follow a ▶ ARENA link and do the move there.",
    "3 · ✔ CLEAR = right · ✘ = try again · · not yet = drill not done. Stuck? Pick 'Show hint' (5 XP instead of 10).",
    "4 · Formatting or hiding drills: press F9 to refresh the check. Tab jumps between yellow cells.",
)
REQUIREMENTS = "Needs Windows with Microsoft Excel 365 or 2021+ (English). In Protected View, click Enable Editing."
REPLAY = ("Replay a stage: select a run of its yellow cells (Ctrl+click to add more), then press Delete. "
          "Undo an arena drill with Ctrl+Z.")
WIDTHS = {"A": 16, "B": 32, "C": 16, "D": 12, "E": 16, "F": 36}


def _band(book: Book, ws, row: int, text: str) -> None:
    book.text(ws, f"A{row}", text, book.fmt("band"))
    for col in "BCDEF":
        ws.write_blank(f"{col}{row}", None, book.fmt("band"))


def render_hub(book: Book, ws, *, title: str, tagline: str, sheets: list[PlacedSheet], boss: PlacedSheet | None,
               how_to=HOW_TO, timer_cell: str | None = None, par: int | None = None) -> dict[str, str]:
    b, f = book, book.fmt
    for col, width in WIDTHS.items():
        ws.set_column(f"{col}:{col}", width)
    ws.hide_gridlines(2)
    ws.set_landscape()
    ws.fit_to_pages(1, 0)
    b.text(ws, "A1", title, f("title"))
    for col in "BCDEF":
        ws.write_blank(f"{col}1", None, f("title_fill"))
    ws.set_row(0, 34)
    b.text(ws, "A2", tagline, f("subtitle"))
    _band(b, ws, 4, "HOW TO PLAY")
    r = 5
    for line in (*how_to, REQUIREMENTS):
        b.text(ws, f"A{r}", line, f("body_nowrap"))
        r += 1
    r += 1
    _band(b, ws, r, "STAGE SELECT")
    r += 1
    for col, label in zip("ABCDEF", ("Stage", "Name", "Score", "Stars", "Status", "Go")):
        b.text(ws, f"{col}{r}", label, f("th"))
    r += 1
    refs: dict[str, str] = {}
    rows = [*sheets, *([boss] if boss else [])]
    first = r
    for p in rows:
        total = f"SUM({p.xp_range})"
        b.text(ws, f"A{r}", p.code, f("label"))
        b.text(ws, f"B{r}", p.name, f("body"))
        b.formula(ws, f"C{r}", f'={total}&" / {p.max_xp}"', f"0 / {p.max_xp}", f("calc_center"))
        b.formula(ws, f"D{r}", stars_formula(total, p.max_xp), "☆☆☆", f("calc_symbol"))
        if p.gate:
            status, cached = f'=IF({p.gate}="OPEN",IF({total}>={p.max_xp}*0.5,"DEFEATED","OPEN"),"LOCKED")', "LOCKED"
        else:
            status = (f'=IF({total}>={p.max_xp},"PERFECT",IF({total}>={p.max_xp}*0.5,"CLEARED",'
                      f'IF({total}>0,"IN PROGRESS","NEW")))')
            cached = "NEW"
        b.formula(ws, f"E{r}", status, cached, f("calc_center"))
        refs[f"status:{p.code}"] = sheet_ref(ws.name, f"E{r}")
        label = "Go to the Boss" if p.gate else f"Go to {p.code} {p.name}"
        ws.write_url(f"F{r}", f"internal:{quote_sheetname(p.sheet)}!A1", f("link"), string=label)
        r += 1
    last_stage = first + len(sheets) - 1
    r += 1
    grand = "+".join(f"SUM({p.xp_range})" for p in rows)
    grand_max = sum(p.max_xp for p in rows)
    b.text(ws, f"A{r}", "TOTAL SCORE", f("label"))
    b.formula(ws, f"B{r}", f'=({grand})&" / {grand_max}"', f"0 / {grand_max}", f("calc_bold"))
    refs["total"] = sheet_ref(ws.name, f"B{r}")
    r += 1
    time_ref = timer_cell or (boss.time_cell if boss else None)
    par_val = par if par is not None else (boss.par if boss else None)
    b.text(ws, f"A{r}", "RANK", f("label"))
    s_rule = f"AND(_xlpm.p>=1,ISNUMBER({time_ref}),{time_ref}<={par_val})" if time_ref else "_xlpm.p>=1"
    b.formula(ws, f"B{r}", f'=LET(_xlpm.p,({grand})/{grand_max},IF({s_rule},"S",IF(_xlpm.p>=0.9,"A",'
                           f'IF(_xlpm.p>=0.75,"B",IF(_xlpm.p>=0.5,"C","D")))))', "D", f("calc_bold"))
    refs["rank"] = sheet_ref(ws.name, f"B{r}")
    b.text(ws, f"C{r}", "S = 100% and under par · A ≥ 90% · B ≥ 75% · C ≥ 50%", f("muted_nowrap"))
    r += 1
    if time_ref:
        b.text(ws, f"A{r}", "BEST TIME", f("label"))
        b.formula(ws, f"B{r}", f'=IF(ISNUMBER({time_ref}),{time_ref}&" min (par {par_val})","—")', "—",
                  f("calc_bold"))
        r += 1
    b.text(ws, f"A{r}", "NEXT UP", f("label"))
    if sheets:
        pick = f'MATCH("☆☆☆",$D${first}:$D${last_stage},0)'
        after = (f'IF({boss.gate}="OPEN","the Boss","All clear! Aim for rank S")' if boss
                 else '"All clear! Aim for rank S"')
        b.formula(ws, f"B{r}", f'=IFERROR(INDEX($A${first}:$A${last_stage},{pick})&" "&'
                               f'INDEX($B${first}:$B${last_stage},{pick}),{after})',
                  f"{sheets[0].code} {sheets[0].name}", f("calc_bold"))
    refs["next"] = sheet_ref(ws.name, f"B{r}")
    r += 2
    b.text(ws, f"A{r}", REPLAY, f("muted_nowrap"))
    ws.protect("", PROTECT)
    return refs


def render_cheat_codes(book: Book, ws, *, title: str, stages: tuple[Stage, ...]) -> None:
    b, f = book, book.fmt
    for col, width in {"A": 10, "B": 26, "C": 50, "D": 56}.items():
        ws.set_column(f"{col}:{col}", width)
    ws.hide_gridlines(2)
    b.text(ws, "A1", title, f("title"))
    for col in "BCD":
        ws.write_blank(f"{col}1", None, f("title_fill"))
    ws.set_row(0, 34)
    b.text(ws, "A2", "Every move from this world on one page. Keep it open while you play, or print it (Ctrl+P).",
           f("subtitle"))
    for col, label in zip("ABCD", ("Stage", "Keys / Syntax", "What it does", "Pro tip")):
        b.text(ws, f"{col}4", label, f("th"))
    r = 5
    for stage in stages:
        for item in stage.items:
            b.text(ws, f"A{r}", stage.code, f("body_center"))
            b.text(ws, f"B{r}", item.display, f("key"))
            b.text(ws, f"C{r}", item.what, f("body"))
            b.text(ws, f"D{r}", item.tip, f("body"))
            ws.set_row(r - 1, row_height((item.what, 50), (item.tip, 56), (item.display, 26)))
            r += 1
    ws.freeze_panes(4, 0)
    ws.set_landscape()
    ws.fit_to_pages(1, 0)
    ws.repeat_rows(3)
    ws.protect("", PROTECT)
