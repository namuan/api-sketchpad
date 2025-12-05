"""Try It Out widget for live API testing."""

import json
from typing import override

from PyQt6.QtCore import QModelIndex, Qt
from PyQt6.QtGui import QColor, QPainter, QPen
from PyQt6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListView,
    QPushButton,
    QStyle,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ...models.interaction import Interaction
from ...services.api_simulator import APISimulator, SimulatedResponse

HTTP_STATUS_SUCCESS_MIN = 200
HTTP_STATUS_SUCCESS_MAX = 299
HTTP_STATUS_CLIENT_ERROR_MIN = 400
HTTP_STATUS_CLIENT_ERROR_MAX = 499


class _NoTickDelegate(QStyledItemDelegate):
    def __init__(self, padding: int = 8) -> None:
        super().__init__()
        self._padding = padding

    @override
    def paint(
        self, painter: QPainter | None, option: QStyleOptionViewItem, index: QModelIndex
    ) -> None:
        if painter is None:
            return
        bg = (
            QColor("#f2f2f2")
            if option.state & QStyle.StateFlag.State_MouseOver
            else (
                QColor("#e6e6e6")
                if option.state & QStyle.StateFlag.State_Selected
                else QColor("white")
            )
        )
        painter.fillRect(option.rect, bg)
        painter.setPen(QPen(QColor("black")))
        text = index.data()
        rect = option.rect.adjusted(self._padding, 0, 0, 0)
        painter.drawText(
            rect, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, text
        )


class TryItOutWidget(QWidget):
    """Widget for executing live API calls and viewing responses."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.api_simulator = APISimulator()
        self.current_interaction = None
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        """Initialize UI components."""
        layout = QVBoxLayout(self)

        # Endpoint configuration
        endpoint_layout = QHBoxLayout()

        self.method_dropdown = QComboBox()
        self.method_dropdown.addItems(["GET", "POST", "PUT", "DELETE", "PATCH"])
        self.method_dropdown.setStyleSheet(
            """
            QComboBox {
                border: 1px solid #333;
                border-radius: 4px;
                padding: 5px;
                background-color: white;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: black;
                outline: 0;
                selection-background-color: #e6e6e6;
                selection-color: black;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #f2f2f2;
                color: black;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #e6e6e6;
                color: black;
            }
            """
        )

        popup_view = QListView()
        popup_view.setAlternatingRowColors(False)
        popup_view.setStyleSheet("QListView { background-color: white; color: black; }")
        popup_view.setItemDelegate(_NoTickDelegate())
        self.method_dropdown.setView(popup_view)

        self.endpoint_field = QLineEdit()
        self.endpoint_field.setPlaceholderText("Enter endpoint URL")

        self.send_button = QPushButton("Send")

        endpoint_layout.addWidget(self.method_dropdown)
        endpoint_layout.addWidget(self.endpoint_field)
        endpoint_layout.addWidget(self.send_button)

        layout.addLayout(endpoint_layout)

        # Response display
        self.response_preview = QTextEdit()
        self.response_preview.setReadOnly(True)
        self.response_preview.setFontFamily("Consolas")
        self.response_preview.setFontPointSize(10)

        # Status indicator
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.response_preview)
        layout.addWidget(self.status_label)

    def _connect_signals(self) -> None:
        """Connect UI signals to slots."""
        self.send_button.clicked.connect(self.on_send_clicked)

    def load_interaction(self, interaction: Interaction) -> None:
        """Load interaction data into the widget."""
        self.current_interaction = interaction
        self.method_dropdown.setCurrentText(interaction.method)
        self.endpoint_field.setText(interaction.path)

    def on_send_clicked(self) -> None:
        """Execute API call and display response."""
        if not self.current_interaction:
            return

        self.status_label.setText("Sending request...")
        self.status_label.setStyleSheet("color: blue;")

        # Get request parameters
        method = self.method_dropdown.currentText()
        endpoint = self.endpoint_field.text()
        headers = self.current_interaction.request_headers
        body = self.current_interaction.request_body

        # Simulate API call
        response = self.api_simulator.execute_request(method, endpoint, headers, body)

        # Display response
        self.display_response(response)

    def display_response(self, response: SimulatedResponse) -> None:
        """Format and display the API response."""
        # Format headers
        headers = "\n".join([f"{k}: {v}" for k, v in response.headers.items()])

        # Format body
        try:
            body = json.dumps(json.loads(response.body), indent=2)
        except json.JSONDecodeError:
            body = response.body

        # Build response display
        response_text = (
            f"Status: {response.status_code}\n"
            f"Time: {response.elapsed_time:.2f}s\n\n"
            f"Headers:\n{headers}\n\n"
            f"Body:\n{body}"
        )

        self.response_preview.setPlainText(response_text)
        self.status_label.setText(f"Completed in {response.elapsed_time:.2f}s")

        # Set status color based on status code
        if HTTP_STATUS_SUCCESS_MIN <= response.status_code <= HTTP_STATUS_SUCCESS_MAX:
            self.status_label.setStyleSheet("color: green;")
        elif (
            HTTP_STATUS_CLIENT_ERROR_MIN
            <= response.status_code
            <= HTTP_STATUS_CLIENT_ERROR_MAX
        ):
            self.status_label.setStyleSheet("color: orange;")
        else:
            self.status_label.setStyleSheet("color: red;")
