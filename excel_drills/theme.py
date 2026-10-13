"""Design tokens shared by every workbook: fonts, colors, result words and cell formats."""
from __future__ import annotations

FONT_BODY = "Calibri"
FONT_MONO = "Consolas"
FONT_SYMBOL = "Segoe UI Symbol"   # holds ✔ ✘ ★ ☆ (Calibri and Consolas do not)
SIZE_SMALL, SIZE_BODY, SIZE_HEADING, SIZE_TITLE = 11, 12, 14, 20

INK = "#1F2328"
WHITE = "#FFFFFF"
NAVY = "#14213D"
ARCADE_YELLOW = "#FFD60A"
BAND = "#E3E8F4"
INPUT_FILL = "#FFF4CC"
INPUT_BORDER = "#8A6D00"
OK_TEXT, OK_FILL = "#0B6B2B", "#DDF4E4"
BAD_TEXT, BAD_FILL = "#A1121A", "#FCE4E6"
WAIT_TEXT, WAIT_FILL = "#4A4F57", "#F1F3F5"
LOCK_FILL = "#E9ECEF"
HINT_TEXT, HINT_FILL = "#5A3E8A", "#F3EEFC"
KEY_FILL = "#E6ECF5"
MUTED = "#595F69"
LINK = "#0B4FA8"

TAB_COLORS = {"S": "#2F6FDE", "F": "#C2185B", "FINAL": "#B8860B", "DECK": "#2E7D32", "HUB": NAVY}

# Result vocabulary: a symbol and a word, so color is never the only signal.
OK = "✔ CLEAR"
OK_SELF = "✔ CLEAR · self-check"
BAD = "✘ TRY AGAIN"
TYPED = "✘ That's a typed value · enter a formula"
NOT_YET = "· not yet"
NOT_YET_F9 = "· not yet · press F9"
LOCKED = "LOCKED"
LOCKED_PROMPT = "LOCKED · earn ★ on every stage to open the Boss gate"
SHOW_HINT = "Show hint"
DONE = "Done"

_TEXT = {"font_name": FONT_BODY, "font_size": SIZE_BODY, "font_color": INK, "valign": "top"}
_INPUT = {"font_name": FONT_MONO, "font_size": SIZE_BODY, "font_color": INK, "bg_color": INPUT_FILL,
          "border": 1, "border_color": INPUT_BORDER, "locked": False, "valign": "top"}

