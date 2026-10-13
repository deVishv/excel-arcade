"""Final Boss · The Championship — three rounds that mix every world in the course."""
import dataclasses
from statistics import mean

from ..checks import all_equal, format_in, line_break, today_constant, visible_count, visible_other_than
from ..model import (Arena, Challenge, FinalBoss, FinalRound, Fixture, column, do, filled, find, formula, merge,
                     self_check, spill, table)
from ..refs import cells_in
from .datasets import ORDER_HEADER, ORDERS, orders_rows, serial, xl_round
from .f6_dates import end_of_month

CURRENCY = ("C2", "C2-")


def _r(cell: str) -> int:
    return int("".join(ch for ch in cell if ch.isdigit()))


def after(prep: tuple, ch: Challenge) -> Challenge:
    """A mission that builds on earlier missions: tests play the prerequisite fixtures first."""
    return dataclasses.replace(ch, solve=prep + ch.solve, wrong=tuple(prep + w for w in ch.wrong))


# ------------------------------------------------------------------------------------ R1 Shortcut Gauntlet
R1_ARENA = Arena(
    cells=merge(
        {"B5": "TRAIL ▼"}, column("B6", list(range(1, 801))), {"B806": "CHAMPION"},
        {"D5": "SCATTER ▼"}, column("D6", list(range(1, 26))), column("D60", list(range(26, 37))), {"D200": "LEGEND"},
        {"F5": "GO ▼", "F14": "TWO LINES ▼", "F16": "DATE ▼", "H5": "SHARES ▼"},
        column("H6", [0.1, 0.25, 0.5, 0.75, 0.9]), {"H500": "VICTORY"},
        table("B810", ["Order", "Region", "Rep", "Units"], [[o.id, o.region, o.rep, o.units] for o in ORDERS]),
        {"J831": "TROPHY"},
    ),
    pass_code="GAUNTLET", inputs=("F6:F12", "F15", "F17"), headers=("B5", "D5", "F5", "H5", "B810:E810"),
    labels=("F14", "F16"), number_formats={"F17": "d-mmm-yyyy"}, widths={"F": 16},
)
R1_MISSIONS = (
    find("R1.M1", "In the R1 Arena click B6 and press Ctrl+↓. Type the word at the end of the trail.", "One press.",
         "CHAMPION", items=("S1.ctrl_arrow",), wrong=("TRAIL",), verify=("end", "B6", "down")),
    find("R1.M2", "Click D6 and keep pressing Ctrl+↓ until you reach a word. Type it.", "Jump the gaps.", "LEGEND",
         items=("S1.ctrl_arrow",), wrong=("SCATTER",), verify=("end_chain", "D6", "down", 4)),
    find("R1.M3", "Press F5 (or Ctrl+G) and go to H500. Type the word there.", "Go To.", "VICTORY",
         items=("S1.goto",), wrong=("LEGEND",), verify=("value_at", "H500")),
    find("R1.M4", "Press Ctrl+End. Type the word in the last used cell.", "Lowest row, rightmost column.", "TROPHY",
         items=("S1.ctrl_end",), wrong=("VICTORY",), verify=("lastcell",)),
    do("R1.M5", "Select F6:F12, type GO and press Ctrl+Enter.", "Ctrl+Enter fills the selection.",
       all_equal(cells_in("F6:F12"), "GO"), solve=[Fixture("type", "«@F6:F12»", "GO")],
       wrong=[[Fixture("type", "«@F6»", "GO")]], items=("S2.ctrl_enter",), arena_cell="F6"),
    do("R1.M6", "In F15 type Excel, press Alt+Enter, type Arcade, then press Enter.", "Alt+Enter.",
       line_break("F15", "Excel", "Arcade"), solve=[Fixture("linebreak", "«@F15»", ("Excel", "Arcade"))],
       wrong=[[Fixture("type", "«@F15»", "Excel Arcade")]], items=("S2.alt_enter",), arena_cell="F15"),
    do("R1.M7", "Stamp today's date in F17 with Ctrl+;, then Enter.", "Ctrl+;", today_constant("F17"),
       solve=[Fixture("today", "«@F17»")], wrong=[[Fixture("formula", "«@F17»", "=TODAY()")]], items=("S2.date",),
       arena_cell="F17", volatile=True),
    do("R1.M8", "Make H6:H10 percentages with Ctrl+Shift+%. Press F9.", "Ctrl+Shift+5.",
       format_in(cells_in("H6:H10"), ("P0",)), solve=[Fixture("number_format", "«@H6:H10»", "0%")],
       wrong=[[Fixture("number_format", "«@H6:H10»", "0.00")]], items=("S3.percent",), arena_cell="H6", f9=True),
    do("R1.M9", "Filter the table at B810 to show only North: Ctrl+Shift+L, then Alt+↓ on the Region header.",
       "Filter buttons first.",
       f'AND({visible_count("C811:C830")}={sum(o.region == "North" for o in ORDERS)},'
       f'{visible_other_than("C811:C830", "North")}=0)',
       solve=[Fixture("autofilter", "«@B810:E830»", "North", (2,))],
       wrong=[[Fixture("autofilter", "«@B810:E830»", "South", (2,))]], items=("S4.filter", "S4.filter_menu"),
       arena_cell="C810"),
)
R1 = FinalRound("R1", "Shortcut Gauntlet", "prove every shortcut is in your fingers", ("shortcut",), R1_MISSIONS,
                R1_ARENA)

