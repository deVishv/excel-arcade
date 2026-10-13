"""Formulas 1 · Formula Basics — write your first formulas and make them fill down correctly."""
from ..model import Arena, Boss, Formula, Item, Stage, World, column, filled, find, formula, merge, row, table
from .datasets import xl_round


def _r(cell: str) -> int:
    return int("".join(ch for ch in cell if ch.isdigit()))


# ------------------------------------------------------------------------------------ F1-1 Power Up
ITEMS_1 = (
    Item("F1.equals", "concept", "=", "Every formula starts with an equals sign.",
         "Without =, Excel stores what you typed as plain text.", "Which character must every formula start with?",
         ("=", "equals", "equal sign", "equals sign"), "The key left of Backspace."),
    Item("F1.operators", "concept", "+ - * / ^", "Arithmetic: add, subtract, multiply, divide, power.",
         "* multiplies, / divides, ^ raises to a power (2^3 = 8).", "Which operator raises a number to a power?",
         ("^", "caret"), "Shift+6 on a US keyboard."),
    Item("F1.precedence", "concept", "( ) first", "Order: parentheses, then ^, then * and /, then + and -.",
         "=2+3*4 is 14, but =(2+3)*4 is 20.", "What does =2+3*4 return?", ("14",), "Multiply before you add."),
    Item("F1.cellref", "concept", "=B2*C2", "Point at cells instead of typing numbers.",
         "Change B2 and the result updates by itself.", "Type the formula that multiplies cell B2 by cell C2.",
         ("=B2*C2", "=C2*B2", "B2*C2", "C2*B2"), "Start with = then the two cell addresses."),
)
ARENA_1 = Arena(
    cells=merge(
        table("B5", ["Item", "Price", "Qty"], [["Pens", 2.5, 4], ["Pads", 3, 6], ["Tape", 1.75, 8], ["Clips", 0.5, 20]]),
        {"E5": "Your answers ▼", "E6": "Pens: Price × Qty", "E7": "Pads: (Price + 3) × Qty", "E8": "Tape: Qty squared",
         "E9": "Scratch pad"},
    ),
    pass_code="IGNITE", inputs=("F6:F9",), headers=("B5:D5",), labels=("E5",), widths={"E": 26},
)
MISSIONS_1 = (
    formula("F1-1.M1", "In the arena, select F6 and type a formula that multiplies the Price of Pens (C6) by its "
                       "Qty (D6). Press Enter.", "Type =C6*D6.", "F6", "=C6*D6", 10,
            items=("F1.equals", "F1.cellref"), wrong=("=C6+D6", 10)),
    formula("F1-1.M2", "In F7, add 3 to the Price of Pads (C7), then multiply by its Qty (D7). Use parentheses so "
                       "the addition happens first.", "Wrap the addition in ( ).", "F7", "=(C7+3)*D7", 36,
            items=("F1.precedence",), wrong=("=C7+3*D7",)),
    formula("F1-1.M3", "In F8, raise the Qty of Tape (D8) to the power of 2 using ^.", "Type =D8^2.", "F8", "=D8^2",
            64, items=("F1.operators",), wrong=("=D8*2",), contains=("^",)),
    find("F1-1.M4", "Work it out first, then test it in F9 if you like: what does =10-2*3 return? Type the number.",
         "Multiply first: 2*3 = 6.", 4, items=("F1.precedence",), wrong=(24,)),
)
STAGE_1 = Stage("F1-1", "Power Up", "write formulas that calculate from cells", ITEMS_1, MISSIONS_1, ARENA_1)