STYLES: dict[str, dict] = {
    "title": {"font_name": FONT_BODY, "font_size": SIZE_TITLE, "bold": True, "font_color": ARCADE_YELLOW,
              "bg_color": NAVY, "valign": "vcenter"},
    "title_fill": {"font_name": FONT_BODY, "font_size": SIZE_TITLE, "font_color": WHITE, "bg_color": NAVY},
    "subtitle": {"font_name": FONT_BODY, "font_size": SIZE_BODY, "italic": True, "font_color": MUTED, "valign": "top"},
    "score": {"font_name": FONT_MONO, "font_size": SIZE_HEADING, "bold": True, "font_color": NAVY,
              "valign": "vcenter", "hidden": True},
    "stars": {"font_name": FONT_SYMBOL, "font_size": SIZE_HEADING, "font_color": NAVY, "valign": "vcenter", "hidden": True},
    "bar": {"font_name": FONT_MONO, "font_size": SIZE_HEADING, "font_color": NAVY, "valign": "vcenter", "hidden": True},
    "banner": {"font_name": FONT_SYMBOL, "font_size": SIZE_BODY, "bold": True, "font_color": OK_TEXT,
               "valign": "vcenter", "hidden": True},
    "band": {"font_name": FONT_BODY, "font_size": SIZE_HEADING, "bold": True, "font_color": NAVY,
             "bg_color": BAND, "valign": "vcenter"},
    "th": {"font_name": FONT_BODY, "font_size": SIZE_BODY, "bold": True, "font_color": WHITE, "bg_color": NAVY,
           "text_wrap": True, "valign": "vcenter"},
    "body": {**_TEXT, "text_wrap": True},
    "body_nowrap": dict(_TEXT),
    "body_center": {**_TEXT, "align": "center"},
    "label": {**_TEXT, "bold": True},
    "muted": {"font_name": FONT_BODY, "font_size": SIZE_SMALL, "italic": True, "font_color": MUTED,
              "text_wrap": True, "valign": "top"},
    "muted_nowrap": {"font_name": FONT_BODY, "font_size": SIZE_SMALL, "italic": True, "font_color": MUTED,
                     "valign": "top"},              # one-line notes that flow across empty cells to the right
    "key": {"font_name": FONT_MONO, "font_size": SIZE_BODY, "bold": True, "font_color": NAVY,
            "bg_color": KEY_FILL, "text_wrap": True, "valign": "top"},
    "input": dict(_INPUT),
    "input_time": {**_INPUT, "num_format": "h:mm AM/PM"},
    "input_date": {**_INPUT, "num_format": "d-mmm-yyyy"},
    "picker": {**_INPUT, "font_name": FONT_BODY, "font_size": SIZE_SMALL},
    "result": {"font_name": FONT_SYMBOL, "font_size": SIZE_BODY, "bold": True, "font_color": WAIT_TEXT,
               "bg_color": WAIT_FILL, "text_wrap": True, "valign": "top", "hidden": True},
    "hint": {"font_name": FONT_BODY, "font_size": SIZE_SMALL, "italic": True, "font_color": HINT_TEXT,
             "bg_color": HINT_FILL, "text_wrap": True, "valign": "top", "hidden": True},
    "xp": {"font_name": FONT_MONO, "font_size": SIZE_BODY, "bold": True, "font_color": NAVY,
           "align": "center", "valign": "top", "hidden": True},
    "calc": {**_TEXT, "text_wrap": True, "hidden": True},
    "calc_center": {**_TEXT, "align": "center", "hidden": True},
    "calc_bold": {**_TEXT, "bold": True, "hidden": True},
    "calc_symbol": {"font_name": FONT_SYMBOL, "font_size": SIZE_BODY, "font_color": NAVY, "valign": "top",
                    "align": "center", "hidden": True},
    "calc_date": {**_TEXT, "num_format": "d-mmm-yyyy", "hidden": True},
    "calc_minutes": {**_TEXT, "num_format": '0" min"', "hidden": True},
    "link": {"font_name": FONT_BODY, "font_size": SIZE_BODY, "font_color": LINK, "underline": 1, "valign": "top"},
    "pass_label": {"font_name": FONT_BODY, "font_size": SIZE_BODY, "bold": True, "font_color": NAVY, "valign": "vcenter"},
    "pass": {"font_name": FONT_MONO, "font_size": SIZE_HEADING, "bold": True, "font_color": NAVY,
             "bg_color": KEY_FILL, "valign": "vcenter"},
    "trophy": {"font_name": FONT_SYMBOL, "font_size": SIZE_HEADING, "bold": True, "font_color": NAVY,
               "valign": "vcenter"},
    "arena": dict(_TEXT),
    "arena_head": {"font_name": FONT_BODY, "font_size": SIZE_BODY, "bold": True, "font_color": WHITE, "bg_color": NAVY},
    "arena_label": {**_TEXT, "bold": True},
    "arena_input": dict(_INPUT),
}

CF_STYLES: dict[str, dict] = {
    "ok": {"font_color": OK_TEXT, "bg_color": OK_FILL},
    "bad": {"font_color": BAD_TEXT, "bg_color": BAD_FILL},
    "locked": {"font_color": WAIT_TEXT, "bg_color": LOCK_FILL},
}


def _luminance(hex_color: str) -> float:
    def channel(c: float) -> float:
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = (int(hex_color.lstrip("#")[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)


def contrast(fg: str, bg: str) -> float:
    """WCAG 2.1 contrast ratio between two #RRGGBB colors."""
    hi, lo = sorted((_luminance(fg), _luminance(bg)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


class Formats:
    """Creates each named style once per workbook (XlsxWriter formats are per-workbook objects)."""

    def __init__(self, workbook):
        self._wb = workbook
        self._cache: dict = {}

    def __call__(self, name: str, **extra):
        key = (name, tuple(sorted(extra.items())))
        if key not in self._cache:
            self._cache[key] = self._wb.add_format({**STYLES[name], **extra})
        return self._cache[key]

    def cf(self, name: str):
        key = ("cf", name)
        if key not in self._cache:
            self._cache[key] = self._wb.add_format(CF_STYLES[name])
        return self._cache[key]
