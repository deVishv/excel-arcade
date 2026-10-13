"""Shortcuts 2 · Enter & Edit — type, fill, copy and stamp data at speed."""
from ..checks import all_equal, cells_equal, line_break, time_constant, today_constant, values_not_formulas
from ..model import Arena, Boss, Fixture, Formula, Item, Stage, World, do, filled, merge, row, table
from ..refs import cells_in

# ------------------------------------------------------------------------------------ S2-1 Quick Entry
ITEMS_1 = (
    Item("S2.shift_enter", "shortcut", "Shift+Enter", "Confirm the entry and move UP one cell.",
         "Enter alone moves down.", "Which keys confirm an entry and move up one cell?", ("Shift+Enter",),
         "Enter plus Shift."),
    Item("S2.tab", "shortcut", "Tab / Shift+Tab", "Confirm the entry and move right (Shift+Tab moves left).",
         "On a protected sheet, Tab hops between input cells.",
         "Which key confirms an entry and moves one cell to the right?", ("Tab",), "The key above Caps Lock."),
    Item("S2.ctrl_enter", "shortcut", "Ctrl+Enter", "Fill every selected cell with what you just typed.",
         "Select a range, type once, press Ctrl+Enter: done.",
         "Which keys fill every selected cell with what you typed?", ("Ctrl+Enter",), "Enter plus Ctrl."),
    Item("S2.alt_enter", "shortcut", "Alt+Enter", "Start a new line inside the same cell.",
         "Great for addresses and notes.", "Which keys start a new line inside the same cell?", ("Alt+Enter",),
         "Enter plus Alt."),
    Item("S2.esc", "shortcut", "Esc", "Cancel what you are typing; the cell stays unchanged.",
         "Esc also closes menus and dialogs.", "Which key cancels an entry and leaves the cell unchanged?",
         ("Esc",), "The top-left key."),
)
ARENA_1 = Arena(
    cells={"B5": "STATUS ▼", "D5": "TWO LINES ▼", "F5": "TAB ROW ▶", "F10": "UP AND DOWN ▼"},
    pass_code="QUICKSTEP", inputs=("B6:B15", "D6", "F6:H6", "F11:F12"), headers=("B5", "D5"),
    labels=("F5", "F10"), widths={"D": 18},
)
MISSIONS_1 = (
    do("S2-1.M1", "In the arena, select B6:B15 (click B6, then Shift+click B15), type DONE and press Ctrl+Enter. "
                  "Every selected cell gets DONE.", "Ctrl+Enter instead of Enter.", all_equal(cells_in("B6:B15"), "DONE"),
       solve=[Fixture("type", "«@B6:B15»", "DONE")], wrong=[[Fixture("type", "«@B6»", "DONE")]],
       items=("S2.ctrl_enter",), arena_cell="B6"),
    do("S2-1.M2", "In D6 type Line 1, press Alt+Enter, type Line 2, then press Enter.", "Alt+Enter adds the break.",
       line_break("D6", "Line 1", "Line 2"), solve=[Fixture("linebreak", "«@D6»", ("Line 1", "Line 2"))],
       wrong=[[Fixture("type", "«@D6»", "Line 1 Line 2")]], items=("S2.alt_enter",), arena_cell="D6"),
    do("S2-1.M3", "In F6 type Name, press Tab, type Score, press Tab, type Level, then press Enter.",
       "Tab moves one cell right.", cells_equal({"F6": "Name", "G6": "Score", "H6": "Level"}),
       solve=[Fixture("type", "«@F6»", "Name"), Fixture("type", "«@G6»", "Score"), Fixture("type", "«@H6»", "Level")],
       wrong=[[Fixture("type", "«@F6»", "Name Score Level")]], items=("S2.tab",), arena_cell="F6"),
    do("S2-1.M4", "In F12 type Bottom and press Shift+Enter: you move UP to F11. Type Top and press Enter.",
       "Shift+Enter goes up.", cells_equal({"F12": "Bottom", "F11": "Top"}),
       solve=[Fixture("type", "«@F12»", "Bottom"), Fixture("type", "«@F11»", "Top")],
       wrong=[[Fixture("type", "«@F11»", "Bottom")]], items=("S2.shift_enter",), arena_cell="F12"),
)
STAGE_1 = Stage("S2-1", "Quick Entry", "type and move without reaching for the mouse", ITEMS_1, MISSIONS_1, ARENA_1)

