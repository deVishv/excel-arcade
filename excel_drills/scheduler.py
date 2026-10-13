"""Spaced repetition inside the course: review each item at growing distances after its debut.

All stages and Boss stages of all worlds form one play-order timeline. For every item (in debut order)
RECALL reviews are placed at about +1, +4 and +10 positions, in the first later slot with room.
Whatever doesn't fit before the end of the last world goes to the Final Boss.
"""
from __future__ import annotations

from dataclasses import dataclass

OFFSETS = (1, 4, 10)
WARMUP_CAP = 10
BOSS_CAP = 8
MAX_OVERFLOW = 60


@dataclass(frozen=True)
class Slot:
    code: str
    world: str
    index: int
    capacity: int


@dataclass
class Schedule:
    slots: list[Slot]
    reviews: dict[str, list[str]]
    overflow: list[str]
    intro: dict[str, int]


def _slots(worlds, warmup_cap: int, boss_cap: int) -> list[Slot]:
    slots: list[Slot] = []
    for w in worlds:
        for st in w.stages:
            slots.append(Slot(st.code, w.code, len(slots), warmup_cap))
        slots.append(Slot(f"{w.code}-BOSS", w.code, len(slots), boss_cap))
    return slots


def schedule(worlds, *, offsets=OFFSETS, warmup_cap: int = WARMUP_CAP, boss_cap: int = BOSS_CAP) -> Schedule:
    """Place reviews round by round: every item's first review (+1) before anyone's second (+4) or third (+10).

    Round order matters: placing item by item lets early items' long-range reviews fill the slots that
    late items need for their first reviews (found with real content). Targets past the end of the course
    are clamped to the last slot; reviews that still find no room go to the Final Boss.
    """
    slots = _slots(worlds, warmup_cap, boss_cap)
    index = {s.code: s.index for s in slots}
    intro: dict[str, int] = {}
    order: list[str] = []
    for w in worlds:
        for st in w.stages:
            for item in st.items:
                if item.id in intro:
                    raise ValueError(f"item {item.id} is introduced twice")
                intro[item.id] = index[st.code]
                order.append(item.id)
    reviews: dict[str, list[str]] = {s.code: [] for s in slots}
    overflow: list[str] = []
    last = dict(intro)
    for offset in offsets:
        for item_id in order:
            if item_id in overflow:
                continue
            target = max(min(intro[item_id] + offset, len(slots) - 1), last[item_id] + 1)
            slot = next((s for s in slots[target:] if len(reviews[s.code]) < s.capacity), None)
            if slot is None:
                overflow.append(item_id)
                continue
            reviews[slot.code].append(item_id)
            last[item_id] = slot.index
    return Schedule(slots, reviews, overflow, intro)


def retrieval_positions(sched: Schedule, worlds, final_items: set[str]) -> dict[str, list[int]]:
    """Distinct timeline positions after its debut where each item is retrieved again."""
    final = len(sched.slots)
    index = {s.code: s.index for s in sched.slots}
    out: dict[str, set[int]] = {item_id: set() for item_id in sched.intro}
    for code, ids in sched.reviews.items():
        for item_id in ids:
            out[item_id].add(index[code])
    for w in worlds:
        boss = index[f"{w.code}-BOSS"]
        for mission in w.boss.missions:
            for item_id in mission.items:
                if item_id in out and boss > sched.intro[item_id]:
                    out[item_id].add(boss)
    for item_id in (*sched.overflow, *final_items):
        if item_id in out:
            out[item_id].add(final)
    return {k: sorted(v) for k, v in out.items()}


def validate(sched: Schedule, worlds, final_items: set[str], *, max_overflow: int = MAX_OVERFLOW) -> list[str]:
    problems: list[str] = []
    final = len(sched.slots)
    world_at = {s.index: s.world for s in sched.slots}
    for item_id, positions in retrieval_positions(sched, worlds, final_items).items():
        start = sched.intro[item_id]
        need = min(3, (final - start - 1) + 1)          # later slots + the Final Boss, at most 3
        if len(positions) < need:
            problems.append(f"{item_id}: {len(positions)} spaced retrievals, needs {need}")
        if positions and positions[-1] != final and world_at[positions[-1]] == world_at[start]:
            problems.append(f"{item_id}: its last retrieval is still inside its own workbook")
    if len(sched.overflow) > max_overflow:
        problems.append(f"{len(sched.overflow)} reviews overflow into the Final Boss (max {max_overflow})")
    return problems
