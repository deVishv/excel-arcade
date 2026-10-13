"""One normalization rule set for typed answers, shared by Python and the Excel checkers.

Rules are applied in order, after upper-casing. The Excel checker applies the same list as nested
SUBSTITUTE calls, so Python's `normalize` predicts exactly what Excel will compare.
"""
from __future__ import annotations

import re
from itertools import permutations, product

REPLACEMENTS: tuple[tuple[str, str], ...] = (
    (" ", ""),
    ("CONTROL", "CTRL"),
    ("CTL", "CTRL"),
    ("ESCAPE", "ESC"),
    ("RETURN", "ENTER"),
    ("PAGEDOWN", "PGDN"),
    ("PGDOWN", "PGDN"),
    ("PAGEUP", "PGUP"),
    ("ARROWKEYS", "ARROW"),
    ("ARROWKEY", "ARROW"),
    ("ARROWS", "ARROW"),
    ("DOWNARROW", "DOWN"),
    ("UPARROW", "UP"),
    ("LEFTARROW", "LEFT"),
    ("RIGHTARROW", "RIGHT"),
    ("ARROWDOWN", "DOWN"),
    ("ARROWUP", "UP"),
    ("ARROWLEFT", "LEFT"),
    ("ARROWRIGHT", "RIGHT"),
    ("↓", "DOWN"),
    ("↑", "UP"),
    ("←", "LEFT"),
    ("→", "RIGHT"),
    ("SPACEBAR", "SPACE"),
    ("−", "-"),
    ("MINUS", "-"),
    ("PLUS", "+"),
)
MODIFIERS = ("CTRL", "SHIFT", "ALT")
MAX_VARIANTS = 40
_SEPARATORS = ("+", ",", ">", "")
_FUNCTION_NAME = re.compile(r"[A-Z][A-Z0-9.]+")


def normalize(text: object) -> str:
    s = str(text).upper()
    for old, new in REPLACEMENTS:
        s = s.replace(old, new)
    return s


def excel_normalize(ref: str) -> str:
    expr = f"UPPER({ref})"
    for old, new in REPLACEMENTS:
        expr = f'SUBSTITUTE({expr},"{old}","{new}")'
    return expr


def _split_modifiers(norm: str) -> tuple[list[str], str]:
    mods: list[str] = []
    rest = norm
    while True:
        for mod in MODIFIERS:
            if rest.startswith(mod + "+") and len(rest) > len(mod) + 1:
                mods.append(mod)
                rest = rest[len(mod) + 1:]
                break
        else:
            return mods, rest


def _shortcut_variants(answer: str) -> set[str]:
    norm = normalize(answer)
    if "," in norm or ">" in norm:            # KeyTip sequence such as Alt+H, A, C
        head, *tail = re.split(r"[,>]", norm)
        keys = [*head.split("+"), *tail]
        first, rest = keys[0], keys[1:]
        return {first + s1 + s2.join(rest) for s1, s2 in product(_SEPARATORS, repeat=2)}
    mods, key = _split_modifiers(norm)
    if not mods:
        return {norm}
    return {"+".join([*order, key]) for order in permutations(mods)}


def _function_variants(name: str) -> set[str]:
    n = normalize(name)
    return {n, f"={n}", f"{n}()", f"={n}()", f"{n}(", f"={n}("}


def variants(answers: tuple[str, ...], kind: str) -> list[str]:
    out: set[str] = set()
    for answer in answers:
        if kind == "shortcut":
            out |= _shortcut_variants(answer)
        elif kind == "function":
            out |= _function_variants(answer)
        elif kind == "concept":              # an answer that is a function name also accepts =NAME, NAME() …
            out |= _function_variants(answer) if _FUNCTION_NAME.fullmatch(answer) else {normalize(answer)}
        else:
            raise ValueError(f"unknown item kind {kind!r}")
    result = sorted(out)
    if len(result) > MAX_VARIANTS:
        raise ValueError(f"{len(result)} accepted variants exceed {MAX_VARIANTS}: {answers}")
    return result