# ------------------------------------------------------------------------------------ S2-2 Clone Machine
MONTHS6 = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
BUDGET = {"Food": [120, 130, 125, 140, 150, 135], "Rent": [800, 800, 800, 820, 820, 820],
          "Fun": [60, 90, 45, 70, 110, 80], "Travel": [0, 0, 300, 0, 450, 0]}
TOTALS = [sum(v[i] for v in BUDGET.values()) for i in range(6)]
COLS = "CDEFGH"
ITEMS_2 = (
    Item("S2.copy", "shortcut", "Ctrl+C", "Copy the selected cells.", "A moving border shows what's copied; Esc clears it.",
         "Which keys copy the selection?", ("Ctrl+C",), "C for Copy."),
    Item("S2.cut", "shortcut", "Ctrl+X", "Cut the selected cells, ready to move them.",
         "Paste with Ctrl+V to finish the move.", "Which keys cut the selection?", ("Ctrl+X",), "X looks like scissors."),
    Item("S2.paste", "shortcut", "Ctrl+V", "Paste what you copied or cut.", "Paste into the top-left destination cell.",
         "Which keys paste?", ("Ctrl+V",), "Next to C on the keyboard."),
    Item("S2.paste_special", "shortcut", "Ctrl+Alt+V", "Open Paste Special: paste only values, formats and more.",
         "Ctrl+Alt+V, then V, then Enter pastes values only.", "Which keys open Paste Special?", ("Ctrl+Alt+V",),
         "Paste plus Alt."),
    Item("S2.ctrl_r", "shortcut", "Ctrl+R", "Fill Right: copy the left cell into the selected cells to its right.",
         "The twin of Ctrl+D (Fill Down).", "Which keys copy the left cell into the selected cells to its right?",
         ("Ctrl+R",), "R for Right."),
    Item("S2.undo", "shortcut", "Ctrl+Z", "Undo the last action.", "Press again to undo further back.",
         "Which keys undo the last action?", ("Ctrl+Z",), "The bottom-left letter."),
    Item("S2.redo", "shortcut", "Ctrl+Y", "Redo, or repeat the last action.",
         "After an undo it redoes; otherwise it repeats your last action.", "Which keys redo or repeat the last action?",
         ("Ctrl+Y",), "The letter after X."),
)
ARENA_2 = Arena(
    cells=merge(
        {"B5": "Budget"}, row("C5", MONTHS6),
        {"B6": "TOTAL", "C6": Formula("=SUM(C7:C10)", TOTALS[0])},
        *[merge({f"B{7 + i}": cat}, row(f"C{7 + i}", vals)) for i, (cat, vals) in enumerate(BUDGET.items())],
        {"B13": "SNAPSHOT", "B15": "LIVE"},
        {f"{c}15": Formula(f"=SUM({c}7:{c}10)", TOTALS[i]) for i, c in enumerate(COLS)},
        table("B20", ["Player", "Score", "Rank"], [[None, None, None], ["Zelda", 980, 1]]),
    ),
    pass_code="CLONE", inputs=("D6:H6", "C13:H13"), headers=("B5:H5", "B20:D20"), labels=("B6", "B13", "B15"),
)
MISSIONS_2 = (
    filled("S2-2.M1", "C6 holds a SUM formula. In the arena select C6:H6 and press Ctrl+R to fill it to the right.",
           "Select first, then Ctrl+R.", "D6:H6", lambda c: f"=SUM({c[0]}7:{c[0]}10)", TOTALS[1:],
           items=("S2.ctrl_r",), wrong_for=lambda c: TOTALS[COLS.index(c[0])], uses=("SUM",)),
    do("S2-2.M2", "Copy the LIVE row (C15:H15) with Ctrl+C. Click C13, press Ctrl+Alt+V, choose Values (V) and press "
                  "Enter. SNAPSHOT keeps the numbers even if LIVE changes.", "Paste Special, then Values.",
       values_not_formulas({f"{c}13": TOTALS[i] for i, c in enumerate(COLS)}),
       solve=[Fixture("copy_values", "«@C13:H13»", None, ("«@C15:H15»",))],
       wrong=[[Fixture("copy", "«@C15:H15»", None, ("«@C13»",))]], items=("S2.copy", "S2.paste_special"),
       arena_cell="C13"),
    do("S2-2.M3", "Zelda's row (B22:D22) belongs one row up. Select B22:D22, press Ctrl+X, click B21 and press Ctrl+V.",
       "Cut, then paste on B21.", 'AND(«#B21»="Zelda",«#C21»=980,«#D21»=1,COUNTA(«#B22:D22»)=0)',
       solve=[Fixture("cut_paste", "«@B22:D22»", None, ("«@B21»",))],
       wrong=[[Fixture("copy", "«@B22:D22»", None, ("«@B21»",))]], items=("S2.cut", "S2.paste"), arena_cell="B21"),
)
STAGE_2 = Stage("S2-2", "Clone Machine", "copy, move and fill without retyping", ITEMS_2, MISSIONS_2, ARENA_2)

