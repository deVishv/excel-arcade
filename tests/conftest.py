import sys

import pytest


def pytest_collection_modifyitems(config, items):
    if sys.platform == "win32":
        return
    skip = pytest.mark.skip(reason="Excel COM tests need Windows with Microsoft Excel")
    for item in items:
        if "excel" in item.keywords:
            item.add_marker(skip)
