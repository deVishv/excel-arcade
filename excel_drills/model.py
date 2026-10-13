"""Content model: plain data describing worlds, plus small constructors that keep content files short."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from typing import Callable, Literal, Sequence, Union

from xlsxwriter.utility import xl_cell_to_rowcol, xl_rowcol_to_cell

from . import theme as T
from .checks import Check, Condition, Filled, Find, SelfCheck, Spill, Value
from .refs import cells_in, on_arena, row_of

ItemKind = Literal["shortcut", "function", "concept"]
ChallengeKind = Literal["PICK", "RECALL", "FIND", "DO", "FORMULA", "SELF"]
ARENA_HEADER_CELLS = ("A1", "A2", "A3", "B3", "D3")   # title, purpose, PASS CODE label/value, back link
ARENA_FIRST_ROW = 5


@dataclass(frozen=True)
class Item:
    id: str
    kind: ItemKind
    display: str
    what: str
    tip: str
    prompt: str
    answers: tuple[str, ...]
    hint: str
    distractors: tuple[str, ...] = ()


@dataclass(frozen=True)
class Formula:
    """A formula placed on an arena. `cached` is shown before Excel recalculates (Protected View)."""
    text: str
    cached: object
    error_ok: bool = False      # the formula is meant to show an error (e.g. a #SPILL! drill)


ArenaValue = Union[str, int, float, dt.date, Formula, None]


@dataclass(frozen=True)
class Arena:
    cells: dict
    pass_code: str
    inputs: tuple[str, ...] = ()        # cells or ranges styled as yellow input cells
    headers: tuple[str, ...] = ()       # cells or ranges styled as table headers
    labels: tuple[str, ...] = ()        # cells or ranges styled bold
    number_formats: dict = field(default_factory=dict)   # cell or range -> Excel number format
    widths: dict = field(default_factory=dict)           # "B" or "B:D" -> width
    validations: dict = field(default_factory=dict)      # cell -> dropdown values
    names: dict = field(default_factory=dict)            # defined name -> cell


@dataclass(frozen=True)
class Fixture:
    """One step a test performs to play a mission (see tests/excel/actions.py for the actions)."""
    action: str
    target: str = "«ans»"
    value: object = None
    args: tuple = ()


@dataclass(frozen=True)
class Challenge:
    id: str
    kind: ChallengeKind
    prompt: str
    hint: str
    check: Check
    solve: tuple[Fixture, ...]
    wrong: tuple[tuple[Fixture, ...], ...]
    items: tuple[str, ...] = ()
    arena_cell: str | None = None
    input_message: str = ""


@dataclass(frozen=True)
class Stage:
    code: str
    name: str
    goal: str
    items: tuple[Item, ...]
    missions: tuple[Challenge, ...]
    arena: Arena | None = None
    extra_sheets: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class Boss:
    missions: tuple[Challenge, ...]
    arena: Arena
    par_minutes: int


@dataclass(frozen=True)
class World:
    code: str
    track: Literal["S", "F"]
    order: int
    title: str
    tagline: str
    file_name: str
    stages: tuple[Stage, ...]
    boss: Boss


@dataclass(frozen=True)
class FinalRound:
    code: str
    name: str
    goal: str
    recall_kinds: tuple[str, ...]
    missions: tuple[Challenge, ...]
    arena: Arena


@dataclass(frozen=True)
class FinalBoss:
    file_name: str
    rounds: tuple[FinalRound, ...]
    par_minutes: int


# ---- arena helpers ------------------------------------------------------------------------------

def _offset(at: str, dr: int, dc: int) -> str:
    r, c = xl_cell_to_rowcol(at)
    return xl_rowcol_to_cell(r + dr, c + dc)


def column(at: str, values: Sequence[ArenaValue]) -> dict:
    return {_offset(at, i, 0): v for i, v in enumerate(values) if v is not None}


def row(at: str, values: Sequence[ArenaValue]) -> dict:
    return {_offset(at, 0, j): v for j, v in enumerate(values) if v is not None}


def table(at: str, header: Sequence[str], rows: Sequence[Sequence[ArenaValue]]) -> dict:
    out = {_offset(at, 0, j): h for j, h in enumerate(header)}
    for i, values in enumerate(rows, 1):
        out.update({_offset(at, i, j): v for j, v in enumerate(values) if v is not None})
    return out


def merge(*parts: dict) -> dict:
    out: dict = {}
    for part in parts:
        clash = out.keys() & part.keys()
        if clash:
            raise ValueError(f"arena cells defined twice: {sorted(clash)}")
        out.update(part)
    return out


def count_filled(arena: Arena, rng: str) -> int:
    """Non-empty cells of `rng` on the rendered arena sheet, including the fixed header cells."""
    filled = {a for a, v in arena.cells.items() if v is not None and v != ""} | set(ARENA_HEADER_CELLS)
    return len(set(cells_in(rng)) & filled)


# ---- challenge constructors ------------------------------------------------------------------------

def _fix(target: str, value: object) -> Fixture:
    action = "formula" if isinstance(value, str) and value.startswith("=") else "type"
    return Fixture(action, target, value)


def find(id: str, prompt: str, hint: str, answer: object, *, items: Sequence[str], wrong: Sequence[object],
         verify: tuple = ()) -> Challenge:
    return Challenge(id, "FIND", prompt, hint, Find(answer, tuple(verify)),
                     solve=(Fixture("type", "«ans»", answer),),
                     wrong=tuple((Fixture("type", "«ans»", w),) for w in wrong), items=tuple(items))


def formula(id: str, prompt: str, hint: str, cell: str, solution: str, expect: object, *, items: Sequence[str],
            wrong: Sequence[object], uses=(), contains=(), dollar=False, case_sensitive=False,
            volatile=False, key: str | None = None) -> Challenge:
    """The learner types `solution` into arena `cell`; the Key computes the same formula live.

    `key` overrides the Key-sheet formula when the learner's formula can't be stored as-is
    (e.g. LET, whose variable names would need _xlpm. prefixes): give an equivalent formula.
    """
    check = Value(cell, expect, on_arena(key or solution), tuple(uses), tuple(contains), dollar, case_sensitive,
                  volatile)
    return Challenge(id, "FORMULA", prompt, hint, check, solve=(_fix(f"«@{cell}»", solution),),
                     wrong=tuple((_fix(f"«@{cell}»", w),) for w in wrong), items=tuple(items), arena_cell=cell)


def filled(id: str, prompt: str, hint: str, rng: str, solution_for: Callable[[str], str],
           expects: Sequence[object], *, items: Sequence[str], wrong_for: Callable[[str], object],
           uses=(), contains=(), dollar=False, case_sensitive=False,
           key_for: Callable[[str], str] | None = None) -> Challenge:
    """A formula filled over `rng`; solution_for(cell) is the formula the learner ends up with in that cell.

    `key_for(cell)` gives the Key an independent formula when the solution reads cells the learner fills
    in an earlier mission (otherwise the expectation would move with the learner's own answers).
    """
    cells = tuple(cells_in(rng))
    solutions = [solution_for(c) for c in cells]
    keys = [(key_for or solution_for)(c) for c in cells]
    check = Filled(cells, tuple(expects), tuple(on_arena(k) for k in keys), tuple(uses), tuple(contains),
                   dollar, case_sensitive)
    solve = tuple(_fix(f"«@{c}»", s) for c, s in zip(cells, solutions))
    wrong = (tuple(_fix(f"«@{c}»", wrong_for(c)) for c in cells),)
    return Challenge(id, "FORMULA", prompt, hint, check, solve, wrong, tuple(items), arena_cell=cells[0])


def spill(id: str, prompt: str, hint: str, anchor: str, solution: str, expect: Sequence[Sequence[object]], *,
          items: Sequence[str], wrong: Sequence[object], uses=(), key: str | None = None) -> Challenge:
    check = Spill(anchor, tuple(tuple(r) for r in expect), on_arena(key or solution), tuple(uses))
    return Challenge(id, "FORMULA", prompt, hint, check, solve=(_fix(f"«@{anchor}»", solution),),
                     wrong=tuple((_fix(f"«@{anchor}»", w),) for w in wrong), items=tuple(items), arena_cell=anchor)


def do(id: str, prompt: str, hint: str, condition: str, *, solve: Sequence[Fixture],
       wrong: Sequence[Sequence[Fixture]], items: Sequence[str], arena_cell: str, f9: bool = False,
       volatile: bool = False) -> Challenge:
    return Challenge(id, "DO", prompt, hint, Condition(condition, f9, volatile), tuple(solve),
                     tuple(tuple(w) for w in wrong), tuple(items), arena_cell=arena_cell)


def self_check(id: str, prompt: str, hint: str, *, items: Sequence[str]) -> Challenge:
    return Challenge(id, "SELF", prompt, hint, SelfCheck(), solve=(Fixture("type", "«ans»", T.DONE),),
                     wrong=((Fixture("type", "«ans»", "Not yet"),),), items=tuple(items))


# ---- validation ------------------------------------------------------------------------------------

def _arena_problems(where: str, arena: Arena | None) -> list[str]:
    if arena is None:
        return []
    out = []
    if not arena.pass_code:
        out.append(f"{where}: arena needs a pass code")
    for addr in arena.cells:
        if row_of(addr) < ARENA_FIRST_ROW:
            out.append(f"{where}: arena cell {addr} is inside the reserved header rows 1-4")
    return out


def _challenge_problems(where: str, ch: Challenge, has_arena: bool) -> list[str]:
    out = []
    if not 0 < len(ch.hint) <= 110:
        out.append(f"{where} {ch.id}: hint must be 1-110 characters")
    if not 0 < len(ch.prompt) <= 400:
        out.append(f"{where} {ch.id}: prompt must be 1-400 characters")
    if not ch.solve or not ch.wrong:
        out.append(f"{where} {ch.id}: needs a solve fixture and at least one wrong fixture")
    if ch.kind in ("DO", "FORMULA") and not (ch.arena_cell and has_arena):
        out.append(f"{where} {ch.id}: DO/FORMULA missions need an arena cell on an arena")
    return out


def validate_world(world: World) -> list[str]:
    problems: list[str] = []
    seen_items, seen_ids = set(), set()
    for n, stage in enumerate(world.stages, 1):
        where = stage.code
        if stage.code != f"{world.code}-{n}":
            problems.append(f"{where}: stage codes must run {world.code}-1, {world.code}-2, …")
        for item in stage.items:
            if item.id in seen_items or not item.id.startswith(world.code + "."):
                problems.append(f"{where}: bad or duplicate item id {item.id}")
            seen_items.add(item.id)
            if len(item.what) > 100 or len(item.tip) > 120 or not 0 < len(item.hint) <= 110:
                problems.append(f"{where}: {item.id} briefing/hint text too long or empty")
        problems += _arena_problems(where, stage.arena)
        for ch in stage.missions:
            if ch.id in seen_ids:
                problems.append(f"{where}: duplicate challenge id {ch.id}")
            seen_ids.add(ch.id)
            problems += _challenge_problems(where, ch, stage.arena is not None)
    if not world.boss.missions:
        problems.append(f"{world.code} Boss: no missions")
    problems += _arena_problems(f"{world.code} Boss", world.boss.arena)
    for ch in world.boss.missions:
        problems += _challenge_problems(f"{world.code} Boss", ch, True)
    return problems
