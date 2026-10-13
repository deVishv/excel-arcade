import openpyxl
import xlsxwriter


def test_pinned_versions():
    assert xlsxwriter.__version__ == "3.2.9"
    assert openpyxl.__version__ == "3.1.5"


def test_package_imports():
    import excel_drills

    assert excel_drills.__doc__
