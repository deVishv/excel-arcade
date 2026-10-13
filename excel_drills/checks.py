"""Check types: each turns a challenge into an Excel verdict formula plus what the Key sheet must hold.

Template placeholders (resolved by refs.resolve at layout time):
  «ans» answer cell · «key» expected value · «key1»…«keyN» per-cell expectations · «keyrow»/«opts» list
  on the Key row · «spill» expected spill anchor · «sheets» sheet count at build · «@B5» arena cell ·
  «#B21» INDIRECT arena cell (survives cut/paste).
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable

from . import theme as T
from .normalize import excel_normalize
from .writer import BUILD_DATE

ERROR_NAMES = ("#NULL!", "#DIV/0!", "#VALUE!", "#REF!", "#NAME?", "#NUM!", "#N/A", "#GETTING_DATA",
               "#SPILL!", "#CONNECT!", "#BLOCKED!", "#UNKNOWN!", "#FIELD!", "#CALC!")
BOUNDARY = ("=", "(", ",", "+", "-", "*", "/", "&", " ", "<", ">", ":", "@", "^")


_CALL = re.compile(r"(?<=[A-Za-z0-9_.])\(")


def q(text: object) -> str:
    """Excel string literal, split into pieces joined with &.

    Pieces stay under Excel's 255-character literal limit, and a function-call pattern such as
    `SEQUENCE(` never sits inside one literal: XlsxWriter's future-function prefixing rewrites
    `NAME(` even inside strings (found in testing: "SEQUENCE(" was stored as "_xlfn.SEQUENCE(").
    """
    raw = str(text)
    pieces: list[str] = []
    for chunk in [raw[i:i + 120] for i in range(0, len(raw), 120)] or [""]:
        first, *rest = _CALL.split(chunk)
        pieces += [first, *("(" + p for p in rest)]
    return "&".join('"' + p.replace('"', '""') + '"' for p in pieces)


def lit(value: object) -> str:
    if isinstance(value, bool):
        raise TypeError("booleans are never literals here; compare against the text TRUE/FALSE")
    if isinstance(value, (int, float)):
        return format(value, ".15g")
    return q(value)


def error_name(cell: str) -> str:
    names = ",".join(q(n) for n in ERROR_NAMES)
    return f'IFERROR(CHOOSE(ERROR.TYPE({cell}),{names}),"an error")'


def uses_fn(cell: str, fn: str) -> str:
    starts = "{" + ",".join(q(c) for c in BOUNDARY) + "}"
    return f"OR(ISNUMBER(FIND({starts}&{q(fn.upper() + '(')},UPPER(FORMULATEXT({cell})))))"


Uses = tuple  # each entry is a function name, or a tuple of names any one of which will do


def uses_all(cell: str, uses: Uses) -> str:
    """TRUE when the formula in `cell` uses every required function (one of each group of alternatives)."""
    parts = [uses_fn(cell, u) if isinstance(u, str) else "OR(" + ",".join(uses_fn(cell, f) for f in u) + ")"
             for u in uses]
    return "AND(" + ",".join(parts) + ")"


def uses_text(uses: Uses) -> str:
    return " and ".join(u if isinstance(u, str) else "/".join(u) for u in uses)


@dataclass(frozen=True)
class CheckFormula:
    template: str
    blank: object
    volatile: bool = False


@dataclass(frozen=True)
class KeyValue:
    """Something the Key sheet stores: a static value, or `template` computing it live (`value` = cached)."""
    value: object
    template: str | None = None
    volatile: bool = False


class Check:
    def key_values(self) -> tuple[KeyValue, ...]:
        return ()

    def variants(self) -> tuple[str, ...]:
        return ()

    def options(self) -> tuple[str, ...]:
        return ()

    def spill(self) -> KeyValue | None:
        return None

    def formula(self) -> CheckFormula:
        raise NotImplementedError


def _guard(body: str) -> str:
    return f"=IFERROR({body},{q(T.BAD)})"


@dataclass(frozen=True)
class Recall(Check):
    accepted: tuple[str, ...]

    def variants(self):
        return self.accepted

    def formula(self):
        norm = excel_normalize("_xlpm.a")
        body = (f'LET(_xlpm.a,«ans»,IF(TRIM(_xlpm.a&"")="","",'
                f"IF(OR({norm}=«keyrow»),{q(T.OK)},{q(T.BAD)})))")
        return CheckFormula(_guard(body), "")


@dataclass(frozen=True)
class Pick(Check):
    choices: tuple[str, ...]
    correct: str

    def __post_init__(self):
        if self.correct not in self.choices or len(set(self.choices)) != len(self.choices):
            raise ValueError(f"bad PICK choices {self.choices} / {self.correct}")

    def key_values(self):
        return (KeyValue(self.correct),)

    def options(self):
        return self.choices

    def formula(self):
        body = f'IF(«ans»&""="","",IF(«ans»&""=«key»&"",{q(T.OK)},{q(T.BAD)}))'
        return CheckFormula(_guard(body), "")


def find_key(answer: object) -> object:
    return answer.upper().replace(" ", "").replace("$", "") if isinstance(answer, str) else answer


@dataclass(frozen=True)
class Find(Check):
    answer: object
    verify: tuple = ()          # test-only recipe: how Excel itself derives the answer

    def key_values(self):
        if isinstance(self.answer, bool):
            raise TypeError("FIND answers are text or numbers")
        return (KeyValue(find_key(self.answer)),)

    def formula(self):
        if isinstance(self.answer, str):
            test = 'SUBSTITUTE(SUBSTITUTE(UPPER(_xlpm.a&"")," ",""),"$","")=«key»'
        else:
            test = 'ABS(IF(ISNUMBER(_xlpm.a),_xlpm.a,VALUE(_xlpm.a&""))-«key»)<=1E-9*MAX(1,ABS(«key»))'
        body = f'LET(_xlpm.a,«ans»,IF(TRIM(_xlpm.a&"")="","",IF({test},{q(T.OK)},{q(T.BAD)})))'
        return CheckFormula(_guard(body), "")


def _expected(expect: object, formula: str, volatile: bool = False) -> KeyValue:
    if not formula.startswith("="):
        raise ValueError(f"expected-value formula must start with '=': {formula!r}")
    if isinstance(expect, bool):
        return KeyValue("TRUE" if expect else "FALSE", f'=IF({formula[1:]},"TRUE","FALSE")', volatile)
    return KeyValue(expect, formula, volatile)


def _eq(cell: str, key: str, expect: object, case_sensitive: bool) -> str:
    if isinstance(expect, bool):
        return f'AND(ISLOGICAL({cell}),{cell}=({key}="TRUE"))'
    if isinstance(expect, (int, float)):
        return f"AND(ISNUMBER({cell}),ABS({cell}-{key})<=1E-9*MAX(1,ABS({key})))"
    if case_sensitive:
        return f"AND(ISTEXT({cell}),EXACT({cell},{key}))"
    return f"AND(ISTEXT({cell}),{cell}={key})"


def verdict(cells: list[str], keys: list[str], expects: list[object], *, uses=(), contains=(),
            dollar=False, case_sensitive=False) -> str:
    first, single = cells[0], len(cells) == 1
    blank = f"ISBLANK({first})" if single else f"COUNTA({','.join(cells)})=0"
    typed = f"NOT(ISFORMULA({first}))" if single else "OR(" + ",".join(f"NOT(ISFORMULA({c}))" for c in cells) + ")"
    typed_msg = q(T.TYPED) if single else q("✘ Some cells aren't formulas yet")
    has_error = f"ISERROR({first})" if single else "OR(" + ",".join(f"ISERROR({c})" for c in cells) + ")"
    error_msg = (q("✘ Your formula returns ") + "&" + error_name(first)) if single else q("✘ Some cells show an error")
    value_ok = "AND(" + ",".join(f"IFERROR({_eq(c, k, e, case_sensitive)},FALSE)"
                                 for c, k, e in zip(cells, keys, expects)) + ")"
    tail = q(T.OK)
    if dollar:
        tail = f'IF(ISNUMBER(FIND("$",FORMULATEXT({first}))),{tail},{q("✘ CLOSE · add $ so it fills correctly (F4)")})'
    for text in reversed(tuple(contains)):
        tail = f"IF(ISNUMBER(FIND({q(text)},FORMULATEXT({first}))),{tail},{q('✘ CLOSE · your formula needs ' + text)})"
    if uses:
        tail = f"IF({uses_all(first, uses)},{tail},{q('✘ CLOSE · right value, but use ' + uses_text(uses))})"
    return (f'=IF({blank},"",IF({typed},{typed_msg},IF({has_error},{error_msg},'
            f"IF(NOT({value_ok}),{q(T.BAD)},{tail}))))")


@dataclass(frozen=True)
class Value(Check):
    cell: str
    expect: object
    expect_formula: str
    uses: Uses = ()
    contains: tuple[str, ...] = ()
    dollar: bool = False
    case_sensitive: bool = False
    volatile: bool = False

    def key_values(self):
        return (_expected(self.expect, self.expect_formula, self.volatile),)

    def formula(self):
        t = verdict([f"«@{self.cell}»"], ["«key»"], [self.expect], uses=self.uses, contains=self.contains,
                    dollar=self.dollar, case_sensitive=self.case_sensitive)
        return CheckFormula(t, "", self.volatile)


@dataclass(frozen=True)
class Filled(Check):
    cells: tuple[str, ...]
    expects: tuple[object, ...]
    expect_formulas: tuple[str, ...]
    uses: Uses = ()
    contains: tuple[str, ...] = ()
    dollar: bool = False
    case_sensitive: bool = False

    def __post_init__(self):
        if not (len(self.cells) == len(self.expects) == len(self.expect_formulas) >= 2):
            raise ValueError("Filled needs ≥2 cells with one expectation each")

    def key_values(self):
        return tuple(_expected(e, f) for e, f in zip(self.expects, self.expect_formulas))

    def formula(self):
        cells = [f"«@{c}»" for c in self.cells]
        keys = [f"«key{i + 1}»" for i in range(len(self.cells))]
        t = verdict(cells, keys, list(self.expects), uses=self.uses, contains=self.contains,
                    dollar=self.dollar, case_sensitive=self.case_sensitive)
        return CheckFormula(t, "")


@dataclass(frozen=True)
class Spill(Check):
    anchor: str
    expect: tuple[tuple[object, ...], ...]
    expect_formula: str
    uses: Uses = ()

    def spill(self):
        return KeyValue(self.expect[0][0], self.expect_formula)

    def formula(self):
        a = f"«@{self.anchor}»"
        A, K = f"ANCHORARRAY({a})", "ANCHORARRAY(«spill»)"
        same = (f"IFERROR(AND(ROWS({A})=ROWS({K}),COLUMNS({A})=COLUMNS({K}),"
                f"SUM(--({A}={K}))=ROWS({K})*COLUMNS({K})),FALSE)")
        ok = q(T.OK)
        if self.uses:
            ok = f"IF({uses_all(a, self.uses)},{ok},{q('✘ CLOSE · right result, but use ' + uses_text(self.uses))})"
        t = (f'=IF(ISBLANK({a}),"",IF(NOT(ISFORMULA({a})),{q(T.TYPED)},'
             f"IF(ISERROR({a}),{q('✘ Your formula returns ')}&{error_name(a)},IF({same},{ok},{q(T.BAD)}))))")
        return CheckFormula(t, "")


@dataclass(frozen=True)
class Condition(Check):
    """DO mission: ✔ when the condition holds, otherwise '· not yet' (a workbook can't tell untouched from wrong)."""
    condition: str
    f9: bool = False            # formatting/hiding/structure drills: Excel may not recalc until F9
    volatile: bool = False      # result depends on today's date (TODAY/NOW)

    def formula(self):
        wait = T.NOT_YET_F9 if self.f9 else T.NOT_YET
        return CheckFormula(f"=IF(IFERROR({self.condition},FALSE),{q(T.OK)},{q(wait)})", wait, self.volatile)


@dataclass(frozen=True)
class SelfCheck(Check):
    def options(self):
        return (T.DONE,)

    def formula(self):
        return CheckFormula(_guard(f'IF(«ans»={q(T.DONE)},{q(T.OK_SELF)},"")'), "")


# ---- condition helpers (Excel boolean expressions) -------------------------------------------------

def at(addr: str) -> str:
    return f"«@{addr}»"


def _split_range(rng: str) -> tuple[str, int, int]:
    m = re.fullmatch(r"([A-Z]+)(\d+):\1(\d+)", rng.upper())
    if not m:
        raise ValueError(f"need a one-column range like C5:C14, got {rng!r}")
    return m.group(1), int(m.group(2)), int(m.group(3))


def all_equal(addrs: Iterable[str], value: object) -> str:
    return "AND(" + ",".join(f"{at(a)}={lit(value)}" for a in addrs) + ")"


def cells_equal(expected: dict[str, object]) -> str:
    return "AND(" + ",".join(f"{at(a)}={lit(v)}" for a, v in expected.items()) + ")"


def values_not_formulas(expected: dict[str, object]) -> str:
    return "AND(" + ",".join(f"NOT(ISFORMULA({at(a)})),{at(a)}={lit(v)}" for a, v in expected.items()) + ")"


def line_break(addr: str, first: str, second: str) -> str:
    return f"EXACT({at(addr)},{q(first)}&CHAR(10)&{q(second)})"


def today_constant(addr: str) -> str:
    """A whole-day date constant (what Ctrl+; types) from the build date up to today.

    Comparing with TODAY() alone would take the ✔ away the next day; the lower bound keeps
    small numbers such as 5 from passing as dates.
    """
    c = at(addr)
    built = f"DATE({BUILD_DATE.year},{BUILD_DATE.month},{BUILD_DATE.day})"
    return f"AND(ISNUMBER({c}),NOT(ISFORMULA({c})),{c}=INT({c}),{c}>={built},{c}<=TODAY())"


def time_constant(addr: str) -> str:
    c = at(addr)
    return f"AND(ISNUMBER({c}),NOT(ISFORMULA({c})),{c}>0,{c}<1)"


def format_in(addrs: Iterable[str], codes: Iterable[str]) -> str:
    codes = list(codes)
    return "AND(" + ",".join(
        "OR(" + ",".join(f'CELL("format",{at(a)})={q(code)}' for code in codes) + ")" for a in addrs) + ")"


def prefix_is(addrs: Iterable[str], prefix: str = "^") -> str:
    return "AND(" + ",".join(f'CELL("prefix",{at(a)})={q(prefix)}' for a in addrs) + ")"


def column_hidden(addr: str) -> str:
    # CELL("width") returns two items (width, is-default) in Excel 365; take the width so the check can't spill
    return f'INDEX(CELL("width",{at(addr)}),1)=0'


def visible_label_count(rng: str, label: str) -> str:
    col, top, _ = _split_range(rng)
    first = f"{col}{top}"
    return (f"SUMPRODUCT(SUBTOTAL(103,OFFSET({at(first)},ROW({at(rng)})-ROW({at(first)}),0))"
            f"*({at(rng)}={q(label)}))")


def visible_count(rng: str) -> str:
    return f"SUBTOTAL(103,{at(rng)})"


def visible_other_than(rng: str, value: str) -> str:
    col, top, _ = _split_range(rng)
    first = f"{col}{top}"
    return (f"SUMPRODUCT(SUBTOTAL(103,OFFSET({at(first)},ROW({at(rng)})-ROW({at(first)}),0))"
            f"*({at(rng)}<>{q(value)}))")


def _pairs(rng: str) -> tuple[str, str]:
    col, top, bottom = _split_range(rng)
    return f"{col}{top}:{col}{bottom - 1}", f"{col}{top + 1}:{col}{bottom}"


def ascending(rng: str) -> str:
    a, b = _pairs(rng)
    return f"SUMPRODUCT(--({at(a)}>{at(b)}))=0"


def descending(rng: str) -> str:
    a, b = _pairs(rng)
    return f"SUMPRODUCT(--({at(a)}<{at(b)}))=0"


def pairs_intact(id_rng: str, val_rng: str, pairs: dict[str, object]) -> str:
    ids = "{" + ",".join(lit(k) for k in pairs) + "}"
    vals = "{" + ",".join(lit(v) for v in pairs.values()) + "}"
    return f"SUMPRODUCT(--(XLOOKUP({at(id_rng)},{ids},{vals})={at(val_rng)}))={len(pairs)}"


def count_is(rng: str, value: object, n: int) -> str:
    return f"COUNTIF({at(rng)},{lit(value)})={n}"


def sheet_exists(name: str) -> str:
    return f"ISREF(INDIRECT({q(chr(39) + name + chr(39) + '!A1')}))"


def sheets_more_than(_: object = None) -> str:
    return "SHEETS()>«sheets»"


def marker_gap(col: str, upper: str, lower: str, gap: int) -> str:
    whole = at(f"{col}:{col}")
    return f"MATCH({q(lower)},{whole},0)-MATCH({q(upper)},{whole},0)={gap}"
