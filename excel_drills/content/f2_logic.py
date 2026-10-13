"""Formulas 2 · Logic — make formulas decide: comparisons, IF, AND/OR/NOT, IFS and error shields."""
from ..model import Arena, Boss, Formula, Item, Stage, World, filled, find, formula, merge, table


def _r(cell: str) -> int:
    return int("".join(ch for ch in cell if ch.isdigit()))


# Scores sit exactly on the thresholds the missions use (50, 60, 75, 90) so a > vs >= slip changes the answer.
PEOPLE = [["Ava", 92, 17, "No"], ["Ben", 48, 22, "Yes"], ["Cy", 75, 19, "Yes"], ["Dee", 60, 16, "No"],
          ["Eli", 88, 30, "Yes"], ["Fay", 50, 18, "Yes"], ["Gus", 39, 25, "No"], ["Hal", 81, 41, "Yes"],
          ["Ivy", 99, 15, "No"], ["Jo", 70, 20, "No"]]
PEOPLE_HEADER = ["Name", "Score", "Age", "License"]
ROWS = range(6, 16)                                       # PEOPLE sits in B5:E15 (rows 6..15)


def person(cell: str) -> list:
    return PEOPLE[_r(cell) - 6]


def people_arena(pass_code: str, extra: dict, inputs: tuple, headers: tuple = (), labels: tuple = ()) -> Arena:
    return Arena(cells=merge(table("B5", PEOPLE_HEADER, PEOPLE), extra), pass_code=pass_code, inputs=inputs,
                 headers=("B5:E5", *headers), labels=labels, widths={"F": 14, "G": 14})


# ------------------------------------------------------------------------------------ F2-1 True or False
ITEMS_1 = (
    Item("F2.compare", "concept", ">=", "Compare two values: = < > <= >= give TRUE or FALSE.",
         "=B2>=50 is TRUE when B2 is 50 or more.", "Which operator means 'greater than or equal to'?", (">=",),
         "Two characters: > then =."),
    Item("F2.not_equal", "concept", "<>", "Not equal to.", '=A2<>"Closed" is TRUE for anything except Closed.',
         "Which operator means 'not equal to'?", ("<>",), "Less-than then greater-than."),
    Item("F2.quotes", "concept", '"text"', "Text inside a formula goes in double quotes.",
         'Comparisons ignore case: ="YES"="yes" is TRUE.', "What must surround text inside a formula?",
         ("quotes", "double quotes", "quotation marks", '"'), "Shift plus the apostrophe key."),
)
ARENA_1 = people_arena("VERDICT", {"F6": "Ava ≥ 50?", "F7": "Ben not No?", "F8": "Cy = yes?"}, ("G6:G8",),
                       labels=("F6:F8",))
MISSIONS_1 = (
    formula("F2-1.M1", "In G6 write a formula that tests whether Ava's Score (C6) is at least 50. The answer is "
                       "TRUE or FALSE.", "Use >=.", "G6", "=C6>=50", True, items=("F2.compare",), wrong=("=C6<50",)),
    formula("F2-1.M2", 'In G7 test whether Ben\'s License (E7) is NOT equal to "No". Use <>.', 'Type =E7<>"No".',
            "G7", '=E7<>"No"', True, items=("F2.not_equal",), wrong=('=E7="No"',), contains=("<>",)),
    formula("F2-1.M3", 'In G8 test whether Cy\'s License (E8) equals "yes" (type yes in lowercase, inside quotes). '
                       "Excel ignores case when it compares text.", "Text needs quotes.", "G8", '=E8="yes"', True,
            items=("F2.quotes",), wrong=('=E8="no"',)),
)
STAGE_1 = Stage("F2-1", "True or False", "ask Excel yes-or-no questions", ITEMS_1, MISSIONS_1, ARENA_1)

# ------------------------------------------------------------------------------------ F2-2 Fork in the Road
ITEMS_2 = (
    Item("F2.if", "function", "IF", "IF(test, value_if_true, value_if_false) picks one of two results.",
         '=IF(B2>=50,"Pass","Fail")', "Which function returns one value when a test is TRUE and another when FALSE?",
         ("IF",), "Two letters."),
    Item("F2.if_math", "concept", "IF + math", "Each branch can be a calculation, not just text.",
         "=IF(B2>100,B2*0.9,B2) discounts only big orders.", "In =IF(B2>100,B2*0.9,B2), what is returned when B2 is 50?",
         ("50",), "50 is not more than 100."),
    Item("F2.empty_text", "concept", '""', 'Two quotes with nothing between = empty text, a blank-looking result.',
         '=IF(A2="","",A2*2) stays blank until A2 has a value.', "What do you type in a formula for an empty, "
         "blank-looking result?", ('""',), "Two double quotes, nothing inside."),
)
ARENA_2 = people_arena("CROSSROADS", {"F5": "Result", "G5": "Bonus", "I5": "Blank-safe ×2", "J5": "Empty cell ↓"},
                       ("F6:G15", "I6"), headers=("F5:G5", "I5"), labels=("J5",))
