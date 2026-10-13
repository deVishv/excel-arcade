"""Shortcuts 3 · Format — dress numbers, text and cells from the keyboard."""
from ..checks import format_in, prefix_is
from ..model import Arena, Boss, Fixture, Item, Stage, World, do, merge, row, self_check, table
from ..refs import cells_in

CURRENCY, PERCENT, COMMA2, DATE, TIME, GENERAL, ONE_DP = (
    ("C2", "C2-"), ("P0",), (",2",), ("D1", "D4"), ("D7", "D6", "D9", "D8"), ("G",), ("F1", ",1"))


def fmt_do(id, prompt, hint, rng, codes, *, solve_fmt, wrong_fmt, items, wrong_rng=None):
    """A number-format drill: solved by `solve_fmt` on `rng`, rejected with `wrong_fmt`."""
    return do(id, prompt, hint, format_in(cells_in(rng), codes),
              solve=[Fixture("number_format", f"«@{rng}»", solve_fmt)],
              wrong=[[Fixture("number_format", f"«@{wrong_rng or rng}»", wrong_fmt)]],
              items=items, arena_cell=rng.split(":")[0], f9=True)


# ------------------------------------------------------------------------------------ S3-1 Number Skins
ITEMS_1 = (
    Item("S3.currency", "shortcut", "Ctrl+Shift+$", "Currency format with two decimals.",
         "Negative amounts show in parentheses.", "Which keys apply the Currency format?",
         ("Ctrl+Shift+$", "Ctrl+Shift+4"), "Ctrl+Shift plus the dollar key."),
    Item("S3.percent", "shortcut", "Ctrl+Shift+%", "Percent format with no decimals.", "0.25 shows as 25%.",
         "Which keys apply the Percent format?", ("Ctrl+Shift+%", "Ctrl+Shift+5"), "Ctrl+Shift plus the % key."),
    Item("S3.number", "shortcut", "Ctrl+Shift+!", "Number format: two decimals and a thousands separator.",
         "1234567.891 shows as 1,234,567.89.", "Which keys apply the Number format with a thousands separator?",
         ("Ctrl+Shift+!", "Ctrl+Shift+1"), "Ctrl+Shift plus the ! key."),
    Item("S3.date", "shortcut", "Ctrl+Shift+#", "Date format with day, month and year.",
         "Turns a serial number like 46100 into a readable date.", "Which keys apply the Date format?",
         ("Ctrl+Shift+#", "Ctrl+Shift+3"), "Ctrl+Shift plus the # key."),
    Item("S3.time", "shortcut", "Ctrl+Shift+@", "Time format with hours, minutes and AM/PM.", "0.75 shows as 6:00 PM.",
         "Which keys apply the Time format?", ("Ctrl+Shift+@", "Ctrl+Shift+2"), "Ctrl+Shift plus the @ key."),
    Item("S3.general", "shortcut", "Ctrl+Shift+~", "Back to the General format (no special formatting).",
         "Use it to see the raw number behind any format.", "Which keys reset a cell to the General format?",
         ("Ctrl+Shift+~", "Ctrl+Shift+`"), "Ctrl+Shift plus the ~ key."),
)
ARENA_1 = Arena(
    cells=merge(
        table("B5", ["Price", "Share", "Big number", "Date", "Time", "Reset me"], [
            [19.99, 0.25, 1234567.891, 46023, 0.25, 10], [5, 0.5, 98765.4, 46100, 0.5, 20],
            [120.5, 0.125, 1000, 46200, 0.75, 30], [0.75, 0.9, 42, 46300, 0.3333, 40],
            [1499, 0.05, 7, 46388, 0.9, 50]]),
    ),
    pass_code="SKINS", headers=("B5:G5",), number_formats={"G6:G10": "$#,##0.00_);($#,##0.00)"},
    widths={"B:G": 14},
)
MISSIONS_1 = (
    fmt_do("S3-1.M1", "In the arena select B6:B10 and press Ctrl+Shift+$. Then press F9 to check.", "Ctrl+Shift+4.",
           "B6:B10", CURRENCY, solve_fmt="$#,##0.00_);($#,##0.00)", wrong_fmt="0%", items=("S3.currency",)),
    fmt_do("S3-1.M2", "Select C6:C10 and press Ctrl+Shift+%. Then press F9.", "Ctrl+Shift+5.", "C6:C10", PERCENT,
           solve_fmt="0%", wrong_fmt="0.00", items=("S3.percent",)),
    fmt_do("S3-1.M3", "Select D6:D10 and press Ctrl+Shift+!. Then press F9.", "Ctrl+Shift+1.", "D6:D10", COMMA2,
           solve_fmt="#,##0.00", wrong_fmt="0.00", items=("S3.number",)),
    fmt_do("S3-1.M4", "Select E6:E10 and press Ctrl+Shift+#: the numbers become dates. Then press F9.",
           "Ctrl+Shift+3.", "E6:E10", DATE, solve_fmt="d-mmm-yy", wrong_fmt="0", items=("S3.date",)),
    fmt_do("S3-1.M5", "Select F6:F10 and press Ctrl+Shift+@: the fractions become times. Then press F9.",
           "Ctrl+Shift+2.", "F6:F10", TIME, solve_fmt="h:mm AM/PM", wrong_fmt="0.00", items=("S3.time",)),
    fmt_do("S3-1.M6", "G6:G10 are dressed as currency. Select them and press Ctrl+Shift+~ to strip the format. "
                      "Then press F9.", "Ctrl+Shift plus the key left of 1.", "G6:G10", GENERAL,
           solve_fmt="General", wrong_fmt="0%", items=("S3.general",)),
)
STAGE_1 = Stage("S3-1", "Number Skins", "change how numbers look in one keystroke", ITEMS_1, MISSIONS_1, ARENA_1)

