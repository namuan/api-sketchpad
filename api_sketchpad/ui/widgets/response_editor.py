"""Response editor widget for API responses."""

from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

from ...models.response import Response
from ..syntax_highlighter import SyntaxFormat
from .headers_table import HeadersTableWidget
from .syntax_editor import SyntaxHighlightEditor


class ResponseEditor(QWidget):
    """Widget for editing response headers and body."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Initialize UI components."""
        layout = QVBoxLayout(self)

        # Response headers
        layout.addWidget(QLabel("Response Headers:"))
        self.headers_table = HeadersTableWidget()
        layout.addWidget(self.headers_table)

        # Response body
        layout.addWidget(QLabel("Response Body:"))
        self.body_editor = SyntaxHighlightEditor()
        self.body_editor.set_format(SyntaxFormat.JSON)
        layout.addWidget(self.body_editor)

    def load_response(self, response: Response) -> None:
        """Load response data into editor."""
        self.headers_table.set_headers(response.headers)
        self.body_editor.set_text(response.body)

    def save_response(self, response: Response) -> None:
        """Save editor data to response object."""
        response.headers = self.headers_table.get_headers()
        response.body = self.body_editor.get_text()
