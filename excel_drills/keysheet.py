"""The very hidden Key sheet: expected answers, accepted variants, dropdown options and hints."""
from __future__ import annotations

from typing import Callable

from xlsxwriter.utility import xl_rowcol_to_cell

from .checks import Check, KeyValue
from .refs import sheet_ref
from .writer import Book

FIRST_LIST_COL = 4            # column E
MAX_LIST = 40
SPILL_FIRST_ROW = 2000        # 0-based: Excel row 2001
SPILL_STEP = 100


class KeySheet:
    def __init__(self, book: Book, ws):
        self.book, self.ws = book, ws
        ws.very_hidden()
        for col, label in enumerate(("Challenge", "Hint", "Expected", "", "Lists / per-cell expectations →")):
            if label:
                ws.write_string(0, col, label)
        self._row = 1
        self._spills = 0

    def _ref(self, row: int, col: int) -> str:
        return sheet_ref(self.ws.name, xl_rowcol_to_cell(row, col))

    def _put(self, row: int, col: int, kv: KeyValue, resolve_tpl: Callable[[str], str]) -> None:
        cell = xl_rowcol_to_cell(row, col)
        if kv.template is None:
            self.book.put(self.ws, cell, kv.value)
        else:
            self.book.formula(self.ws, cell, resolve_tpl(kv.template), kv.value, volatile=kv.volatile)

    def add(self, label: str, hint: str, check: Check, resolve_tpl: Callable[[str], str]) -> dict[str, str]:
        r = self._row
        self._row += 1
        if self._row >= SPILL_FIRST_ROW:
            raise ValueError("Key sheet rows would collide with the spill area")
        self.ws.write_string(r, 0, label)
        self.ws.write_string(r, 1, hint)
        names = {"hint": self._ref(r, 1)}
        values = check.key_values()
        lists = check.variants() or check.options()
        if len(values) > 1 and lists:
            raise ValueError(f"{label}: a check can't need both per-cell expectations and a list")
        if len(values) == 1:
            self._put(r, 2, values[0], resolve_tpl)
            names["key"] = self._ref(r, 2)
        elif values:
            if len(values) > MAX_LIST:
                raise ValueError(f"{label}: too many expected cells")
            for i, kv in enumerate(values):
                self._put(r, FIRST_LIST_COL + i, kv, resolve_tpl)
                names[f"key{i + 1}"] = self._ref(r, FIRST_LIST_COL + i)
            names["key"] = names["key1"]
        if lists:
            if len(lists) > MAX_LIST:
                raise ValueError(f"{label}: too many list entries")
            for i, text in enumerate(lists):
                self.ws.write_string(r, FIRST_LIST_COL + i, text)
            span = f"{xl_rowcol_to_cell(r, FIRST_LIST_COL)}:{xl_rowcol_to_cell(r, FIRST_LIST_COL + len(lists) - 1)}"
            names["keyrow"] = names["opts"] = sheet_ref(self.ws.name, span)
        spill = check.spill()
        if spill is not None:
            sr = SPILL_FIRST_ROW + SPILL_STEP * self._spills
            self._spills += 1
            self._put(sr, FIRST_LIST_COL, spill, resolve_tpl)
            names["spill"] = self._ref(sr, FIRST_LIST_COL)
        return names
