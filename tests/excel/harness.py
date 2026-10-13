"""Real-Excel test oracle: our own invisible Excel instance, working on temp copies, never saving."""
from __future__ import annotations

import contextlib
import itertools
import shutil
import tempfile
from pathlib import Path

import pythoncom
import win32com.client as w32

from excel_drills.refs import split_ref

XL_CALC_AUTOMATIC = -4105
_names = itertools.count(1)


def is_error(value) -> bool:
    """pywin32 returns Excel error values as large negative ints (e.g. -2146826246 for #N/A)."""
    return isinstance(value, int) and -2146826300 <= value <= -2146826200


def same(got, expected) -> bool:
    if isinstance(expected, (int, float)) and not isinstance(expected, bool):
        return isinstance(got, (int, float)) and abs(got - expected) <= 1e-9 * max(1, abs(expected))
    if expected == "":
        return got in ("", None)
    return got == expected


class ExcelSession:
    def __init__(self):
        self.xl = None

    def start(self) -> None:
        pythoncom.CoInitialize()
        self.xl = w32.DispatchEx("Excel.Application")     # our own process, never the user's Excel
        self.xl.Visible = False
        self.xl.DisplayAlerts = False
        self.xl.ScreenUpdating = False

    def stop(self) -> None:
        if self.xl is None:
            return
        with contextlib.suppress(Exception):
            while self.xl.Workbooks.Count:
                self.xl.Workbooks(1).Close(SaveChanges=False)
        with contextlib.suppress(Exception):
            self.xl.Quit()
        self.xl = None

    @contextlib.contextmanager
    def open(self, src: Path):
        if self.xl is None:
            self.start()
        tmp = Path(tempfile.mkdtemp(prefix="xltest_"))
        copy = tmp / f"run{next(_names)}.xlsx"          # Excel can't open two files with the same name
        shutil.copy(src, copy)
        try:
            try:
                wb = self.xl.Workbooks.Open(str(copy))
            except Exception:
                self.stop()                               # a failed open can poison the next one
                raise
            try:
                self.xl.Calculation = XL_CALC_AUTOMATIC
                self.xl.CalculateFull()
                yield wb
            finally:
                with contextlib.suppress(Exception):
                    wb.Close(SaveChanges=False)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def calc(self) -> None:
        self.xl.Calculate()


def read(wb, ref: str):
    sheet, addr = split_ref(ref)
    return wb.Worksheets(sheet).Range(addr).Value2


def read_cell(wb, sheet: str, cell: str):
    return wb.Worksheets(sheet).Range(cell).Value2
