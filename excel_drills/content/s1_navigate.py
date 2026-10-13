"""Shortcuts 1 · Navigate & Select — move and select anywhere on a sheet without the mouse."""
from ..model import Arena, Boss, Item, Stage, World, column, count_filled, find, merge, row, table
from ..refs import row_of

# ------------------------------------------------------------------------------------ S1-1 Warp Zones
ITEMS_1 = (
    Item("S1.ctrl_arrow", "shortcut", "Ctrl+Arrow", "Jump to the edge of the current data block.",
         "Land on a blank? The next press leaps to the next filled cell.",
         "Which keys jump to the edge of the current data block (any direction)?",
         ("Ctrl+Arrow", "Ctrl+Down", "Ctrl+Up", "Ctrl+Left", "Ctrl+Right"), "Hold Ctrl and tap an arrow key."),
    Item("S1.ctrl_home", "shortcut", "Ctrl+Home", "Jump to cell A1, the top-left corner of the sheet.",
         "The fastest way back to the start of any sheet.",
         "Which keys take you to the very first cell of the sheet (A1)?", ("Ctrl+Home",),
         "Ctrl plus the key that means 'start'."),
    Item("S1.ctrl_end", "shortcut", "Ctrl+End", "Jump to the last used cell: lowest used row, rightmost used column.",
         "A quick way to see how big a sheet really is.",
         "Which keys jump to the last used cell on the sheet?", ("Ctrl+End",), "Ctrl plus the opposite of Home."),
    Item("S1.home", "shortcut", "Home", "Move to column A of the row you are in.",
         "Ctrl+Home goes to A1; Home alone stays in your row.",
         "Which single key moves to column A of the current row?", ("Home",), "One key, no Ctrl."),
)
ARENA_1 = Arena(
    cells=merge(
        {"B5": "TRAIL ▼"}, column("B6", list(range(1, 1800))), {"B1805": "COMET"},
        {"D5": "ISLANDS ▼"}, column("D6", list(range(1, 16))), column("D30", list(range(16, 47))),
        column("D100", list(range(47, 78))), {"D400": "NEBULA"},
        {"F9": "ROW TRAIL ▶"}, row("F10", list(range(1, 11))), {"P10": "PULSAR"},
        {"H20": "START HERE", "A20": "ANCHOR"},
        {"P1805": "ORBIT"},
    ),
    pass_code="QUASAR", headers=("B5", "D5", "F9"), labels=("H20",),
)
MISSIONS_1 = (
    find("S1-1.M1", "In the arena, click B6 and press Ctrl+↓. You fly to the bottom of the TRAIL. "
                    "Type the word you land on.", "Ctrl+↓ stops at the last filled cell before a blank.", "COMET",
         items=("S1.ctrl_arrow",), wrong=("TRAIL",), verify=("end", "B6", "down")),
    find("S1-1.M2", "In the arena, click D6. Keep pressing Ctrl+↓: each press jumps to the next edge, even across "
                    "the gaps. Type the word where the islands end.", "Just keep pressing until you reach a word.",
         "NEBULA", items=("S1.ctrl_arrow",), wrong=("ISLANDS",), verify=("end_chain", "D6", "down", 6)),
    find("S1-1.M3", "In the arena, click F10 and press Ctrl+→. Type the word you land on.",
         "→ works just like ↓, sideways.", "PULSAR", items=("S1.ctrl_arrow",), wrong=("ORBIT",),
         verify=("end", "F10", "right")),
    find("S1-1.M4", "In the arena, press Ctrl+End to jump to the last used cell. Type the word there.",
         "Ctrl+End = lowest used row + rightmost used column.", "ORBIT", items=("S1.ctrl_end",),
         wrong=("COMET",), verify=("lastcell",)),
    find("S1-1.M5", "In the arena, click H20 (START HERE) and press Home. Type the word in the cell you land on.",
         "Home jumps to column A of the same row.", "ANCHOR", items=("S1.home",), wrong=("START HERE",),
         verify=("home", "H20")),
)
STAGE_1 = Stage("S1-1", "Warp Zones", "cross huge tables in one keystroke", ITEMS_1, MISSIONS_1, ARENA_1)

