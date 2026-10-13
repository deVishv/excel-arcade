"""How tests play missions (fixture actions) and how Excel itself solves FIND puzzles (truth recipes).

pywin32 rule (verified in Excel): late-bound calls stop at the first optional parameter you leave out, and
every keyword argument after that gap is dropped WITHOUT an error. `Range.Sort(Key1=, Order1=, Header=)`
silently ignored Header (Key2 sits in between), `Cells.Find(What=, LookIn=, ...)` ignored everything after
the missing After, and `Worksheets.Add(After=)` put the sheet first. So every call below either passes its
arguments with no gap or uses an object with plain properties (Worksheet.Sort). test_actions.py pins this.
"""
from __future__ import annotations

import re

from excel_drills.refs import resolve, split_ref

XL_DOWN, XL_UP, XL_TO_LEFT, XL_TO_RIGHT = -4121, -4162, -4159, -4161
DIRECTIONS = {"down": XL_DOWN, "up": XL_UP, "left": XL_TO_LEFT, "right": XL_TO_RIGHT}
XL_LAST_CELL, XL_CENTER, XL_LEFT = 11, -4108, -4131
XL_ASCENDING, XL_DESCENDING, XL_YES, XL_NO, XL_SORT_ON_VALUES = 1, 2, 1, 2, 0
XL_WHOLE, XL_PART, XL_VALUES, XL_BY_ROWS, XL_NEXT = 1, 2, -4163, 1, 1
LIGHT = {"type", "formula", "clear", "linebreak", "today", "now_time"}   # undoable by restoring Formula2


def rng(wb, ref: str):
    sheet, addr = split_ref(ref)
    return wb.Worksheets(sheet).Range(addr)


def _sort(r, key, *, descending: bool, header: bool) -> None:
    so = r.Worksheet.Sort
    so.SortFields.Clear()
    so.SortFields.Add(Key=key, SortOn=XL_SORT_ON_VALUES, Order=XL_DESCENDING if descending else XL_ASCENDING)
    so.SetRange(r)
    so.Header = XL_YES if header else XL_NO
    so.Apply()


def _cells_with(r, value) -> list:
    ws = r.Worksheet
    used = ws.UsedRange
    last = used.Row + used.Rows.Count - 1
    return [ws.Cells(i, r.Column) for i in range(1, last + 1) if ws.Cells(i, r.Column).Value2 == value]


def apply(wb, fx, names: dict, arena_sheet: str | None) -> None:
    target = resolve(fx.target, names, arena_sheet) if fx.target else ""
    args = tuple(resolve(a, names, arena_sheet) if isinstance(a, str) and "«" in a else a for a in fx.args)
    a = fx.action
    if a == "type":
        rng(wb, target).Value2 = fx.value
    elif a == "formula":
        rng(wb, target).Formula2 = fx.value
    elif a == "clear":
        rng(wb, target).ClearContents()
    elif a == "linebreak":
        rng(wb, target).Value2 = "\n".join(fx.value)
    elif a == "today":
        rng(wb, target).Value2 = wb.Application.Evaluate("TODAY()")
    elif a == "now_time":
        rng(wb, target).Value2 = wb.Application.Evaluate("MOD(NOW(),1)")
    elif a == "number_format":
        rng(wb, target).NumberFormat = fx.value
    elif a == "align_center":
        rng(wb, target).HorizontalAlignment = XL_CENTER
    elif a == "align_left":
        rng(wb, target).HorizontalAlignment = XL_LEFT
    elif a == "hide_rows":
        rng(wb, target).EntireRow.Hidden = True
    elif a == "hide_cols":
        rng(wb, target).EntireColumn.Hidden = True
    elif a == "hide_rows_where":
        for cell in _cells_with(rng(wb, target), fx.value):
            cell.EntireRow.Hidden = True
    elif a == "delete_rows":
        rng(wb, target).EntireRow.Delete()
    elif a == "delete_rows_where":
        for cell in reversed(_cells_with(rng(wb, target), fx.value)):
            cell.EntireRow.Delete()
    elif a == "insert_rows":
        rng(wb, target).EntireRow.Insert()
    elif a == "insert_rows_above":
        cell = _cells_with(rng(wb, target), fx.value)[0]
        cell.Worksheet.Range(f"{cell.Row}:{cell.Row + args[0] - 1}").EntireRow.Insert()
    elif a == "autofilter":
        rng(wb, target).AutoFilter(Field=args[0], Criteria1=fx.value)
    elif a == "sort":                    # the table at target, header row first, sorted by column args[0]
        r = rng(wb, target)
        col, first, last = args[0], r.Row + 1, r.Row + r.Rows.Count - 1
        _sort(r, r.Worksheet.Range(f"{col}{first}:{col}{last}"), descending=fx.value == "desc", header=True)
    elif a == "sort_column_only":        # the classic mistake: one column sorted, its rows left behind
        r = rng(wb, target)
        _sort(r, r.Columns(1), descending=fx.value == "desc", header=False)
    elif a == "add_sheet":
        wb.Worksheets.Add(None, wb.Worksheets(wb.Worksheets.Count))     # (Before, After): no gap
    elif a == "rename_sheet":
        old, new = fx.value
        wb.Worksheets(old).Name = new
    elif a == "replace":
        what, repl = fx.value
        rng(wb, target).Replace(What=what, Replacement=repl, LookAt=XL_WHOLE, SearchOrder=XL_BY_ROWS, MatchCase=False)
    elif a == "copy_values":
        rng(wb, target).Value2 = rng(wb, args[0]).Value2
    elif a == "copy":
        rng(wb, target).Copy(rng(wb, args[0]))
    elif a == "cut_paste":
        rng(wb, target).Cut(rng(wb, args[0]))
    elif a == "flash_fill":
        rng(wb, target).FlashFill()          # the range must include the typed example cell (verified in Excel)
    elif a == "pick_hint":
        rng(wb, names["picker"]).Value2 = "Show hint"
    elif a == "paste_error":             # an error VALUE, as pasted from elsewhere: typing "=1/0" into a
        scratch = wb.Worksheets(wb.Worksheets.Count).Range("XFD1")   # Text-formatted cell only stores text
        scratch.Formula2 = fx.value
        scratch.Copy()
        rng(wb, target).PasteSpecial(XL_VALUES)
        wb.Application.CutCopyMode = False
        scratch.ClearContents()
    else:
        raise ValueError(f"unknown fixture action {a!r}")