# ------------------------------------------------------------------------------------ S2-3 Stamps & Smart Fill
NAMES = ["Ada Lovelace", "Alan Turing", "Grace Hopper", "Katherine Johnson", "Tim Berners-Lee",
         "Margaret Hamilton", "Linus Torvalds", "Hedy Lamarr"]
FIRSTS = [n.split()[0] for n in NAMES]
ITEMS_3 = (
    Item("S2.date", "shortcut", "Ctrl+;", "Type today's date as a fixed value.",
         "Unlike =TODAY(), it never changes later.", "Which keys type today's date as a fixed value?",
         ("Ctrl+;", "Ctrl+Semicolon"), "Ctrl plus the semicolon key."),
    Item("S2.time", "shortcut", "Ctrl+Shift+:", "Type the current time as a fixed value.",
         "Stamp a START and a FINISH time to time yourself.", "Which keys type the current time as a fixed value?",
         ("Ctrl+Shift+:", "Ctrl+Shift+;", "Ctrl+:", "Ctrl+Shift+Colon"), "The date keys plus Shift."),
    Item("S2.flash_fill", "shortcut", "Ctrl+E", "Flash Fill: Excel spots your pattern and fills the column.",
         "Type one or two examples first, then press Ctrl+E.", "Which keys run Flash Fill?", ("Ctrl+E",),
         "E for Example."),
    Item("S2.alt_down", "shortcut", "Alt+↓", "Open a cell's dropdown list.", "Then choose with the arrows and Enter.",
         "Which keys open the dropdown list of a cell?", ("Alt+Down",), "Alt plus an arrow."),
)
ARENA_3 = Arena(
    cells=merge({"B6": "Today's date →", "B8": "Time now →"},
                table("B11", ["Full name", "First name"], [[n, None] for n in NAMES]), {"B22": "Medal →"}),
    pass_code="STAMP", inputs=("C6", "C8", "C12:C19", "C22"), headers=("B11:C11",), labels=("B6", "B8", "B22"),
    number_formats={"C6": "d-mmm-yyyy", "C8": "h:mm AM/PM"}, validations={"C22": ("Bronze", "Silver", "Gold")},
    widths={"B": 20, "C": 18},
)
MISSIONS_3 = (
    do("S2-3.M1", "In the arena select C6, press Ctrl+; and then Enter. Excel types today's date as a fixed value.",
       "Ctrl and the semicolon key.", today_constant("C6"), solve=[Fixture("today", "«@C6»")],
       wrong=[[Fixture("formula", "«@C6»", "=TODAY()")]], items=("S2.date",), arena_cell="C6", volatile=True),
    do("S2-3.M2", "Select C8, press Ctrl+Shift+: and then Enter.", "The date keys plus Shift.", time_constant("C8"),
       solve=[Fixture("now_time", "«@C8»")], wrong=[[Fixture("formula", "«@C8»", "=NOW()-TODAY()")]],
       items=("S2.time",), arena_cell="C8"),
    do("S2-3.M3", "In C12 type Ada (the first name in B12) and press Enter. Then, with C13 selected, press Ctrl+E: "
                  "Flash Fill completes the column.", "One example is enough.",
       values_not_formulas({f"C{12 + i}": f for i, f in enumerate(FIRSTS)}),
       solve=[Fixture("type", "«@C12»", "Ada"), Fixture("flash_fill", "«@C12:C19»")],
       wrong=[[Fixture("type", "«@C12»", "Ada")]], items=("S2.flash_fill",), arena_cell="C12"),
    do("S2-3.M4", "Select C22, press Alt+↓ to open its list, choose Gold and press Enter.", "Alt plus the down arrow.",
       cells_equal({"C22": "Gold"}), solve=[Fixture("type", "«@C22»", "Gold")],
       wrong=[[Fixture("type", "«@C22»", "Silver")]], items=("S2.alt_down",), arena_cell="C22"),
)
STAGE_3 = Stage("S2-3", "Stamps & Smart Fill", "stamp dates and times, let Excel finish your pattern",
                ITEMS_3, MISSIONS_3, ARENA_3)