# ------------------------------------------------------------------------------------ S1-2 Teleport
ITEMS_2 = (
    Item("S1.goto", "shortcut", "F5 / Ctrl+G", "Open Go To: type an address or a name and jump there.",
         "Type a range like B2:D9 to jump there and select it.", "Which key opens the Go To box?",
         ("F5", "Ctrl+G"), "A function key, or Ctrl plus G."),
    Item("S1.ctrl_pgdn", "shortcut", "Ctrl+PgDn", "Move to the next sheet tab.",
         "Hold Ctrl and keep tapping PgDn to flip through every tab.", "Which keys move to the next sheet?",
         ("Ctrl+PgDn",), "Ctrl plus Page Down."),
    Item("S1.ctrl_pgup", "shortcut", "Ctrl+PgUp", "Move to the previous sheet tab.",
         "Pairs with Ctrl+PgDn: Up goes left.", "Which keys move to the previous sheet?", ("Ctrl+PgUp",),
         "Ctrl plus Page Up."),
    Item("S1.pgdn", "shortcut", "PgDn / PgUp", "Scroll one screen down / up.",
         "Faster than holding ↓ when you just want to browse.", "Which key scrolls one screen down?", ("PgDn",),
         "Page Down."),
    Item("S1.alt_pgdn", "shortcut", "Alt+PgDn / Alt+PgUp", "Scroll one screen right / left.",
         "Wide sheet? Alt+PgDn pages sideways.", "Which keys scroll one screen to the right?", ("Alt+PgDn",),
         "Alt plus Page Down."),
)
ARENA_2 = Arena(
    cells={"B5": "Teleport targets are hidden on this sheet. Use Go To (F5 or Ctrl+G).",
           "K777": "VORTEX", "M40": "GALAXY"},
    pass_code="ZEPHYR", labels=("B5",), names={"TREASURE": "M40"},
)
MISSIONS_2 = (
    find("S1-2.M1", "Go to the arena sheet, press F5 (or Ctrl+G), type K777 in the Reference box and press Enter. "
                    "Type the word you land on.", "Go To jumps on the sheet you're on: open the arena first.",
         "VORTEX", items=("S1.goto",), wrong=("GALAXY",), verify=("value_at", "K777")),
    find("S1-2.M2", "Press F5 and double-click TREASURE in the Go To list (names work from any sheet). "
                    "Type the word you land on.", "Defined names are listed at the top of the Go To box.",
         "GALAXY", items=("S1.goto",), wrong=("VORTEX",), verify=("name", "TREASURE")),
    find("S1-2.M3", "From this sheet press Ctrl+PgDn once. Type the PASS CODE shown in cell B3 of the sheet you "
                    "land on.", "Ctrl+PgDn = the next tab to the right.", "ZEPHYR", items=("S1.ctrl_pgdn",),
         wrong=("QUASAR",), verify=("pass_code", 1)),
    find("S1-2.M4", "From this sheet press Ctrl+PgUp once. Type the PASS CODE shown in cell B3 of the sheet you "
                    "land on.", "Ctrl+PgUp = the previous tab to the left.", "QUASAR", items=("S1.ctrl_pgup",),
         wrong=("ZEPHYR",), verify=("pass_code", -1)),
)
STAGE_2 = Stage("S1-2", "Teleport", "jump to any cell or sheet instantly", ITEMS_2, MISSIONS_2, ARENA_2)

# ------------------------------------------------------------------------------------ S1-3 Lasso
POINTS = [(i * 7) % 23 + 1 for i in range(1, 201)]
SHIPS = [["Comet", 4, 120], ["Nova", 6, 95], ["Vega", 3, 140], ["Orion", 8, 210], ["Lyra", 2, 60],
         ["Draco", 5, 175], ["Hydra", 7, 130], ["Cygnus", 4, 88], ["Pyxis", 1, 45], ["Ara", 6, 160]]
