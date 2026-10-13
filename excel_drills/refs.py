"""Placeholders «…» let content name cells before layout decides where they live."""
from __future__ import annotations

import re

from xlsxwriter.utility import quote_sheetname, xl_cell_to_rowcol, xl_rowcol_to_cell

TOKEN = re.compile(r"«([^«»]+)»")
_PART = re.compile(r"^\$?([A-Z]{1,3})?\$?(\d+)?$")
_REF = re.compile(r"^(?:'((?:[^']|'')+)'|([^'!]+))!(.+)$")
_A1 = re.compile(r"(?<![A-Za-z_.$])(\$?[A-Z]{1,3}\$?\d+(?::\$?[A-Z]{1,3}\$?\d+)?)(?![\w(])")


def absolute(addr: str) -> str:
    """'B5' -> '$B$5', 'B5:C9' -> '$B$5:$C$9', 'B:B' -> '$B:$B', '5:7' -> '$5:$7'."""
    out = []
    for part in addr.upper().split(":"):
        m = _PART.match(part)
        if not part or not m or not (m.group(1) or m.group(2)):
            raise ValueError(f"not an A1 address: {addr!r}")
        col, row = m.groups()
        out.append((f"${col}" if col else "") + (f"${row}" if row else ""))
    return ":".join(out)


def sheet_ref(sheet: str, addr: str) -> str:
    return f"{quote_sheetname(sheet)}!{absolute(addr)}"


def resolve(template: str, names: dict[str, str], arena_sheet: str | None) -> str:
    def sub(m: re.Match) -> str:
        key = m.group(1)
        if key[0] in "@#":
            if arena_sheet is None:
                raise KeyError(f"«{key}» used but there is no arena sheet")
            if key[0] == "@":
                return sheet_ref(arena_sheet, key[1:])
            target = f"'{arena_sheet.replace(chr(39), chr(39) * 2)}'!{key[1:]}"
            return 'INDIRECT("' + target.replace('"', '""') + '")'
        if key not in names:
            raise KeyError(f"unknown placeholder «{key}»")
        return names[key]

    out = TOKEN.sub(sub, template)
    if "«" in out or "»" in out:
        raise ValueError(f"unresolved placeholder in {out!r}")
    return out


def split_ref(ref: str) -> tuple[str, str]:
    m = _REF.match(ref)
    if not m:
        raise ValueError(f"not a sheet reference: {ref!r}")
    sheet = m.group(1).replace("''", "'") if m.group(1) else m.group(2)
    return sheet, m.group(3).replace("$", "")


_SPILL = re.compile(r"(\$?[A-Z]{1,3}\$?\d+)#")


def on_arena(formula: str) -> str:
    """'=SUM(B5:B9)*$E$2' -> '=SUM(«@B5:B9»)*«@E2»'; 'O6#' -> 'ANCHORARRAY(«@O6»)'; quoted text untouched."""
    parts = formula.split('"')
    for i in range(0, len(parts), 2):
        part = _SPILL.sub(r"ANCHORARRAY(\1)", parts[i])
        parts[i] = _A1.sub(lambda m: "«@" + m.group(1).replace("$", "") + "»", part)
    return '"'.join(parts)


def has_raw_spill_operator(formula: str) -> bool:
    """True if a cell reference outside quotes is followed by '#' (must be written as ANCHORARRAY)."""
    return any(_SPILL.search(part) for part in formula.split('"')[0::2])


def cells_in(rng: str) -> list[str]:
    """Row-major list of the cells in 'B5:C6' (or ['D7'] for one cell)."""
    first, _, last = rng.upper().replace("$", "").partition(":")
    r1, c1 = xl_cell_to_rowcol(first)
    r2, c2 = xl_cell_to_rowcol(last or first)
    return [xl_rowcol_to_cell(r, c) for r in range(r1, r2 + 1) for c in range(c1, c2 + 1)]


def col_of(addr: str) -> str:
    return re.match(r"\$?([A-Z]+)", addr.upper()).group(1)


def row_of(addr: str) -> int:
    return int(re.search(r"(\d+)$", addr).group(1))
