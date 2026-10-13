"""Shortcuts 4 · Organize & Analyze — reshape sheets, find anything, filter and sort."""
from ..checks import (ascending, column_hidden, count_is, descending, marker_gap, pairs_intact, sheet_exists,
                      sheets_more_than, visible_count, visible_label_count, visible_other_than)
from ..model import Arena, Boss, Fixture, Item, Stage, World, column, do, find, merge, self_check, table
from .datasets import ORDERS

# ------------------------------------------------------------------------------------ S4-1 Construction Crew
SECRETS = ["open", "SECRET", "open", "open", "SECRET", "open", "open", "open"]
LIST = ["KEEP", "KEEP", "DELETE ME", "DELETE ME", "DELETE ME", "KEEP", "KEEP", "KEEP", "KEEP", "KEEP"]
ITEMS_1 = (
    Item("S4.insert", "shortcut", "Ctrl+Shift++", "Insert cells; with whole rows selected, insert whole rows.",
         "Select rows with Shift+Space first, then Ctrl+Shift++.", "Which keys insert cells or rows?",
         ("Ctrl+Shift++", "Ctrl+Shift+=", "Ctrl++", "Ctrl+Plus"), "Ctrl+Shift plus the + key."),
    Item("S4.delete", "shortcut", "Ctrl+-", "Delete the selected cells; with whole rows selected, delete the rows.",
         "Shift+Space first, then Ctrl+-.", "Which keys delete the selected cells or rows?", ("Ctrl+-", "Ctrl+Minus"),
         "Ctrl plus the minus key."),
    Item("S4.hide_rows", "shortcut", "Ctrl+9", "Hide the selected rows.", "Hidden rows keep their data.",
         "Which keys hide the selected rows?", ("Ctrl+9",), "Ctrl plus a number key."),
    Item("S4.hide_cols", "shortcut", "Ctrl+0", "Hide the selected columns.", "Pair with Ctrl+Space to grab the column.",
         "Which keys hide the selected columns?", ("Ctrl+0",), "Ctrl plus zero."),
)
ARENA_1 = Arena(
    cells=merge(
        {"H5": "HIDE ME"}, column("H6", [1, 2, 3, 4, 5]),
        {"B12": "SECRET LIST"}, column("B13", SECRETS), column("C13", list(range(1, 9))),
        {"B24": "ROW ABOVE", "B25": "INSERT ABOVE"},
        {"B29": "LIST"}, column("B30", LIST), column("C30", list(range(1, 11))),
    ),
    pass_code="BUILDER", headers=("H5",), labels=("B12", "B24", "B25", "B29"), widths={"B": 16},
)
MISSIONS_1 = (
    do("S4-1.M1", "In the LIST block, rows with DELETE ME must go. Click the first DELETE ME cell, press Shift+Space, "
                  "then Shift+↓ twice to select all three rows, and press Ctrl+-.", "Shift+Space selects the row.",
       f'AND({count_is("B:B", "DELETE ME", 0)},{count_is("B:B", "KEEP", 7)})',
       solve=[Fixture("delete_rows_where", "«@B:B»", "DELETE ME")], wrong=[[Fixture("delete_rows", "«@B32»")]],
       items=("S4.delete",), arena_cell="B32"),
    do("S4-1.M2", "Click INSERT ABOVE (B25), press Shift+Space, then Shift+↓ once to select two rows, and press "
                  "Ctrl+Shift++ to insert two blank rows above it.", "Select two rows to insert two.",
       marker_gap("B", "ROW ABOVE", "INSERT ABOVE", 3),
       solve=[Fixture("insert_rows_above", "«@B:B»", "INSERT ABOVE", (2,))],
       wrong=[[Fixture("insert_rows_above", "«@B:B»", "INSERT ABOVE", (1,))]], items=("S4.insert",), arena_cell="B25"),
    do("S4-1.M3", "Hide both SECRET rows: click a SECRET cell, press Shift+Space, then Ctrl+9. Repeat for the other "
                  "one, then press F9.", "Ctrl+9 hides the selected row.",
       f'AND({visible_label_count("B13:B20", "SECRET")}=0,{visible_count("B13:B20")}=6)',
       solve=[Fixture("hide_rows_where", "«@B:B»", "SECRET")], wrong=[[Fixture("hide_rows", "«@B14»")]],
       items=("S4.hide_rows",), arena_cell="B14", f9=True),
    do("S4-1.M4", "Click H5 (HIDE ME), press Ctrl+Space to select column H, then Ctrl+0 to hide it. Press F9.",
       "Ctrl+Space, then Ctrl+0.", column_hidden("H5"), solve=[Fixture("hide_cols", "«@H5»")],
       wrong=[[Fixture("hide_cols", "«@G5»")]], items=("S4.hide_cols",), arena_cell="H5", f9=True),
)
STAGE_1 = Stage("S4-1", "Construction Crew", "insert, delete and hide rows and columns", ITEMS_1, MISSIONS_1, ARENA_1)