# ------------------------------------------------------------------------------------ F1-2 Big Six
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
SALES = [420, 515, 380, 610, 450, 555, 700, 640, 480, 530, 690, 720]
RETURNS = [3, 5, "n/a", 2, 4, 6, "n/a", 1, 0, 2, 3, 5]
ITEMS_2 = (
    Item("F1.sum", "function", "SUM", "Add up numbers: =SUM(B2:B10).", "A range is first:last joined by a colon.",
         "Which function adds up a range of numbers?", ("SUM",), "Three letters."),
    Item("F1.average", "function", "AVERAGE", "The mean of the numbers in a range.",
         "Blank cells and text are skipped, not counted as 0.", "Which function returns the mean of a range?",
         ("AVERAGE",), "Starts with AVER."),
    Item("F1.max", "function", "MAX", "The largest number in a range.", "Pair it with MIN to see the spread.",
         "Which function returns the largest number in a range?", ("MAX",), "Short for maximum."),
    Item("F1.min", "function", "MIN", "The smallest number in a range.", "Text such as n/a is ignored.",
         "Which function returns the smallest number in a range?", ("MIN",), "Short for minimum."),
    Item("F1.count", "function", "COUNT", "Count the cells that hold numbers.",
         "Text doesn't count: use COUNTA for any filled cell.", "Which function counts only the cells that hold numbers?",
         ("COUNT",), "The plain counting function."),
    Item("F1.counta", "function", "COUNTA", "Count the cells that are not empty (numbers, text, anything).",
         "The A stands for 'all'.", "Which function counts every non-empty cell?", ("COUNTA",), "COUNT plus one letter."),
    Item("F1.autosum", "shortcut", "Alt+=", "AutoSum: insert =SUM() over the numbers above or to the left.",
         "Select the cell under a column of numbers, press Alt+=, then Enter.", "Which keys insert an AutoSum formula?",
         ("Alt+=",), "Alt plus the equals key."),
)
ARENA_2 = Arena(
    cells=merge(
        table("B5", ["Month", "Sales", "Returns"], [[m, s, r] for m, s, r in zip(MONTHS, SALES, RETURNS)]),
        {"B18": "TOTAL ▶"},
        {"F5": "Your answers ▼", "F6": "Average sales", "F7": "Best month", "F8": "Worst month",
         "F9": "Returns that are numbers", "F10": "Filled Returns cells"},
    ),
    pass_code="TALLY", inputs=("C18", "G6:G10"), headers=("B5:D5",), labels=("B18", "F5"), widths={"F": 26},
)
MISSIONS_2 = (
    formula("F1-2.M1", "In the arena, select C18 (just under Sales) and press Alt+= then Enter. AutoSum writes the "
                       "SUM formula for you.", "Alt and = together.", "C18", "=SUM(C6:C17)", sum(SALES),
            items=("F1.sum", "F1.autosum"), wrong=("=C6+C7",), uses=("SUM",)),
    formula("F1-2.M2", "In G6, find the average monthly Sales with AVERAGE.", "=AVERAGE(C6:C17)", "G6",
            "=AVERAGE(C6:C17)", sum(SALES) / len(SALES), items=("F1.average",), wrong=("=SUM(C6:C17)/10",),
            uses=("AVERAGE",)),
    formula("F1-2.M3", "In G7, find the best month's Sales with MAX.", "=MAX(C6:C17)", "G7", "=MAX(C6:C17)",
            max(SALES), items=("F1.max",), wrong=("=MIN(C6:C17)",), uses=("MAX",)),
    formula("F1-2.M4", "In G8, find the worst month's Sales with MIN.", "=MIN(C6:C17)", "G8", "=MIN(C6:C17)",
            min(SALES), items=("F1.min",), wrong=("=MAX(C6:C17)",), uses=("MIN",)),
    formula("F1-2.M5", "In G9, count how many Returns cells (D6:D17) hold numbers. Use COUNT.", "COUNT skips n/a.",
            "G9", "=COUNT(D6:D17)", sum(isinstance(r, int) for r in RETURNS), items=("F1.count",),
            wrong=("=COUNTA(D6:D17)",), uses=("COUNT",)),
    formula("F1-2.M6", "In G10, count every filled Returns cell, text included. Use COUNTA.", "COUNTA counts text too.",
            "G10", "=COUNTA(D6:D17)", len(RETURNS), items=("F1.counta",), wrong=("=COUNT(D6:D17)",),
            uses=("COUNTA",)),
)
STAGE_2 = Stage("F1-2", "Big Six", "summarize a column with six core functions", ITEMS_2, MISSIONS_2, ARENA_2)

