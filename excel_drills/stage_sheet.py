"""Stage, Boss and Final-round sheets: score header, briefing, and the challenge table."""
from __future__ import annotations

from dataclasses import dataclass, field

from xlsxwriter.utility import quote_sheetname

from . import theme as T
from .checks import q
from .keysheet import KeySheet
from .model import Boss, Challenge, FinalRound, Item, Stage
from .refs import resolve, sheet_ref
from .writer import Book, row_height

COLS = "ABCDEFG"
WIDTHS = {"A": 6, "B": 58, "C": 30, "D": 24, "E": 12, "F": 44, "G": 7}
HEADERS = ("#", "Mission", "Your answer", "Result", "Hint?", "Hint", "XP")
PROTECT = {"select_locked_cells": True, "select_unlocked_cells": True, "format_columns": True, "format_rows": True}
INPUT_MESSAGES = {
    "RECALL": ("Type your answer", "Type keys joined with +, like Ctrl+Shift+L. For a function, type its name, "
                                   "like SUMIFS. Case and spaces don't matter."),
    "PICK": ("Pick an answer", "Press Alt+Down to open the list, choose with the arrow keys, then press Enter."),
    "FIND": ("Type what you found", "Do the move in the arena, then type the word or number you found here."),
    "SELF": ("Self-check", "Do the task in the arena, then pick Done from the list (Alt+Down)."),
}
HINT_TITLE, HINT_MESSAGE = "Need a hint?", "Pick 'Show hint' (Alt+Down). This question then gives 5 XP instead of 10."


@dataclass
class PlacedChallenge:
    challenge: Challenge
    label: str
    section: str
    sheet: str
    row: int
    names: dict
    arena_sheet: str | None
    result: str
    picker: str
    xp: str


@dataclass
class PlacedSheet:
    code: str
    name: str
    sheet: str
    arena_sheet: str | None
    first_row: int
    last_row: int
    max_xp: int
    challenges: list = field(default_factory=list)
    gate: str | None = None
    time_cell: str | None = None
    par: int | None = None

    @property
    def xp_range(self) -> str:
        return sheet_ref(self.sheet, f"G{self.first_row}:G{self.last_row}")


