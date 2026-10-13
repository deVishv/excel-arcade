"""Formulas 3 · Conditional Math — count, add and average only the rows that match."""
import datetime as dt
from statistics import mean

from ..model import Arena, Boss, Item, Stage, World, formula, merge, table
from .datasets import ORDER_HEADER, ORDERS, orders_rows, serial

START, END = dt.date(2026, 2, 1), dt.date(2026, 3, 31)


def orders_arena(pass_code: str, labels: dict[str, str]) -> Arena:
    """ORDERS in B5:H25, criteria cells in K, mission labels in L and answer cells in M."""
    cells = merge(table("B5", ORDER_HEADER, orders_rows()),
                  {"K5": "Min units", "K6": 40, "K8": "Start", "K9": START, "K10": "End", "K11": END}, labels)
    inputs = tuple(f"M{c[1:]}" for c in labels)
    return Arena(cells=cells, pass_code=pass_code, inputs=inputs, headers=("B5:H5",), labels=("K5", "K8", "K10"),
                 number_formats={"C6:C25": "d-mmm-yy", "K9": "d-mmm-yy", "K11": "d-mmm-yy"},
                 widths={"C": 11, "L": 30})


def east(o):
    return o.region == "East"


# ------------------------------------------------------------------------------------ F3-1 Counters
ITEMS_1 = (
    Item("F3.countif", "function", "COUNTIF", "Count the cells that meet one condition.",
         '=COUNTIF(D6:D25,"East") counts the East rows.', "Which function counts cells that meet one condition?",
         ("COUNTIF",), "COUNT plus IF."),
    Item("F3.criteria_ops", "concept", '">50"', "Put comparison criteria in quotes: \">50\", \"<>East\".",
         "The operator goes inside the quotes with the value.", 'Type the COUNTIF criteria for "greater than 50", '
         "quotes included.", ('">50"',), "Quotes around >50."),
    Item("F3.wildcards", "concept", "* and ?", '* matches any text, ? one character: "G*" = starts with G.',
         'Wildcards work in COUNTIF, SUMIF and their IFS cousins.', "Which wildcard matches any number of characters?",
         ("*", "asterisk"), "Shift+8."),
)
ARENA_1 = orders_arena("COUNTER", {"L6": "East orders", "L7": "Orders over 50 units", "L8": "Products starting with G",
                                   "L9": "Orders not from East"})
MISSIONS_1 = (
    formula("F3-1.M1", 'In M6 count the East orders: =COUNTIF(D6:D25,"East").', "Range first, then the criteria.",
            "M6", '=COUNTIF(D6:D25,"East")', sum(east(o) for o in ORDERS), items=("F3.countif",),
            wrong=('=COUNTIF(D6:D25,"West")',), uses=("COUNTIF",)),
    formula("F3-1.M2", "In M7 count the orders with more than 50 units (G6:G25).", 'Criteria ">50" in quotes.', "M7",
            '=COUNTIF(G6:G25,">50")', sum(o.units > 50 for o in ORDERS), items=("F3.criteria_ops",),
            wrong=('=COUNTIF(G6:G25,">=50")',), uses=(("COUNTIF", "COUNTIFS"),)),
    formula("F3-1.M3", "In M8 count the products (F6:F25) whose name starts with G.", 'Use "G*".', "M8",
            '=COUNTIF(F6:F25,"G*")', sum(o.product.startswith("G") for o in ORDERS), items=("F3.wildcards",),
            wrong=('=COUNTIF(F6:F25,"G")',), uses=(("COUNTIF", "COUNTIFS"),), contains=("*",)),
    formula("F3-1.M4", "In M9 count the orders NOT from East.", 'Criteria "<>East".', "M9",
            '=COUNTIF(D6:D25,"<>East")', sum(not east(o) for o in ORDERS), items=("F3.criteria_ops",),
            wrong=('=COUNTIF(D6:D25,"East")',), uses=(("COUNTIF", "COUNTIFS"),), contains=("<>",)),
)
STAGE_1 = Stage("F3-1", "Counters", "count only the rows you care about", ITEMS_1, MISSIONS_1, ARENA_1)

