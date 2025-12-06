"""UI integration for importing OpenAPI specs from the File menu."""

from __future__ import annotations

from typing import TYPE_CHECKING, override

from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import QFileDialog, QMessageBox

from ..services.openapi_import_service import OpenAPIImportService

if TYPE_CHECKING:
    from ..repository import InteractionRepository
    from .main_window import MainWindow


class ImportWorker(QThread):
    """Background worker to parse OpenAPI without blocking the UI."""

    result_ok = pyqtSignal(list)
    result_error = pyqtSignal(str)

    def __init__(self, file_path: str) -> None:
        super().__init__()
        self._file_path = file_path
        self._service = OpenAPIImportService()

    @override
    def run(self) -> None:
        success, interactions, error = self._service.import_file(self._file_path)
        if success and interactions is not None:
            self.result_ok.emit(interactions)
        else:
            self.result_error.emit(error or "Import failed")


class ImportIntegration:
    """Attaches OpenAPI import flow to a window."""

    def __init__(self, parent: MainWindow, repository: InteractionRepository) -> None:
        self._parent = parent
        self._repository = repository
        self._worker: ImportWorker | None = None

    def prompt_and_import(self) -> None:
        """Prompt for a spec file and import in the background."""
        file_path, _ = QFileDialog.getOpenFileName(
            self._parent,
            "Import OpenAPI",
            "",
            "OpenAPI Spec (*.yaml *.yml *.json)",
        )
        if not file_path:
            return

        worker = ImportWorker(file_path)
        self._worker = worker
        worker.result_ok.connect(self._on_import_ok)  # type: ignore[arg-type]
        worker.result_error.connect(self._on_import_error)  # type: ignore[arg-type]
        worker.finished.connect(self._on_worker_finished)
        worker.finished.connect(worker.deleteLater)
        worker.start()

    def _on_import_ok(self, interactions: list) -> None:
        self._repository.clear()
        for i in interactions:
            self._repository.add_interaction(i)
        if hasattr(self._parent, "navigation_panel"):
            if self._repository.interactions:
                first = self._repository.interactions[0]
                self._repository.set_current_interaction(first)
            self._parent.navigation_panel.refresh_list()
            if self._repository.interactions:
                self._parent.navigation_panel.interaction_selected.emit(
                    self._repository.interactions[0]
                )
            else:
                self._parent.navigation_panel.interactions_empty.emit()
        if hasattr(self._parent, "status_bar"):
            self._parent.status_bar.showMessage("OpenAPI imported", 3000)

    def _on_import_error(self, message: str) -> None:
        QMessageBox.critical(self._parent, "Import Error", message)

    def _on_worker_finished(self) -> None:
        self._worker = None
