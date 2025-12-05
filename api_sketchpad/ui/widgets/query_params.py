"""Query params widget for managing URL query parameters."""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from .key_value_row import KeyValueRow


class QueryParamsWidget(QWidget):
    """Widget for managing query parameters with key-value rows."""

    params_changed = pyqtSignal(dict)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._rows: list[KeyValueRow] = []
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Initialize the UI components."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(5)

        # Header row with label and add button
        header_layout = QHBoxLayout()
        header_label = QLabel("Query Params")
        header_label.setStyleSheet("font-size: 12px; color: #555;")

        self.add_button = QPushButton("+ Add new query param")
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
        self.add_button.clicked.connect(self._on_add_param)

        header_layout.addWidget(header_label)
        header_layout.addStretch()
        header_layout.addWidget(self.add_button)
        main_layout.addLayout(header_layout)

        # Container for rows
        self.container = QWidget()
        self.container.setObjectName("queryParamsContainer")
        self.container.setStyleSheet("""
            #queryParamsContainer {
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

    def _on_add_param(self) -> None:
        """Add a new empty query param row."""
        self._add_row("", "")
        self._emit_params_changed()

    def _add_row(self, name: str, value: str) -> KeyValueRow:
        """Add a new row with the given name and value."""
        row = KeyValueRow()
        row.set_name(name)
        row.set_value(value)
        row.delete_clicked.connect(lambda r=row: self._on_remove_row(r))
        row.value_changed.connect(self._emit_params_changed)

        self._rows.append(row)
        self.container_layout.addWidget(row)
        return row

    def _on_remove_row(self, row: KeyValueRow) -> None:
        """Remove a query param row."""
        if row in self._rows:
            self._rows.remove(row)
            self.container_layout.removeWidget(row)
            row.deleteLater()
            self._emit_params_changed()

    def _emit_params_changed(self) -> None:
        """Emit the params_changed signal."""
        self.params_changed.emit(self.get_params())

    def set_params(self, params: dict) -> None:
        """Populate widget with query params."""
        # Clear existing rows
        for row in self._rows[:]:
            self.container_layout.removeWidget(row)
            row.deleteLater()
        self._rows.clear()

        # Add rows for each param
        for key, value in params.items():
            self._add_row(key, value)

        # Add empty rows if none exist
        if not params:
            for _ in range(3):
                self._add_row("", "")

    def get_params(self) -> dict:
        """Get query params as dictionary."""
        params = {}
        for row in self._rows:
            name = row.get_name()
            if name:  # Only include non-empty keys
                params[name] = row.get_value()
        return params
