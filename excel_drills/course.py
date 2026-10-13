"""The whole course in play order: items, the review schedule and auto-generated PICK/RECALL challenges."""
from __future__ import annotations

import hashlib

from .checks import Pick, Recall
from .model import Challenge, FinalBoss, Fixture, Item, World, validate_world
from .normalize import normalize, variants
from .scheduler import Schedule, schedule, validate

WRONG_RECALL = {"shortcut": "Ctrl+Q", "function": "NOPE", "concept": "NOPE"}


def _h(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()


class Course:
    def __init__(self, worlds: tuple[World, ...], final: FinalBoss | None = None):
        self.worlds = tuple(worlds)
        self.final = final
        self.items: dict[str, Item] = {}
        self.origin: dict[str, str] = {}
        self.world_of: dict[str, str] = {}
        for w in self.worlds:
            for st in w.stages:
                for item in st.items:
                    if item.id in self.items:
                        raise ValueError(f"item {item.id} is introduced twice")
                    self.items[item.id] = item
                    self.origin[item.id] = f"{st.code} {st.name}"
                    self.world_of[item.id] = w.code
        self._variants = {i: set(variants(it.answers, it.kind)) for i, it in self.items.items()}
        self.schedule: Schedule = schedule(self.worlds)

    def accepted(self, item_id: str) -> tuple[str, ...]:
        return tuple(sorted(self._variants[item_id]))

    def recall(self, item_id: str, cid: str, *, flashback: bool) -> Challenge:
        item = self.items[item_id]
        prompt = f"{item.prompt}  (from {self.origin[item_id]})" if flashback else item.prompt
        wrong = WRONG_RECALL[item.kind]
        if normalize(wrong) in self._variants[item_id]:
            raise ValueError(f"{item_id}: the generic wrong answer is accepted")
        return Challenge(cid, "RECALL", prompt, item.hint, Recall(self.accepted(item_id)),
                         solve=(Fixture("type", "«ans»", item.answers[0]),),
                         wrong=((Fixture("type", "«ans»", wrong),),), items=(item_id,))

    def pick(self, item_id: str, cid: str) -> Challenge:
        item = self.items[item_id]
        mine = self._variants[item_id]
        if item.distractors:
            options = list(item.distractors)
        else:
            pool = [o for o in self.items.values()
                    if o.id != item.id and o.kind == item.kind and o.display != item.display
                    and not (self._variants[o.id] & mine)]
            pool.sort(key=lambda o: (self.world_of[o.id] != self.world_of[item.id], _h(item.id + o.id)))
            options = []
            for o in pool:
                if o.display not in options:
                    options.append(o.display)
                if len(options) == 3:
                    break
        if len(options) < 3:
            raise ValueError(f"{item_id}: needs 3 PICK distractors, found {options}")
        choices = tuple(sorted([item.display, *options], key=lambda d: _h(item.id + d)))
        if normalize(item.display) in mine:              # the option itself answers the recall question
            prompt = "Pick " + item.prompt[5:] if item.prompt.startswith("Type ") else item.prompt
        else:                                            # e.g. "( ) first" can't answer "What does =2+3*4 return?"
            prompt = f"Which move is this? {item.what}"
        return Challenge(cid, "PICK", prompt, item.hint, Pick(choices, item.display),
                         solve=(Fixture("type", "«ans»", item.display),),
                         wrong=((Fixture("type", "«ans»", options[0]),),), items=(item_id,))

    def final_items(self) -> set[str]:
        if self.final is None:
            return set()
        return {i for rnd in self.final.rounds for m in rnd.missions for i in m.items}

    def problems(self) -> list[str]:
        out = validate(self.schedule, self.worlds, self.final_items())
        for w in self.worlds:
            out += validate_world(w)
            for container in (*w.stages, w.boss):
                for m in container.missions:
                    out += [f"{m.id}: unknown item {i}" for i in m.items if i not in self.items]
        return out