# ------------------------------------------------------------------------------------ F1-3 Anchors
TAX_PRICES = [20, 35, 12.5, 80, 46, 9.99, 150, 64]
DISCOUNT_PRICES = [40, 25, 60, 15, 90]
ITEMS_3 = (
    Item("F1.absolute", "concept", "$A$1", "An absolute reference never shifts when the formula is copied.",
         "Use it for one fixed cell that every row needs, like a tax rate.",
         "Type the absolute version of the reference E6.", ("$E$6",), "Put $ before the column and the row."),
    Item("F1.mixed", "concept", "$A1 / A$1", "Mixed reference: lock only the column ($A1) or only the row (A$1).",
         "Perfect for grids where one side stays fixed.", "Type a reference to C16 that locks only the row.",
         ("C$16",), "The $ goes right before 16."),
    Item("F1.f4", "shortcut", "F4", "While editing a reference, cycle A1 → $A$1 → A$1 → $A1.",
         "Click inside the reference in the formula, then tap F4.",
         "Which key adds or cycles the $ signs on a reference you are editing?", ("F4",),
         "A function key between F3 and F5."),
    Item("F1.ctrl_d", "shortcut", "Ctrl+D", "Fill Down: copy the top cell into the selected cells below.",
         "Select the formula cell plus the cells under it, then press Ctrl+D.",
         "Which keys copy the top cell down into the selected cells?", ("Ctrl+D",), "D for Down."),
)
ARENA_3 = Arena(
    cells=merge(
        table("B5", ["Price", "Tax"], [[p, None] for p in TAX_PRICES]),
        {"E5": "Tax rate", "E6": 0.08},
        {"B16": "Price ↓ · Discount →"}, row("C16", [0.1, 0.2, 0.3]), column("B17", DISCOUNT_PRICES),
    ),
    pass_code="ANCHOR", inputs=("C6:C13", "C17:C21"), headers=("B5:C5",), labels=("E5", "B16"),
    number_formats={"E6": "0%", "C16:E16": "0%"}, widths={"B": 20},
)
MISSIONS_3 = (
    filled("F1-3.M1", "In the arena, select C6 and type =B6*$E$6 (click E6, then press F4 to add the $ signs). "
                      "Then select C6:C13 and press Ctrl+D to fill it down.", "Without $, the rate cell slides down.",
           "C6:C13", lambda c: f"=B{_r(c)}*$E$6", [p * 0.08 for p in TAX_PRICES],
           items=("F1.absolute", "F1.f4", "F1.ctrl_d"), wrong_for=lambda c: f"=B{_r(c)}*E{_r(c)}", dollar=True),
    filled("F1-3.M2", "In C17 type =$B17*(1-C$16): $B locks the price column, $16 locks the discount row. Then "
                      "select C17:C21 and press Ctrl+D.", "Two $ signs, in different places.", "C17:C21",
           lambda c: f"=$B{_r(c)}*(1-C$16)", [p * (1 - 0.1) for p in DISCOUNT_PRICES],
           items=("F1.mixed", "F1.ctrl_d"), wrong_for=lambda c: f"=B{_r(c)}*(1-C{_r(c) - 1})", dollar=True),
)
STAGE_3 = Stage("F1-3", "Anchors", "lock references so formulas fill correctly", ITEMS_3, MISSIONS_3, ARENA_3)