class ChallengeTable:
    """Writes section bands and challenge rows on one sheet, tracking the next free (1-based) row."""

    def __init__(self, book: Book, ws, key: KeySheet, *, arena_sheet: str | None, start_row: int,
                 extra_names: dict | None = None, gate: str | None = None):
        self.book, self.ws, self.key = book, ws, key
        self.arena_sheet = arena_sheet
        self.r = start_row
        self.extra_names = dict(extra_names or {})
        self.gate = gate
        self.placed: list[PlacedChallenge] = []

    def band(self, text: str) -> None:
        f = self.book.fmt
        self.book.text(self.ws, f"A{self.r}", text, f("band"))
        for col in COLS[1:]:
            self.ws.write_blank(f"{col}{self.r}", None, f("band"))
        self.ws.set_row(self.r - 1, 22)
        self.r += 1

    def header(self, labels=HEADERS) -> None:
        for col, label in zip(COLS, labels):
            if label:
                self.book.text(self.ws, f"{col}{self.r}", label, self.book.fmt("th"))
            else:
                self.ws.write_blank(f"{col}{self.r}", None, self.book.fmt("th"))
        self.r += 1

    def note(self, text: str) -> None:
        self.book.text(self.ws, f"B{self.r}", text, self.book.fmt("muted"))
        self.r += 1

    def link(self, text: str, sheet: str, cell: str = "A1") -> None:
        self.ws.write_url(f"B{self.r}", f"internal:{quote_sheetname(sheet)}!{cell}", self.book.fmt("link"),
                          string=text)
        self.r += 1

    def blank(self) -> None:
        self.r += 1

    def add(self, ch: Challenge, label: str, section: str) -> PlacedChallenge:
        b, ws, f, r = self.book, self.ws, self.book.fmt, self.r
        self.r += 1
        names = {**self.extra_names, "ans": sheet_ref(ws.name, f"C{r}"), "picker": sheet_ref(ws.name, f"E{r}")}

        def res(template: str) -> str:
            return resolve(template, names, self.arena_sheet)

        names.update(self.key.add(f"{ws.name} {label}", ch.hint, ch.check, res))
        b.text(ws, f"A{r}", label, f("body_center"))
        if self.gate:
            b.formula(ws, f"B{r}", f'=IF({self.gate}="OPEN",{q(ch.prompt)},{q(T.LOCKED_PROMPT)})',
                      T.LOCKED_PROMPT, f("calc"))
        else:
            b.text(ws, f"B{r}", ch.prompt, f("body"))
        if ch.kind in ("DO", "FORMULA"):
            if not (self.arena_sheet and ch.arena_cell):
                raise ValueError(f"{ch.id}: DO/FORMULA missions need an arena sheet and cell")
            ws.write_url(f"C{r}", f"internal:{quote_sheetname(self.arena_sheet)}!{ch.arena_cell}", f("link"),
                         string=f"▶ ARENA {label} (cell {ch.arena_cell})",
                         tip=f"Go to {self.arena_sheet}, cell {ch.arena_cell}")
        else:
            ws.write_blank(f"C{r}", None, f("input", num_format="@"))
            title, message = INPUT_MESSAGES[ch.kind]
            dv = {"validate": "any", "input_title": title, "input_message": ch.input_message or message}
            if ch.kind == "PICK":
                dv = {**dv, "validate": "list", "source": "=" + names["opts"]}
            elif ch.kind == "SELF":
                dv = {**dv, "validate": "list", "source": [T.DONE]}
            ws.data_validation(f"C{r}", dv)
        cf = ch.check.formula()
        text, cached = res(cf.template), cf.blank
        if self.gate:
            text, cached = f'=IF({self.gate}="OPEN",{text[1:]},{q(T.LOCKED)})', T.LOCKED
        b.formula(ws, f"D{r}", text, cached, f("result"), volatile=cf.volatile)
        ws.write_blank(f"E{r}", None, f("picker"))
        ws.data_validation(f"E{r}", {"validate": "list", "source": [T.SHOW_HINT],
                                     "input_title": HINT_TITLE, "input_message": HINT_MESSAGE})
        b.formula(ws, f"F{r}", f'=IF(E{r}={q(T.SHOW_HINT)},{names["hint"]},"")', "", f("hint"))
        b.formula(ws, f"G{r}", f'=IF(LEFT(D{r},1)="✔",IF(E{r}={q(T.SHOW_HINT)},5,10),0)', 0, f("xp"))
        link_text = f"▶ ARENA {label} (cell {ch.arena_cell or 'A1'})"
        prompt_text = T.LOCKED_PROMPT if self.gate and len(T.LOCKED_PROMPT) > len(ch.prompt) else ch.prompt
        ws.set_row(r - 1, row_height((prompt_text, WIDTHS["B"]), (ch.hint, WIDTHS["F"] * 0.9),
                                     (link_text, WIDTHS["C"])))
        placed = PlacedChallenge(ch, label, section, ws.name, r, names, self.arena_sheet,
                                 sheet_ref(ws.name, f"D{r}"), sheet_ref(ws.name, f"E{r}"), sheet_ref(ws.name, f"G{r}"))
        self.placed.append(placed)
        return placed


def stars_formula(total: str, max_xp: int) -> str:
    return (f'=IF({total}>={max_xp},"★★★",IF({total}>={max_xp}*0.8,"★★☆",'
            f'IF({total}>={max_xp}*0.5,"★☆☆","☆☆☆")))')


def bar_formula(total: str, max_xp: int) -> str:
    n = f"ROUND(10*{total}/{max_xp},0)"
    return f'=REPT("█",{n})&REPT("░",10-{n})&"  "&TEXT({total}/{max_xp},"0%")'


def setup_columns(ws) -> None:
    for col, width in WIDTHS.items():
        ws.set_column(f"{col}:{col}", width)
    ws.set_landscape()
    ws.fit_to_pages(1, 0)
    ws.repeat_rows(0, 3)