ITEMS_3 = (
    Item("S1.shift_arrow", "shortcut", "Shift+Arrow", "Grow the selection one cell at a time.",
         "Overshot? Shift plus the opposite arrow shrinks it back.", "Which keys grow the selection by one cell?",
         ("Shift+Arrow", "Shift+Down", "Shift+Up", "Shift+Left", "Shift+Right"), "Hold Shift and tap an arrow."),
    Item("S1.ctrl_shift_arrow", "shortcut", "Ctrl+Shift+Arrow", "Extend the selection to the edge of the data block.",
         "Select a whole column of data in one move: Ctrl+Shift+↓.",
         "Which keys extend the selection all the way to the edge of the data?",
         ("Ctrl+Shift+Arrow", "Ctrl+Shift+Down", "Ctrl+Shift+Up", "Ctrl+Shift+Left", "Ctrl+Shift+Right"),
         "The warp-zone keys plus Shift."),
    Item("S1.ctrl_shift_end", "shortcut", "Ctrl+Shift+End", "Extend the selection to the last used cell.",
         "Grabs everything from here to the end of the data.",
         "Which keys extend the selection to the last used cell?", ("Ctrl+Shift+End",), "Ctrl+End plus Shift."),
    Item("S1.ctrl_shift_home", "shortcut", "Ctrl+Shift+Home", "Extend the selection back to cell A1.",
         "Selects everything above and to the left of you.", "Which keys extend the selection back to cell A1?",
         ("Ctrl+Shift+Home",), "Ctrl+Home plus Shift."),
)
ARENA_3 = Arena(
    cells=merge(
        {"B5": "POINTS ▼"}, column("B6", POINTS),
        table("D5", ["Ship", "Crew", "Fuel"], SHIPS),
        {"H5": "NOTES"}, column("H6", ["launch", "dock", "refuel", "repair"]),
    ),
    pass_code="COSMOS", headers=("B5", "D5:F5", "H5"),
)
COUNT_TO_END = count_filled(ARENA_3, "D6:H205")
COUNT_TO_A1 = count_filled(ARENA_3, "A1:H12")
MISSIONS_3 = (
    find("S1-3.M1", "In the arena, click B6 and press Ctrl+Shift+↓ to select every POINTS value. Type the Sum "
                    "shown in the status bar (bottom right).", "No Sum in the status bar? Right-click it and tick Sum.",
         sum(POINTS), items=("S1.ctrl_shift_arrow",), wrong=(sum(POINTS) + 1,), verify=("sum_down", "B6")),
    find("S1-3.M2", "In the arena, click B6, then press Shift+↓ four times so five cells are selected. Type the "
                    "status-bar Sum.", "Each Shift+↓ adds one row.", sum(POINTS[:5]), items=("S1.shift_arrow",),
         wrong=(sum(POINTS[:4]),), verify=("sum", "B6:B10")),
    find("S1-3.M3", "In the arena, click D6 and press Ctrl+Shift+End. Type the Count shown in the status bar.",
         "Count = how many filled cells are selected.", COUNT_TO_END, items=("S1.ctrl_shift_end",),
         wrong=(COUNT_TO_END + 1,), verify=("counta_to_last", "D6")),
    find("S1-3.M4", "In the arena, click H12 and press Ctrl+Shift+Home. Type the status-bar Count.",
         "The selection now runs from A1 to H12.", COUNT_TO_A1, items=("S1.ctrl_shift_home",),
         wrong=(COUNT_TO_A1 - 1,), verify=("counta", "A1:H12")),
)
STAGE_3 = Stage("S1-3", "Lasso", "select big blocks in one move", ITEMS_3, MISSIONS_3, ARENA_3)

# ------------------------------------------------------------------------------------ S1-4 Grab
GEMS = [(i * 13) % 37 + 5 for i in range(1, 21)]
PLANETS = [["Mercury", 0, "No", 4223], ["Venus", 0, "No", 2802], ["Earth", 1, "No", 24], ["Mars", 2, "No", 25],
           ["Jupiter", 95, "Yes", 10], ["Saturn", 146, "Yes", 11], ["Uranus", 28, "Yes", 17],
           ["Neptune", 16, "Yes", 16], ["Ceres", 0, "No", 9], ["Pluto", 5, "No", 153], ["Haumea", 2, "Yes", 4],
           ["Eris", 1, "No", 26]]