# ------------------------------------------------------------------------------------ R2 Formula Gauntlet
REGIONS = [["East", "Mia"], ["West", "Noah"], ["North", "Zoe"], ["South", "Liam"]]
LATEST = max(o.date for o in ORDERS)
R2_ARENA = Arena(
    cells=merge(
        table("B5", ORDER_HEADER, orders_rows()), {"I5": "Flag"},
        table("K5", ["Region", "Manager"], REGIONS),
        {"N6": "West Gadget revenue", "N7": "North orders with 50+ units", "N8": "Manager of South",
         "N9": "East average revenue (rounded)", "N10": "Different products", "N11": "Month-end of the latest order",
         "Q5": "Raj's orders ▼"},
    ),
    pass_code="FORMULAS", inputs=("I6:I25", "O6:O11", "Q6"), headers=("B5:I5", "K5:L5", "Q5"),
    number_formats={"C6:C25": "d-mmm-yy", "O11": "d-mmm-yyyy"}, widths={"C": 11, "N": 30, "O": 14},
)
R2_MISSIONS = (
    formula("R2.M1", "In O6 add the Revenue of West orders for Gadget.", "SUMIFS, sum range first.", "O6",
            '=SUMIFS(H6:H25,D6:D25,"West",F6:F25,"Gadget")',
            sum(o.revenue for o in ORDERS if o.region == "West" and o.product == "Gadget"), items=("F3.sumifs",),
            wrong=('=SUMIF(D6:D25,"West",H6:H25)',), uses=("SUMIFS",)),
    formula("R2.M2", "In O7 count the North orders with at least 50 units.", "COUNTIFS with \">=50\".", "O7",
            '=COUNTIFS(D6:D25,"North",G6:G25,">=50")', sum(o.region == "North" and o.units >= 50 for o in ORDERS),
            items=("F3.countifs", "F3.criteria_ops"), wrong=('=COUNTIFS(D6:D25,"North",G6:G25,">50")',),
            uses=("COUNTIFS",)),
    formula("R2.M3", 'In O8 return the Manager of "South" from the table in K5:L9 with XLOOKUP.',
            'XLOOKUP("South",…).', "O8", '=XLOOKUP("South",K6:K9,L6:L9)', dict(REGIONS)["South"],
            items=("F4.xlookup",), wrong=('=XLOOKUP("West",K6:K9,L6:L9)',), uses=("XLOOKUP",)),
    formula("R2.M4", "In O9 average the East Revenue and round it to a whole number, in one formula.",
            "ROUND(AVERAGEIFS(…),0).", "O9", '=ROUND(AVERAGEIFS(H6:H25,D6:D25,"East"),0)',
            xl_round(mean(o.revenue for o in ORDERS if o.region == "East"), 0), items=("F1.round", "F3.averageifs"),
            wrong=('=AVERAGEIFS(H6:H25,D6:D25,"East")',), uses=("ROUND", "AVERAGEIFS")),
    formula("R2.M5", "In O10 count the different Products with COUNTA and UNIQUE.", "COUNTA(UNIQUE(…)).", "O10",
            "=COUNTA(UNIQUE(F6:F25))", len({o.product for o in ORDERS}), items=("F7.unique",),
            wrong=("=COUNTA(F6:F25)",), uses=("COUNTA", "UNIQUE")),
    formula("R2.M6", "In O11 return the last day of the month of the latest order date (EOMONTH of MAX).",
            "EOMONTH(MAX(C6:C25),0).", "O11", "=EOMONTH(MAX(C6:C25),0)", serial(end_of_month(LATEST)),
            items=("F6.eomonth", "F1.max"), wrong=("=MAX(C6:C25)",), uses=("EOMONTH", "MAX")),
    filled("R2.M7", 'In I6 return "Star" when Units ≥ 50 AND Revenue ≥ 2500, otherwise "-". Fill down to I25.',
           "IF(AND(…)).", "I6:I25", lambda c: f'=IF(AND(G{_r(c)}>=50,H{_r(c)}>=2500),"Star","-")',
           ["Star" if o.units >= 50 and o.revenue >= 2500 else "-" for o in ORDERS], items=("F2.if", "F2.and"),
           wrong_for=lambda c: f'=IF(OR(G{_r(c)}>=50,H{_r(c)}>=2500),"Star","-")', uses=("IF", "AND")),
    spill("R2.M8", "In Q6 spill the Order IDs of Raj's orders with FILTER.", 'FILTER(B6:B25,E6:E25="Raj").', "Q6",
          '=FILTER(B6:B25,E6:E25="Raj")', [[o.id] for o in ORDERS if o.rep == "Raj"], items=("F7.filter",),
          wrong=('=FILTER(B6:B25,E6:E25="Kim")',), uses=("FILTER",)),
)
R2 = FinalRound("R2", "Formula Gauntlet", "answer real questions with the right formula", ("function", "concept"),
                R2_MISSIONS, R2_ARENA)

