"""Arena sheets: unprotected practice areas where DO/FIND/FORMULA missions happen."""
from __future__ import annotations

from xlsxwriter.utility import quote_sheetname

from .model import Arena, Formula
from .refs import cells_in, sheet_ref
from .writer import Book

PURPOSE = "Practice area · everything here is editable. Missions and their checks are on the stage sheet."


def _expand(specs) -> set[str]:
    out: set[str] = set()
    for spec in specs:
        out.update(cells_in(spec))
    return out


def _formats(arena: Arena) -> dict[str, str]:
    out: dict[str, str] = {}
    for spec, fmt in arena.number_formats.items():
        for cell in cells_in(spec):
            out[cell] = fmt
    return out


def render_arena(book: Book, ws, arena: Arena, *, title: str, back_sheet: str) -> None:
    f = book.fmt
    ws.set_column("A:A", 14)
    ws.set_column("B:Z", 13)
    for spec, width in arena.widths.items():
        ws.set_column(spec if ":" in spec else f"{spec}:{spec}", width)
    book.text(ws, "A1", title, f("title"))
    book.text(ws, "A2", PURPOSE, f("subtitle"))
    book.text(ws, "A3", "PASS CODE", f("pass_label"))
    book.text(ws, "B3", arena.pass_code, f("pass"))
    ws.write_url("D3", f"internal:{quote_sheetname(back_sheet)}!A1", f("link"), string=f"◀ Back to {back_sheet}")
    inputs, headers, labels = _expand(arena.inputs), _expand(arena.headers), _expand(arena.labels)
    num = _formats(arena)

    def style(cell: str):
        name = ("arena_input" if cell in inputs else "arena_head" if cell in headers
                else "arena_label" if cell in labels else "arena")
        return f(name, num_format=num[cell]) if cell in num else f(name)

    for cell, value in arena.cells.items():
        if isinstance(value, Formula):
            book.formula(ws, cell, value.text, value.cached, style(cell), error_ok=value.error_ok)
        else:
            book.put(ws, cell, value, style(cell))
    for cell in sorted(inputs - arena.cells.keys()):
        ws.write_blank(cell, None, style(cell))
    for cell, values in arena.validations.items():
        ws.data_validation(cell, {"validate": "list", "source": list(values), "input_title": "Pick from the list",
                                  "input_message": "Press Alt+Down to open the list, then choose with the arrow keys."})
    for name, cell in arena.names.items():
        book.wb.define_name(name, "=" + sheet_ref(ws.name, cell))


def render_extra(book: Book, ws, purpose: str) -> None:
    """A plain extra sheet a mission works on (e.g. 'Rename Me')."""
    book.text(ws, "A1", ws.name.upper(), book.fmt("title"))
    book.text(ws, "A2", purpose, book.fmt("subtitle"))
