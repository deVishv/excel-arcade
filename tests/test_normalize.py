import pytest

from excel_drills.normalize import REPLACEMENTS, excel_normalize, normalize, variants


@pytest.mark.parametrize("typed, expected", [
    ("ctrl + shift + l", "CTRL+SHIFT+L"),
    ("Control+Page Down", "CTRL+PGDN"),
    ("Ctrl+↓", "CTRL+DOWN"),
    ("Ctrl+Down Arrow", "CTRL+DOWN"),
    ("ctrl+arrow keys", "CTRL+ARROW"),
    ("Ctrl+Minus", "CTRL+-"),
    ("Ctrl+Plus", "CTRL++"),
    ("Shift+Spacebar", "SHIFT+SPACE"),
    ("Escape", "ESC"),
    ("Ctl+End", "CTRL+END"),
])
def test_normalize(typed, expected):
    assert normalize(typed) == expected


def test_normalize_keeps_wildcard_characters_literal():
    assert normalize("Ctrl+*") == "CTRL+*"


def test_shortcut_variants_permute_modifiers():
    assert variants(("Ctrl+Shift+L",), "shortcut") == ["CTRL+SHIFT+L", "SHIFT+CTRL+L"]


def test_plus_key_survives_modifier_split():
    assert variants(("Ctrl+Shift++",), "shortcut") == ["CTRL+SHIFT++", "SHIFT+CTRL++"]


def test_keytip_sequences_accept_common_separators():
    got = set(variants(("Alt+H, A, C",), "shortcut"))
    assert {"ALT+H,A,C", "ALT,H,A,C", "ALTHAC", "ALT+H+A+C", "ALT>H>A>C"} <= got


def test_function_variants():
    assert set(variants(("SUMIFS",), "function")) == {
        "SUMIFS", "=SUMIFS", "SUMIFS()", "=SUMIFS()", "SUMIFS(", "=SUMIFS(",
    }


def test_concept_answers_are_only_normalized():
    assert variants(('">50"', ">50"), "concept") == ['">50"', ">50"]


def test_too_many_variants_rejected():
    many = tuple(f"Ctrl+{c}" for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%")
    with pytest.raises(ValueError):
        variants(many, "shortcut")


def test_excel_expression_applies_rules_in_python_order():
    expr = excel_normalize("A1")
    assert expr.startswith("SUBSTITUTE(" * len(REPLACEMENTS) + "UPPER(A1)")
    assert expr.index('" ",""') < expr.index('"PLUS","+"')
