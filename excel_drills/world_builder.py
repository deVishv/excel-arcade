"""Turn one World into a workbook: Start, stages + arenas, Boss + arena, Cheat Codes, Key."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from . import theme as T
from .arena_sheet import render_arena, render_extra
from .course import Course
from .hub_sheet import render_cheat_codes, render_hub
from .keysheet import KeySheet
from .model import World
from .stage_sheet import PlacedSheet, render_boss, render_stage
from .writer import Book

TRACK_NAMES = {"S": "Shortcuts", "F": "Formulas"}


@dataclass
class BuiltWorkbook:
    path: Path
    formulas: list
    sheets: list[PlacedSheet]
    hub: dict[str, str]
    sheet_names: list[str]


def build_world(course: Course, world: World, out_dir: Path) -> BuiltWorkbook:
    track = TRACK_NAMES[world.track]
    number = world.code[1:]
    book = Book(Path(out_dir) / world.file_name, title=f"{track} {number} · {world.title}",
                subject=f"Excel practice: {world.tagline}", keywords=f"Excel, practice, {track.lower()}, {world.title}")
    hub_ws = book.sheet("Start", T.TAB_COLORS["HUB"])
    layout = []
    for st in world.stages:
        ws = book.sheet(f"{st.code} {st.name}", T.TAB_COLORS[world.track])
        aws = book.sheet(f"{st.code} Arena") if st.arena else None
        extras = [(book.sheet(name), purpose) for name, purpose in st.extra_sheets]
        layout.append((st, ws, aws, extras))
    boss_ws = book.sheet("Boss", T.TAB_COLORS["FINAL"])
    boss_aws = book.sheet("Boss Arena")
    codes_ws = book.sheet("Cheat Codes", T.TAB_COLORS["HUB"])
    key = KeySheet(book, book.sheet("Key"))
    extra_names = {"sheets": str(len(book.wb.worksheets()))}

    placed: list[PlacedSheet] = []
    for i, (st, ws, aws, extras) in enumerate(layout):
        if aws is not None:
            render_arena(book, aws, st.arena, title=f"ARENA ▸ {st.code} {st.name.upper()}", back_sheet=ws.name)
        for extra_ws, purpose in extras:
            render_extra(book, extra_ws, purpose)
        warm = [course.recall(item_id, f"{st.code}.W{j}", flashback=True)
                for j, item_id in enumerate(course.schedule.reviews[st.code], 1)]
        training = [course.pick(item.id, f"{st.code}.T{j}") for j, item in enumerate(st.items, 1)]
        recalls = [course.recall(item.id, f"{st.code}.R{j}", flashback=False) for j, item in enumerate(st.items, 1)]
        nxt = layout[i + 1][0] if i + 1 < len(layout) else None
        placed.append(render_stage(book, ws, key, st, warmups=warm, training=training, recalls=recalls,
                                   arena_sheet=aws.name if aws else None,
                                   next_label=f"{nxt.code} {nxt.name}" if nxt else "Boss", extra_names=extra_names))
    render_arena(book, boss_aws, world.boss.arena, title=f"BOSS ARENA ▸ {world.title.upper()}", back_sheet=boss_ws.name)
    flash = [course.recall(item_id, f"{world.code}-BOSS.F{j}", flashback=True)
             for j, item_id in enumerate(course.schedule.reviews[f"{world.code}-BOSS"], 1)]
    boss = render_boss(book, boss_ws, key, title=world.title, boss=world.boss, flashbacks=flash,
                       arena_sheet=boss_aws.name, stages=placed, extra_names=extra_names)
    hub = render_hub(book, hub_ws, title=f"{track.upper()} {number} ▸ {world.title.upper()}", tagline=world.tagline,
                     sheets=placed, boss=boss)
    render_cheat_codes(book, codes_ws, title=f"CHEAT CODES ▸ {world.title.upper()}", stages=world.stages)
    hub_ws.activate()
    names = [ws.name for ws in book.wb.worksheets()]
    book.close()
    return BuiltWorkbook(book.path, book.formulas, [*placed, boss], hub, names)