# ------------------------------------------------------------------------------------ S4-2 Sheet Master
ITEMS_2 = (
    Item("S4.new_sheet", "shortcut", "Shift+F11", "Insert a new worksheet.", "Alt+Shift+F1 does the same.",
         "Which keys insert a new worksheet?", ("Shift+F11", "Alt+Shift+F1"), "Shift plus F11."),
    Item("S4.rename", "shortcut", "Alt+H, O, R", "Rename the current sheet (KeyTips: Home, Format, Rename).",
         "Type the new name, then Enter.", "Which KeyTips rename the current sheet?", ("Alt+H, O, R",),
         "Alt, H, O, R one after another."),
    Item("S4.save", "shortcut", "Ctrl+S", "Save the workbook.", "Save early, save often.", "Which keys save the workbook?",
         ("Ctrl+S",), "S for Save."),
    Item("S4.save_as", "shortcut", "F12", "Open Save As to save a copy or change the name.",
         "Keep the original and practice on a copy.", "Which key opens Save As?", ("F12",), "The last function key."),
    Item("S4.new_wb", "shortcut", "Ctrl+N", "Create a new blank workbook.", "Starts fresh in a new window.",
         "Which keys create a new blank workbook?", ("Ctrl+N",), "N for New."),
    Item("S4.open", "shortcut", "Ctrl+O", "Open a workbook (and see your recent files).", "Recent files are listed first.",
         "Which keys open a workbook?", ("Ctrl+O",), "O for Open."),
    Item("S4.close", "shortcut", "Ctrl+W", "Close the current workbook window.", "Excel asks before losing changes.",
         "Which keys close the current workbook?", ("Ctrl+W",), "W for Window."),
    Item("S4.print", "shortcut", "Ctrl+P", "Open Print (with a preview).", "Check the preview before paper.",
         "Which keys open Print?", ("Ctrl+P",), "P for Print."),
)
ARENA_2 = Arena(cells={"B5": "Sheet tricks happen on the sheet tabs. The missions are on the stage sheet."},
                pass_code="TABS", labels=("B5",))
MISSIONS_2 = (
    do("S4-2.M1", "Press Shift+F11 to insert a new worksheet, then come back here and press F9.", "Shift+F11.",
       sheets_more_than(), solve=[Fixture("add_sheet", "")], wrong=[[Fixture("type", "«@B7»", "x")]],
       items=("S4.new_sheet",), arena_cell="B5", f9=True),
    do("S4-2.M2", "Go to the sheet named Rename Me (Ctrl+PgDn), press Alt, H, O, R, type Vault and press Enter. Come "
                  "back and press F9.", "Home → Format → Rename.", sheet_exists("Vault"),
       solve=[Fixture("rename_sheet", "", ("Rename Me", "Vault"))],
       wrong=[[Fixture("rename_sheet", "", ("Rename Me", "Vaults"))]], items=("S4.rename",), arena_cell="B5", f9=True),
    self_check("S4-2.M3", "Save your progress with Ctrl+S (or keep the original and use F12 to save a copy). Then pick "
                          "Done.", "Ctrl+S or F12.", items=("S4.save", "S4.save_as")),
)
STAGE_2 = Stage("S4-2", "Sheet Master", "manage sheets and files from the keyboard", ITEMS_2, MISSIONS_2, ARENA_2,
                extra_sheets=(("Rename Me", "Rename this sheet to Vault with Alt, H, O, R (mission on stage S4-2)."),))

# ------------------------------------------------------------------------------------ S4-3 Detective
POOL = ["Apple", "Banana", "Cherry", "Gadget Pro", "Mini Gadget", "Widget", "Gizmo", "Kiwi", "Lemon", "Mango",
        "Gadget Max", "Nut Mix", "Olive", "Pear", "Quince"]
TECH = {"Gadget Pro", "Mini Gadget", "Widget", "Gizmo", "Gadget Max"}