def write_header(book: Book, ws, *, title: str, purpose: str, first: int, last: int, max_xp: int,
                 next_label: str | None) -> None:
    f = book.fmt
    book.text(ws, "A1", title, f("title"))
    for col in COLS[1:]:
        ws.write_blank(f"{col}1", None, f("title_fill"))
    ws.set_row(0, 34)
    book.text(ws, "A2", purpose, f("subtitle"))
    total = f"SUM($G${first}:$G${last})"
    book.formula(ws, "A3", f'="SCORE "&TEXT({total},"0000")&" / {max_xp:04d}"', f"SCORE 0000 / {max_xp:04d}",
                 f("score"))
    book.formula(ws, "C3", stars_formula(total, max_xp), "☆☆☆", f("stars"))
    book.formula(ws, "D3", bar_formula(total, max_xp), "░" * 10 + "  0%", f("bar"))
    if next_label:
        book.formula(ws, "F3", f'=IF({total}>={max_xp}*0.5,{q("STAGE CLEAR! ▶ Next: " + next_label)},"")', "",
                     f("banner"))
    ws.set_row(2, 26)
    ws.freeze_panes(4, 0)


def add_result_colors(book: Book, ws, first: int, last: int) -> None:
    rng, top = f"D{first}:D{last}", f"$D{first}"
    ws.conditional_format(rng, {"type": "formula", "criteria": f'=LEFT({top},1)="✔"', "format": book.fmt.cf("ok")})
    ws.conditional_format(rng, {"type": "formula", "criteria": f'=LEFT({top},1)="✘"', "format": book.fmt.cf("bad")})
    ws.conditional_format(rng, {"type": "formula", "criteria": f'={top}="{T.LOCKED}"',
                                "format": book.fmt.cf("locked")})


def _briefing(table: ChallengeTable, items: tuple[Item, ...]) -> None:
    b, ws, f = table.book, table.ws, table.book.fmt
    table.band("BRIEFING · new moves in this stage")
    table.header(("#", "What it does · Pro tip", "Keys / Syntax", "", "", "", ""))
    for n, item in enumerate(items, 1):
        r = table.r
        b.text(ws, f"A{r}", n, f("body_center"))
        ws.write_rich_string(f"B{r}", f("label"), item.what, "\n", f("muted"), "Tip: " + item.tip, f("body"))
        b.text(ws, f"C{r}", item.display, f("key"))
        ws.set_row(r - 1, row_height((item.what + "\n" + "Tip: " + item.tip, WIDTHS["B"]),
                                     (item.display, WIDTHS["C"])))
        table.r += 1


def _finish(book: Book, ws, table: ChallengeTable, *, code: str, name: str, title: str, purpose: str,
            next_label: str | None, **extra) -> PlacedSheet:
    first, last = table.placed[0].row, table.placed[-1].row
    max_xp = 10 * len(table.placed)
    write_header(book, ws, title=title, purpose=purpose, first=first, last=last, max_xp=max_xp, next_label=next_label)
    add_result_colors(book, ws, first, last)
    ws.protect("", PROTECT)
    return PlacedSheet(code, name, ws.name, table.arena_sheet, first, last, max_xp, table.placed, **extra)


def render_stage(book: Book, ws, key: KeySheet, stage: Stage, *, warmups: list[Challenge], training: list[Challenge],
                 recalls: list[Challenge], arena_sheet: str | None, next_label: str, extra_names: dict) -> PlacedSheet:
    setup_columns(ws)
    t = ChallengeTable(book, ws, key, arena_sheet=arena_sheet, start_row=5, extra_names=extra_names)
    _briefing(t, stage.items)
    t.blank()
    t.band("WARM-UP · flashback to earlier stages")
    if warmups:
        t.header()
        for i, ch in enumerate(warmups, 1):
            t.add(ch, f"W{i}", "warmup")
    else:
        t.note("Nothing to review yet — fresh start!")
    if training:
        t.blank()
        t.band("TRAINING · recognize the move (pick from the list)")
        t.header()
        for i, ch in enumerate(training, 1):
            t.add(ch, f"T{i}", "training")
    t.blank()
    t.band("CHALLENGES · recall it, then do it")
    if arena_sheet:
        t.link(f"▶ Open {arena_sheet} (or press Ctrl+PgDn)", arena_sheet)
    t.header()
    for i, ch in enumerate([*recalls, *stage.missions], 1):
        t.add(ch, f"C{i}", "challenge")
    return _finish(book, ws, t, code=stage.code, name=stage.name, title=f"STAGE {stage.code} ▸ {stage.name.upper()}",
                   purpose=f"Goal: {stage.goal}", next_label=next_label)


