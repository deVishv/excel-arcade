"""Formulas 5 · Text — cut, clean, search and assemble text with formulas."""
import datetime as dt

from ..model import Arena, Boss, Item, Stage, World, column, formula, merge

# ------------------------------------------------------------------------------------ F5-1 Cut & Splice
CODE = "AB-1234-X"
ITEMS_1 = (
    Item("F5.left", "function", "LEFT", "LEFT(text, n): the first n characters.", '=LEFT("AB-1234-X",2) gives AB.',
         "Which function returns characters from the start of a text?", ("LEFT",), "The start side."),
    Item("F5.right", "function", "RIGHT", "RIGHT(text, n): the last n characters.", '=RIGHT("AB-1234-X",1) gives X.',
         "Which function returns characters from the end of a text?", ("RIGHT",), "The end side."),
    Item("F5.mid", "function", "MID", "MID(text, start, n): n characters from position start.",
         '=MID("AB-1234-X",4,4) gives 1234.', "Which function returns characters from the middle of a text?",
         ("MID",), "Short for middle."),
    Item("F5.len", "function", "LEN", "LEN(text): how many characters, spaces included.", "Great for spotting extra "
         "spaces.", "Which function counts the characters in a text?", ("LEN",), "Short for length."),
    Item("F5.amp", "concept", "&", 'Join text with &: =B13&" "&C13.', 'Add " " between pieces for a space.',
         "Which character joins pieces of text in a formula?", ("&", "ampersand"), "Shift+7."),
)
ARENA_1 = Arena(
    cells={"B5": "Code", "B6": CODE, "D5": "Task", "D6": "First 2 characters", "D7": "Last character",
           "D8": "The 4 digits", "D9": "Length", "B12": "First", "C12": "Last", "B13": "Grace", "C13": "Hopper",
           "D13": "Full name →"},
    pass_code="SPLICE", inputs=("E6:E9", "E13"), headers=("B5", "D5", "B12:C12"), labels=("D13",), widths={"D": 20, "E": 18},
)
MISSIONS_1 = (
    formula("F5-1.M1", "In E6 return the first 2 characters of the code in B6 with LEFT.", "=LEFT(B6,2)", "E6",
            "=LEFT(B6,2)", CODE[:2], items=("F5.left",), wrong=("=LEFT(B6,3)",), uses=("LEFT",), case_sensitive=True),
    formula("F5-1.M2", "In E7 return the last character of B6 with RIGHT.", "=RIGHT(B6,1)", "E7", "=RIGHT(B6,1)",
            CODE[-1], items=("F5.right",), wrong=("=RIGHT(B6,2)",), uses=("RIGHT",), case_sensitive=True),
    formula("F5-1.M3", "In E8 return the 4 digits (they start at character 4) with MID.", "=MID(B6,4,4)", "E8",
            "=MID(B6,4,4)", CODE[3:7], items=("F5.mid",), wrong=("=MID(B6,3,4)",), uses=("MID",), case_sensitive=True),
    formula("F5-1.M4", "In E9 count the characters in B6 with LEN.", "=LEN(B6)", "E9", "=LEN(B6)", len(CODE),
            items=("F5.len",), wrong=("=LEN(B6)-1",), uses=("LEN",)),
    formula("F5-1.M5", 'In E13 join B13 and C13 with a space between: =B13&" "&C13.', 'Three pieces: B13, " ", C13.',
            "E13", '=B13&" "&C13', "Grace Hopper", items=("F5.amp",), wrong=("=B13&C13",), contains=("&",),
            case_sensitive=True),
)
STAGE_1 = Stage("F5-1", "Cut & Splice", "cut pieces out of text and glue them together", ITEMS_1, MISSIONS_1, ARENA_1)

