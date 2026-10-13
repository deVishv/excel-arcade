"""Content invariants for every shipped world (and the demo)."""
import pytest

from excel_drills.content import FINAL, WORLDS
from excel_drills.model import validate_world
from tests.demo_content import DEMO

ALL = (DEMO, *WORLDS)


@pytest.mark.parametrize("world", ALL, ids=lambda w: w.code)
def test_world_is_valid(world):
    assert validate_world(world) == []


@pytest.mark.parametrize("world", ALL, ids=lambda w: w.code)
def test_row_drills_say_shift_space(world):
    for stage in (*world.stages, world.boss):
        for m in stage.missions:
            acts = {f.action for f in m.solve}
            if acts & {"delete_rows", "delete_rows_where", "insert_rows", "insert_rows_above", "hide_rows_where"}:
                assert "Shift+Space" in m.prompt, m.id


def test_full_course_schedule_when_complete():
    if len(WORLDS) < 11 or FINAL is None:
        pytest.skip("full-course spacing is validated once all 11 worlds and the Final Boss exist")
    from excel_drills.course import Course
    assert Course(WORLDS, FINAL).problems() == []