def render_boss(book: Book, ws, key: KeySheet, *, title: str, boss: Boss, flashbacks: list[Challenge],
                arena_sheet: str, stages: list[PlacedSheet], extra_names: dict) -> PlacedSheet:
    setup_columns(ws)
    b, f = book, book.fmt
    t = ChallengeTable(book, ws, key, arena_sheet=arena_sheet, start_row=5, extra_names=extra_names, gate="$C$10")
    t.band("SPEEDRUN · stamp START, beat the Boss, stamp FINISH")
    stamp = {"validate": "any", "input_title": "Stamp the time", "input_message": "Press Ctrl+Shift+: to type the current time."}
    b.text(ws, "B6", "START · select C6 and press Ctrl+Shift+:", f("label"))
    ws.write_blank("C6", None, f("input_time"))
    ws.data_validation("C6", stamp)
    b.text(ws, "B7", "FINISH · select C7 and press Ctrl+Shift+:", f("label"))
    ws.write_blank("C7", None, f("input_time"))
    ws.data_validation("C7", stamp)
    b.text(ws, "B8", "TIME", f("label"))
    b.formula(ws, "C8", '=IF(OR(C6="",C7=""),"",ROUND(MOD(C7-C6,1)*1440,0))', "", f("calc_minutes"))
    b.text(ws, "B9", "PAR", f("label"))
    b.put(ws, "C9", boss.par_minutes, f("calc_minutes"))
    b.text(ws, "B10", "BOSS GATE", f("label"))
    cond = ",".join(f"SUM({p.xp_range})>={p.max_xp}*0.5" for p in stages)
    b.formula(ws, "C10", f'=IF(AND({cond}),"OPEN","LOCKED")', "LOCKED", f("calc_bold"))
    closed = "Earn ★ on every stage to open the gate"
    b.formula(ws, "D10", f'=IF(C10="OPEN","Gate open · go!",{q(closed)})', closed, f("calc"))
    t.r = 12
    if flashbacks:
        t.band("FLASHBACK · moves from earlier worlds")
        t.header()
        for i, ch in enumerate(flashbacks, 1):
            t.add(ch, f"F{i}", "flashback")
        t.blank()
    t.band("BOSS MISSIONS")
    t.link(f"▶ Open {arena_sheet} (or press Ctrl+PgDn)", arena_sheet)
    t.header()
    for i, ch in enumerate(boss.missions, 1):
        t.add(ch, f"B{i}", "boss")
    return _finish(book, ws, t, code="BOSS", name="Boss", title=f"BOSS ▸ {title.upper()}",
                   purpose="Every move from this world in one gauntlet. Clear it under par for rank S.",
                   next_label=None, gate=sheet_ref(ws.name, "C10"), time_cell=sheet_ref(ws.name, "C8"),
                   par=boss.par_minutes)


def render_round(book: Book, ws, key: KeySheet, rnd: FinalRound, *, recalls: list[Challenge], arena_sheet: str,
                 next_label: str | None, extra_names: dict) -> PlacedSheet:
    setup_columns(ws)
    t = ChallengeTable(book, ws, key, arena_sheet=arena_sheet, start_row=5, extra_names=extra_names)
    if recalls:
        t.band("GAUNTLET · rapid recall from the whole course")
        t.header()
        for i, ch in enumerate(recalls, 1):
            t.add(ch, f"G{i}", "gauntlet")
        t.blank()
    t.band("MISSIONS")
    t.link(f"▶ Open {arena_sheet} (or press Ctrl+PgDn)", arena_sheet)
    t.header()
    for i, ch in enumerate(rnd.missions, 1):
        t.add(ch, f"M{i}", "mission")
    return _finish(book, ws, t, code=rnd.code, name=rnd.name, title=f"{rnd.code} ▸ {rnd.name.upper()}",
                   purpose=f"Goal: {rnd.goal}", next_label=next_label)
