from PyQt6.QtWidgets import QApplication
import pytest

from api_sketchpad.models.interaction import Interaction
from api_sketchpad.ui.main_window import MainWindow


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _get_item_widget_for_row(panel: MainWindow, row: int):
    item = panel.navigation_panel.interaction_list.item(row)
    return panel.navigation_panel.interaction_list.itemWidget(item)


def test_highlight_selected_item(qapp):  # noqa: ARG001
    w = MainWindow()

    i1 = Interaction(name="First", description="desc1", method="GET", path="/a")
    i2 = Interaction(name="Second", description="desc2", method="POST", path="/b")
    w.repository.add_interaction(i1)
    w.repository.add_interaction(i2)
    w.repository.set_current_interaction(i1)
    w.navigation_panel.refresh_list()

    w_item0 = _get_item_widget_for_row(w, 0)
    w_item1 = _get_item_widget_for_row(w, 1)
    assert w_item0.property("selected") is True
    assert w_item1.property("selected") is False

    w.navigation_panel.interaction_list.setCurrentRow(1)
    QApplication.processEvents()

    w_item0 = _get_item_widget_for_row(w, 0)
    w_item1 = _get_item_widget_for_row(w, 1)
    assert w_item0.property("selected") is False
    assert w_item1.property("selected") is True