# ------------------------------------------------------------------------------------ F3-2 Money Bags
ITEMS_2 = (
    Item("F3.sumif", "function", "SUMIF", "Add the values whose row meets one condition.",
         '=SUMIF(D6:D25,"West",H6:H25): test range, criteria, then sum range.',
         "Which function adds values that meet one condition?", ("SUMIF",), "SUM plus IF."),
    Item("F3.averageif", "function", "AVERAGEIF", "Average the values whose row meets one condition.",
         "Same argument order as SUMIF.", "Which function averages values that meet one condition?", ("AVERAGEIF",),
         "AVERAGE plus IF."),
)
ARENA_2 = orders_arena("MONEYBAG", {"L6": "West revenue", "L7": "Kim's average units",
                                    "L8": "Revenue of orders with 40+ units"})
MISSIONS_2 = (
    formula("F3-2.M1", 'In M6 add up the Revenue (H) of the West orders: =SUMIF(D6:D25,"West",H6:H25).',
            "Test range, criteria, sum range.", "M6", '=SUMIF(D6:D25,"West",H6:H25)',
            sum(o.revenue for o in ORDERS if o.region == "West"), items=("F3.sumif",),
            wrong=('=SUMIF(D6:D25,"West",G6:G25)',), uses=("SUMIF",)),
    formula("F3-2.M2", "In M7 average the Units (G) of Kim's orders (Rep in column E).", "AVERAGEIF.", "M7",
            '=AVERAGEIF(E6:E25,"Kim",G6:G25)', mean(o.units for o in ORDERS if o.rep == "Kim"),
            items=("F3.averageif",), wrong=('=AVERAGEIF(E6:E25,"Lee",G6:G25)',), uses=(("AVERAGEIF", "AVERAGEIFS"),)),
    formula("F3-2.M3", "In M8 add up the Revenue of orders with 40 or more Units.", 'Criteria ">=40".', "M8",
            '=SUMIF(G6:G25,">=40",H6:H25)', sum(o.revenue for o in ORDERS if o.units >= 40),
            items=("F3.sumif", "F3.criteria_ops"), wrong=('=SUMIF(G6:G25,">40",H6:H25)',), uses=(("SUMIF", "SUMIFS"),)),
)
STAGE_2 = Stage("F3-2", "Money Bags", "add and average with a condition", ITEMS_2, MISSIONS_2, ARENA_2)

# ------------------------------------------------------------------------------------ F3-3 Multi-Filter
ITEMS_3 = (
    Item("F3.countifs", "function", "COUNTIFS", "Count rows that meet several conditions at once.",
         "Pairs of range + criteria; every pair must match.", "Which function counts rows that meet several "
         "conditions?", ("COUNTIFS",), "COUNTIF plus S."),
    Item("F3.sumifs", "function", "SUMIFS", "Add values whose rows meet several conditions.",
         "The sum range comes FIRST in SUMIFS (last in SUMIF).", "Which function adds values that meet several "
         "conditions?", ("SUMIFS",), "SUMIF plus S."),
    Item("F3.averageifs", "function", "AVERAGEIFS", "Average values whose rows meet several conditions.",
         "Average range first, then range/criteria pairs.", "Which function averages values that meet several "
         "conditions?", ("AVERAGEIFS",), "AVERAGEIF plus S."),
)
ARENA_3 = orders_arena("FILTERS", {"L6": "East orders over 30 units", "L7": "East Widget revenue",
                                   "L8": "Kim's average East revenue"})
MISSIONS_3 = (
    formula("F3-3.M1", "In M6 count the East orders with more than 30 units.", "COUNTIFS with two pairs.", "M6",
            '=COUNTIFS(D6:D25,"East",G6:G25,">30")', sum(east(o) and o.units > 30 for o in ORDERS),
            items=("F3.countifs",), wrong=('=COUNTIF(D6:D25,"East")',), uses=("COUNTIFS",)),
    formula("F3-3.M2", "In M7 add the Revenue of East orders for Widget.", "Sum range first in SUMIFS.", "M7",
            '=SUMIFS(H6:H25,D6:D25,"East",F6:F25,"Widget")',
            sum(o.revenue for o in ORDERS if east(o) and o.product == "Widget"), items=("F3.sumifs",),
            wrong=('=SUMIFS(H6:H25,D6:D25,"East")',), uses=("SUMIFS",)),
    formula("F3-3.M3", "In M8 average the Revenue of Kim's East orders.", "AVERAGEIFS.", "M8",
            '=AVERAGEIFS(H6:H25,E6:E25,"Kim",D6:D25,"East")',
            mean(o.revenue for o in ORDERS if o.rep == "Kim" and east(o)), items=("F3.averageifs",),
            wrong=('=AVERAGEIFS(H6:H25,E6:E25,"Kim")',), uses=("AVERAGEIFS",)),
)
STAGE_3 = Stage("F3-3", "Multi-Filter", "stack several conditions", ITEMS_3, MISSIONS_3, ARENA_3)