def snapshot(wb, fixtures, names: dict, arena_sheet: str | None) -> list:
    saved = []
    for fx in fixtures:
        if fx.target:
            r = rng(wb, resolve(fx.target, names, arena_sheet))
            saved.append((r, r.Formula2))
    return saved


def restore(saved: list) -> None:
    for r, formula in reversed(saved):
        r.Formula2 = formula


_A1 = re.compile(r"\$?([A-Z]{1,3})\$?(\d+)")


def truth(wb, verify: tuple, *, arena_sheet: str, stage_sheet: str):
    """Ask Excel itself for the answer the shortcut produces."""
    kind, *a = verify
    ws = wb.Worksheets(arena_sheet)
    fn = wb.Application.WorksheetFunction
    if kind == "end":
        return ws.Range(a[0]).End(DIRECTIONS[a[1]]).Value2
    if kind == "end_chain":
        cell = ws.Range(a[0])
        for _ in range(a[2]):
            cell = cell.End(DIRECTIONS[a[1]])
        return cell.Value2
    if kind == "lastcell":
        return ws.Cells.SpecialCells(XL_LAST_CELL).Value2
    if kind == "home":
        return ws.Cells(ws.Range(a[0]).Row, 1).Value2
    if kind == "value_at":
        return ws.Range(a[0]).Value2
    if kind == "name":
        return wb.Names(a[0]).RefersToRange.Value2
    if kind == "pass_code":
        names = [s.Name for s in wb.Worksheets]
        return wb.Worksheets(names[names.index(stage_sheet) + a[0]]).Range("B3").Value2
    if kind == "sum_down":
        start = ws.Range(a[0])
        return fn.Sum(ws.Range(start, start.End(XL_DOWN)))
    if kind == "sum":
        return fn.Sum(ws.Range(a[0]))
    if kind == "counta":
        return fn.CountA(ws.Range(a[0]))
    if kind == "counta_to_last":
        return fn.CountA(ws.Range(ws.Range(a[0]), ws.Cells.SpecialCells(XL_LAST_CELL)))
    if kind == "counta_region":
        return fn.CountA(ws.Range(a[0]).CurrentRegion)
    if kind == "col_sum":
        return fn.Sum(ws.Columns(a[0]))
    if kind == "row_counta":
        return fn.CountA(ws.Rows(a[0]))
    if kind == "nonformula_in":          # late-bound Range.Address is a plain string; GetAddress takes arguments
        return next(c.GetAddress(False, False) for c in ws.Range(a[0]) if not c.HasFormula)
    if kind == "formula_ref_outside":
        inside = {c.GetAddress(False, False) for c in ws.Range(a[1])}
        refs = ["".join(m.groups()) for m in _A1.finditer(ws.Range(a[0]).Formula)]
        return next(r for r in refs if r not in inside)
    if kind == "find_offset":            # every argument up to MatchCase, so Excel's remembered options can't leak in
        found = ws.Cells.Find(What=a[0], After=ws.Cells(1, 1), LookIn=XL_VALUES, LookAt=XL_PART,
                              SearchOrder=XL_BY_ROWS, SearchDirection=XL_NEXT, MatchCase=False)
        return ws.Cells(found.Row, found.Column + a[1]).Value2
    if kind == "countif_contains":
        return fn.CountIf(ws.UsedRange, f"*{a[0]}*")
    raise ValueError(f"unknown verify recipe {kind!r}")
