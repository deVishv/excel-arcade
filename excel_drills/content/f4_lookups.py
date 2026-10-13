"""Formulas 4 · Lookups — find a value in one column and bring back its partner from another."""
from ..model import Arena, Boss, Item, Stage, World, column, filled, formula, merge, spill, table
from .datasets import PRODUCT_HEADER, PRODUCTS, products_rows

BY_ID = {p.id: p for p in PRODUCTS}
BY_NAME = {p.name: p for p in PRODUCTS}
TIERS = [[0, 0], [10, 0.05], [50, 0.1], [100, 0.15]]
GRADES = [[0, "F"], [60, "D"], [70, "C"], [80, "B"], [90, "A"]]


def _r(cell: str) -> int:
    return int("".join(ch for ch in cell if ch.isdigit()))


def tier(qty: int) -> float:
    return [d for q, d in TIERS if q <= qty][-1]


def letter(score: int) -> str:
    return [g for s, g in GRADES if s <= score][-1]


def products_arena(pass_code: str, extra: dict, inputs: tuple, *, headers: tuple = (), labels: tuple = (),
                   number_formats: dict | None = None) -> Arena:
    """PRODUCTS in B5:F20 (rows 6..20); lookup questions in columns I/J and beyond."""
    return Arena(cells=merge(table("B5", PRODUCT_HEADER, products_rows()), extra), pass_code=pass_code, inputs=inputs,
                 headers=("B5:F5", *headers), labels=labels, number_formats=number_formats or {},
                 widths={"C": 13, "I": 14, "J": 14})


# ------------------------------------------------------------------------------------ F4-1 Seeker
ORDER_IDS = ["P-03", "P-11", "P-01", "P-14"]
ITEMS_1 = (
    Item("F4.xlookup", "function", "XLOOKUP", "XLOOKUP(lookup_value, lookup_array, return_array) finds a match and "
         "returns its partner.", "Works left or right, exact match by default.", "Which modern function finds a "
         "value and returns the matching item from another column?", ("XLOOKUP",), "X plus LOOKUP."),
    Item("F4.lock_ranges", "concept", "$B$6:$B$20", "Lock lookup ranges with $ before you fill the formula down.",
         "Otherwise the ranges slide down and miss rows.", "Which symbol locks a range so it doesn't shift when "
         "you fill down?", ("$", "dollar", "dollar sign"), "The F4 symbol."),
)
ARENA_1 = products_arena("SEEKER", merge({"I5": "Find ID", "I6": "P-07", "J5": "Price"}, {"I9": "Order IDs", "J9": "Stock"},
                                         column("I10", ORDER_IDS)), ("J6", "J10:J13"), headers=("I5:J5", "I9:J9"))
MISSIONS_1 = (
    formula("F4-1.M1", "In J6 find the Price of the product whose ID is in I6: =XLOOKUP(I6,B6:B20,E6:E20).",
            "Look up in IDs, return from Price.", "J6", "=XLOOKUP(I6,B6:B20,E6:E20)", BY_ID["P-07"].price,
            items=("F4.xlookup",), wrong=("=XLOOKUP(I6,B6:B20,F6:F20)",), uses=("XLOOKUP",)),
    filled("F4-1.M2", "In J10 write =XLOOKUP(I10,$B$6:$B$20,$F$6:$F$20) to get the Stock, then fill down to J13 with "
                      "Ctrl+D. The $ signs keep the ranges in place.", "Lock both ranges with F4.", "J10:J13",
           lambda c: f"=XLOOKUP(I{_r(c)},$B$6:$B$20,$F$6:$F$20)", [BY_ID[i].stock for i in ORDER_IDS],
           items=("F4.xlookup", "F4.lock_ranges"),
           wrong_for=lambda c: f"=XLOOKUP(I{_r(c)},B{_r(c) - 4}:B{_r(c) + 10},F{_r(c) - 4}:F{_r(c) + 10})",
           uses=("XLOOKUP",), dollar=True),
)
STAGE_1 = Stage("F4-1", "Seeker", "look up a value and bring back its partner", ITEMS_1, MISSIONS_1, ARENA_1)