# ------------------------------------------------------------------------------------ F3-4 Extremes
ITEMS_4 = (
    Item("F3.maxifs", "function", "MAXIFS", "The largest value whose row meets your conditions.",
         "Max range first, then range/criteria pairs.", "Which function returns the largest value that meets "
         "conditions?", ("MAXIFS",), "MAX plus IFS."),
    Item("F3.minifs", "function", "MINIFS", "The smallest value whose row meets your conditions.",
         "Same layout as MAXIFS.", "Which function returns the smallest value that meets conditions?", ("MINIFS",),
         "MIN plus IFS."),
    Item("F3.cell_criteria", "concept", '">="&K6', 'Join an operator to a cell with &: ">="&K6.',
         "Change K6 and the result follows.", 'Which character joins ">=" to a cell reference in criteria?',
         ("&", "ampersand"), "Shift+7."),
    Item("F3.date_range", "concept", "start/end pairs", "Dates between two days: one criteria pair for >= start, one "
         "for <= end.", 'SUMIFS(H6:H25,C6:C25,">="&K9,C6:C25,"<="&K11)', "How many range/criteria pairs do you need "
         "for 'dates between a start and an end'?", ("2", "two"), "One pair per edge."),
)
ARENA_4 = orders_arena("EXTREMES", {"L6": "Biggest East revenue", "L7": "Fewest Widget units",
                                    "L8": "Orders with units ≥ K6", "L9": "Revenue between K9 and K11"})
MISSIONS_4 = (
    formula("F3-4.M1", "In M6 find the largest East Revenue with MAXIFS.", "MAXIFS(H6:H25,D6:D25,\"East\")", "M6",
            '=MAXIFS(H6:H25,D6:D25,"East")', max(o.revenue for o in ORDERS if east(o)), items=("F3.maxifs",),
            wrong=("=MAX(H6:H25)",), uses=("MAXIFS",)),
    formula("F3-4.M2", "In M7 find the fewest Units in any Widget order with MINIFS.", "MINIFS.", "M7",
            '=MINIFS(G6:G25,F6:F25,"Widget")', min(o.units for o in ORDERS if o.product == "Widget"),
            items=("F3.minifs",), wrong=("=MIN(G6:G25)",), uses=("MINIFS",)),
    formula("F3-4.M3", 'In M8 count the orders whose Units are at least the number in K6. Build the criteria with '
                       '">="&K6.', "Join with &.", "M8", '=COUNTIF(G6:G25,">="&K6)', sum(o.units >= 40 for o in ORDERS),
            items=("F3.cell_criteria",), wrong=('=COUNTIF(G6:G25,">=K6")',), uses=(("COUNTIF", "COUNTIFS"),), contains=("&",)),
    formula("F3-4.M4", "In M9 add the Revenue of orders dated from K9 to K11 (both included). Use SUMIFS with two "
                       "date pairs.", 'C6:C25,">="&K9 and C6:C25,"<="&K11.', "M9",
            '=SUMIFS(H6:H25,C6:C25,">="&K9,C6:C25,"<="&K11)',
            sum(o.revenue for o in ORDERS if START <= o.date <= END), items=("F3.date_range", "F3.sumifs"),
            wrong=('=SUMIFS(H6:H25,C6:C25,">="&K9)',), uses=("SUMIFS",), contains=("&",)),
)
STAGE_4 = Stage("F3-4", "Extremes", "find highs, lows and date windows", ITEMS_4, MISSIONS_4, ARENA_4)