MISSIONS_2 = (
    filled("F2-2.M1", 'In F6 write =IF(C6>=50,"Pass","Fail"), then select F6:F15 and press Ctrl+D.',
           "Text results need quotes.", "F6:F15", lambda c: f'=IF(C{_r(c)}>=50,"Pass","Fail")',
           ["Pass" if p[1] >= 50 else "Fail" for p in PEOPLE], items=("F2.if",),
           wrong_for=lambda c: f'=IF(C{_r(c)}>50,"Pass","Fail")', uses=("IF",)),
    filled("F2-2.M2", "In G6: if the Score is 80 or more, the bonus is Score × 10, otherwise 0. Fill down to G15.",
           "=IF(C6>=80,C6*10,0)", "G6:G15", lambda c: f"=IF(C{_r(c)}>=80,C{_r(c)}*10,0)",
           [p[1] * 10 if p[1] >= 80 else 0 for p in PEOPLE], items=("F2.if_math",),
           wrong_for=lambda c: f"=IF(C{_r(c)}>=80,10,0)", uses=("IF",)),
    formula("F2-2.M3", 'J6 is empty. In I6 write a formula that shows empty text ("") when J6 is empty, otherwise '
                       "J6*2.", '=IF(J6="","",J6*2)', "I6", '=IF(J6="","",J6*2)', "", items=("F2.empty_text",),
            wrong=("=J6*2",), uses=("IF",)),
)
STAGE_2 = Stage("F2-2", "Fork in the Road", "return different results with IF", ITEMS_2, MISSIONS_2, ARENA_2)

# ------------------------------------------------------------------------------------ F2-3 Combo Moves
ITEMS_3 = (
    Item("F2.and", "function", "AND", "TRUE only when every condition is TRUE.", "=AND(B2>=18,C2=\"Yes\")",
         "Which function is TRUE only when all its conditions are TRUE?", ("AND",), "Three letters: all must pass."),
    Item("F2.or", "function", "OR", "TRUE when at least one condition is TRUE.", "=OR(B2>=90,C2<16)",
         "Which function is TRUE when at least one condition is TRUE?", ("OR",), "Two letters: any can pass."),
    Item("F2.not", "function", "NOT", "Flip TRUE to FALSE and FALSE to TRUE.", '=NOT(B2="Yes") is TRUE for No.',
         "Which function flips TRUE and FALSE?", ("NOT",), "Three letters: the opposite."),
)
ARENA_3 = people_arena("COMBO", {"F5": "Can drive", "G5": "Prize", "I5": "Ava unlicensed?"}, ("F6:G15", "I6"),
                       headers=("F5:G5", "I5"))
MISSIONS_3 = (
    filled("F2-3.M1", 'Can they drive? In F6: "Yes" if Age (D6) is at least 18 AND License (E6) is "Yes", otherwise '
                      '"No". Fill down to F15.', 'IF(AND(D6>=18,E6="Yes"),"Yes","No")', "F6:F15",
           lambda c: f'=IF(AND(D{_r(c)}>=18,E{_r(c)}="Yes"),"Yes","No")',
           ["Yes" if p[2] >= 18 and p[3] == "Yes" else "No" for p in PEOPLE], items=("F2.and",),
           wrong_for=lambda c: f'=IF(OR(D{_r(c)}>=18,E{_r(c)}="Yes"),"Yes","No")', uses=("AND",)),
    filled("F2-3.M2", 'Prize if Score is at least 90 OR Age is under 16. In G6 return "Prize" or "No prize"; fill '
                      "down to G15.", "OR inside IF.", "G6:G15",
           lambda c: f'=IF(OR(C{_r(c)}>=90,D{_r(c)}<16),"Prize","No prize")',
           ["Prize" if p[1] >= 90 or p[2] < 16 else "No prize" for p in PEOPLE], items=("F2.or",),
           wrong_for=lambda c: f'=IF(AND(C{_r(c)}>=90,D{_r(c)}<16),"Prize","No prize")', uses=("OR",)),
    formula("F2-3.M3", 'In I6 return TRUE when Ava (row 6) does NOT have a License of "Yes". Use NOT.',
            'NOT(E6="Yes")', "I6", '=NOT(E6="Yes")', True, items=("F2.not",), wrong=('=E6="Yes"',), uses=("NOT",)),
)
STAGE_3 = Stage("F2-3", "Combo Moves", "combine conditions with AND, OR and NOT", ITEMS_3, MISSIONS_3, ARENA_3)