def _product(i: int) -> str:
    return "Dragonfruit" if i == 200 else POOL[(i * 7) % len(POOL)]


INVENTORY = [[f"SKU-{1000 + i}", _product(i), "Tech" if _product(i) in TECH else "Food", (i * 13) % 90 + 5,
              "N/A" if i % 9 == 4 else ("OK" if i % 2 else "Check")] for i in range(300)]
DRAGON_STOCK = next(r[3] for r in INVENTORY if r[1] == "Dragonfruit")
GADGETS = sum("gadget" in r[1].lower() for r in INVENTORY)
NA_COUNT = sum(r[4] == "N/A" for r in INVENTORY)
ITEMS_3 = (
    Item("S4.find", "shortcut", "Ctrl+F", "Find text or numbers anywhere on the sheet.",
         "Find All lists every match and counts them.", "Which keys open Find?", ("Ctrl+F",), "F for Find."),
    Item("S4.replace", "shortcut", "Ctrl+H", "Find and replace text or numbers.", "Replace All fixes every match at once.",
         "Which keys open Find and Replace on the Replace tab?", ("Ctrl+H",), "The letter after G."),
)
ARENA_3 = Arena(cells=table("B5", ["SKU", "Product", "Category", "Stock", "Note"], INVENTORY),
                pass_code="SLEUTH", headers=("B5:F5",), widths={"C": 14})
MISSIONS_3 = (
    find("S4-3.M1", "In the arena press Ctrl+F, search for Dragonfruit and press Enter. Type the Stock number in its "
                    "row.", "Stock is two columns right of the product.", DRAGON_STOCK, items=("S4.find",),
         wrong=(DRAGON_STOCK + 1,), verify=("find_offset", "Dragonfruit", 2)),
    do("S4-3.M2", "Press Ctrl+H. Replace every N/A in the Note column with 0: Find what N/A, Replace with 0, then "
                  "Replace All.", "Replace All, not Replace.",
       f'AND({count_is("F6:F305", "N/A", 0)},{count_is("F6:F305", 0, NA_COUNT)})',
       solve=[Fixture("replace", "«@F6:F305»", ("N/A", "0"))], wrong=[[Fixture("replace", "«@F6:F105»", ("N/A", "0"))]],
       items=("S4.replace",), arena_cell="F6"),
    find("S4-3.M3", "Press Ctrl+F, type Gadget and click Find All. The dialog reports how many cells were found. Type "
                    "that number.", "The count is at the bottom of the Find window.", GADGETS, items=("S4.find",),
         wrong=(GADGETS + 1,), verify=("countif_contains", "Gadget")),
)
STAGE_3 = Stage("S4-3", "Detective", "find and fix anything in seconds", ITEMS_3, MISSIONS_3, ARENA_3)

# ------------------------------------------------------------------------------------ S4-4 Data Wrangler
PLAYERS = [["Ann", 40, "Silver"], ["Bo", 90, "Gold"], ["Cy", 70, "Gold"], ["Di", 10, "Bronze"], ["Ed", 55, "Silver"],
           ["Flo", 85, "Gold"], ["Gil", 25, "Bronze"], ["Hu", 65, "Silver"], ["Ida", 95, "Gold"], ["Jay", 35, "Bronze"]]