# ------------------------------------------------------------------------------------ F4-2 Safety Net
ITEMS_2 = (
    Item("F4.if_not_found", "concept", "if_not_found", "XLOOKUP's 4th argument: what to show when nothing matches.",
         '=XLOOKUP(A2,B:B,C:C,"Not found") instead of #N/A.', "Which XLOOKUP argument number sets the result when "
         "no match is found?", ("4", "4th", "fourth", "if_not_found"), "After lookup, lookup array, return array."),
    Item("F4.multi_return", "concept", "return 2+ columns", "Give XLOOKUP a return range two columns wide and both "
         "values spill out.", "One formula, several answers side by side.", "If the return array is E6:F20, how many "
         "columns does the result spill into?", ("2", "two"), "Count E and F."),
)
ARENA_2 = products_arena("SAFETYNET", {"I5": "Find ID", "I6": "P-99", "J5": "Product", "I8": "Find ID", "I9": "P-05",
                                       "J8": "Price", "K8": "Stock"}, ("J6", "J9"), headers=("I5:J5", "I8:K8"))
MISSIONS_2 = (
    formula("F4-2.M1", 'I6 holds an ID that doesn\'t exist. In J6 look up its Product (column C) and show "Not found" '
                       "instead of an error.", "Use XLOOKUP's 4th argument.", "J6", '=XLOOKUP(I6,B6:B20,C6:C20,"Not found")',
            "Not found", items=("F4.if_not_found",), wrong=("=XLOOKUP(I6,B6:B20,C6:C20)",), uses=("XLOOKUP",)),
    spill("F4-2.M2", "In J9 return BOTH the Price and the Stock of the ID in I9 with one XLOOKUP: make the return "
                     "array E6:F20.", "The result spills into J9:K9.", "J9", "=XLOOKUP(I9,B6:B20,E6:F20)",
          [[BY_ID["P-05"].price, BY_ID["P-05"].stock]], items=("F4.multi_return",),
          wrong=("=XLOOKUP(I9,B6:B20,E6:E20)",), uses=("XLOOKUP",)),
)
STAGE_2 = Stage("F4-2", "Safety Net", "handle missing values and return several columns", ITEMS_2, MISSIONS_2, ARENA_2)

# ------------------------------------------------------------------------------------ F4-3 Old School
ITEMS_3 = (
    Item("F4.vlookup", "function", "VLOOKUP", "VLOOKUP(value, table, column_number, FALSE) searches the FIRST "
         "column of a table.", "Still everywhere in older files.", "Which classic function searches the first column "
         "of a table and returns a column by number?", ("VLOOKUP",), "V for vertical."),
    Item("F4.vlookup_false", "concept", "FALSE = exact", "End VLOOKUP with FALSE for an exact match.",
         "Forget it and VLOOKUP may return a wrong neighbor.", "Which 4th argument makes VLOOKUP find an exact match?",
         ("FALSE", "0"), "The opposite of TRUE."),
)
ARENA_3 = products_arena("CLASSIC", {"I5": "Find ID", "I6": "P-12", "J5": "Category", "I8": "Find ID", "I9": "P-04",
                                     "J8": "Stock"}, ("J6", "J9"), headers=("I5:J5", "I8:J8"))