# ------------------------------------------------------------------------------------ F2-4 Multi-Level
def grade(score: int) -> str:
    return "A" if score >= 90 else "B" if score >= 75 else "C"


def medal(score: int) -> str:
    return "Gold" if score >= 90 else "Silver" if score >= 75 else "Bronze" if score >= 60 else "None"


ITEMS_4 = (
    Item("F2.nested_if", "concept", "IF inside IF", "Put an IF in the 'false' slot to handle three or more outcomes.",
         '=IF(B2>=90,"A",IF(B2>=75,"B","C"))', "How many IF functions does a nested IF need for 3 outcomes?",
         ("2", "two"), "One fewer than the outcomes."),
    Item("F2.ifs", "function", "IFS", "Check conditions in order and return the first match.",
         '=IFS(B2>=90,"Gold",B2>=75,"Silver",TRUE,"Other")', "Which function tests several conditions in order "
         "without nesting?", ("IFS",), "IF plus one letter."),
    Item("F2.ifs_true", "concept", "TRUE, …", "End IFS with TRUE and a fallback to catch everything else.",
         "Without it, unmatched values show #N/A.", "In IFS, what do you put as the last test to catch all "
         "remaining cases?", ("TRUE",), "A test that is always true."),
)
ARENA_4 = people_arena("LADDER", {"F5": "Grade", "G5": "Medal", "I5": "Try this", "I6": '=IFS(5>9,"A",5>3,"B",TRUE,"C")'},
                       ("F6:G15",), headers=("F5:G5", "I5"))
MISSIONS_4 = (
    filled("F2-4.M1", 'Grades with nested IF: in F6 return "A" for a Score of 90+, "B" for 75+, otherwise "C". '
                      "Fill down to F15.", "IF inside the second IF slot.", "F6:F15",
           lambda c: f'=IF(C{_r(c)}>=90,"A",IF(C{_r(c)}>=75,"B","C"))', [grade(p[1]) for p in PEOPLE],
           items=("F2.nested_if",), wrong_for=lambda c: f'=IFS(C{_r(c)}>=90,"A",C{_r(c)}>=75,"B",TRUE,"C")',
           uses=("IF",)),
    filled("F2-4.M2", 'Medals with IFS: in G6 return "Gold" for 90+, "Silver" for 75+, "Bronze" for 60+, and "None" '
                      "otherwise (end with TRUE). Fill down to G15.", "TRUE catches the rest.", "G6:G15",
           lambda c: f'=IFS(C{_r(c)}>=90,"Gold",C{_r(c)}>=75,"Silver",C{_r(c)}>=60,"Bronze",TRUE,"None")',
           [medal(p[1]) for p in PEOPLE], items=("F2.ifs", "F2.ifs_true"),
           wrong_for=lambda c: f'=IFS(C{_r(c)}>=90,"Gold",C{_r(c)}>=75,"Silver",C{_r(c)}>=60,"Bronze")',
           uses=("IFS",)),
    find("F2-4.M3", 'What does =IFS(5>9,"A",5>3,"B",TRUE,"C") return? (It is written as text in the arena\'s I6 if '
                    "you want to try it.) Type the result.", "IFS stops at the first TRUE test.", "B",
         items=("F2.ifs",), wrong=("C",)),
)
STAGE_4 = Stage("F2-4", "Multi-Level", "handle three or more outcomes", ITEMS_4, MISSIONS_4, ARENA_4)