# ------------------------------------------------------------------------------------ R3 Real-World Mission
RAW = [["  ada  LOVELACE", "E", "1,250"], ["grace HOPPER ", "W", "980"], ["alan turing", "N", "2,400"],
       ["  KATHERINE johnson", "S", "760"], ["tim berners-lee", "E", "1,100"], ["MARGARET hamilton", "W", "3,050"],
       ["linus torvalds ", "N", "640"], ["hedy LAMARR", "E", "1,875"], ["annie easley", "S", "2,200"],
       ["  dorothy vaughan", "W", "450"], ["mary JACKSON", "N", "1,010"], ["joan clarke", "E", "890"]]
CODES = [["E", "East"], ["W", "West"], ["N", "North"], ["S", "South"]]
CODE_NAME = dict(CODES)


def xl_proper(text: str) -> str:
    """Excel's PROPER: a letter is capitalized unless the character before it is a letter."""
    out, prev_letter = [], False
    for ch in text:
        out.append(ch.lower() if prev_letter else ch.upper())
        prev_letter = ch.isalpha()
    return "".join(out)


def clean(name: str) -> str:
    return xl_proper(" ".join(name.split()))


def amount(text: str) -> int:
    return int(text.replace(",", ""))


R3_ARENA = Arena(
    cells=merge(
        table("B5", ["Raw name", "Code", "Amount (text)", "Clean name", "Amount", "Region", "Big?"],
              [[n, c, a, None, None, None, None] for n, c, a in RAW]),
        table("K5", ["Code", "Region"], CODES),
        {"N6": "East total", "Q5": "Regions, A→Z ▼"},
    ),
    pass_code="MISSION", inputs=("E6:H17", "O6", "Q6"), headers=("B5:H5", "K5:L5", "Q5"), labels=("N6",),
    widths={"B": 22, "E": 22, "N": 14},
)
R3_M1 = filled("R3.M1", "Clean the names: in E6 write =PROPER(TRIM(B6)) and fill down to E17.", "TRIM inside PROPER.",
               "E6:E17", lambda c: f"=PROPER(TRIM(B{_r(c)}))", [clean(n) for n, _, _ in RAW],
               items=("F5.proper", "F5.trim"), wrong_for=lambda c: f"=PROPER(B{_r(c)})", uses=("PROPER", "TRIM"),
               case_sensitive=True)