# ------------------------------------------------------------------------------------ Boss
BOSS_ARENA = orders_arena("CONDOR", {"L6": "North orders", "L7": "Gadget revenue", "L8": "Lee's average units",
                                     "L9": "South orders over 20 units", "L10": "Revenue: Raj + Gizmo",
                                     "L11": "Smallest East units", "L12": "Orders with units ≥ K6",
                                     "L13": "Revenue between K9 and K11"})
BOSS_MISSIONS = (
    formula("F3-B.M1", "In M6 count the North orders.", "COUNTIF.", "M6", '=COUNTIF(D6:D25,"North")',
            sum(o.region == "North" for o in ORDERS), items=("F3.countif",), wrong=('=COUNTIF(D6:D25,"East")',),
            uses=(("COUNTIF", "COUNTIFS"),)),
    formula("F3-B.M2", "In M7 add the Revenue of all Gadget orders.", "SUMIF.", "M7", '=SUMIF(F6:F25,"Gadget",H6:H25)',
            sum(o.revenue for o in ORDERS if o.product == "Gadget"), items=("F3.sumif",),
            wrong=('=SUMIF(F6:F25,"Gizmo",H6:H25)',), uses=(("SUMIF", "SUMIFS"),)),
    formula("F3-B.M3", "In M8 average Lee's Units.", "AVERAGEIF.", "M8", '=AVERAGEIF(E6:E25,"Lee",G6:G25)',
            mean(o.units for o in ORDERS if o.rep == "Lee"), items=("F3.averageif",),
            wrong=('=AVERAGEIF(E6:E25,"Lee",H6:H25)',), uses=(("AVERAGEIF", "AVERAGEIFS"),)),
    formula("F3-B.M4", "In M9 count South orders with more than 20 units.", "COUNTIFS.", "M9",
            '=COUNTIFS(D6:D25,"South",G6:G25,">20")', sum(o.region == "South" and o.units > 20 for o in ORDERS),
            items=("F3.countifs",), wrong=('=COUNTIF(D6:D25,"South")',), uses=("COUNTIFS",)),
    formula("F3-B.M5", "In M10 add the Revenue of Raj's Gizmo orders.", "SUMIFS, sum range first.", "M10",
            '=SUMIFS(H6:H25,E6:E25,"Raj",F6:F25,"Gizmo")',
            sum(o.revenue for o in ORDERS if o.rep == "Raj" and o.product == "Gizmo"), items=("F3.sumifs",),
            wrong=('=SUMIFS(H6:H25,E6:E25,"Raj")',), uses=("SUMIFS",)),
    formula("F3-B.M6", "In M11 find the smallest Units among East orders.", "MINIFS.", "M11",
            '=MINIFS(G6:G25,D6:D25,"East")', min(o.units for o in ORDERS if east(o)), items=("F3.minifs",),
            wrong=('=MAXIFS(G6:G25,D6:D25,"East")',), uses=("MINIFS",)),
    formula("F3-B.M7", 'In M12 count orders with Units ≥ K6, building the criteria with ">="&K6.', "Join with &.",
            "M12", '=COUNTIFS(G6:G25,">="&K6)', sum(o.units >= 40 for o in ORDERS), items=("F3.cell_criteria",),
            wrong=('=COUNTIFS(G6:G25,">=K6")',), uses=(("COUNTIF", "COUNTIFS"),), contains=("&",)),
    formula("F3-B.M8", "In M13 add the Revenue dated from K9 to K11.", "Two date pairs.", "M13",
            '=SUMIFS(H6:H25,C6:C25,">="&K9,C6:C25,"<="&K11)', sum(o.revenue for o in ORDERS if START <= o.date <= END),
            items=("F3.date_range",), wrong=('=SUMIFS(H6:H25,C6:C25,"<="&K11)',), uses=("SUMIFS",), contains=("&",)),
)

WORLD = World(
    code="F3", track="F", order=6, title="Conditional Math",
    tagline="Count, add and average only the rows that match.",
    file_name="06 Formulas 3 - Conditional Math.xlsx",
    stages=(STAGE_1, STAGE_2, STAGE_3, STAGE_4),
    boss=Boss(BOSS_MISSIONS, BOSS_ARENA, par_minutes=15),
)