# ------------------------------------------------------------------------------------ Boss
BOSS_NAMES = ["Ada Lovelace", "Alan Turing", "Grace Hopper", "Hedy Lamarr", "Linus Torvalds", "Annie Easley"]
LASTS = [n.split(" ", 1)[1] for n in BOSS_NAMES]
QDATA = {"Red": [10, 14, 9, 12], "Blue": [8, 11, 15, 7], "Gold": [13, 6, 10, 16]}
QT = [sum(v[i] for v in QDATA.values()) for i in range(4)]
QCOLS = "CDEF"
BOSS_ARENA = Arena(
    cells=merge(
        {"B5": "READY ▼", "D5": "ADDRESS ▼", "F5": "SIGNED ON ▼", "F8": "TIER ▼"},
        table("I5", ["Full name", "Last name"], [[n, None] for n in BOSS_NAMES]),
        table("L5", ["Hero", "Power", "Level"], [[None, None, None], ["Nova", 88, 3]]),
        {"B14": "Team"}, row("C14", ["Q1", "Q2", "Q3", "Q4"]),
        {"B15": "TOTAL", "C15": Formula("=SUM(C16:C18)", QT[0])},
        *[merge({f"B{16 + i}": team}, row(f"C{16 + i}", vals)) for i, (team, vals) in enumerate(QDATA.items())],
        {"B21": "SNAPSHOT", "B23": "LIVE"},
        {f"{c}23": Formula(f"=SUM({c}16:{c}18)", QT[i]) for i, c in enumerate(QCOLS)},
    ),
    pass_code="EDITOR", inputs=("B6:B12", "D6", "F6", "F9", "D15:F15", "C21:F21", "J6:J11"),
    headers=("B5", "D5", "I5:J5", "L5:N5", "B14:F14"), labels=("F5", "F8", "B15", "B21", "B23"),
    number_formats={"F6": "d-mmm-yyyy"}, validations={"F9": ("Gold", "Platinum", "Diamond")},
    widths={"D": 18, "I": 18, "J": 16},
)
BOSS_MISSIONS = (
    do("S2-B.M1", "In the Boss Arena select B6:B12, type READY and press Ctrl+Enter.", "Ctrl+Enter fills the selection.",
       all_equal(cells_in("B6:B12"), "READY"), solve=[Fixture("type", "«@B6:B12»", "READY")],
       wrong=[[Fixture("type", "«@B6»", "READY")]], items=("S2.ctrl_enter",), arena_cell="B6"),
    do("S2-B.M2", "In D6 type Street, press Alt+Enter, type City, then press Enter.", "Alt+Enter inside the cell.",
       line_break("D6", "Street", "City"), solve=[Fixture("linebreak", "«@D6»", ("Street", "City"))],
       wrong=[[Fixture("type", "«@D6»", "Street City")]], items=("S2.alt_enter",), arena_cell="D6"),
    filled("S2-B.M3", "C15 sums the Q1 column. Select C15:F15 and press Ctrl+R.", "Fill Right.", "D15:F15",
           lambda c: f"=SUM({c[0]}16:{c[0]}18)", QT[1:], items=("S2.ctrl_r",),
           wrong_for=lambda c: QT[QCOLS.index(c[0])], uses=("SUM",)),
    do("S2-B.M4", "Copy LIVE (C23:F23) and paste only its values into SNAPSHOT (C21) with Ctrl+Alt+V, V.",
       "Paste Special → Values.", values_not_formulas({f"{c}21": QT[i] for i, c in enumerate(QCOLS)}),
       solve=[Fixture("copy_values", "«@C21:F21»", None, ("«@C23:F23»",))],
       wrong=[[Fixture("copy", "«@C23:F23»", None, ("«@C21»",))]], items=("S2.paste_special",), arena_cell="C21"),
    do("S2-B.M5", "Select F6 and stamp today's date with Ctrl+;, then Enter.", "Ctrl+;", today_constant("F6"),
       solve=[Fixture("today", "«@F6»")], wrong=[[Fixture("formula", "«@F6»", "=TODAY()")]], items=("S2.date",),
       arena_cell="F6", volatile=True),
    do("S2-B.M6", "In J6 type Lovelace (the last name in I6), then select J7 and press Ctrl+E.", "Flash Fill.",
       values_not_formulas({f"J{6 + i}": last for i, last in enumerate(LASTS)}),
       solve=[Fixture("type", "«@J6»", "Lovelace"), Fixture("flash_fill", "«@J6:J11»")],
       wrong=[[Fixture("type", "«@J6»", "Lovelace")]], items=("S2.flash_fill",), arena_cell="J6"),
    do("S2-B.M7", "Move Nova's row (L7:N7) up one row: select it, Ctrl+X, click L6, Ctrl+V.", "Cut and paste.",
       'AND(«#L6»="Nova",«#M6»=88,«#N6»=3,COUNTA(«#L7:N7»)=0)',
       solve=[Fixture("cut_paste", "«@L7:N7»", None, ("«@L6»",))],
       wrong=[[Fixture("copy", "«@L7:N7»", None, ("«@L6»",))]], items=("S2.cut", "S2.paste"), arena_cell="L6"),
    do("S2-B.M8", "Select F9, press Alt+↓ and choose Platinum.", "Alt+↓ opens the list.", cells_equal({"F9": "Platinum"}),
       solve=[Fixture("type", "«@F9»", "Platinum")], wrong=[[Fixture("type", "«@F9»", "Gold")]],
       items=("S2.alt_down",), arena_cell="F9"),
)

WORLD = World(
    code="S2", track="S", order=3, title="Enter & Edit",
    tagline="Type, fill, copy and stamp data at speed.",
    file_name="03 Shortcuts 2 - Enter and Edit.xlsx",
    stages=(STAGE_1, STAGE_2, STAGE_3),
    boss=Boss(BOSS_MISSIONS, BOSS_ARENA, par_minutes=10),
)