MISSIONS_3 = (
    formula("F4-3.M1", "In J6 return the Category of the ID in I6 with =VLOOKUP(I6,B6:F20,3,FALSE). Category is the "
                       "3rd column of B:F.", "Count columns from B.", "J6", "=VLOOKUP(I6,B6:F20,3,FALSE)",
            BY_ID["P-12"].category, items=("F4.vlookup", "F4.vlookup_false"), wrong=("=VLOOKUP(I6,B6:F20,2,FALSE)",),
            uses=("VLOOKUP",)),
    formula("F4-3.M2", "In J9 return the Stock of the ID in I9 with VLOOKUP. Stock is column 5 of B:F.", "B=1 … F=5.",
            "J9", "=VLOOKUP(I9,B6:F20,5,FALSE)", BY_ID["P-04"].stock, items=("F4.vlookup",),
            wrong=("=VLOOKUP(I9,B6:F20,4,FALSE)",), uses=("VLOOKUP",)),
)
STAGE_3 = Stage("F4-3", "Old School", "read and write classic VLOOKUP", ITEMS_3, MISSIONS_3, ARENA_3)

# ------------------------------------------------------------------------------------ F4-4 Power Couple
ITEMS_4 = (
    Item("F4.index", "function", "INDEX", "INDEX(range, n) returns the n-th item of a range.",
         "=INDEX(E6:E20,5) is the 5th price.", "Which function returns the item at a given position in a range?",
         ("INDEX",), "Like a book's index."),
    Item("F4.match", "function", "MATCH", "MATCH(value, range, 0) returns the position of a value.",
         "The 0 means exact match.", "Which function returns the position of a value in a range?", ("MATCH",),
         "It finds a match."),
    Item("F4.index_match", "concept", "INDEX+MATCH", "=INDEX(return_range, MATCH(value, lookup_range, 0)) looks up "
         "in any direction.", "Works even when the answer is LEFT of the lookup column.", "Which function goes inside "
         "INDEX to find the row position?", ("MATCH", "XMATCH"), "The position finder."),
    Item("F4.xmatch", "function", "XMATCH", "Modern MATCH: exact match by default.", "=XMATCH(\"Kiwi\",C6:C20)",
         "Which modern function returns a position with an exact match by default?", ("XMATCH",), "X plus MATCH."),
)
ARENA_4 = products_arena("COUPLE", {"I5": "Find name", "I6": "Kiwi", "J5": "Position", "I8": "Find name",
                                    "I9": "Mango", "J8": "ID", "I11": "Find name", "I12": "Okra", "J11": "XMATCH",
                                    "I14": "5th price →"}, ("J6", "J9", "J12", "J14"),
                         headers=("I5:J5", "I8:J8", "I11:J11"), labels=("I14",))
MISSIONS_4 = (
    formula("F4-4.M1", "In J6 return the position of the name in I6 within C6:C20: =MATCH(I6,C6:C20,0).",
            "0 = exact.", "J6", "=MATCH(I6,C6:C20,0)", [p.name for p in PRODUCTS].index("Kiwi") + 1,
            items=("F4.match",), wrong=("=MATCH(I6,B6:B20,0)",), uses=("MATCH",)),
    formula("F4-4.M2", "The ID is LEFT of the names. In J9 return the ID of the product named in I9 with "
                       "=INDEX(B6:B20,MATCH(I9,C6:C20,0)).", "MATCH finds the row, INDEX fetches it.", "J9",
            "=INDEX(B6:B20,MATCH(I9,C6:C20,0))", BY_NAME["Mango"].id, items=("F4.index_match", "F4.index"),
            wrong=("=INDEX(C6:C20,MATCH(I9,C6:C20,0))",), uses=("INDEX", "MATCH")),
    formula("F4-4.M3", "In J12 return the position of the name in I12 with XMATCH.", "No 0 needed.", "J12",
            "=XMATCH(I12,C6:C20)", [p.name for p in PRODUCTS].index("Okra") + 1, items=("F4.xmatch",),
            wrong=("=MATCH(I12,C6:C20,0)",), uses=("XMATCH",)),
    formula("F4-4.M4", "In J14 return the 5th Price in E6:E20 with INDEX.", "=INDEX(E6:E20,5)", "J14", "=INDEX(E6:E20,5)",
            PRODUCTS[4].price, items=("F4.index",), wrong=("=INDEX(E6:E20,4)",), uses=("INDEX",)),
)
STAGE_4 = Stage("F4-4", "Power Couple", "combine INDEX and MATCH for any-direction lookups", ITEMS_4, MISSIONS_4,
                ARENA_4)