# ------------------------------------------------------------------------------------ F2-5 Error Shield
UNITS = [["Pens", 120, 10], ["Ink", 90, 0], ["Pads", 60, 4], ["Tape", 0, 0], ["Glue", 45, 9], ["Clips", 30, 0]]
NAMES = ["Ava", None, "Cy", None, "Eli"]
ENTRIES = [12, "12", 7.5, "n/a", 3]
ITEMS_5 = (
    Item("F2.iferror", "function", "IFERROR", "Replace any error with a value you choose.",
         "=IFERROR(A2/B2,0) shows 0 instead of #DIV/0!.", "Which function replaces any error with your own value?",
         ("IFERROR",), "IF plus ERROR."),
    Item("F2.ifna", "function", "IFNA", "Replace only #N/A, the 'not found' error.",
         "Ideal around lookups: other errors still show.", "Which function replaces only the #N/A error?",
         ("IFNA",), "IF plus NA."),
    Item("F2.isblank", "function", "ISBLANK", "TRUE if a cell is empty.", '=IF(ISBLANK(A2),"Missing","OK")',
         "Which function is TRUE when a cell is empty?", ("ISBLANK",), "IS plus BLANK."),
    Item("F2.isnumber", "function", "ISNUMBER", "TRUE if a value is a number (not text that looks like one).",
         '"12" typed as text is not a number.', "Which function is TRUE when a value is a number?",
         ("ISNUMBER",), "IS plus NUMBER."),
)
ARENA_5 = Arena(
    cells=merge(
        table("B5", ["Product", "Total", "Units"], UNITS), {"E5": "Per unit"},
        {"B14": "Lookup result →", "D14": Formula("=NA()", "#N/A", error_ok=True), "E14": "Shielded →"},
        table("B16", ["Name"], [[n] for n in NAMES]), {"C16": "Check"},
        table("D22", ["Entry"], [[e] for e in ENTRIES]), {"E22": "Type"},
    ),
    pass_code="SHIELD", inputs=("E6:E11", "F14", "C17:C21", "E23:E27"),
    headers=("B5:E5", "B16:C16", "D22:E22"), labels=("B14", "E14"),
)
MISSIONS_5 = (
    filled("F2-5.M1", "Per unit = Total ÷ Units, but some Units are 0. In E6 write =IFERROR(C6/D6,0) and fill down "
                      "to E11.", "Wrap the division in IFERROR.", "E6:E11",
           lambda c: f"=IFERROR(C{_r(c)}/D{_r(c)},0)", [t / u if u else 0 for _, t, u in UNITS],
           items=("F2.iferror",), wrong_for=lambda c: f"=C{_r(c)}/D{_r(c)}", uses=("IFERROR",)),
    formula("F2-5.M2", 'D14 shows #N/A (a failed lookup). In F14 write =IFNA(D14,"Missing").', "Only #N/A is replaced.",
            "F14", '=IFNA(D14,"Missing")', "Missing", items=("F2.ifna",), wrong=('=IFERROR(D14,"Missing")',),
            uses=("IFNA",)),
    filled("F2-5.M3", 'In C17 show "Missing" when the Name (B17) is empty, otherwise "OK". Use ISBLANK, then fill '
                      "down to C21.", "ISBLANK inside IF.", "C17:C21",
           lambda c: f'=IF(ISBLANK(B{_r(c)}),"Missing","OK")', ["Missing" if n is None else "OK" for n in NAMES],
           items=("F2.isblank",), wrong_for=lambda c: f'=IF(B{_r(c)}="","Missing","OK")', uses=("ISBLANK",)),
    filled("F2-5.M4", 'In E23 return "Number" when the Entry (D23) is a number, otherwise "Text". Use ISNUMBER, then '
                      "fill down to E27.", '"12" in quotes is text.', "E23:E27",
           lambda c: f'=IF(ISNUMBER(D{_r(c)}),"Number","Text")',
           ["Number" if isinstance(e, (int, float)) else "Text" for e in ENTRIES], items=("F2.isnumber",),
           wrong_for=lambda c: f'=IF(ISTEXT(D{_r(c)}),"Text","Number")', uses=("ISNUMBER",)),
)
STAGE_5 = Stage("F2-5", "Error Shield", "keep errors and blanks from breaking your sheet", ITEMS_5, MISSIONS_5, ARENA_5)

