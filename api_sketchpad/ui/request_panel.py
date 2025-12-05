"""Request panel for configuring API interactions."""

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ..models.interaction import Interaction
from ..services.validation import ValidationService
from .syntax_highlighter import SyntaxFormat
from .widgets.headers_table import HeadersTableWidget
from .widgets.syntax_editor import SyntaxHighlightEditor


class RequestPanel(QWidget):
    """Middle panel for configuring API request parameters."""

    interaction_updated = pyqtSignal(Interaction)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.current_interaction = None
        self._updating = False
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        """Initialize UI components."""
        main_layout = QVBoxLayout(self)

        # Interaction metadata
        meta_layout = QFormLayout()

        self.name_field = QLineEdit()
        self.name_field.setMaxLength(255)
        meta_layout.addRow(QLabel("Interaction Name:"), self.name_field)

        self.description_field = QTextEdit()
        meta_layout.addRow(QLabel("Description:"), self.description_field)

        # HTTP method and endpoint
        self.method_dropdown = QComboBox()
        self.method_dropdown.addItems([
            "GET",
            "POST",
            "PUT",
            "DELETE",
            "PATCH",
            "HEAD",
            "OPTIONS",
        ])

        self.path_field = QLineEdit()
        self.path_field.setPlaceholderText("/api/endpoint")

        endpoint_layout = QHBoxLayout()
        endpoint_layout.addWidget(self.method_dropdown)
        endpoint_layout.addWidget(self.path_field)
        meta_layout.addRow(QLabel("Endpoint:"), endpoint_layout)

        main_layout.addLayout(meta_layout)

        # Request headers
        self.headers_table = HeadersTableWidget()
        main_layout.addWidget(QLabel("Request Headers:"))
        main_layout.addWidget(self.headers_table)

        # Request body
        self.body_editor = SyntaxHighlightEditor()
        main_layout.addWidget(QLabel("Request Body:"))
        main_layout.addWidget(self.body_editor)

        main_layout.addStretch()

    def _connect_signals(self) -> None:
        """Connect UI signals to slots."""
        self.name_field.textChanged.connect(self._on_field_changed)
        self.description_field.textChanged.connect(self._on_field_changed)
        self.method_dropdown.currentTextChanged.connect(self._on_field_changed)
        self.path_field.textChanged.connect(self._on_field_changed)
        self.headers_table.headers_changed.connect(self._on_field_changed)
        self.body_editor.textChanged.connect(self._on_field_changed)

    def load_interaction(self, interaction: Interaction) -> None:
        """Load an interaction into the panel."""
        self.current_interaction = interaction

        # Block signals while loading to prevent premature updates
        self._set_block_signals(block=True)

        self.name_field.setText(interaction.name)
        self.description_field.setPlainText(interaction.description)
        self.method_dropdown.setCurrentText(interaction.method)
        self.path_field.setText(interaction.path)
        self.headers_table.set_headers(interaction.request_headers)
        self.body_editor.set_text(interaction.request_body)

        # Set editor format based on Content-Type header
        content_type = interaction.request_headers.get("Content-Type", "")
        if "xml" in content_type:
            self.body_editor.set_format(SyntaxFormat.XML)
        else:
            self.body_editor.set_format(SyntaxFormat.JSON)

        # Restore signals
        self._set_block_signals(block=False)

    def save_to_interaction(self) -> None:
        """Save current UI state to interaction."""
        if not self.current_interaction:
            return
        ci = self.current_interaction
        ci.name = self.name_field.text()
        ci.description = self.description_field.toPlainText()
        ci.method = self.method_dropdown.currentText()
        ci.path = self.path_field.text()
        ci.request_headers = self.headers_table.get_headers()
        ci.request_body = self.body_editor.get_text()

    def _on_field_changed(self) -> None:
        """Handle any field change and update interaction."""
        if self.current_interaction and not self._updating:
            self._updating = True
            self.save_to_interaction()

            # Validate path
            valid, error = ValidationService.validate_url_path(
                self.current_interaction.path
            )
            if not valid:
                self.path_field.setStyleSheet("border: 1px solid red;")
                self.path_field.setToolTip(error)
            else:
                self.path_field.setStyleSheet("")
                self.path_field.setToolTip("")

            self.interaction_updated.emit(self.current_interaction)
            self._updating = False

    def _set_block_signals(self, *, block: bool) -> None:
        self.name_field.blockSignals(block)
        self.description_field.blockSignals(block)
        self.method_dropdown.blockSignals(block)
        self.path_field.blockSignals(block)