ITEMS_4 = (
    Item("S1.shift_space", "shortcut", "Shift+Space", "Select the entire row.",
         "Memory hook: Shift+Space = row, Ctrl+Space = column.", "Which keys select the entire row?",
         ("Shift+Space",), "The long key plus Shift."),
    Item("S1.ctrl_space", "shortcut", "Ctrl+Space", "Select the entire column.",
         "Next world: Ctrl+0 hides the column you selected.", "Which keys select the entire column?",
         ("Ctrl+Space",), "The long key plus Ctrl."),
    Item("S1.ctrl_a", "shortcut", "Ctrl+A", "Select the current data block; keep pressing to select the whole sheet.",
         "Ctrl+Shift+* also selects the current data block.",
         "Which keys select the current data block (and the whole sheet if you keep pressing)?",
         ("Ctrl+A", "Ctrl+Shift+Space"), "Think 'A' for All."),
)
ARENA_4 = Arena(
    cells=merge(
        {"F5": "GEMS ▼"}, column("F6", GEMS),
        {"B30": "ROW 30 ▶", "C30": 7, "E30": 9, "G30": "gem", "I30": 4, "K30": "end"},
        {"B38": "PLANETS"}, table("B40", ["Planet", "Moons", "Rings", "Day (h)"], PLANETS),
    ),
    pass_code="METEOR", headers=("F5", "B40:E40"), labels=("B30", "B38"),
)
ROW_30 = sum(1 for a in ARENA_4.cells if row_of(a) == 30)
PLANET_CELLS = (len(PLANETS) + 1) * 4
MISSIONS_4 = (
    find("S1-4.M1", "In the arena, click any cell in column F and press Ctrl+Space to select the whole column. "
                    "Type the status-bar Sum.", "Ctrl+Space = column.", sum(GEMS), items=("S1.ctrl_space",),
         wrong=(sum(GEMS) + 1,), verify=("col_sum", "F")),
    find("S1-4.M2", "In the arena, click any cell in row 30 and press Shift+Space to select the whole row. "
                    "Type the status-bar Count.", "Shift+Space = row.", ROW_30, items=("S1.shift_space",),
         wrong=(ROW_30 + 1,), verify=("row_counta", 30)),
    find("S1-4.M3", "In the arena, click any cell inside the PLANETS table (it starts at B40) and press Ctrl+A once. "
                    "Excel selects just that block. Type the status-bar Count.", "One press of Ctrl+A in data = the "
                    "current block.", PLANET_CELLS, items=("S1.ctrl_a",), wrong=(PLANET_CELLS + 1,),
         verify=("counta_region", "C45")),
)
STAGE_4 = Stage("S1-4", "Grab", "grab whole rows, columns and blocks", ITEMS_4, MISSIONS_4, ARENA_4)

# ------------------------------------------------------------------------------------ Boss
ENERGY = [(i * 11) % 29 + 3 for i in range(1, 101)]
CRYSTALS = [(i * 5) % 17 + 2 for i in range(1, 26)]
MOONS = [["Moon", "Earth", 3474, "ancient"], ["Phobos", "Mars", 22, 1877], ["Deimos", "Mars", 12, 1877],
         ["Io", "Jupiter", 3643, 1610], ["Europa", "Jupiter", 3122, 1610], ["Ganymede", "Jupiter", 5268, 1610],
         ["Callisto", "Jupiter", 4821, 1610], ["Titan", "Saturn", 5150, 1655], ["Rhea", "Saturn", 1527, 1672],
         ["Iapetus", "Saturn", 1469, 1671], ["Dione", "Saturn", 1123, 1684], ["Miranda", "Uranus", 472, 1948],
         ["Ariel", "Uranus", 1158, 1851], ["Triton", "Neptune", 2707, 1846], ["Charon", "Pluto", 1212, 1978]]
