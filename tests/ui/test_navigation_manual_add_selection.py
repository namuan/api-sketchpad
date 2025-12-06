from PyQt6.QtWidgets import QApplication
import pytest

from api_sketchpad.ui.main_window import MainWindow


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_manual_add_only_last_selected(qapp):  # noqa: ARG001
    w = MainWindow()

    w.navigation_panel.add_button.click()
    w.navigation_panel.add_button.click()
    QApplication.processEvents()

    # Two items
    assert w.navigation_panel.interaction_list.count() == 2

    def _sel(row: int) -> bool:
        item = w.navigation_panel.interaction_list.item(row)
        widget = w.navigation_panel.interaction_list.itemWidget(item)
        return bool(widget.property("selected"))

    assert _sel(0) is False
    assert _sel(1) is True
