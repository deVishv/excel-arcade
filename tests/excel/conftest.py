import pytest

from tests.excel.harness import ExcelSession


@pytest.fixture
def excel():
    session = ExcelSession()
    yield session
    session.stop()