BOSS_ARENA = Arena(
    cells=merge(
        {"B5": "LONG TRAIL ▼"}, column("B6", list(range(1, 2496))), {"B2501": "TITAN"},
        {"D5": "ISLANDS ▼"}, column("D6", list(range(1, 46))), column("D80", list(range(46, 57))), {"D300": "ECLIPSE"},
        {"F5": "ENERGY ▼"}, column("F6", ENERGY),
        {"H5": "CRYSTALS"}, column("H6", CRYSTALS),
        {"J20": 5, "L20": "x", "N20": 8, "P20": "y", "R20": 13},
        {"L38": "MOONS"}, table("L40", ["Moon", "Planet", "Km", "Found"], MOONS),
        {"S40": "START", "A40": "LAUNCH"},
        {"Q900": "HALO"},
        {"J1199": "ROW TRAIL ▶"}, row("J1200", list(range(1, 12))), {"U1200": "AURORA"},
        {"U2501": "ZENITH"},
    ),
    pass_code="SUPERNOVA", headers=("B5", "D5", "F5", "H5", "J1199", "L40:O40"), labels=("L38", "S40"),
)
BOSS_ROW_20 = sum(1 for a in BOSS_ARENA.cells if row_of(a) == 20)
MOON_CELLS = (len(MOONS) + 1) * 4
BOSS_MISSIONS = (
    find("S1-B.M1", "In the Boss Arena, click B6 and press Ctrl+↓. Type the word at the end of the long trail.",
         "One press of Ctrl+↓.", "TITAN", items=("S1.ctrl_arrow",), wrong=("TRAIL",), verify=("end", "B6", "down")),
    find("S1-B.M2", "Click D6 and keep pressing Ctrl+↓ across the gaps. Type the word you reach.",
         "Keep pressing until you hit a word.", "ECLIPSE", items=("S1.ctrl_arrow",), wrong=("ISLANDS",),
         verify=("end_chain", "D6", "down", 4)),
    find("S1-B.M3", "Press F5, go to J1200, then press Ctrl+→. Type the word you land on.",
         "Teleport first, then warp sideways.", "AURORA", items=("S1.goto", "S1.ctrl_arrow"), wrong=("TITAN",),
         verify=("end", "J1200", "right")),
    find("S1-B.M4", "Press Ctrl+End. Type the word in the last used cell.", "Lowest row, rightmost column.",
         "ZENITH", items=("S1.ctrl_end",), wrong=("AURORA",), verify=("lastcell",)),
    find("S1-B.M5", "Press F5 (or Ctrl+G) and go to Q900. Type the word there.", "Type Q900 in Reference.",
         "HALO", items=("S1.goto",), wrong=("ZENITH",), verify=("value_at", "Q900")),
    find("S1-B.M6", "Click F6 and press Ctrl+Shift+↓ to select all ENERGY values. Type the status-bar Sum.",
         "Ctrl+Shift+↓ selects to the edge.", sum(ENERGY), items=("S1.ctrl_shift_arrow",), wrong=(sum(ENERGY) + 1,),
         verify=("sum_down", "F6")),
    find("S1-B.M7", "Click any cell in column H and press Ctrl+Space. Type the status-bar Sum.",
         "Ctrl+Space = column.", sum(CRYSTALS), items=("S1.ctrl_space",), wrong=(sum(CRYSTALS) - 1,),
         verify=("col_sum", "H")),
    find("S1-B.M8", "Click inside the MOONS table (it starts at L40) and press Ctrl+A once. Type the status-bar "
                    "Count.", "One press selects the current block.", MOON_CELLS, items=("S1.ctrl_a",),
         wrong=(MOON_CELLS - 4,), verify=("counta_region", "M45")),
    find("S1-B.M9", "Click S40 (START) and press Home. Type the word in the cell you land on.", "Home = column A.",
         "LAUNCH", items=("S1.home",), wrong=("START",), verify=("home", "S40")),
    find("S1-B.M10", "Click any cell in row 20 and press Shift+Space. Type the status-bar Count.",
         "Shift+Space = row.", BOSS_ROW_20, items=("S1.shift_space",), wrong=(BOSS_ROW_20 - 1,),
         verify=("row_counta", 20)),
)

WORLD = World(
    code="S1", track="S", order=1, title="Navigate & Select",
    tagline="Move and select anywhere on a sheet without touching the mouse.",
    file_name="01 Shortcuts 1 - Navigate and Select.xlsx",
    stages=(STAGE_1, STAGE_2, STAGE_3, STAGE_4),
    boss=Boss(BOSS_MISSIONS, BOSS_ARENA, par_minutes=10),
)
