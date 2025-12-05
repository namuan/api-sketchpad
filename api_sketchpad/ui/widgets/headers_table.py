"""Headers table widget for managing HTTP headers."""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QCompleter,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from .key_value_row import KeyValueRow


class HeadersTableWidget(QWidget):
    """Widget for managing HTTP headers with key-value rows."""

    headers_changed = pyqtSignal(dict)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._rows: list[KeyValueRow] = []
        self._header_name_suggestions: list[str] = [
            "Accept",
            "Content-Type",
            "Authorization",
            "Cache-Control",
            "Accept-Language",
            "Accept-Encoding",
            "User-Agent",
        ]
        self._value_suggestions_map: dict[str, list[str]] = {
            "Content-Type": [
                "application/json",
                "application/xml",
                "text/plain",
                "multipart/form-data",
                "application/x-www-form-urlencoded",
                "application/octet-stream",
            ],
            "Accept": [
                "application/json",
                "application/xml",
                "text/plain",
                "*/*",
            ],
            "Authorization": [
                "Bearer ",
                "Basic ",
            ],
        }
        self._default_value_suggestions: list[str] = [
            "application/json",
            "text/plain",
        ]
        self._name_completer = QCompleter(self._header_name_suggestions)
        self._name_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._name_completer.setCompletionMode(
            QCompleter.CompletionMode.PopupCompletion
        )
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Initialize the UI components."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(5)

        # Header row with label and add button
        header_layout = QHBoxLayout()
        header_label = QLabel("Headers")
        header_label.setStyleSheet("font-size: 12px; color: #555;")

        self.add_button = QPushButton("+ Add new header")
        self.add_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_button.setStyleSheet("""
            QPushButton {
                border: 1px solid #333;
                border-radius: 10px;
                padding: 2px 8px;
                font-size: 10px;
                background: white;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
        """)
        self.add_button.clicked.connect(self._on_add_header)

        header_layout.addWidget(header_label)
        header_layout.addStretch()
        header_layout.addWidget(self.add_button)
        main_layout.addLayout(header_layout)

        # Container for rows
        self.container = QWidget()
        self.container.setObjectName("headersContainer")
        self.container.setStyleSheet("""
            #headersContainer {
                border: 1px solid #333;
                border-radius: 0px;
                background-color: white;
            }
        """)
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setSpacing(5)
        self.container_layout.setContentsMargins(5, 5, 5, 5)

        # Column titles
        titles_layout = QHBoxLayout()
        name_label = QLabel("Name")
        value_label = QLabel("Value")
        name_label.setStyleSheet("font-size: 10px; font-weight: bold; border: none;")
        value_label.setStyleSheet("font-size: 10px; font-weight: bold; border: none;")
        titles_layout.addWidget(name_label, 1)
        titles_layout.addWidget(value_label, 1)
        titles_layout.addSpacing(25)  # Space for delete icon
        self.container_layout.addLayout(titles_layout)

        main_layout.addWidget(self.container)

    def _on_add_header(self) -> None:
        """Add a new empty header row."""
        self._add_row("", "")
        self._emit_headers_changed()

    def _add_row(self, name: str, value: str) -> KeyValueRow:
        """Add a new row with the given name and value."""
        row = KeyValueRow()
        row.set_name(name)
        row.set_value(value)
        row.delete_clicked.connect(lambda r=row: self._on_remove_row(r))
        row.value_changed.connect(self._emit_headers_changed)
        row.name_input.setCompleter(self._name_completer)
        self._update_value_completer(row)
        row.name_input.textChanged.connect(
            lambda _text, r=row: self._update_value_completer(r)
        )

        self._rows.append(row)
        self.container_layout.addWidget(row)
        return row

    def _on_remove_row(self, row: KeyValueRow) -> None:
        """Remove a header row."""
        if row in self._rows:
            self._rows.remove(row)
            self.container_layout.removeWidget(row)
            row.setParent(None)
            row.deleteLater()
            self._emit_headers_changed()

    def _emit_headers_changed(self) -> None:
        """Emit the headers_changed signal."""
        self.headers_changed.emit(self.get_headers())

    def set_headers(self, headers: dict) -> None:
        """Populate widget with headers."""
        # Clear existing rows
        for row in self._rows[:]:
            self.container_layout.removeWidget(row)
            row.setParent(None)
            row.deleteLater()
        self._rows.clear()

        # Add rows for each header
        for key, value in headers.items():
            self._add_row(key, value)

    def get_headers(self) -> dict:
        """Get headers as dictionary."""
        headers = {}
        for row in self._rows:
            name = row.get_name()
            if name:  # Only include non-empty keys
                headers[name] = row.get_value()
        return headers

    def _update_value_completer(self, row: KeyValueRow) -> None:
        name = row.get_name()
        suggestions = self._value_suggestions_map.get(
            name, self._default_value_suggestions
        )
        completer = QCompleter(suggestions)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        row.value_input.setCompleter(completer)
