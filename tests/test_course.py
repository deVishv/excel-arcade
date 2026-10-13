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


def test_pick_correct_option_answers_the_question(course):
    """The highlighted option must answer the question shown (found in review: 'What does =2+3*4 return?' had
    '( ) first' as its only right option). Otherwise the question is the move's own description."""
    for item_id, item in course.items.items():
        ch = course.pick(item_id, "X.T1")
        assert not ch.prompt.startswith("Type "), f"{item_id}: a dropdown question can't ask to type"
        if normalize(item.display) not in course.accepted(item_id):
            assert ch.prompt == f"Which move is this? {item.what}", item_id


def test_recall_accepts_equally_right_answers():
    from excel_drills.content import FINAL, WORLDS
    course = Course(WORLDS, FINAL)
    assert {"XMATCH", "MATCH()", "=MATCH("} <= set(course.accepted("F4.index_match"))
    assert "SEARCH" in course.accepted("F5.left_find")
    assert "DOUBLEQUOTE" in course.accepted("F2.quotes")
    assert "UNIQUE()" in course.accepted("F7.nesting")


def test_pick_is_deterministic(course):
    for item_id in course.items:
        assert course.pick(item_id, "a").check.choices == course.pick(item_id, "a").check.choices