# ------------------------------------------------------------------------------------ F1-4 Precision
ITEMS_4 = (
    Item("F1.round", "function", "ROUND", "Round to a number of digits: =ROUND(3.14159,2) gives 3.14.",
         "Negative digits round to tens or hundreds: =ROUND(1234,-2) is 1200.",
         "Which function rounds a number to a chosen number of digits?", ("ROUND",), "The plain rounding function."),
    Item("F1.roundup", "function", "ROUNDUP", "Always round away from zero: =ROUNDUP(2.1,0) gives 3.",
         "Good for 'how many boxes do I need?'", "Which function always rounds up, away from zero?", ("ROUNDUP",),
         "ROUND plus a direction."),
    Item("F1.rounddown", "function", "ROUNDDOWN", "Always round toward zero: chop off the extra digits.",
         "=ROUNDDOWN(7.86,1) gives 7.8.", "Which function always rounds down, toward zero?", ("ROUNDDOWN",),
         "ROUND plus the other direction."),
)
ARENA_4 = Arena(
    cells=merge(
        table("B5", ["Value"], [[3.14159], [2.4], [7.86], [1234.5]]),
        {"C5": "Do this", "C6": "2 decimals", "C7": "up to a whole number", "C8": "down to 1 decimal",
         "C9": "nearest hundred"},
    ),
    pass_code="DECIMAL", inputs=("D6:D9",), headers=("B5:C5",), widths={"C": 24},
)
MISSIONS_4 = (
    formula("F1-4.M1", "In D6, round B6 to 2 decimals with ROUND.", "=ROUND(B6,2)", "D6", "=ROUND(B6,2)", 3.14,
            items=("F1.round",), wrong=("=ROUND(B6,1)",), uses=("ROUND",)),
    formula("F1-4.M2", "In D7, round B7 UP to a whole number with ROUNDUP.", "0 digits = whole number.", "D7",
            "=ROUNDUP(B7,0)", 3, items=("F1.roundup",), wrong=("=ROUND(B7,0)",), uses=("ROUNDUP",)),
    formula("F1-4.M3", "In D8, round B8 DOWN to 1 decimal with ROUNDDOWN.", "=ROUNDDOWN(B8,1)", "D8",
            "=ROUNDDOWN(B8,1)", 7.8, items=("F1.rounddown",), wrong=("=ROUND(B8,1)",), uses=("ROUNDDOWN",)),
    formula("F1-4.M4", "In D9, round B9 to the nearest hundred with ROUND (use -2 digits).", "Negative digits.",
            "D9", "=ROUND(B9,-2)", 1200, items=("F1.round",), wrong=("=ROUND(B9,2)",), uses=("ROUND",)),
)
STAGE_4 = Stage("F1-4", "Precision", "round numbers exactly the way you want", ITEMS_4, MISSIONS_4, ARENA_4)

