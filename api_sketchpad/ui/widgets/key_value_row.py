"""Key-value row widget for headers and query params."""

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QLineEdit, QWidget

from .red_minus_icon import RedMinusIcon


class KeyValueRow(QWidget):
    """
    Represents a row with Name, Value inputs and a delete button.
    Used for Headers and Query Params.
    """

    delete_clicked = pyqtSignal()
    value_changed = pyqtSignal()

    def __init__(
        self,
        name_placeholder: str = "Name",
        value_placeholder: str = "Value",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._setup_ui(name_placeholder, value_placeholder)
        self._connect_signals()

    def _setup_ui(self, name_placeholder: str, value_placeholder: str) -> None:
        """Initialize UI components."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 2, 0, 2)
        layout.setSpacing(5)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText(name_placeholder)
        self.name_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #333;
                border-radius: 4px;
                padding: 4px;
                background-color: white;
            }
        """)

        self.value_input = QLineEdit()
        self.value_input.setPlaceholderText(value_placeholder)
        self.value_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #333;
                border-radius: 4px;
                padding: 4px;
                background-color: white;
            }
        """)

        self.delete_btn = RedMinusIcon(size=18)

        layout.addWidget(self.name_input, 1)
        layout.addWidget(self.value_input, 1)
        layout.addWidget(self.delete_btn)

    def _connect_signals(self) -> None:
        """Connect signals to slots."""
        self.delete_btn.clicked.connect(self.delete_clicked.emit)
        self.name_input.textChanged.connect(self.value_changed.emit)
        self.value_input.textChanged.connect(self.value_changed.emit)

    def get_name(self) -> str:
        """Get the name field value."""
        return self.name_input.text().strip()

    def get_value(self) -> str:
        """Get the value field value."""
        return self.value_input.text().strip()

    def set_name(self, name: str) -> None:
        """Set the name field value."""
        self.name_input.setText(name)

    def set_value(self, value: str) -> None:
        """Set the value field value."""
        self.value_input.setText(value)
