import pytest
import xlsxwriter

from excel_drills import theme as T


def test_contrast_reference_values():
    assert T.contrast("#000000", "#FFFFFF") == pytest.approx(21.0)
    assert T.contrast("#FFFFFF", "#FFFFFF") == pytest.approx(1.0)


@pytest.mark.parametrize("name", sorted(T.STYLES))
def test_every_style_meets_wcag_aa(name):
    spec = T.STYLES[name]
    fg = spec.get("font_color", T.INK)
    bg = spec.get("bg_color", T.WHITE)
    assert T.contrast(fg, bg) >= 4.5, f"{name}: {fg} on {bg}"


@pytest.mark.parametrize("name", sorted(T.CF_STYLES))
def test_conditional_styles_meet_wcag_aa(name):
    spec = T.CF_STYLES[name]
    assert T.contrast(spec["font_color"], spec["bg_color"]) >= 4.5


def test_input_border_is_visible_against_white():
    assert T.contrast(T.INPUT_BORDER, T.WHITE) >= 3.0


@pytest.mark.parametrize("name", sorted(T.STYLES))
def test_fonts_and_sizes(name):
    spec = T.STYLES[name]
    assert spec["font_name"] in {T.FONT_BODY, T.FONT_MONO, T.FONT_SYMBOL}
    assert spec["font_size"] >= 11


def test_result_words_carry_symbols():
    assert T.OK.startswith("✔") and T.OK_SELF.startswith("✔")
    assert T.BAD.startswith("✘") and T.TYPED.startswith("✘")
    assert T.NOT_YET.startswith("·") and T.NOT_YET_F9.startswith("·")


def test_formats_are_cached(tmp_path):
    wb = xlsxwriter.Workbook(str(tmp_path / "x.xlsx"))
    fmt = T.Formats(wb)
    assert fmt("body") is fmt("body")
    assert fmt("body", num_format="0") is not fmt("body")
    assert fmt.cf("ok") is fmt.cf("ok")
    wb.close()