# ------------------------------------------------------------------------------------ S3-2 Text Style
ITEMS_2 = (
    Item("S3.bold", "shortcut", "Ctrl+B", "Bold on or off.", "Ctrl+2 does the same.", "Which keys toggle bold?",
         ("Ctrl+B", "Ctrl+2"), "B for Bold."),
    Item("S3.italic", "shortcut", "Ctrl+I", "Italic on or off.", "Ctrl+3 does the same.", "Which keys toggle italic?",
         ("Ctrl+I", "Ctrl+3"), "I for Italic."),
    Item("S3.underline", "shortcut", "Ctrl+U", "Underline on or off.", "Ctrl+4 does the same.",
         "Which keys toggle underline?", ("Ctrl+U", "Ctrl+4"), "U for Underline."),
    Item("S3.strike", "shortcut", "Ctrl+5", "Strikethrough on or off.", "Handy for crossing off done tasks.",
         "Which keys toggle strikethrough?", ("Ctrl+5",), "Ctrl plus a number key."),
)
ARENA_2 = Arena(cells={"B6": "Make me bold", "B7": "Make me italic", "B8": "Underline me", "B9": "Strike me out"},
                pass_code="STYLE", widths={"B": 22})
MISSIONS_2 = (
    self_check("S3-2.M1", "In the arena: make B6 bold (Ctrl+B), B7 italic (Ctrl+I), B8 underlined (Ctrl+U) and B9 "
                          "struck through (Ctrl+5). Then pick Done here.", "Select each cell, then press its keys.",
               items=("S3.bold", "S3.italic", "S3.underline", "S3.strike")),
)
STAGE_2 = Stage("S3-2", "Text Style", "emphasize text without the ribbon", ITEMS_2, MISSIONS_2, ARENA_2)

# ------------------------------------------------------------------------------------ S3-3 Format Power
ITEMS_3 = (
    Item("S3.format_cells", "shortcut", "Ctrl+1", "Open Format Cells: every number, alignment, font and border option.",
         "Ctrl+1 then Tab through the choices.", "Which keys open the Format Cells dialog?", ("Ctrl+1",),
         "Ctrl plus the number 1."),
    Item("S3.border", "shortcut", "Ctrl+Shift+&", "Add an outline border around the selection.",
         "Ctrl+Shift+_ removes it again.", "Which keys add an outline border?", ("Ctrl+Shift+&", "Ctrl+Shift+7"),
         "Ctrl+Shift plus the & key."),
    Item("S3.no_border", "shortcut", "Ctrl+Shift+_", "Remove the outline border from the selection.",
         "Pairs with Ctrl+Shift+&.", "Which keys remove the outline border?", ("Ctrl+Shift+_", "Ctrl+Shift+-"),
         "Ctrl+Shift plus the underscore key."),
    Item("S3.keytips", "shortcut", "Alt", "Show KeyTips: a letter for every ribbon command.",
         "Alt, H opens the Home tab; follow the letters from there.", "Which key shows the ribbon KeyTips?",
         ("Alt", "F10"), "The key next to the spacebar."),
    Item("S3.center", "shortcut", "Alt+H, A, C", "Center the cell contents (KeyTips: Home, Align, Center).",
         "Press the keys one after another, not together.", "Which KeyTips center the selected cells?",
         ("Alt+H, A, C",), "Alt, then H, then A, then C."),
    Item("S3.fill_color", "shortcut", "Alt+H, H", "Open the Fill Color menu (KeyTips: Home, Fill).",
         "Use the arrow keys to pick a color, then Enter.", "Which KeyTips open the Fill Color menu?",
         ("Alt+H, H",), "Alt, then H, then H again."),
    Item("S3.repeat", "shortcut", "F4", "Repeat your last action, like the same format on another cell.",
         "Ctrl+Y repeats too.", "Which key repeats your last action?", ("F4", "Ctrl+Y"), "A function key."),
)
ARENA_3 = Arena(
    cells=merge(
        table("B5", ["1 decimal", "Center me", "Percent ×4", "Box me"],
              [[3.14159, "left", 0.1, "box"], [2.71828, "middle", 0.2, "box"], [1.41421, "right", 0.3, "box"],
               [1.73205, "top", 0.4, "box"]]),
    ),
    pass_code="POWER", headers=("B5:E5",), widths={"B:E": 14},
)
MISSIONS_3 = (
    fmt_do("S3-3.M1", "In the arena select B6:B9, press Ctrl+1, choose Number with 1 decimal place and press Enter. "
                      "Then press F9.", "Number category, Decimal places = 1.", "B6:B9", ONE_DP, solve_fmt="0.0",
           wrong_fmt="0.00", items=("S3.format_cells",)),
    do("S3-3.M2", "Select C6:C9 and press Alt, H, A, C (one after another) to center the text. Then press F9.",
       "Home → Align → Center.", prefix_is(cells_in("C6:C9")), solve=[Fixture("align_center", "«@C6:C9»")],
       wrong=[[Fixture("align_left", "«@C6:C9»")]], items=("S3.center", "S3.keytips"), arena_cell="C6", f9=True),
    fmt_do("S3-3.M3", "Select D6 and press Ctrl+Shift+%. Then click D7 and press F4, click D8 and press F4, click D9 "
                      "and press F4. Then press F9.", "F4 repeats the last format.", "D6:D9", PERCENT, solve_fmt="0%",
           wrong_fmt="0%", wrong_rng="D6", items=("S3.repeat",)),
    self_check("S3-3.M4", "Give E6:E9 an outline border (Ctrl+Shift+&), remove it (Ctrl+Shift+_), add it again, then "
                          "give the cells a yellow fill with Alt, H, H. Pick Done here.", "Borders first, then fill.",
               items=("S3.border", "S3.no_border", "S3.fill_color")),
)
STAGE_3 = Stage("S3-3", "Format Power", "reach every format option from the keyboard", ITEMS_3, MISSIONS_3, ARENA_3)

