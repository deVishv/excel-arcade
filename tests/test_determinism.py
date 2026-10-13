"""Same content → byte-identical files (so rebuilding never creates noise in git)."""
from excel_drills.content import FINAL, WORLDS
from excel_drills.course import Course
from excel_drills.world_builder import build_world


def test_rebuild_is_byte_identical(tmp_path):
    course = Course(WORLDS, FINAL)
    (tmp_path / "a").mkdir()
    (tmp_path / "b").mkdir()
    first = build_world(course, WORLDS[0], tmp_path / "a").path.read_bytes()
    second = build_world(course, WORLDS[0], tmp_path / "b").path.read_bytes()
    assert first == second