# ------------------------------------------------------------------------------------ F4-5 Tiers
ITEMS_5 = (
    Item("F4.xlookup_approx", "concept", "match_mode -1", "XLOOKUP(…,,-1): exact match or the next smaller item.",
         "Perfect for discount tiers and grade bands.", "Which XLOOKUP match_mode returns an exact match or the next "
         "smaller item?", ("-1",), "Minus one."),
    Item("F4.vlookup_true", "concept", "VLOOKUP TRUE", "Approximate VLOOKUP: the first column must be sorted "
         "smallest to largest.", "Unsorted bands give wrong answers silently.", "For an approximate VLOOKUP, how must "
         "the first column be sorted?", ("ascending", "smallest to largest", "A to Z", "A-Z"), "Low to high."),
)
ARENA_5 = products_arena("TIERS", merge(
    {"I5": "Quantity", "I6": 64, "J5": "Discount", "I8": "Score", "I9": 83, "J8": "Grade"},
    table("L5", ["Min qty", "Discount"], TIERS), table("L12", ["Min score", "Grade"], GRADES)),
    ("J6", "J9"), headers=("I5:J5", "I8:J8", "L5:M5", "L12:M12"), number_formats={"M6:M9": "0%", "J6": "0%"})
MISSIONS_5 = (
    formula("F4-5.M1", "In J6 find the discount for the quantity in I6 from the tiers in L6:M9: "
                       "=XLOOKUP(I6,L6:L9,M6:M9,,-1).", "-1 = exact or next smaller.", "J6",
            "=XLOOKUP(I6,L6:L9,M6:M9,,-1)", tier(64), items=("F4.xlookup_approx",),
            wrong=("=XLOOKUP(I6,L6:L9,M6:M9)",), uses=("XLOOKUP",), contains=("-1",)),
    formula("F4-5.M2", "In J9 find the grade for the score in I9 from L13:M17 with =VLOOKUP(I9,L13:M17,2,TRUE).",
            "TRUE = approximate (sorted bands).", "J9", "=VLOOKUP(I9,L13:M17,2,TRUE)", letter(83),
            items=("F4.vlookup_true",), wrong=("=VLOOKUP(I9,L13:M17,2,FALSE)",), uses=("VLOOKUP",)),
)
STAGE_5 = Stage("F4-5", "Tiers", "look up bands, tiers and grades", ITEMS_5, MISSIONS_5, ARENA_5)

# ------------------------------------------------------------------------------------ Boss
BOSS_IDS = ["P-02", "P-08", "P-15", "P-06"]
BOSS_ARENA = products_arena("LOOKOUT", merge(
    {"I5": "Find ID", "I6": "P-10", "J5": "Price"}, {"I8": "Order IDs", "J8": "Stock"}, column("I9", BOSS_IDS),
    {"I14": "Find ID", "I15": "P-77", "J14": "Product"}, {"I17": "Find ID", "I18": "P-13", "J17": "Price", "K17": "Stock"},
    {"I20": "Find ID", "I21": "P-09", "J20": "Category"}, {"I23": "Find name", "I24": "Fig", "J23": "ID"},
    {"I26": "Find name", "I27": "Leek", "J26": "Position"}, {"I29": "Quantity", "I30": 120, "J29": "Discount"},
    table("L5", ["Min qty", "Discount"], TIERS)),
    ("J6", "J9:J12", "J15", "J18", "J21", "J24", "J27", "J30"),
    headers=("I5:J5", "I8:J8", "I14:J14", "I17:K17", "I20:J20", "I23:J23", "I26:J26", "I29:J29", "L5:M5"),
    number_formats={"M6:M9": "0%", "J30": "0%"})