# ------------------------------------------------------------------------------------ F5-2 Clean Up
MESSY = "  ada   LOVELACE "
ITEMS_2 = (
    Item("F5.trim", "function", "TRIM", "Remove extra spaces: leading, trailing and doubles.",
         "Imported data is full of hidden spaces.", "Which function removes extra spaces from text?", ("TRIM",),
         "Trims the edges."),
    Item("F5.upper", "function", "UPPER", "Convert text to CAPITALS.", "Handy for codes and IDs.",
         "Which function converts text to all capitals?", ("UPPER",), "Upper case."),
    Item("F5.lower", "function", "LOWER", "Convert text to lowercase.", "Good for email addresses.",
         "Which function converts text to all lowercase?", ("LOWER",), "Lower case."),
    Item("F5.proper", "function", "PROPER", "Capitalize Each Word.", "Combine with TRIM to tidy names.",
         "Which function capitalizes the first letter of each word?", ("PROPER",), "Proper names."),
    Item("F5.substitute", "function", "SUBSTITUTE", "SUBSTITUTE(text, old, new): replace every old with new.",
         '=SUBSTITUTE(A2,"-","/") turns 2026-03-15 into 2026/03/15.', "Which function replaces every occurrence of "
         "some text with other text?", ("SUBSTITUTE",), "Swap one thing for another."),
)
ARENA_2 = Arena(
    cells={"B5": "Raw text", "B6": MESSY, "B7": "grace hopper", "B8": "ALAN TURING", "B9": "2026-03-15",
           "C5": "Task", "C6": "Trim it", "C7": "Capitals", "C8": "Lowercase", "C9": "Slashes", "C10": "Tidy B6 name"},
    pass_code="CLEANUP", inputs=("D6:D10",), headers=("B5:C5",), widths={"B": 22, "C": 16, "D": 20},
)
MISSIONS_2 = (
    formula("F5-2.M1", "In D6 remove the extra spaces from B6 with TRIM.", "=TRIM(B6)", "D6", "=TRIM(B6)",
            " ".join(MESSY.split()), items=("F5.trim",), wrong=("=B6",), uses=("TRIM",), case_sensitive=True),
    formula("F5-2.M2", "In D7 convert B7 to capitals with UPPER.", "=UPPER(B7)", "D7", "=UPPER(B7)", "GRACE HOPPER",
            items=("F5.upper",), wrong=("=PROPER(B7)",), uses=("UPPER",), case_sensitive=True),
    formula("F5-2.M3", "In D8 convert B8 to lowercase with LOWER.", "=LOWER(B8)", "D8", "=LOWER(B8)", "alan turing",
            items=("F5.lower",), wrong=("=PROPER(B8)",), uses=("LOWER",), case_sensitive=True),
    formula("F5-2.M4", 'In D9 replace every "-" in B9 with "/" using SUBSTITUTE.', '=SUBSTITUTE(B9,"-","/")', "D9",
            '=SUBSTITUTE(B9,"-","/")', "2026/03/15", items=("F5.substitute",), wrong=('=SUBSTITUTE(B9,"-","")',),
            uses=("SUBSTITUTE",)),
    formula("F5-2.M5", "In D10 tidy the name in B6: remove the extra spaces AND capitalize each word in one formula.",
            "PROPER around TRIM.", "D10", "=PROPER(TRIM(B6))", "Ada Lovelace", items=("F5.proper", "F5.trim"),
            wrong=("=PROPER(B6)",), uses=("PROPER", "TRIM"), case_sensitive=True),
)
STAGE_2 = Stage("F5-2", "Clean Up", "tidy messy text", ITEMS_2, MISSIONS_2, ARENA_2)

# ------------------------------------------------------------------------------------ F5-3 Find the Gem
EMAIL, NAME = "kim@arcade.io", "Grace Hopper"
ITEMS_3 = (
    Item("F5.find", "function", "FIND", "FIND(what, text): the position of what. Case-sensitive.",
         '=FIND("@","kim@arcade.io") gives 4.', "Which function returns the position of text, matching case?",
         ("FIND",), "It finds things."),
    Item("F5.search", "function", "SEARCH", "SEARCH(what, text): like FIND, but ignores case and allows wildcards.",
         "Use SEARCH when you don't care about capitals.", "Which function returns a position while ignoring case?",
         ("SEARCH",), "Like FIND, but case-blind."),
    Item("F5.left_find", "concept", "LEFT + FIND", '=LEFT(A2,FIND("@",A2)-1) takes everything before the @.',
         "FIND supplies the cut point; -1 drops the @ itself.", "Which function supplies the cut position inside "
         '=LEFT(A2, ____("@",A2)-1)?', ("FIND",), "The position finder."),
)
ARENA_3 = Arena(
    cells={"B5": "Text", "B6": EMAIL, "B7": NAME, "C5": "Task", "C6": "Position of @", "C7": "Position of ARCADE",
           "C8": "Username (before @)", "C9": "Last name"},
    pass_code="GEMFIND", inputs=("D6:D9",), headers=("B5:C5",), widths={"B": 18, "C": 20, "D": 16},
)
MISSIONS_3 = (
    formula("F5-3.M1", 'In D6 find the position of "@" in B6 with FIND.', '=FIND("@",B6)', "D6", '=FIND("@",B6)',
            EMAIL.index("@") + 1, items=("F5.find",), wrong=('=FIND(".",B6)',), uses=("FIND",)),
    formula("F5-3.M2", 'In D7 find where "ARCADE" starts in B6, ignoring case. Use SEARCH (FIND would fail here).',
            "SEARCH is case-blind.", "D7", '=SEARCH("ARCADE",B6)', EMAIL.lower().index("arcade") + 1,
            items=("F5.search",), wrong=('=FIND("ARCADE",B6)',), uses=("SEARCH",)),
    formula("F5-3.M3", 'In D8 return the username: everything in B6 before the "@". Combine LEFT and FIND.',
            '=LEFT(B6,FIND("@",B6)-1)', "D8", '=LEFT(B6,FIND("@",B6)-1)', EMAIL.split("@")[0],
            items=("F5.left_find", "F5.left"), wrong=('=LEFT(B6,FIND("@",B6))',), uses=("LEFT", "FIND"),
            case_sensitive=True),
    formula("F5-3.M4", 'In D9 return the last name from B7: everything after the space. Use MID and FIND.',
            '=MID(B7,FIND(" ",B7)+1,100)', "D9", '=MID(B7,FIND(" ",B7)+1,100)', NAME.split(" ")[1],
            items=("F5.find", "F5.mid"), wrong=('=MID(B7,FIND(" ",B7),100)',), uses=("MID", "FIND"),
            case_sensitive=True),
)
STAGE_3 = Stage("F5-3", "Find the Gem", "locate text inside text and cut around it", ITEMS_3, MISSIONS_3, ARENA_3)

