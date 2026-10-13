"""Formulas 7 · Dynamic Arrays — one formula, many results: SEQUENCE, FILTER, SORT, UNIQUE and LET."""
from statistics import mean

from ..model import Arena, Boss, Fixture, Formula, Item, Stage, World, do, formula, merge, spill, table
from .datasets import ORDER_HEADER, ORDERS, orders_rows, serial


def orders_arena(pass_code: str, extra: dict, inputs: tuple, *, headers: tuple = (), labels: tuple = ()) -> Arena:
    """ORDERS in B5:H25 (rows 6..25). Answer areas start in column K."""
    return Arena(cells=merge(table("B5", ORDER_HEADER, orders_rows()), extra), pass_code=pass_code, inputs=inputs,
                 headers=("B5:H5", *headers), labels=labels, number_formats={"C6:C25": "d-mmm-yy"},
                 widths={"C": 11})


def row_values(o) -> list:
    return [o.id, serial(o.date), o.region, o.rep, o.product, o.units, o.revenue]


EAST = [o for o in ORDERS if o.region == "East"]

# ------------------------------------------------------------------------------------ F7-1 Spill Zone
ITEMS_1 = (
    Item("F7.spill", "concept", "spill", "One formula can return many values; they spill into the cells around it.",
         "Edit only the top-left cell; the rest follow.", "What is it called when one formula's results flow into "
         "neighboring cells?", ("spill", "spilling", "spills"), "Like water spilling over."),
    Item("F7.spill_error", "concept", "#SPILL!", "#SPILL! means something is in the way of the results.",
         "Clear the blocking cells and the results appear.", "Which error appears when a spill range is blocked?",
         ("#SPILL!", "SPILL", "#SPILL"), "#SPILL! with an exclamation mark."),
    Item("F7.spill_ref", "concept", "H5#", "Add # after the top-left cell to refer to the whole spill.",
         "=SUM(H5#) grows and shrinks with the spill.", "How do you refer to the whole spill that starts in H5?",
         ("H5#",), "The cell address plus #."),
    Item("F7.sequence", "function", "SEQUENCE", "SEQUENCE(rows) spills the numbers 1, 2, 3 …",
         "=SEQUENCE(4,1,10,10) spills 10, 20, 30, 40.", "Which function spills a list of sequential numbers?",
         ("SEQUENCE",), "A series of numbers in order."),
)
ARENA_1 = orders_arena(
    "SPILLWAY",
    {"K5": "SEQUENCE ▼", "M5": "Blocked spill", "M6": Formula("=SEQUENCE(5)", "#SPILL!", error_ok=True),
     "M8": "BLOCK", "O5": "Ready-made spill", "O6": Formula("=SEQUENCE(4,1,10,10)", 10), "K19": "Sum of O6#"},
    ("K6", "K20"), headers=("K5", "M5", "O5"), labels=("K19", "M8"))
MISSIONS_1 = (
    spill("F7-1.M1", "In K6 type =SEQUENCE(10) and press Enter. One formula fills K6:K15.", "Just one cell to type in.",
          "K6", "=SEQUENCE(10)", [[i] for i in range(1, 11)], items=("F7.sequence", "F7.spill"),
          wrong=("=SEQUENCE(9)",), uses=("SEQUENCE",)),
    do("F7-1.M2", "M6 shows #SPILL! because M8 is in its way. Click M8 and press Delete: five numbers spill into place.",
       "Clear the blocking cell.", "AND(ISFORMULA(«@M6»),ROWS(ANCHORARRAY(«@M6»))=5)",   # M8 holds a spilled 3 once solved
       solve=[Fixture("clear", "«@M8»")], wrong=[[Fixture("type", "«@M8»", "STILL HERE")]],
       items=("F7.spill_error",), arena_cell="M8"),
    formula("F7-1.M3", "O6 spills four numbers. In K20 add up the whole spill with =SUM(O6#).", "# = the whole spill.",
            "K20", "=SUM(O6#)", 100, items=("F7.spill_ref",), wrong=("=SUM(O6)",), contains=("#",)),
)
STAGE_1 = Stage("F7-1", "Spill Zone", "let one formula fill many cells", ITEMS_1, MISSIONS_1, ARENA_1)

