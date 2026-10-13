from excel_drills.model import Arena, Boss, Item, Stage, World, find
from excel_drills.scheduler import retrieval_positions, schedule, validate


def _item(i):
    return Item(i, "shortcut", i, "w", "t", "p?", ("Ctrl+" + i[-1],), "h")


def _world(code, n_stages, items_per_stage, boss_items=()):
    stages = []
    for s in range(1, n_stages + 1):
        items = tuple(_item(f"{code}.{s}{k}") for k in "abcdefgh"[:items_per_stage])
        stages.append(Stage(f"{code}-{s}", f"S{s}", "g", items, ()))
    boss = Boss((find(f"{code}-B.M1", "p", "h", "X", items=boss_items, wrong=("Y",)),), Arena({}, "P"), 5)
    return World(code, "S", 1, "T", "t", f"{code}.xlsx", tuple(stages), boss)


def test_reviews_land_after_debut_with_growing_gaps():
    worlds = (_world("A1", 3, 2), _world("B1", 3, 2), _world("C1", 3, 2))
    sched = schedule(worlds)
    pos = retrieval_positions(sched, worlds, set())
    first = pos["A1.1a"]
    assert first[0] == 1 and len(first) >= 3
    gaps = [b - a for a, b in zip([0, *first], first)]
    assert gaps == sorted(gaps)                       # expanding intervals
    assert all(len(v) == len(set(v)) for v in sched.reviews.values())


def test_capacity_is_respected_and_overflow_goes_to_final():
    worlds = (_world("A1", 2, 8),)
    sched = schedule(worlds, warmup_cap=2, boss_cap=1)
    assert all(len(v) <= 2 for k, v in sched.reviews.items() if not k.endswith("BOSS"))
    assert len(sched.reviews["A1-BOSS"]) <= 1
    assert sched.overflow


def test_validate_reports_too_few_retrievals():
    worlds = (_world("A1", 2, 8),)
    sched = schedule(worlds, warmup_cap=1, boss_cap=0)
    problems = validate(sched, worlds, set())
    assert any("spaced retrievals" in p for p in problems)


def test_validate_passes_a_roomy_course():
    worlds = tuple(_world(c, 4, 2, boss_items=()) for c in ("A1", "B1", "C1", "D1"))
    assert validate(schedule(worlds), worlds, set()) == []