# ------------------------------------------------------------------------------------ F5-4 Assemble
TAGS = ["red", "green", None, "blue", "gold"]
ITEMS_4 = (
    Item("F5.textjoin", "function", "TEXTJOIN", "TEXTJOIN(delimiter, ignore_empty, range) joins a whole range.",
         '=TEXTJOIN(", ",TRUE,B6:B10) skips blanks.', "Which function joins a range of text with a delimiter?",
         ("TEXTJOIN",), "TEXT plus JOIN."),
    Item("F5.text", "function", "TEXT", "TEXT(value, format) turns a number or date into formatted text.",
         '=TEXT(B12,"yyyy-mm-dd") gives 2026-03-15.', "Which function turns a number or date into formatted text?",
         ("TEXT",), "Four letters."),
    Item("F5.value", "function", "VALUE", "VALUE(text) turns number-looking text into a real number.",
         'Text "42" can\'t be summed until VALUE converts it.', "Which function turns text that looks like a number "
         "into a number?", ("VALUE",), "The opposite of TEXT."),
)
ARENA_4 = Arena(
    cells=merge({"B5": "Tags"}, column("B6", TAGS),
                {"B11": "Date", "B12": dt.date(2026, 3, 15), "B13": "Text number", "B14": "42", "B15": "Amount",
                 "B16": 1234.5, "C5": "Task", "C6": "Join the tags", "C12": "Date as yyyy-mm-dd",
                 "C14": "Make it a number", "C16": "Label the amount"}),
    pass_code="ASSEMBLE", inputs=("D6", "D12", "D14", "D16"), headers=("B5", "C5"), labels=("B11", "B13", "B15"),
    number_formats={"B12": "d-mmm-yyyy"}, widths={"B": 14, "C": 20, "D": 26},
)
MISSIONS_4 = (
    formula("F5-4.M1", 'In D6 join the tags in B6:B10 with ", " and skip the blank one: =TEXTJOIN(", ",TRUE,B6:B10).',
            "TRUE ignores empty cells.", "D6", '=TEXTJOIN(", ",TRUE,B6:B10)', ", ".join(t for t in TAGS if t),
            items=("F5.textjoin",), wrong=('=TEXTJOIN(", ",FALSE,B6:B10)',), uses=("TEXTJOIN",), case_sensitive=True),
    formula("F5-4.M2", 'In D12 show the date in B12 as text in the format yyyy-mm-dd.', '=TEXT(B12,"yyyy-mm-dd")',
            "D12", '=TEXT(B12,"yyyy-mm-dd")', "2026-03-15", items=("F5.text",), wrong=('=TEXT(B12,"dd-mm-yyyy")',),
            uses=("TEXT",)),
    formula("F5-4.M3", "B14 holds the text \"42\". In D14 turn it into a real number with VALUE.", "=VALUE(B14)",
            "D14", "=VALUE(B14)", 42, items=("F5.value",), wrong=("=B14",), uses=("VALUE",)),
    formula("F5-4.M4", 'In D16 build the label Total: $1,234.50 from B16 using & and TEXT with the format '
                       '"$#,##0.00".', '="Total: "&TEXT(B16,"$#,##0.00")', "D16", '="Total: "&TEXT(B16,"$#,##0.00")',
            "Total: $1,234.50", items=("F5.text", "F5.amp"), wrong=('="Total: "&B16',), uses=("TEXT",),
            case_sensitive=True),
)
STAGE_4 = Stage("F5-4", "Assemble", "join, format and convert text", ITEMS_4, MISSIONS_4, ARENA_4)

