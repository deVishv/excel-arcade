"""Build the workbooks: python -m excel_drills.build [--out workbooks] [--only S1]."""
from __future__ import annotations

import argparse
from pathlib import Path

from .course import Course
from .world_builder import build_world


def build_all(out_dir: Path, *, only: str | None = None) -> list[Path]:
    from .content import FINAL, WORLDS

    course = Course(WORLDS, FINAL)
    if only is None:
        problems = course.problems()
        if problems:
            raise SystemExit("Content problems:\n  " + "\n  ".join(problems))
    out_dir.mkdir(parents=True, exist_ok=True)
    return [build_world(course, w, out_dir).path for w in course.worlds if only in (None, w.code)]


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description="Build the Excel Arcade workbooks.")
    parser.add_argument("--out", default="workbooks", help="output folder (default: workbooks)")
    parser.add_argument("--only", help="build one workbook (world code such as S1) without full-course validation")
    args = parser.parse_args(argv)
    for path in build_all(Path(args.out), only=args.only):
        print(f"built {path}")


if __name__ == "__main__":
    main()
