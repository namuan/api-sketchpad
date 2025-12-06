from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication
import pytest

from api_sketchpad.services.openapi_import_service import OpenAPIImportService
from api_sketchpad.ui.main_window import MainWindow


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_auto_selects_first_interaction_on_import(qapp):  # noqa: ARG001
    w = MainWindow()
    spec_path = Path(__file__).resolve().parents[2] / "petstore-openapi.json"
    service = OpenAPIImportService()
    success, interactions, error = service.import_file(str(spec_path))
    assert success, error or "import failed"
    assert interactions and len(interactions) > 0

    w.import_integration._on_import_ok(interactions)
    QApplication.processEvents()

    first = w.repository.interactions[0]
    assert w.repository.get_current_interaction() == first

    current_item = w.navigation_panel.interaction_list.currentItem()
    assert current_item is not None
    assert current_item.data(Qt.ItemDataRole.UserRole) == first

    assert w.request_panel.current_interaction == first
    assert w.response_panel.current_interaction == first