# ------------------------------------------------------------------------------------ Boss
BOSS_ARENA = Arena(
    cells=merge(
        {"B5": "Raw", "B6": "  jo   PARK ", "B7": "QX-5512-B", "B8": "lee@quest.dev", "B9": "Ada Lovelace",
         "B10": "2026/12/31", "B11": "77", "B12": dt.date(2026, 7, 4)},
        {"C5": "Task", "C6": "Tidy name", "C7": "Middle digits", "C8": "Username", "C9": "Last name",
         "C10": "Dashes instead of /", "C11": "As a number", "C12": "Date as dd/mm/yyyy", "C13": "Tag list"},
        {"B14": "Tags"}, column("B15", ["alpha", None, "beta", "gamma"]),
    ),
    pass_code="WORDSMITH", inputs=("D6:D13",), headers=("B5:C5",), labels=("B14",),
    number_formats={"B12": "d-mmm-yyyy"}, widths={"B": 18, "C": 20, "D": 24},
)
BOSS_MISSIONS = (
    formula("F5-B.M1", "In D6 tidy B6: no extra spaces, each word capitalized.", "PROPER(TRIM(…)).", "D6",
            "=PROPER(TRIM(B6))", "Jo Park", items=("F5.proper", "F5.trim"), wrong=("=TRIM(B6)",),
            uses=("PROPER", "TRIM"), case_sensitive=True),
    formula("F5-B.M2", "In D7 return the 4 digits in the middle of B7 (they start at character 4).", "MID.", "D7",
            "=MID(B7,4,4)", "5512", items=("F5.mid",), wrong=("=MID(B7,4,3)",), uses=("MID",)),
    formula("F5-B.M3", 'In D8 return the username in B8 (everything before "@").', "LEFT and FIND.", "D8",
            '=LEFT(B8,FIND("@",B8)-1)', "lee", items=("F5.left_find",), wrong=('=LEFT(B8,FIND("@",B8))',),
            uses=("LEFT", "FIND"), case_sensitive=True),
    formula("F5-B.M4", "In D9 return the last name from B9 (after the space).", "MID and FIND.", "D9",
            '=MID(B9,FIND(" ",B9)+1,100)', "Lovelace", items=("F5.find",), wrong=('=LEFT(B9,FIND(" ",B9)-1)',),
            uses=("MID", "FIND"), case_sensitive=True),
    formula("F5-B.M5", 'In D10 replace every "/" in B10 with "-".', "SUBSTITUTE.", "D10", '=SUBSTITUTE(B10,"/","-")',
            "2026-12-31", items=("F5.substitute",), wrong=('=SUBSTITUTE(B10,"/","")',), uses=("SUBSTITUTE",)),
    formula("F5-B.M6", "In D11 turn the text in B11 into a number.", "VALUE.", "D11", "=VALUE(B11)", 77,
            items=("F5.value",), wrong=("=B11",), uses=("VALUE",)),
    formula("F5-B.M7", 'In D12 show the date in B12 as text like 04/07/2026 (format "dd/mm/yyyy").', "TEXT.", "D12",
            '=TEXT(B12,"dd/mm/yyyy")', "04/07/2026", items=("F5.text",), wrong=('=TEXT(B12,"mm/dd/yyyy")',),
            uses=("TEXT",)),
    formula("F5-B.M8", 'In D13 join the tags in B15:B18 with " | ", skipping the blank.', "TEXTJOIN with TRUE.", "D13",
            '=TEXTJOIN(" | ",TRUE,B15:B18)', "alpha | beta | gamma", items=("F5.textjoin",),
            wrong=('=TEXTJOIN(" | ",FALSE,B15:B18)',), uses=("TEXTJOIN",), case_sensitive=True),
)

WORLD = World(
    code="F5", track="F", order=9, title="Text",
    tagline="Cut, clean, search and assemble text with formulas.",
    file_name="09 Formulas 5 - Text.xlsx",
    stages=(STAGE_1, STAGE_2, STAGE_3, STAGE_4),
    boss=Boss(BOSS_MISSIONS, BOSS_ARENA, par_minutes=15),
)
