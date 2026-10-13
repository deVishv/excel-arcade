import pytest

from excel_drills.refs import absolute, cells_in, on_arena, resolve, sheet_ref, split_ref


@pytest.mark.parametrize("addr, expected", [
    ("B5", "$B$5"), ("b5:c9", "$B$5:$C$9"), ("B:B", "$B:$B"), ("5:7", "$5:$7"), ("$E$2", "$E$2"),
])
def test_absolute(addr, expected):
    assert absolute(addr) == expected


def test_absolute_rejects_garbage():
    with pytest.raises(ValueError):
        absolute("B5C")


def test_sheet_ref_quotes_when_needed():
    assert sheet_ref("Key", "C5") == "Key!$C$5"
    assert sheet_ref("S1-1 Arena", "B5") == "'S1-1 Arena'!$B$5"


def test_resolve_names_arena_and_indirect():
    out = resolve('=IF(«ans»="",«@B5»+«@C5:C9»,«#B21»)', {"ans": "'S1-1 Warp Zones'!$C$12"}, "S1-1 Arena")
    assert out == "=IF('S1-1 Warp Zones'!$C$12=\"\",'S1-1 Arena'!$B$5+'S1-1 Arena'!$C$5:$C$9,INDIRECT(\"'S1-1 Arena'!B21\"))"


def test_resolve_errors():
    with pytest.raises(KeyError):
        resolve("=«nope»", {}, None)
    with pytest.raises(KeyError):
        resolve("=«@B5»", {}, None)


def test_split_ref():
    assert split_ref("'S1-1 Arena'!$B$5") == ("S1-1 Arena", "B5")
    assert split_ref("Key!$E$3:$H$3") == ("Key", "E3:H3")
    assert split_ref("'It''s'!A1") == ("It's", "A1")


def test_on_arena_wraps_refs_outside_quotes():
    assert on_arena('=SUM(B5:B9)*$E$2+LOG10(4)&"A1"') == '=SUM(«@B5:B9»)*«@E2»+LOG10(4)&"A1"'


def test_on_arena_turns_spill_operator_into_anchorarray():
    # XlsxWriter must store the # spill operator as ANCHORARRAY(); a raw "#" corrupts the file.
    assert on_arena("=SUM(O6#)") == "=SUM(ANCHORARRAY(«@O6»))"


def test_cells_in():
    assert cells_in("B5:C6") == ["B5", "C5", "B6", "C6"]
    assert cells_in("D7") == ["D7"]