# ------------------------------------------------------------------------------------ Boss
BOSS_ARENA = Arena(
    cells=merge(
        table("B5", PEOPLE_HEADER, PEOPLE),
        {"F5": "Pass?", "G5": "Eligible", "H5": "Star", "I5": "Tier", "J5": "Status", "L5": "Not licensed?"},
        table("B20", ["Product", "Total", "Units"], UNITS), {"E20": "Per unit"},
        table("G20", ["Name"], [[n] for n in NAMES]), {"H20": "Check"},
    ),
    pass_code="LOGICLORD", inputs=("F6:J15", "L6", "E21:E26", "H21:H25"),
    headers=("B5:J5", "L5", "B20:E20", "G20:H20"), widths={"J": 12, "L": 14},
)
BOSS_MISSIONS = (
    filled("F2-B.M1", 'In F6 return "Pass" for a Score of 60 or more, otherwise "Fail". Fill down to F15.', "IF.",
           "F6:F15", lambda c: f'=IF(C{_r(c)}>=60,"Pass","Fail")', ["Pass" if p[1] >= 60 else "Fail" for p in PEOPLE],
           items=("F2.if",), wrong_for=lambda c: f'=IF(C{_r(c)}>60,"Pass","Fail")', uses=("IF",)),
    filled("F2-B.M2", 'In G6 return "Yes" when Age is 18+ AND Score is 70+, otherwise "No". Fill down to G15.', "AND.",
           "G6:G15", lambda c: f'=IF(AND(D{_r(c)}>=18,C{_r(c)}>=70),"Yes","No")',
           ["Yes" if p[2] >= 18 and p[1] >= 70 else "No" for p in PEOPLE], items=("F2.and",),
           wrong_for=lambda c: f'=IF(OR(D{_r(c)}>=18,C{_r(c)}>=70),"Yes","No")', uses=("AND",)),
    filled("F2-B.M3", 'In H6 return "Star" when Score is 95+ OR Age is 40+, otherwise "No". Fill down to H15.', "OR.",
           "H6:H15", lambda c: f'=IF(OR(C{_r(c)}>=95,D{_r(c)}>=40),"Star","No")',
           ["Star" if p[1] >= 95 or p[2] >= 40 else "No" for p in PEOPLE], items=("F2.or",),
           wrong_for=lambda c: f'=IF(AND(C{_r(c)}>=95,D{_r(c)}>=40),"Star","No")', uses=("OR",)),
    filled("F2-B.M4", 'In I6 use IFS: "Gold" for 90+, "Silver" for 75+, "Bronze" for 60+, otherwise "None". Fill down.',
           "End with TRUE.", "I6:I15",
           lambda c: f'=IFS(C{_r(c)}>=90,"Gold",C{_r(c)}>=75,"Silver",C{_r(c)}>=60,"Bronze",TRUE,"None")',
           [medal(p[1]) for p in PEOPLE], items=("F2.ifs", "F2.ifs_true"),
           wrong_for=lambda c: f'=IFS(C{_r(c)}>=90,"Gold",C{_r(c)}>=75,"Silver",C{_r(c)}>=60,"Bronze")',
           uses=("IFS",)),
    filled("F2-B.M5", 'In J6 return "VIP" for Score 80+ AND Age 18+, otherwise "Member" for Score 60+, otherwise '
                      '"Guest". Fill down to J15.', "AND inside the first IF.", "J6:J15",
           lambda c: f'=IF(AND(C{_r(c)}>=80,D{_r(c)}>=18),"VIP",IF(C{_r(c)}>=60,"Member","Guest"))',
           ["VIP" if p[1] >= 80 and p[2] >= 18 else "Member" if p[1] >= 60 else "Guest" for p in PEOPLE],
           items=("F2.nested_if", "F2.and"),
           wrong_for=lambda c: f'=IF(C{_r(c)}>=80,"VIP",IF(C{_r(c)}>=60,"Member","Guest"))', uses=("IF", "AND")),
    formula("F2-B.M6", 'In L6 return TRUE when Ava (row 6) is NOT licensed (E6 is not "Yes"). Use NOT.', "NOT(…)",
            "L6", '=NOT(E6="Yes")', True, items=("F2.not",), wrong=('=E6="Yes"',), uses=("NOT",)),
    filled("F2-B.M7", "In E21 divide Total by Units with an IFERROR shield (0 on errors). Fill down to E26.",
           "IFERROR(C21/D21,0)", "E21:E26", lambda c: f"=IFERROR(C{_r(c)}/D{_r(c)},0)",
           [t / u if u else 0 for _, t, u in UNITS], items=("F2.iferror",), wrong_for=lambda c: f"=C{_r(c)}/D{_r(c)}",
           uses=("IFERROR",)),
    filled("F2-B.M8", 'In H21 show "Missing" when the Name (G21) is empty, otherwise "OK" (use ISBLANK). Fill down to '
                      "H25.", "ISBLANK.", "H21:H25", lambda c: f'=IF(ISBLANK(G{_r(c)}),"Missing","OK")',
           ["Missing" if n is None else "OK" for n in NAMES], items=("F2.isblank",),
           wrong_for=lambda c: f'=IF(ISBLANK(G{_r(c)}),"OK","Missing")', uses=("ISBLANK",)),
)

WORLD = World(
    code="F2", track="F", order=4, title="Logic",
    tagline="Make formulas decide: comparisons, IF, AND/OR/NOT, IFS and error shields.",
    file_name="04 Formulas 2 - Logic.xlsx",
    stages=(STAGE_1, STAGE_2, STAGE_3, STAGE_4, STAGE_5),
    boss=Boss(BOSS_MISSIONS, BOSS_ARENA, par_minutes=15),
)
