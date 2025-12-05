"""Error dialog for displaying application errors."""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class ErrorDialog(QDialog):
    """Custom dialog for displaying error messages with details."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Error")
        self.setMinimumSize(400, 300)
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Initialize UI components."""
        layout = QVBoxLayout(self)

        # Error message
        self.message_label = QLabel()
        self.message_label.setWordWrap(True)
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message_label.setStyleSheet("font-weight: bold; color: red;")
        layout.addWidget(self.message_label)

        # Technical details
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setFontFamily("Consolas")
        self.details_text.setFontPointSize(10)
        self.details_text.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        layout.addWidget(self.details_text)

        # Buttons
        button_layout = QHBoxLayout()

        self.copy_button = QPushButton("Copy Details")
        self.copy_button.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )
        self.copy_button.clicked.connect(self._on_copy_details)

        self.close_button = QPushButton("Close")
        self.close_button.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )
        self.close_button.clicked.connect(self.accept)

        button_layout.addWidget(self.copy_button)
        button_layout.addStretch()
        button_layout.addWidget(self.close_button)
        layout.addLayout(button_layout)

    def show_error(self, title: str, message: str, details: str = "") -> None:
        """Display error information in the dialog."""
        self.setWindowTitle(title)
        self.message_label.setText(message)
        self.details_text.setPlainText(details)
        self.exec()

    def _on_copy_details(self) -> None:
        """Copy error details to clipboard."""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.details_text.toPlainText())