BOSS_MISSIONS = (
    formula("F4-B.M1", "In J6 return the Price of the ID in I6 with XLOOKUP.", "XLOOKUP(I6,…).", "J6",
            "=XLOOKUP(I6,B6:B20,E6:E20)", BY_ID["P-10"].price, items=("F4.xlookup",),
            wrong=("=XLOOKUP(I6,B6:B20,F6:F20)",), uses=("XLOOKUP",)),
    filled("F4-B.M2", "In J9 return the Stock of I9 with locked ranges, then fill down to J12.", "$ on both ranges.",
           "J9:J12", lambda c: f"=XLOOKUP(I{_r(c)},$B$6:$B$20,$F$6:$F$20)", [BY_ID[i].stock for i in BOSS_IDS],
           items=("F4.lock_ranges",), wrong_for=lambda c: f"=XLOOKUP(I{_r(c)},B{_r(c) - 3}:B{_r(c) + 11},"
                                                          f"F{_r(c) - 3}:F{_r(c) + 11})",
           uses=(("XLOOKUP", "VLOOKUP", "INDEX"),), dollar=True),
    formula("F4-B.M3", 'In J15 look up the Product for I15 and show "Not found" when it is missing.', "4th argument.",
            "J15", '=XLOOKUP(I15,B6:B20,C6:C20,"Not found")', "Not found", items=("F4.if_not_found",),
            wrong=("=XLOOKUP(I15,B6:B20,C6:C20)",), uses=(("XLOOKUP", "VLOOKUP", "INDEX"),)),
    spill("F4-B.M4", "In J18 return the Price AND the Stock of I18 with one XLOOKUP.", "Return array E6:F20.", "J18",
          "=XLOOKUP(I18,B6:B20,E6:F20)", [[BY_ID["P-13"].price, BY_ID["P-13"].stock]], items=("F4.multi_return",),
          wrong=("=XLOOKUP(I18,B6:B20,E6:E20)",), uses=("XLOOKUP",)),
    formula("F4-B.M5", "In J21 return the Category of I21 with VLOOKUP (exact match).", "Column 3, FALSE.", "J21",
            "=VLOOKUP(I21,B6:F20,3,FALSE)", BY_ID["P-09"].category, items=("F4.vlookup", "F4.vlookup_false"),
            wrong=("=VLOOKUP(I21,B6:F20,2,FALSE)",), uses=("VLOOKUP",)),
    formula("F4-B.M6", "In J24 return the ID of the product named in I24 (the ID is to the LEFT). Use INDEX and MATCH.",
            "INDEX(B…,MATCH(…,C…,0)).", "J24", "=INDEX(B6:B20,MATCH(I24,C6:C20,0))", BY_NAME["Fig"].id,
            items=("F4.index_match",), wrong=("=INDEX(C6:C20,MATCH(I24,C6:C20,0))",), uses=("INDEX", "MATCH")),
    formula("F4-B.M7", "In J27 return the position of I27 in C6:C20 with XMATCH.", "XMATCH.", "J27",
            "=XMATCH(I27,C6:C20)", [p.name for p in PRODUCTS].index("Leek") + 1, items=("F4.xmatch",),
            wrong=("=XMATCH(I27,B6:B20)",), uses=("XMATCH",)),
    formula("F4-B.M8", "In J30 find the discount tier for the quantity in I30 from L6:M9.", "match_mode -1.", "J30",
            "=XLOOKUP(I30,L6:L9,M6:M9,,-1)", tier(120), items=("F4.xlookup_approx",),
            wrong=("=XLOOKUP(I30,L6:L9,M6:M9)",), uses=(("XLOOKUP", "VLOOKUP"),)),
)

WORLD = World(
    code="F4", track="F", order=8, title="Lookups",
    tagline="Find a value in one column and bring back its partner from another.",
    file_name="08 Formulas 4 - Lookups.xlsx",
    stages=(STAGE_1, STAGE_2, STAGE_3, STAGE_4, STAGE_5),
    boss=Boss(BOSS_MISSIONS, BOSS_ARENA, par_minutes=15),
)