# ------------------------------------------------------------------------------------ F7-2 Sifter
ITEMS_2 = (
    Item("F7.filter", "function", "FILTER", "FILTER(range, condition) spills only the matching rows.",
         '=FILTER(B6:H25,D6:D25="East")', "Which function returns only the rows that meet a condition?",
         ("FILTER",), "Like a coffee filter."),
    Item("F7.filter_and", "concept", "(…)*(…)", "Multiply conditions for AND; add them for OR.",
         '(D6:D25="East")*(G6:G25>40) keeps rows that pass both.', "In FILTER, which operator joins two conditions "
         "so BOTH must be true?", ("*", "asterisk"), "Multiply."),
    Item("F7.if_empty", "concept", "if_empty", "FILTER's 3rd argument: what to show when nothing matches.",
         'Without it, an empty result is #CALC!.', "Which FILTER argument number sets what to show when nothing "
         "matches?", ("3", "3rd", "third", "if_empty"), "After array and include."),
)
ARENA_2 = orders_arena("SIFTER", {"K5": "East orders ▼", "K19": "Big East orders ▼", "K29": "Central orders ▼"},
                       ("K6", "K20", "K30"), headers=("K5", "K19", "K29"))
MISSIONS_2 = (
    spill("F7-2.M1", 'In K6 spill every East order (all columns): =FILTER(B6:H25,D6:D25="East").', "One formula.",
          "K6", '=FILTER(B6:H25,D6:D25="East")', [row_values(o) for o in EAST], items=("F7.filter",),
          wrong=('=FILTER(B6:H25,D6:D25="West")',), uses=("FILTER",)),
    spill("F7-2.M2", "In K20 spill the Order IDs of East orders with more than 40 units. Join the two conditions with *.",
          '(D6:D25="East")*(G6:G25>40)', "K20", '=FILTER(B6:B25,(D6:D25="East")*(G6:G25>40))',
          [[o.id] for o in EAST if o.units > 40], items=("F7.filter_and",),
          wrong=('=FILTER(B6:B25,(D6:D25="East")+(G6:G25>40))',), uses=("FILTER",)),
    formula("F7-2.M3", 'There is no Central region. In K30 filter the Order IDs for "Central" and show None when '
                       "nothing matches.", "Third argument.", "K30", '=FILTER(B6:B25,D6:D25="Central","None")', "None",
            items=("F7.if_empty",), wrong=('=FILTER(B6:B25,D6:D25="Central")',), uses=("FILTER",)),
)
STAGE_2 = Stage("F7-2", "Sifter", "pull out exactly the rows you need", ITEMS_2, MISSIONS_2, ARENA_2)

# ------------------------------------------------------------------------------------ F7-3 Sorter
ITEMS_3 = (
    Item("F7.sort", "function", "SORT", "SORT(range, column, order) spills a sorted copy; -1 = largest first.",
         "The original data never moves.", "Which function spills a sorted copy of a range?", ("SORT",),
         "Four letters."),
    Item("F7.sortby", "function", "SORTBY", "SORTBY(range, by_range, order) sorts by a column you don't show.",
         "=SORTBY(B6:B25,C6:C25,-1) lists IDs newest first.", "Which function sorts a range by another range?",
         ("SORTBY",), "SORT plus BY."),
    Item("F7.unique", "function", "UNIQUE", "UNIQUE(range) spills each different value once.",
         "Wrap in COUNTA to count the distinct values.", "Which function returns each distinct value once?",
         ("UNIQUE",), "One of a kind."),
)
ARENA_3 = orders_arena("SORTER", {"K5": "Revenue, big → small", "M5": "IDs, newest first", "O5": "Regions",
                                  "Q5": "How many reps?"}, ("K6", "M6", "O6", "Q6"), headers=("K5", "M5", "O5", "Q5"))
MISSIONS_3 = (
    spill("F7-3.M1", "In K6 spill the Revenue column (H6:H25) sorted largest first: =SORT(H6:H25,,-1).",
          "-1 = descending.", "K6", "=SORT(H6:H25,,-1)", [[r] for r in sorted((o.revenue for o in ORDERS), reverse=True)],
          items=("F7.sort",), wrong=("=SORT(H6:H25)",), uses=("SORT",)),
    spill("F7-3.M2", "In M6 spill the Order IDs sorted by Date, newest first: =SORTBY(B6:B25,C6:C25,-1).",
          "Sort IDs by the date column.", "M6", "=SORTBY(B6:B25,C6:C25,-1)",
          [[o.id] for o in sorted(ORDERS, key=lambda o: o.date, reverse=True)], items=("F7.sortby",),
          wrong=("=SORTBY(B6:B25,C6:C25,1)",), uses=("SORTBY",)),
    spill("F7-3.M3", "In O6 spill each Region once: =UNIQUE(D6:D25).", "Order of first appearance.", "O6",
          "=UNIQUE(D6:D25)", [[r] for r in dict.fromkeys(o.region for o in ORDERS)], items=("F7.unique",),
          wrong=("=UNIQUE(E6:E25)",), uses=("UNIQUE",)),
    formula("F7-3.M4", "In Q6 count the different Reps with =COUNTA(UNIQUE(E6:E25)).", "COUNTA around UNIQUE.", "Q6",
            "=COUNTA(UNIQUE(E6:E25))", len({o.rep for o in ORDERS}), items=("F7.unique",),
            wrong=("=COUNTA(E6:E25)",), uses=("COUNTA", "UNIQUE")),
)
STAGE_3 = Stage("F7-3", "Sorter", "sort and de-duplicate with one formula", ITEMS_3, MISSIONS_3, ARENA_3)

