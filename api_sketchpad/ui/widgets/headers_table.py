"""Headers table widget for managing HTTP headers."""

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class HeadersTableWidget(QWidget):
    """Table widget for managing HTTP headers with add/remove functionality."""

    headers_changed = pyqtSignal(dict)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        """Initialize the UI components."""
        self.layout = QHBoxLayout(self)

        # Create table widget
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Header", "Value"])
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.DoubleClicked)

        # Create buttons
        self.add_button = QPushButton("Add Header")
        self.remove_button = QPushButton("Remove Header")

        # Button layout
        button_layout = QVBoxLayout()
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)
        button_layout.addStretch()

        # Main layout
        self.layout.addWidget(self.table)
        self.layout.addLayout(button_layout)

    def _connect_signals(self) -> None:
        """Connect signals to slots."""
        self.add_button.clicked.connect(self._on_add_header)
        self.remove_button.clicked.connect(self._on_remove_header)
        self.table.cellChanged.connect(self._on_cell_changed)

    def _on_add_header(self) -> None:
        """Open dialog to add new header."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Header")

        layout = QVBoxLayout(dialog)

        # Key input
        key_label = QLabel("Header Key:")
        self.key_edit = QLineEdit()
        layout.addWidget(key_label)
        layout.addWidget(self.key_edit)

        # Value input
        value_label = QLabel("Header Value:")
        self.value_edit = QLineEdit()
        layout.addWidget(value_label)
        layout.addWidget(self.value_edit)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            key = self.key_edit.text().strip()
            value = self.value_edit.text().strip()

            if key:  # Only add if key is non-empty
                self._add_table_row(key, value)
                self._emit_headers_changed()

    def _on_remove_header(self) -> None:
        """Remove selected header."""
        current_row = self.table.currentRow()
        if current_row >= 0:
            self.table.removeRow(current_row)
            self._emit_headers_changed()

    def _on_cell_changed(self, row: int, column: int) -> None:
        """Handle cell edits and validate."""
        if column == 0:  # Header key column
            key_item = self.table.item(row, 0)
            if key_item and not key_item.text().strip():
                key_item.setText("")  # Clear invalid empty key
        self._emit_headers_changed()

    def _add_table_row(self, key: str, value: str) -> None:
        """Add a new row to the table."""
        row = self.table.rowCount()
        self.table.insertRow(row)

        key_item = QTableWidgetItem(key)
        value_item = QTableWidgetItem(value)

        self.table.setItem(row, 0, key_item)
        self.table.setItem(row, 1, value_item)

    def set_headers(self, headers: dict) -> None:
        """Populate table with headers."""
        blocked = True
        self.table.blockSignals(blocked)
        try:
            self.table.setRowCount(0)
            for key, value in headers.items():
                self._add_table_row(key, value)
        finally:
            blocked = False
            self.table.blockSignals(blocked)

    def get_headers(self) -> dict:
        """Get headers as dictionary."""
        headers = {}
        for row in range(self.table.rowCount()):
            key_item = self.table.item(row, 0)
            value_item = self.table.item(row, 1)

            if key_item and key_item.text().strip():
                key = key_item.text().strip()
                value = value_item.text().strip() if value_item else ""
                headers[key] = value
        return headers

    def _emit_headers_changed(self) -> None:
        """Emit headers_changed signal with current headers."""
        self.headers_changed.emit(self.get_headers())
