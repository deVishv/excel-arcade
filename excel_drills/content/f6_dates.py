"""Formulas 6 · Dates — build, split and shift dates; count days and workdays."""
import datetime as dt

from ..model import Arena, Boss, Item, Stage, World, formula, merge
from ..writer import BUILD_DATE
from .datasets import add_workdays, serial, workday_count

D1, D2 = dt.date(2026, 3, 15), dt.date(2026, 5, 1)          # a Sunday and a Friday
BIRTH = dt.date(1990, 8, 20)


def weekday_excel(day: dt.date) -> int:
    """WEEKDAY(day) with the default return type: Sunday = 1 … Saturday = 7."""
    return day.isoweekday() % 7 + 1


def add_months(day: dt.date, months: int) -> dt.date:
    m = day.month - 1 + months
    y, m = day.year + m // 12, m % 12 + 1
    last = [31, 29 if y % 4 == 0 and (y % 100 or y % 400 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1]
    return dt.date(y, m, min(day.day, last))


def end_of_month(day: dt.date) -> dt.date:
    return add_months(day.replace(day=1), 1) - dt.timedelta(1)


def full_years(start: dt.date, end: dt.date) -> int:
    return end.year - start.year - ((end.month, end.day) < (start.month, start.day))


def full_months(start: dt.date, end: dt.date) -> int:
    return (end.year - start.year) * 12 + end.month - start.month - (end.day < start.day)


DATE_FMT = "d-mmm-yyyy"

# ------------------------------------------------------------------------------------ F6-1 Calendar
ITEMS_1 = (
    Item("F6.today", "function", "TODAY", "=TODAY() is today's date; it updates every day.",
         "Use Ctrl+; instead when the date must never change.", "Which function returns today's date?", ("TODAY",),
         "Five letters."),
    Item("F6.now", "function", "NOW", "=NOW() is today's date AND the current time.", "It updates on every recalc.",
         "Which function returns the current date and time?", ("NOW",), "Three letters."),
    Item("F6.date", "function", "DATE", "DATE(year, month, day) builds a real date.", "=DATE(2026,7,4) is 4 July 2026.",
         "Which function builds a date from a year, month and day?", ("DATE",), "Four letters."),
    Item("F6.year", "function", "YEAR", "YEAR(date) returns the year number.", "=YEAR(B6) gives 2026.",
         "Which function returns the year of a date?", ("YEAR",), "Four letters."),
    Item("F6.month", "function", "MONTH", "MONTH(date) returns 1 to 12.", "=MONTH(B6) gives 3 for March.",
         "Which function returns the month number of a date?", ("MONTH",), "Five letters."),
    Item("F6.day", "function", "DAY", "DAY(date) returns the day of the month, 1 to 31.", "=DAY(B6) gives 15.",
         "Which function returns the day of the month?", ("DAY",), "Three letters."),
    Item("F6.weekday", "function", "WEEKDAY", "WEEKDAY(date) returns 1 (Sunday) to 7 (Saturday).",
         "WEEKDAY(date,2) counts Monday as 1 instead.", "Which function returns the day of the week as a number?",
         ("WEEKDAY",), "WEEK plus DAY."),
)
ARENA_1 = Arena(
    cells={"B5": "Date", "B6": D1, "C5": "Task", "C6": "Today", "C7": "Build 4 July 2026", "C8": "Year of B6",
           "C9": "Month of B6", "C10": "Day of B6", "C11": "Weekday of B6"},
    pass_code="CALENDAR", inputs=("D6:D11",), headers=("B5:C5",),
    number_formats={"B6": DATE_FMT, "D6:D7": DATE_FMT}, widths={"B": 14, "C": 20, "D": 16},
)
MISSIONS_1 = (
    formula("F6-1.M1", "In D6 return today's date with a formula.", "No arguments: =TODAY()", "D6", "=TODAY()",
            serial(BUILD_DATE.date()), items=("F6.today",), wrong=("=NOW()",), uses=("TODAY",), volatile=True),
    formula("F6-1.M2", "In D7 build the date 4 July 2026 with DATE.", "=DATE(2026,7,4)", "D7", "=DATE(2026,7,4)",
            serial(dt.date(2026, 7, 4)), items=("F6.date",), wrong=("=DATE(2026,4,7)",), uses=("DATE",)),
    formula("F6-1.M3", "In D8 return the year of the date in B6.", "=YEAR(B6)", "D8", "=YEAR(B6)", D1.year,
            items=("F6.year",), wrong=("=MONTH(B6)",), uses=("YEAR",)),
    formula("F6-1.M4", "In D9 return the month number of B6.", "=MONTH(B6)", "D9", "=MONTH(B6)", D1.month,
            items=("F6.month",), wrong=("=DAY(B6)",), uses=("MONTH",)),
    formula("F6-1.M5", "In D10 return the day of the month of B6.", "=DAY(B6)", "D10", "=DAY(B6)", D1.day,
            items=("F6.day",), wrong=("=MONTH(B6)",), uses=("DAY",)),
    formula("F6-1.M6", "In D11 return the weekday number of B6 (Sunday = 1).", "=WEEKDAY(B6)", "D11", "=WEEKDAY(B6)",
            weekday_excel(D1), items=("F6.weekday",), wrong=("=WEEKDAY(B6,2)",), uses=("WEEKDAY",)),
)
STAGE_1 = Stage("F6-1", "Calendar", "build dates and take them apart", ITEMS_1, MISSIONS_1, ARENA_1)

# ------------------------------------------------------------------------------------ F6-2 Date Math
ITEMS_2 = (
    Item("F6.subtract", "concept", "=end-start", "Subtract two dates to get the days between them.",
         "Dates are numbers underneath, so plain minus works.", "What do you get when you subtract an earlier date "
         "from a later one (one word)?", ("days", "number of days"), "Not hours."),
    Item("F6.add_days", "concept", "=date+30", "Add a number to a date to move forward that many days.",
         "=B6+30 is 30 days after B6.", "Type the formula for the date 30 days after the date in B6.",
         ("=B6+30", "B6+30", "=30+B6", "30+B6"), "Plain plus."),
    Item("F6.datedif", "function", "DATEDIF", 'DATEDIF(start, end, "Y"/"M"/"D") counts full years, months or days.',
         'Perfect for ages: =DATEDIF(birthday,TODAY(),"Y").', "Which function counts full years or months between "
         "two dates?", ("DATEDIF",), "DATE plus DIF."),
)
ARENA_2 = Arena(
    cells={"B5": "Dates", "B6": D1, "B7": D2, "B9": BIRTH, "B10": D1, "A6": "Start", "A7": "End", "A9": "Birthday",
           "A10": "On", "C5": "Task", "C6": "Days from B6 to B7", "C7": "30 days after B6",
           "C8": "Age in full years (B9 → B10)", "C9": "Full months B6 → B7"},
    pass_code="DATEMATH", inputs=("D6:D9",), headers=("B5", "C5"), labels=("A6", "A7", "A9", "A10"),
    number_formats={"B6:B10": DATE_FMT, "D7": DATE_FMT}, widths={"B": 14, "C": 30, "D": 16},
)
MISSIONS_2 = (
    formula("F6-2.M1", "In D6 count the days from B6 to B7 by subtracting the dates.", "=B7-B6", "D6", "=B7-B6",
            (D2 - D1).days, items=("F6.subtract",), wrong=("=B6-B7",)),
    formula("F6-2.M2", "In D7 return the date 30 days after B6.", "=B6+30", "D7", "=B6+30",
            serial(D1 + dt.timedelta(30)), items=("F6.add_days",), wrong=("=B6+3",)),
    formula("F6-2.M3", 'In D8 return the age in full years from the birthday in B9 to the date in B10: '
                       '=DATEDIF(B9,B10,"Y").', '"Y" = full years.', "D8", '=DATEDIF(B9,B10,"Y")', full_years(BIRTH, D1),
            items=("F6.datedif",), wrong=('=DATEDIF(B9,B10,"M")',), uses=("DATEDIF",)),
    formula("F6-2.M4", 'In D9 count the full months from B6 to B7 with DATEDIF and "M".', '"M" = full months.', "D9",
            '=DATEDIF(B6,B7,"M")', full_months(D1, D2), items=("F6.datedif",), wrong=('=DATEDIF(B6,B7,"D")',),
            uses=("DATEDIF",)),
)
STAGE_2 = Stage("F6-2", "Date Math", "add, subtract and measure dates", ITEMS_2, MISSIONS_2, ARENA_2)

# ------------------------------------------------------------------------------------ F6-3 Deadlines
ITEMS_3 = (
    Item("F6.edate", "function", "EDATE", "EDATE(date, months) moves by whole months.", "=EDATE(B6,3) is 3 months on.",
         "Which function moves a date forward or back by whole months?", ("EDATE",), "E plus DATE."),
    Item("F6.eomonth", "function", "EOMONTH", "EOMONTH(date, months) returns a month's last day.",
         "=EOMONTH(B6,0) is the end of B6's month.", "Which function returns the last day of a month?", ("EOMONTH",),
         "End Of MONTH."),
    Item("F6.networkdays", "function", "NETWORKDAYS", "Count the Monday–Friday days between two dates (both included).",
         "Add a holiday list as a third argument.", "Which function counts the working days between two dates?",
         ("NETWORKDAYS",), "NET WORK DAYS."),
    Item("F6.workday", "function", "WORKDAY", "WORKDAY(start, n): the date n working days later.",
         "Skips weekends automatically.", "Which function returns the date a number of working days later?",
         ("WORKDAY",), "WORK plus DAY."),
)
ARENA_3 = Arena(
    cells={"B5": "Dates", "A6": "Start", "B6": D1, "A7": "End", "B7": D2, "C5": "Task", "C6": "3 months after B6",
           "C7": "End of B6's month", "C8": "Workdays B6 → B7", "C9": "10 workdays after B6"},
    pass_code="DEADLINE", inputs=("D6:D9",), headers=("B5", "C5"), labels=("A6", "A7"),
    number_formats={"B6:B7": DATE_FMT, "D6:D7": DATE_FMT, "D9": DATE_FMT}, widths={"B": 14, "C": 24, "D": 16},
)
MISSIONS_3 = (
    formula("F6-3.M1", "In D6 return the date 3 months after B6 with EDATE.", "=EDATE(B6,3)", "D6", "=EDATE(B6,3)",
            serial(add_months(D1, 3)), items=("F6.edate",), wrong=("=B6+90",), uses=("EDATE",)),
    formula("F6-3.M2", "In D7 return the last day of B6's month with EOMONTH.", "=EOMONTH(B6,0)", "D7",
            "=EOMONTH(B6,0)", serial(end_of_month(D1)), items=("F6.eomonth",), wrong=("=EOMONTH(B6,1)",),
            uses=("EOMONTH",)),
    formula("F6-3.M3", "In D8 count the working days from B6 to B7 with NETWORKDAYS.", "=NETWORKDAYS(B6,B7)", "D8",
            "=NETWORKDAYS(B6,B7)", workday_count(D1, D2), items=("F6.networkdays",), wrong=("=B7-B6",),
            uses=("NETWORKDAYS",)),
    formula("F6-3.M4", "In D9 return the date 10 working days after B6 with WORKDAY.", "=WORKDAY(B6,10)", "D9",
            "=WORKDAY(B6,10)", serial(add_workdays(D1, 10)), items=("F6.workday",), wrong=("=B6+10",),
            uses=("WORKDAY",)),
)
STAGE_3 = Stage("F6-3", "Deadlines", "plan with months, month-ends and workdays", ITEMS_3, MISSIONS_3, ARENA_3)

# ------------------------------------------------------------------------------------ Boss
B1, B2, HIRED = dt.date(2026, 9, 9), dt.date(2026, 11, 27), dt.date(2019, 4, 30)
BOSS_ARENA = Arena(
    cells=merge({"A6": "Start", "B6": B1, "A7": "End", "B7": B2, "A8": "Hired", "B8": HIRED, "B5": "Dates"},
                {"C5": "Task", "C6": "Year of B6", "C7": "Weekday of B6", "C8": "Days B6 → B7",
                 "C9": "Full years hired (B8 → B6)", "C10": "2 months after B6", "C11": "End of B7's month",
                 "C12": "Workdays B6 → B7", "C13": "15 workdays after B6"}),
    pass_code="TIMEKEEPER", inputs=("D6:D13",), headers=("B5", "C5"), labels=("A6", "A7", "A8"),
    number_formats={"B6:B8": DATE_FMT, "D10:D11": DATE_FMT, "D13": DATE_FMT}, widths={"B": 14, "C": 28, "D": 16},
)
BOSS_MISSIONS = (
    formula("F6-B.M1", "In D6 return the year of B6.", "YEAR.", "D6", "=YEAR(B6)", B1.year, items=("F6.year",),
            wrong=("=MONTH(B6)",), uses=("YEAR",)),
    formula("F6-B.M2", "In D7 return the weekday number of B6 (Sunday = 1).", "WEEKDAY.", "D7", "=WEEKDAY(B6)",
            weekday_excel(B1), items=("F6.weekday",), wrong=("=WEEKDAY(B6,2)",), uses=("WEEKDAY",)),
    formula("F6-B.M3", "In D8 count the days from B6 to B7.", "Subtract.", "D8", "=B7-B6", (B2 - B1).days,
            items=("F6.subtract",), wrong=("=B6-B7",)),
    formula("F6-B.M4", "In D9 count the full years from B8 to B6 with DATEDIF.", '"Y".', "D9", '=DATEDIF(B8,B6,"Y")',
            full_years(HIRED, B1), items=("F6.datedif",), wrong=('=DATEDIF(B8,B6,"M")',), uses=("DATEDIF",)),
    formula("F6-B.M5", "In D10 return the date 2 months after B6.", "EDATE.", "D10", "=EDATE(B6,2)",
            serial(add_months(B1, 2)), items=("F6.edate",), wrong=("=B6+60",), uses=("EDATE",)),
    formula("F6-B.M6", "In D11 return the last day of B7's month.", "EOMONTH.", "D11", "=EOMONTH(B7,0)",
            serial(end_of_month(B2)), items=("F6.eomonth",), wrong=("=EOMONTH(B7,-1)",), uses=("EOMONTH",)),
    formula("F6-B.M7", "In D12 count the working days from B6 to B7.", "NETWORKDAYS.", "D12", "=NETWORKDAYS(B6,B7)",
            workday_count(B1, B2), items=("F6.networkdays",), wrong=("=B7-B6",), uses=("NETWORKDAYS",)),
    formula("F6-B.M8", "In D13 return the date 15 working days after B6.", "WORKDAY.", "D13", "=WORKDAY(B6,15)",
            serial(add_workdays(B1, 15)), items=("F6.workday",), wrong=("=B6+15",), uses=("WORKDAY",)),
)

WORLD = World(
    code="F6", track="F", order=10, title="Dates",
    tagline="Build, split and shift dates; count days and workdays.",
    file_name="10 Formulas 6 - Dates.xlsx",
    stages=(STAGE_1, STAGE_2, STAGE_3),
    boss=Boss(BOSS_MISSIONS, BOSS_ARENA, par_minutes=12),
)