VISITS = [["Jan", 1200], ["Feb", 1350], ["Mar", 1600], ["Apr", 1500], ["May", 1800], ["Jun", 2100]]
ORDER_ROWS = [[o.id, o.region, o.rep, o.units] for o in ORDERS]
ITEMS_4 = (
    Item("S4.filter", "shortcut", "Ctrl+Shift+L", "Turn filter buttons on or off for a table of data.",
         "Press again to clear all filters at once.", "Which keys turn filter buttons on and off?", ("Ctrl+Shift+L",),
         "Ctrl+Shift plus L."),
    Item("S4.filter_menu", "shortcut", "Alt+↓ (on a header)", "On a header with a filter button, open its filter menu.",
         "Arrow down the list, Space to tick, Enter to apply.", "Which keys open the filter menu of a header cell?",
         ("Alt+Down",), "The same keys that open a dropdown."),
    Item("S4.table", "shortcut", "Ctrl+T", "Turn a range into an Excel Table (filters, banding, auto-expanding).",
         "Ctrl+L does the same.", "Which keys turn a range into a Table?", ("Ctrl+T", "Ctrl+L"), "T for Table."),
    Item("S4.sort_az", "shortcut", "Alt+A, S, A", "Sort A→Z / smallest to largest (KeyTips: Data, Sort).",
         "Click a cell in the column you sort by first.", "Which KeyTips sort A to Z?", ("Alt+A, S, A",),
         "Alt, A, S, then A for ascending."),
    Item("S4.sort_za", "shortcut", "Alt+A, S, D", "Sort Z→A / largest to smallest (KeyTips: Data, Sort).",
         "Whole rows move together, so records stay intact.", "Which KeyTips sort Z to A?", ("Alt+A, S, D",),
         "Alt, A, S, then D for descending."),
    Item("S4.chart", "shortcut", "Alt+F1", "Drop an instant chart of the selected data on the sheet.",
         "F11 puts the chart on its own sheet.", "Which keys insert an instant chart on the sheet?", ("Alt+F1",),
         "Alt plus F1."),
)
ARENA_4 = Arena(
    cells=merge(table("B5", ["Order", "Region", "Rep", "Units"], ORDER_ROWS),
                table("B30", ["Player", "Score", "Level"], PLAYERS),
                table("B45", ["Month", "Visitors"], VISITS)),
    pass_code="WRANGLER", headers=("B5:E5", "B30:D30", "B45:C45"),
)
MISSIONS_4 = (
    do("S4-4.M1", "Click inside the table at B5 and press Ctrl+Shift+L to add filter buttons. On the Region header "
                  "(C5) press Alt+↓ and show only East.", "Untick Select All, tick East, Enter.",
       f'AND({visible_count("C6:C25")}={sum(o.region == "East" for o in ORDERS)},'
       f'{visible_other_than("C6:C25", "East")}=0)',
       solve=[Fixture("autofilter", "«@B5:E25»", "East", (2,))], wrong=[[Fixture("autofilter", "«@B5:E25»", "West", (2,))]],
       items=("S4.filter", "S4.filter_menu"), arena_cell="C5"),
    do("S4-4.M2", "Click any Score in the table at B30 (column C) and press Alt, A, S, D to sort largest to smallest.",
       "Data → Sort Z to A.",
       f'AND({descending("C31:C40")},{pairs_intact("B31:B40", "C31:C40", {p[0]: p[1] for p in PLAYERS})})',
       solve=[Fixture("sort", "«@B30:D40»", "desc", ("C",))], wrong=[[Fixture("sort_column_only", "«@C31:C40»", "desc")]],
       items=("S4.sort_za",), arena_cell="C31"),
    self_check("S4-4.M3", "Click inside the table at B45 and press Ctrl+T, then Enter. Next select B45:C51 and press "
                          "Alt+F1 to drop in a chart. Pick Done.", "Ctrl+T, then Alt+F1.", items=("S4.table", "S4.chart")),
)
STAGE_4 = Stage("S4-4", "Data Wrangler", "filter, sort, tabulate and chart", ITEMS_4, MISSIONS_4, ARENA_4)

# ------------------------------------------------------------------------------------ Boss
SHUFFLED = [PLAYERS[i] for i in (8, 1, 6, 0, 9, 2, 7, 4, 5, 3)]
MINERALS = ["Quartz", "Basalt", "Granite", "Slate", "Marble", "Obsidian", "Jade", "Onyx", "Topaz", "Agate"]
VAULT = [["Zircon" if i == 42 else f"{MINERALS[i % 10]} {i // 10 + 1}", (i * 17) % 70 + 3,
          "TBD" if i % 7 == 3 else ("Ready" if i % 2 else "Packed")] for i in range(60)]