# ------------------------------------------------------------------------------------ Boss
BOSS_ARENA = Arena(
    cells=merge(table("B5", ["Cost", "Rate", "Day", "Clock", "Raw", "Measure", "Label", "Growth"], [
        [250, 0.15, 46050, 0.375, 99, 2.345, "one", 0.05], [1200.5, 0.4, 46150, 0.6, 55, 9.876, "two", 0.12],
        [75, 0.08, 46250, 0.125, 12, 4.4444, "three", 0.3]])),
    pass_code="RUNWAY", headers=("B5:I5",), number_formats={"F6:F8": "$#,##0.00_);($#,##0.00)"}, widths={"B:I": 13},
)
BOSS_MISSIONS = (
    fmt_do("S3-B.M1", "In the Boss Arena make B6:B8 currency (Ctrl+Shift+$). Press F9.", "Ctrl+Shift+4.", "B6:B8",
           CURRENCY, solve_fmt="$#,##0.00_);($#,##0.00)", wrong_fmt="0.00", items=("S3.currency",)),
    fmt_do("S3-B.M2", "Make C6:C8 percent (Ctrl+Shift+%). Press F9.", "Ctrl+Shift+5.", "C6:C8", PERCENT,
           solve_fmt="0%", wrong_fmt="0.00", items=("S3.percent",)),
    fmt_do("S3-B.M3", "Make D6:D8 dates (Ctrl+Shift+#). Press F9.", "Ctrl+Shift+3.", "D6:D8", DATE,
           solve_fmt="d-mmm-yy", wrong_fmt="0", items=("S3.date",)),
    fmt_do("S3-B.M4", "Make E6:E8 times (Ctrl+Shift+@). Press F9.", "Ctrl+Shift+2.", "E6:E8", TIME,
           solve_fmt="h:mm AM/PM", wrong_fmt="0.00", items=("S3.time",)),
    fmt_do("S3-B.M5", "F6:F8 wear currency. Reset them to General (Ctrl+Shift+~). Press F9.", "Ctrl+Shift+~.",
           "F6:F8", GENERAL, solve_fmt="General", wrong_fmt="0%", items=("S3.general",)),
    fmt_do("S3-B.M6", "Give G6:G8 exactly 1 decimal place through Ctrl+1. Press F9.", "Format Cells → Number.",
           "G6:G8", ONE_DP, solve_fmt="0.0", wrong_fmt="0.000", items=("S3.format_cells",)),
    do("S3-B.M7", "Center H6:H8 with Alt, H, A, C. Press F9.", "KeyTips.", prefix_is(cells_in("H6:H8")),
       solve=[Fixture("align_center", "«@H6:H8»")], wrong=[[Fixture("align_left", "«@H6:H8»")]],
       items=("S3.center",), arena_cell="H6", f9=True),
    fmt_do("S3-B.M8", "Make I6 a percent with Ctrl+Shift+%, then use F4 on I7 and I8. Press F9.", "F4 repeats.",
           "I6:I8", PERCENT, solve_fmt="0%", wrong_fmt="0%", wrong_rng="I6", items=("S3.repeat", "S3.percent")),
)

WORLD = World(
    code="S3", track="S", order=5, title="Format",
    tagline="Dress numbers, text and cells from the keyboard.",
    file_name="05 Shortcuts 3 - Format.xlsx",
    stages=(STAGE_1, STAGE_2, STAGE_3),
    boss=Boss(BOSS_MISSIONS, BOSS_ARENA, par_minutes=8),
)
