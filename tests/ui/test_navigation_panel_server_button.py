from PyQt6.QtWidgets import QApplication
import pytest

from api_sketchpad.ui.main_window import MainWindow


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_server_button_initial_text(qapp):  # noqa: ARG001
    w = MainWindow()
    btn = w.navigation_panel.server_button
    assert btn.text() == "Start Server"


def test_server_button_updates_running_state(qapp):  # noqa: ARG001
    w = MainWindow()
    w.navigation_panel.update_server_status(8123)
    assert w.navigation_panel.server_button.text() == "Stop Server (port 8123)"
    w.navigation_panel.update_server_status(None)
    assert w.navigation_panel.server_button.text() == "Start Server"


def test_cannot_start_server_with_no_interactions(qapp):  # noqa: ARG001
    w = MainWindow()
    # No interactions in repository
    w.navigation_panel.server_button.click()
    QApplication.processEvents()
    assert w._mock_server is None
    assert w.navigation_panel.server_button.text() == "Start Server"
