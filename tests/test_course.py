import pytest

from excel_drills import theme as T
from excel_drills.checks import Pick, Recall
from excel_drills.course import Course
from excel_drills.normalize import normalize
from tests.demo_content import DEMO


@pytest.fixture(scope="module", params=["demo", "real"])
def course(request):
    if request.param == "demo":
        return Course((DEMO,))
    from excel_drills.content import FINAL, WORLDS
    return Course(WORLDS, FINAL)


def test_recall_challenge():
    course = Course((DEMO,))
    ch = course.recall("D1.ctrl_end", "X.R1", flashback=True)
    assert isinstance(ch.check, Recall) and "CTRL+END" in ch.check.accepted
    assert ch.prompt.endswith("(from D1-1 Alpha)")
    assert normalize(ch.wrong[0][0].value) not in ch.check.accepted


def test_pick_has_exactly_one_correct_option(course):
    for item_id, item in course.items.items():
        ch = course.pick(item_id, "X.T1")
        assert isinstance(ch.check, Pick)
        assert ch.check.choices.count(item.display) == 1 and len(ch.check.choices) == 4
        for option in ch.check.choices:
            if option == item.display:
                continue
            for other in course.items.values():
                if other.display == option:
                    assert not (set(course.accepted(other.id)) & set(course.accepted(item_id)))


def test_pick_is_deterministic(course):
    for item_id in course.items:
        assert course.pick(item_id, "a").check.choices == course.pick(item_id, "a").check.choices