# ------------------------------------------------------------------------------------ F7-4 Combo
ITEMS_4 = (
    Item("F7.let", "function", "LET", "LET(name, value, calculation) names a value so you write it once.",
         "=LET(rev,H6:H25,SUM(rev)/COUNT(rev))", "Which function lets you name a value inside a formula?", ("LET",),
         "Three letters: let x be…"),
    Item("F7.nesting", "concept", "SORT(UNIQUE(…))", "Nest dynamic functions: the inner result feeds the outer one.",
         "=SORT(UNIQUE(E6:E25)) gives a sorted list of reps.", "In =SORT(UNIQUE(E6:E25)), which function removes the "
         "duplicates?", ("UNIQUE",), "The inner one."),
)
ARENA_4 = orders_arena(
    "COMBO",
    {"K5": "Average revenue (LET)", "K9": "Reps, A→Z", "K19": "East products, A→Z", "K29": "Rows in Q6#",
     "Q5": "Regions (ready-made)", "Q6": Formula("=UNIQUE(D6:D25)", "East")},
    ("K6", "K10", "K20", "K30"), headers=("K5", "K9", "K19", "K29", "Q5"))
MISSIONS_4 = (
    formula("F7-4.M1", "In K6 compute the average Revenue with LET: =LET(rev,H6:H25,SUM(rev)/COUNT(rev)).",
            "Name the range once, use it twice.", "K6", "=LET(rev,H6:H25,SUM(rev)/COUNT(rev))",
            mean(o.revenue for o in ORDERS), items=("F7.let",), wrong=("=AVERAGE(H6:H25)",), uses=("LET",),
            key="=AVERAGE(H6:H25)"),
    spill("F7-4.M2", "In K10 spill each Rep once, sorted A→Z: =SORT(UNIQUE(E6:E25)).", "UNIQUE inside SORT.", "K10",
          "=SORT(UNIQUE(E6:E25))", [[r] for r in sorted({o.rep for o in ORDERS})], items=("F7.nesting",),
          wrong=("=UNIQUE(E6:E25)",), uses=("SORT", "UNIQUE")),
    spill("F7-4.M3", "In K20 spill the products sold in East, each once, sorted A→Z. Nest FILTER inside UNIQUE inside "
                     "SORT.", 'SORT(UNIQUE(FILTER(F6:F25,D6:D25="East")))', "K20",
          '=SORT(UNIQUE(FILTER(F6:F25,D6:D25="East")))', [[p] for p in sorted({o.product for o in EAST})],
          items=("F7.nesting", "F7.filter"), wrong=('=UNIQUE(FILTER(F6:F25,D6:D25="East"))',),
          uses=("SORT", "UNIQUE", "FILTER")),
    formula("F7-4.M4", "Q6 spills the regions. In K30 count how many rows that spill has with =ROWS(Q6#).",
            "# = the whole spill.", "K30", "=ROWS(Q6#)", len({o.region for o in ORDERS}), items=("F7.spill_ref",),
            wrong=("=ROWS(Q6)",), contains=("#",)),
)
STAGE_4 = Stage("F7-4", "Combo", "nest dynamic functions and name values with LET", ITEMS_4, MISSIONS_4, ARENA_4)

# ------------------------------------------------------------------------------------ Boss
WEST = [o for o in ORDERS if o.region == "West"]
BOSS_ARENA = orders_arena(
    "ARRAYMANCER",
    # The West FILTER spills 7 columns wide (M6:S10), so the ready-made spill lives in column U.
    {"K5": "SEQUENCE(5)", "M5": "West orders", "K13": "Kim's IDs", "K29": "Units, big → small", "M29": "Products",
     "O29": "How many products?", "Q29": "Reps, A→Z", "U5": "Ready-made", "U6": Formula("=SEQUENCE(3,1,5,5)", 5),
     "U12": "Sum of U6#", "W5": "IDs, newest first", "W29": "Central orders"},
    ("K6", "M6", "K14", "K30", "M30", "O30", "Q30", "U13", "W6", "W30"),
    headers=("K5", "M5", "K13", "K29", "M29", "O29", "Q29", "U5", "W5", "W29"), labels=("U12",))