# ------------------------------------------------------------------------------------ F1-5 X-Ray
POINTS_5 = {r: Formula(f"=B{r}*10+5", (r - 5) * 10 + 5) for r in range(6, 16)}
POINTS_5[12] = 75                                       # the one typed-over cell (same value as its formula)
ITEMS_5 = (
    Item("F1.show_formulas", "shortcut", "Ctrl+`", "Show formulas instead of results; press again to switch back.",
         "The ` key sits left of 1. Great for spotting typed-over formulas.",
         "Which keys switch between showing results and showing formulas?",
         ("Ctrl+`", "Ctrl+Grave", "Ctrl+Grave accent", "Ctrl+Backtick"), "Ctrl plus the key left of 1."),
    Item("F1.f2", "shortcut", "F2", "Edit the active cell; its references light up in color.",
         "Each colored reference matches a colored box on the sheet.",
         "Which key edits the active cell and color-codes its references?", ("F2",), "The function key after F1."),
    Item("F1.tab_complete", "shortcut", "Tab", "While typing a function, Tab inserts the highlighted suggestion.",
         "Type =SU, arrow down to SUMIFS, press Tab: Excel types SUMIFS( for you.",
         "While typing a function name, which key inserts the highlighted AutoComplete suggestion?", ("Tab",),
         "The key above Caps Lock."),
    Item("F1.ctrl_shift_a", "shortcut", "Ctrl+Shift+A", "After a function name, insert its argument names.",
         "Type =XLOOKUP then Ctrl+Shift+A to see every argument at once.",
         "Which keys insert a function's argument names after you type its name?", ("Ctrl+Shift+A",),
         "Ctrl+Shift plus A for arguments."),
    Item("F1.shift_f3", "shortcut", "Shift+F3", "Open the Insert Function dialog.",
         "Search for a function by describing what you need.", "Which keys open the Insert Function dialog?",
         ("Shift+F3",), "Shift plus F3."),
)
ARENA_5 = Arena(
    cells=merge(
        {"B5": "Day", "C5": "Points"}, column("B6", list(range(1, 11))), {f"C{r}": v for r, v in POINTS_5.items()},
        {"E5": "Total", "E6": Formula("=SUM(C6:C15)+H20", 650)},
        {"H19": "Bonus", "H20": 50},
        {"F8": "Average points", "F9": "Total ÷ 7, 1 decimal"},
    ),
    pass_code="XRAY", inputs=("G8:G9",), headers=("B5:C5", "E5"), labels=("H19",), widths={"F": 22},
)
MISSIONS_5 = (
    find("F1-5.M1", "In the arena press Ctrl+` to show formulas. One cell in C6:C15 is a typed number, not a "
                    "formula. Type its address, then press Ctrl+` again to switch back.",
         "Look for the cell without an = sign.", "C12", items=("F1.show_formulas",), wrong=("C11",),
         verify=("nonformula_in", "C6:C15")),
    find("F1-5.M2", "In the arena select E6 and press F2. Each reference lights up in its own color. One reference "
                    "points outside the Points column: type its address, then press Esc.",
         "It's not in column C.", "H20", items=("F1.f2",), wrong=("C6",),
         verify=("formula_ref_outside", "E6", "C6:C15")),
    formula("F1-5.M3", "In G8 type =AVER, then press Tab when AutoComplete highlights AVERAGE. Finish the formula so "
                       "it averages C6:C15.", "Tab accepts the suggestion.", "G8", "=AVERAGE(C6:C15)", 60,
            items=("F1.tab_complete",), wrong=("=SUM(C6:C15)",), uses=("AVERAGE",)),
    formula("F1-5.M4", "In G9 type =ROUND and press Ctrl+Shift+A: Excel writes ROUND(number,num_digits). Replace the "
                       "argument names so G9 shows E6 divided by 7, rounded to 1 decimal.",
            "number = E6/7, num_digits = 1.", "G9", "=ROUND(E6/7,1)", 92.9, items=("F1.ctrl_shift_a",),
            wrong=("=E6/7",), uses=("ROUND",)),
)
STAGE_5 = Stage("F1-5", "X-Ray", "see inside formulas and write them faster", ITEMS_5, MISSIONS_5, ARENA_5)

# ------------------------------------------------------------------------------------ Boss
SHOP = [["Lamp", 12, 30, 5, 4], ["Mug", 3, 9, 20, 5], ["Desk", 85, 160, 2, "TBD"], ["Chair", 40, 95, 4, 3],
        ["Pen", 0.4, 1.6, 100, 5], ["Book", 6, 18, 12, 4], ["Clock", 10, 25, 6, "TBD"], ["Plant", 4, 11, 9, 2],
        ["Rug", 30, 70, 3, 5], ["Fan", 22, 45, 7, 4]]