R3_M2 = filled("R3.M2", "Turn the text amounts into numbers: in F6 write =VALUE(D6) and fill down to F17.", "VALUE.",
               "F6:F17", lambda c: f"=VALUE(D{_r(c)})", [amount(a) for _, _, a in RAW], items=("F5.value",),
               wrong_for=lambda c: f"=D{_r(c)}", uses=("VALUE",))
R3_M3 = filled("R3.M3", "Look up each Region name: in G6 write =XLOOKUP(C6,$K$6:$K$9,$L$6:$L$9) and fill down to G17.",
               "Lock the code table with $.", "G6:G17", lambda c: f"=XLOOKUP(C{_r(c)},$K$6:$K$9,$L$6:$L$9)",
               [CODE_NAME[c] for _, c, _ in RAW], items=("F4.xlookup", "F4.lock_ranges"),
               wrong_for=lambda c: f"=XLOOKUP(C{_r(c)},K{_r(c)}:K{_r(c) + 3},L{_r(c)}:L{_r(c) + 3})",
               uses=("XLOOKUP",), dollar=True)
R3_MISSIONS = (
    R3_M1, R3_M2, R3_M3,
    after(R3_M2.solve + R3_M3.solve, formula(
        "R3.M4", 'In O6 total the East amounts from your new columns: =SUMIFS(F6:F17,G6:G17,"East").',
        "Needs the Amount and Region columns first.", "O6", '=SUMIFS(F6:F17,G6:G17,"East")',
        sum(amount(a) for _, c, a in RAW if c == "E"), items=("F3.sumifs",), wrong=('=SUMIFS(F6:F17,G6:G17,"West")',),
        uses=("SUMIFS",), key='=SUMPRODUCT(VALUE(D6:D17)*(C6:C17="E"))')),
    after(R3_M2.solve, filled(
        "R3.M5", 'In H6 flag big orders: "Big" when the Amount (F6) is at least 1000, otherwise empty text. Fill down '
                 "to H17.", 'IF(F6>=1000,"Big","").', "H6:H17", lambda c: f'=IF(F{_r(c)}>=1000,"Big","")',
        ["Big" if amount(a) >= 1000 else "" for _, _, a in RAW], items=("F2.if", "F2.empty_text"),
        wrong_for=lambda c: f'=IF(F{_r(c)}>1000,"Big","No")', uses=("IF",),
        key_for=lambda c: f'=IF(VALUE(D{_r(c)})>=1000,"Big","")')),
    after(R3_M3.solve, spill(
        "R3.M6", "In Q6 spill each Region once, sorted A→Z, from your Region column (G6:G17).", "SORT(UNIQUE(…)).",
        "Q6", "=SORT(UNIQUE(G6:G17))", [[r] for r in sorted({CODE_NAME[c] for _, c, _ in RAW})],
        items=("F7.nesting",), wrong=("=UNIQUE(G6:G17)",), uses=("SORT", "UNIQUE"),
        key="=SORT(UNIQUE(XLOOKUP(C6:C17,K6:K9,L6:L9)))")),
    after(R3_M2.solve, do(
        "R3.M7", "Dress the Amount column F6:F17 as currency with Ctrl+Shift+$. Press F9.", "Ctrl+Shift+4.",
        format_in(cells_in("F6:F17"), CURRENCY), solve=[Fixture("number_format", "«@F6:F17»", "$#,##0.00_);($#,##0.00)")],
        wrong=[[Fixture("number_format", "«@F6:F17»", "0.00")]], items=("S3.currency",), arena_cell="F6", f9=True)),
    self_check("R3.M8", "Click inside the table at B5 and press Ctrl+T, then Enter: your cleaned data becomes an Excel "
                        "Table. Pick Done.", "Ctrl+T.", items=("S4.table",)),
)
R3 = FinalRound("R3", "Real-World Mission", "clean a messy export and report on it", (), R3_MISSIONS, R3_ARENA)

FINAL = FinalBoss(file_name="12 Final Boss - Championship.xlsx", rounds=(R1, R2, R3), par_minutes=45)
