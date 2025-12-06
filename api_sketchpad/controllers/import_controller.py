"""Controller to orchestrate importing OpenAPI specs into the repository."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt6.QtCore import QObject, pyqtSignal

from ..models.interaction import Interaction
from ..services.openapi_import_service import OpenAPIImportService

if TYPE_CHECKING:
    from ..repository import InteractionRepository


class ImportController(QObject):
    """Coordinates OpenAPI imports and repository updates."""

    import_completed = pyqtSignal(list)
    import_failed = pyqtSignal(str)

    def __init__(self, repository: InteractionRepository) -> None:
        super().__init__()
        self._repository = repository
        self._service = OpenAPIImportService()

    def import_openapi_file(self, file_path: str) -> None:
        """Import interactions from an OpenAPI file and update the repository."""
        success, interactions, error = self._service.import_file(file_path)
        if not success or interactions is None:
            self.import_failed.emit(error or "Import failed")
            return

        self._repository.clear()
        for i in interactions:
            if isinstance(i, Interaction):
                self._repository.add_interaction(i)
        self.import_completed.emit(interactions)