ZIRCON = next(r[1] for r in VAULT if r[0] == "Zircon")
TBD = sum(r[2] == "TBD" for r in VAULT)
HIDE2 = ["ok", "HIDDEN", "ok", "ok", "HIDDEN", "ok", "ok", "ok"]
LIST2 = ["KEEP", "REMOVE", "KEEP", "REMOVE", "KEEP", "REMOVE", "KEEP", "KEEP"]
BOSS_ARENA = Arena(
    cells=merge(
        table("B5", ["Order", "Region", "Rep", "Units"], ORDER_ROWS),
        table("B30", ["Player", "Score", "Level"], SHUFFLED),
        table("B45", ["Mineral", "Stock", "Status"], VAULT),
        {"B110": "HIDE LIST"}, column("B111", HIDE2),
        {"B122": "ROW ABOVE", "B123": "INSERT ABOVE"},
        {"B127": "LIST"}, column("B128", LIST2),
    ),
    pass_code="ORGANIZER", headers=("B5:E5", "B30:D30", "B45:D45"), labels=("B110", "B122", "B123", "B127"),
    widths={"B": 16},
)
BOSS_MISSIONS = (
    do("S4-B.M1", "Filter the table at B5 to show only West (Ctrl+Shift+L, then Alt+↓ on Region).", "Filter buttons first.",
       f'AND({visible_count("C6:C25")}={sum(o.region == "West" for o in ORDERS)},'
       f'{visible_other_than("C6:C25", "West")}=0)',
       solve=[Fixture("autofilter", "«@B5:E25»", "West", (2,))], wrong=[[Fixture("autofilter", "«@B5:E25»", "East", (2,))]],
       items=("S4.filter", "S4.filter_menu"), arena_cell="C5"),
    do("S4-B.M2", "Sort the table at B30 by Player name A→Z: click a name, then Alt, A, S, A.", "Ascending.",
       f'AND({ascending("B31:B40")},{pairs_intact("B31:B40", "C31:C40", {p[0]: p[1] for p in PLAYERS})})',
       solve=[Fixture("sort", "«@B30:D40»", "asc", ("B",))], wrong=[[Fixture("sort_column_only", "«@B31:B40»", "asc")]],
       items=("S4.sort_az",), arena_cell="B31"),
    find("S4-B.M3", "Use Ctrl+F to find Zircon. Type its Stock (the cell to its right).", "Ctrl+F, Enter.", ZIRCON,
         items=("S4.find",), wrong=(ZIRCON + 1,), verify=("find_offset", "Zircon", 1)),
    do("S4-B.M4", "Use Ctrl+H to replace every TBD in the Status column with Pending (Replace All).", "Ctrl+H.",
       f'AND({count_is("D46:D105", "TBD", 0)},{count_is("D46:D105", "Pending", TBD)})',
       solve=[Fixture("replace", "«@D46:D105»", ("TBD", "Pending"))],
       wrong=[[Fixture("replace", "«@D46:D75»", ("TBD", "Pending"))]], items=("S4.replace",), arena_cell="D46"),
    do("S4-B.M5", "Hide both HIDDEN rows in the HIDE LIST (Shift+Space, then Ctrl+9). Press F9.", "Ctrl+9.",
       f'AND({visible_label_count("B111:B118", "HIDDEN")}=0,{visible_count("B111:B118")}=6)',
       solve=[Fixture("hide_rows_where", "«@B:B»", "HIDDEN")], wrong=[[Fixture("hide_rows", "«@B112»")]],
       items=("S4.hide_rows",), arena_cell="B112", f9=True),
    do("S4-B.M6", "Insert two blank rows above INSERT ABOVE (Shift+Space, Shift+↓, Ctrl+Shift++).", "Two rows.",
       marker_gap("B", "ROW ABOVE", "INSERT ABOVE", 3),
       solve=[Fixture("insert_rows_above", "«@B:B»", "INSERT ABOVE", (2,))],
       wrong=[[Fixture("insert_rows_above", "«@B:B»", "INSERT ABOVE", (1,))]], items=("S4.insert",), arena_cell="B123"),
    do("S4-B.M7", "Delete the three REMOVE rows in LIST: select each with Shift+Space and press Ctrl+-.", "Ctrl+-.",
       f'AND({count_is("B:B", "REMOVE", 0)},{count_is("B:B", "KEEP", 5)})',
       solve=[Fixture("delete_rows_where", "«@B:B»", "REMOVE")], wrong=[[Fixture("delete_rows", "«@B129»")]],
       items=("S4.delete",), arena_cell="B129"),
    do("S4-B.M8", "Insert a new worksheet with Shift+F11, come back and press F9.", "Shift+F11.", sheets_more_than(),
       solve=[Fixture("add_sheet", "")], wrong=[[Fixture("type", "«@E46»", "x")]], items=("S4.new_sheet",),
       arena_cell="B5", f9=True),
)

WORLD = World(
    code="S4", track="S", order=7, title="Organize & Analyze",
    tagline="Reshape sheets, find anything, filter and sort from the keyboard.",
    file_name="07 Shortcuts 4 - Organize and Analyze.xlsx",
    stages=(STAGE_1, STAGE_2, STAGE_3, STAGE_4),
    boss=Boss(BOSS_MISSIONS, BOSS_ARENA, par_minutes=12),
)