BOSS_MISSIONS = (
    spill("F7-B.M1", "In K6 spill the numbers 1 to 5.", "SEQUENCE.", "K6", "=SEQUENCE(5)", [[i] for i in range(1, 6)],
          items=("F7.sequence",), wrong=("=SEQUENCE(4)",), uses=("SEQUENCE",)),
    spill("F7-B.M2", 'In M6 spill the West orders, every column.', "FILTER.", "M6", '=FILTER(B6:H25,D6:D25="West")',
          [row_values(o) for o in WEST], items=("F7.filter",), wrong=('=FILTER(B6:H25,D6:D25="East")',),
          uses=("FILTER",)),
    spill("F7-B.M3", "In K14 spill the Order IDs of Kim's orders with more than 20 units.", "Multiply two conditions.",
          "K14", '=FILTER(B6:B25,(E6:E25="Kim")*(G6:G25>20))', [[o.id] for o in ORDERS if o.rep == "Kim" and o.units > 20],
          items=("F7.filter_and",), wrong=('=FILTER(B6:B25,(E6:E25="Kim")+(G6:G25>20))',), uses=("FILTER",)),
    spill("F7-B.M4", "In K30 spill the Units column sorted largest first.", "SORT with -1.", "K30", "=SORT(G6:G25,,-1)",
          [[u] for u in sorted((o.units for o in ORDERS), reverse=True)], items=("F7.sort",), wrong=("=SORT(G6:G25)",),
          uses=("SORT",)),
    spill("F7-B.M5", "In M30 spill each Product once.", "UNIQUE.", "M30", "=UNIQUE(F6:F25)",
          [[p] for p in dict.fromkeys(o.product for o in ORDERS)], items=("F7.unique",), wrong=("=UNIQUE(E6:E25)",),
          uses=("UNIQUE",)),
    formula("F7-B.M6", "In O30 count the different Products.", "COUNTA(UNIQUE(…)).", "O30", "=COUNTA(UNIQUE(F6:F25))",
            len({o.product for o in ORDERS}), items=("F7.unique",), wrong=("=COUNTA(F6:F25)",),
            uses=("COUNTA", "UNIQUE")),
    spill("F7-B.M7", "In Q30 spill each Rep once, sorted A→Z.", "Nest UNIQUE in SORT.", "Q30", "=SORT(UNIQUE(E6:E25))",
          [[r] for r in sorted({o.rep for o in ORDERS})], items=("F7.nesting",), wrong=("=UNIQUE(E6:E25)",),
          uses=("SORT", "UNIQUE")),
    formula("F7-B.M8", "In U13 add up the whole spill in U6 with U6#.", "SUM(U6#).", "U13", "=SUM(U6#)", 30,
            items=("F7.spill_ref",), wrong=("=SUM(U6)",), contains=("#",)),
    spill("F7-B.M9", "In W6 spill the Order IDs sorted by Date, newest first, with SORTBY.", "Sort the IDs by C6:C25.",
          "W6", "=SORTBY(B6:B25,C6:C25,-1)", [[o.id] for o in sorted(ORDERS, key=lambda o: o.date, reverse=True)],
          items=("F7.sortby",), wrong=("=SORTBY(B6:B25,C6:C25,1)",), uses=("SORTBY",)),
    formula("F7-B.M10", 'In W30 filter the Order IDs for the region "Central" and show None when nothing matches.',
            "FILTER's third argument.", "W30", '=FILTER(B6:B25,D6:D25="Central","None")', "None",
            items=("F7.if_empty",), wrong=('=FILTER(B6:B25,D6:D25="Central")',), uses=("FILTER",)),
)

WORLD = World(
    code="F7", track="F", order=11, title="Dynamic Arrays",
    tagline="One formula, many results: SEQUENCE, FILTER, SORT, UNIQUE and LET.",
    file_name="11 Formulas 7 - Dynamic Arrays.xlsx",
    stages=(STAGE_1, STAGE_2, STAGE_3, STAGE_4),
    boss=Boss(BOSS_MISSIONS, BOSS_ARENA, par_minutes=15),
)
