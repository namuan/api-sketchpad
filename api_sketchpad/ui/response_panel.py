"""Response panel for defining expected API responses."""

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QInputDialog,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from ..models.interaction import Interaction
from ..models.response import Response
from .widgets.response_editor import ResponseEditor


class ResponsePanel(QWidget):
    """Right panel for defining expected responses by status code."""

    interaction_updated = pyqtSignal(Interaction)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.current_interaction = None
        self.response_editors = {}
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        """Initialize UI components."""
        main_layout = QVBoxLayout(self)

        # Status code tabs
        self.status_tabs = QTabWidget()
        self.status_tabs.setTabsClosable(True)
        main_layout.addWidget(self.status_tabs)

        # Add/Remove buttons
        button_layout = QHBoxLayout()

        self.add_button = QPushButton("Add Status Code")
        self.remove_button = QPushButton("Remove Status Code")

        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)
        button_layout.addStretch()

        main_layout.addLayout(button_layout)

    def _connect_signals(self) -> None:
        """Connect signals to slots."""
        self.add_button.clicked.connect(self._on_add_status)
        self.remove_button.clicked.connect(self._on_remove_status)
        self.status_tabs.tabCloseRequested.connect(self._on_remove_status)
        self.status_tabs.currentChanged.connect(self._on_tab_changed)

    def load_interaction(self, interaction: Interaction) -> None:
        """Load interaction responses into tabs."""
        self.current_interaction = interaction
        self.response_editors = {}
        self.status_tabs.clear()

        # Create tabs for each status code
        for status_code, response in interaction.responses.items():
            self._add_status_tab(status_code, response)

        # Add default tabs if empty
        if not interaction.responses:
            for code in [200, 400, 500]:
                self._add_status_tab(code, interaction.responses.get(code))

    def _add_status_tab(self, status_code: int, response: Response) -> None:
        """Add a new tab for a status code."""
        editor = ResponseEditor()
        editor.load_response(response)
        editor.headers_table.headers_changed.connect(self._on_response_changed)
        editor.body_editor.textChanged.connect(self._on_response_changed)

        self.status_tabs.addTab(editor, str(status_code))
        self.response_editors[status_code] = editor

    def _on_add_status(self) -> None:
        """Add new status code tab."""
        status_code, ok = QInputDialog.getInt(
            self, "Add Status Code", "Enter HTTP status code:", 200, 100, 599
        )

        if ok and status_code not in self.response_editors:
            # Create new response
            response = Response(status_code=status_code)
            self.current_interaction.responses[status_code] = response
            self._add_status_tab(status_code, response)
            self.interaction_updated.emit(self.current_interaction)

    def _on_remove_status(self, index: int | None = None) -> None:
        """Remove current status code tab."""
        if index is None:
            index = self.status_tabs.currentIndex()

        status_code = int(self.status_tabs.tabText(index))

        # Confirm removal for non-default codes
        if status_code not in {200, 400, 500}:
            reply = QMessageBox.question(
                self,
                "Confirm Removal",
                f"Remove status code {status_code}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        # Remove from interaction and UI
        del self.current_interaction.responses[status_code]
        self.status_tabs.removeTab(index)
        del self.response_editors[status_code]
        self.interaction_updated.emit(self.current_interaction)

    def _on_tab_changed(self, index: int) -> None:
        """Handle tab changes - nothing needed currently."""

    def _on_response_changed(self) -> None:
        """Save changes when any response field is modified."""
        if self.current_interaction:
            # Save all responses from editors
            for status_code, editor in self.response_editors.items():
                response = self.current_interaction.responses[status_code]
                editor.save_response(response)

            self.interaction_updated.emit(self.current_interaction)
