from PyQt6.QtWidgets import QApplication
import pytest

from api_sketchpad.ui.widgets.headers_table import HeadersTableWidget
from api_sketchpad.ui.widgets.query_params import QueryParamsWidget


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_delete_header_row_removes_widget(qapp):  # noqa: ARG001
    w = HeadersTableWidget()
    w.set_headers({"X-A": "1", "X-B": "2"})
    assert len(w._rows) == 2

    # Delete second row
    w._rows[1].delete_btn.click()

    # Process deferred deletion
    QApplication.processEvents()

    # Verify row removed
    assert len(w._rows) == 1
    names = [r.get_name() for r in w._rows]
    assert "X-B" not in names


def test_delete_query_param_row_removes_widget(qapp):  # noqa: ARG001
    w = QueryParamsWidget()
    w.set_params({"a": "1", "b": "2"})
    assert len(w._rows) == 2

    # Delete first row
    w._rows[0].delete_btn.click()
    QApplication.processEvents()

    assert len(w._rows) == 1
    names = [r.get_name() for r in w._rows]
    assert "a" not in names


def test_query_params_no_auto_empty_rows(qapp):  # noqa: ARG001
    w = QueryParamsWidget()
    w.set_params({})
    assert len(w._rows) == 0
    # Add a row via button
    w.add_button.click()
    QApplication.processEvents()
    assert len(w._rows) == 1