DOUBLES = {r: Formula(f"=E{r}*2", SHOP[r - 6][3] * 2) for r in range(6, 16)}
DOUBLES[9] = SHOP[3][3] * 2                              # typed over: Chair's Qty × 2
BOSS_ARENA = Arena(
    cells=merge(
        table("B5", ["Item", "Cost", "Price", "Qty", "Rating"], SHOP),
        {"G5": "Profit", "H5": "Tax", "K5": "Tax rate", "K6": 0.07, "L5": "Double qty"},
        {f"L{r}": v for r, v in DOUBLES.items()},
        {"I8": "Total qty", "I9": "Average price", "I10": "Largest qty", "I11": "Numeric ratings",
         "I12": "Avg price, 1 dp"},
    ),
    pass_code="FORMULON", inputs=("G6:G15", "H6:H15", "J8:J12"), headers=("B5:H5", "K5", "L5"),
    number_formats={"K6": "0%"}, widths={"I": 18},
)
BOSS_MISSIONS = (
    formula("F1-B.M1", "In J8, total the Qty column (E6:E15) with SUM.", "=SUM(E6:E15)", "J8", "=SUM(E6:E15)",
            sum(r[3] for r in SHOP), items=("F1.sum",), wrong=("=E6+E7",), uses=("SUM",)),
    formula("F1-B.M2", "In J9, average the Price column with AVERAGE.", "=AVERAGE(D6:D15)", "J9", "=AVERAGE(D6:D15)",
            sum(r[2] for r in SHOP) / len(SHOP), items=("F1.average",), wrong=("=AVERAGE(C6:C15)",),
            uses=("AVERAGE",)),
    formula("F1-B.M3", "In J10, find the largest Qty with MAX.", "=MAX(E6:E15)", "J10", "=MAX(E6:E15)",
            max(r[3] for r in SHOP), items=("F1.max",), wrong=("=MIN(E6:E15)",), uses=("MAX",)),
    formula("F1-B.M4", "In J11, count the Ratings that are numbers (F6:F15).", "Which function skips TBD?", "J11",
            "=COUNT(F6:F15)", sum(isinstance(r[4], int) for r in SHOP), items=("F1.count",),
            wrong=("=COUNTA(F6:F15)",), uses=("COUNT",)),
    filled("F1-B.M5", "In G6 calculate the profit: (Price - Cost) × Qty. Fill it down to G15 with Ctrl+D.",
           "Parentheses first.", "G6:G15", lambda c: f"=(D{_r(c)}-C{_r(c)})*E{_r(c)}",
           [(r[2] - r[1]) * r[3] for r in SHOP], items=("F1.precedence", "F1.ctrl_d"),
           wrong_for=lambda c: f"=D{_r(c)}-C{_r(c)}*E{_r(c)}"),
    filled("F1-B.M6", "In H6 calculate the tax: Price × the rate in K6. Lock K6 with F4, then fill down to H15.",
           "=D6*$K$6", "H6:H15", lambda c: f"=D{_r(c)}*$K$6", [r[2] * 0.07 for r in SHOP],
           items=("F1.absolute", "F1.f4"), wrong_for=lambda c: f"=D{_r(c)}*K{_r(c)}", dollar=True),
    formula("F1-B.M7", "In J12, average the Price column and round to 1 decimal in one formula.",
            "ROUND around AVERAGE.", "J12", "=ROUND(AVERAGE(D6:D15),1)", xl_round(sum(r[2] for r in SHOP) / 10, 1),
            items=("F1.round", "F1.average"), wrong=("=AVERAGE(D6:D15)",), uses=("ROUND", "AVERAGE")),
    find("F1-B.M8", "Press Ctrl+` in the Boss Arena. One cell in L6:L15 was typed over. Type its address.",
         "No = sign.", "L9", items=("F1.show_formulas",), wrong=("L8",), verify=("nonformula_in", "L6:L15")),
)

WORLD = World(
    code="F1", track="F", order=2, title="Formula Basics",
    tagline="Write your first formulas and make them fill down correctly.",
    file_name="02 Formulas 1 - Formula Basics.xlsx",
    stages=(STAGE_1, STAGE_2, STAGE_3, STAGE_4, STAGE_5),
    boss=Boss(BOSS_MISSIONS, BOSS_ARENA, par_minutes=15),
)
