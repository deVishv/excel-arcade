import pytest

from excel_drills import checks as C
from excel_drills import theme as T


def test_q_escapes_and_splits():
    assert C.q('say "hi"') == '"say ""hi"""'
    long = C.q("x" * 450)
    assert long.count("&") == 3 and all(len(p) <= 255 for p in long.split("&"))


def test_q_never_puts_a_function_call_inside_one_literal():
    # XlsxWriter's future-function prefixing would rewrite "XLOOKUP(" even inside a string
    assert C.q("use XLOOKUP(") == '"use XLOOKUP"&"("'
    assert C.q("Press F5 (or Ctrl+G)") == '"Press F5 (or Ctrl+G)"'


def test_lit_rejects_bool():
    with pytest.raises(TypeError):
        C.lit(True)
    assert C.lit(0.08) == "0.08" and C.lit(3) == "3" and C.lit("A") == '"A"'


def test_recall_formula_is_guarded_and_wildcard_safe():
    cf = C.Recall(("CTRL+END",)).formula()
    assert cf.blank == "" and cf.template.startswith("=IFERROR(LET(_xlpm.a,«ans»")
    assert "=«keyrow»)" in cf.template and "MATCH(" not in cf.template


def test_pick_compares_as_text():
    cf = C.Pick(("A", "B", "C"), "B").formula()
    assert '«ans»&""=«key»&""' in cf.template
    with pytest.raises(ValueError):
        C.Pick(("A", "B"), "Z")


def test_find_text_and_number():
    text = C.Find("Comet")
    assert text.key_values()[0].value == "COMET"
    assert '"$",""' in text.formula().template
    num = C.Find(6690)
    assert "VALUE(" in num.formula().template and "1E-9" in num.formula().template


def test_value_bool_expectation_stored_as_text():
    v = C.Value("G6", True, "=C6>=50")
    kv = v.key_values()[0]
    assert kv.value == "TRUE" and kv.template == '=IF(C6>=50,"TRUE","FALSE")'
    assert "ISLOGICAL(«@G6»)" in v.formula().template


def test_value_uses_find_with_boundaries_not_search():
    t = C.Value("F5", 10, "=«@C6»*«@D6»", uses=("SUMIFS",), dollar=True).formula().template
    assert '&"SUMIFS"&"(",UPPER(FORMULATEXT(«@F5»))' in t
    assert "SEARCH(" not in t and "add $" in t


def test_filled_names_each_expectation():
    f = C.Filled(("C6", "C7"), (1.6, 2.8), ("=«@B6»*«@E5»", "=«@B7»*«@E5»"))
    assert [kv.template for kv in f.key_values()] == ["=«@B6»*«@E5»", "=«@B7»*«@E5»"]
    assert "«key2»" in f.formula().template and "COUNTA(«@C6»,«@C7»)=0" in f.formula().template


def test_spill_compares_whole_arrays():
    s = C.Spill("K6", ((1,), (2,)), "=SEQUENCE(2)", uses=("SEQUENCE",))
    t = s.formula().template
    assert "ANCHORARRAY(«@K6»)" in t and "ANCHORARRAY(«spill»)" in t
    assert s.spill().template == "=SEQUENCE(2)"


def test_condition_blank_and_volatility():
    plain = C.Condition("«@B6»=1")
    assert plain.formula().blank == T.NOT_YET and not plain.formula().volatile
    f9 = C.Condition(C.format_in(["B6"], ["P0"]), f9=True)
    # f9 only changes the wording; "volatile" is reserved for results that depend on today's date
    assert f9.formula().blank == T.NOT_YET_F9 and not f9.formula().volatile
    assert C.Condition(C.today_constant("C6"), volatile=True).formula().volatile


def test_condition_helpers():
    assert C.all_equal(["B6", "B7"], "DONE") == 'AND(«@B6»="DONE",«@B7»="DONE")'
    assert C.line_break("D6", "Line 1", "Line 2") == 'EXACT(«@D6»,"Line 1"&CHAR(10)&"Line 2")'
    assert C.ascending("C5:C8") == "SUMPRODUCT(--(«@C5:C7»>«@C6:C8»))=0"
    assert C.descending("C5:C8") == "SUMPRODUCT(--(«@C5:C7»<«@C6:C8»))=0"
    assert C.sheet_exists("Vault") == 'ISREF(INDIRECT("\'Vault\'!A1"))'
    assert "XLOOKUP(«@B6:B7»," in C.pairs_intact("B6:B7", "C6:C7", {"A": 1, "B": 2})
    assert C.marker_gap("B", "ROW ABOVE", "INSERT ABOVE", 3) == \
        'MATCH("INSERT ABOVE",«@B:B»,0)-MATCH("ROW ABOVE",«@B:B»,0)=3'


def test_self_check():
    s = C.SelfCheck()
    assert s.options() == (T.DONE,)
    assert T.OK_SELF in s.formula().template


def test_self_check_result_is_error_guarded():
    # Global Constraint: no learner-facing result may show an Excel error (a pasted #N/A would break the score)
    assert C.SelfCheck().formula().template.startswith("=IFERROR(")
