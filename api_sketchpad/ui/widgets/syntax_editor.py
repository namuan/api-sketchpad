"""Syntax highlighting editor widget for JSON/XML content."""

from typing import override

from PyQt6.QtCore import QMimeData
from PyQt6.QtWidgets import QTextEdit, QWidget

from ...ui.syntax_highlighter import SyntaxFormat, SyntaxHighlighter


class SyntaxHighlightEditor(QTextEdit):
    """Text editor with syntax highlighting for JSON/XML content."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._highlighter = SyntaxHighlighter(self.document())
        self._format = SyntaxFormat.JSON
        self._setup_editor()

    def _setup_editor(self) -> None:
        """Initialize editor settings."""
        self.setAcceptRichText(False)
        self.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.setFontFamily("Consolas")
        self.setFontPointSize(10)

    def set_format(self, fmt: SyntaxFormat) -> None:
        """Set content format (JSON/XML) and update highlighting."""
        self._format = fmt
        self._highlighter.set_format(fmt)

    def get_text(self) -> str:
        """Get plain text content."""
        return self.toPlainText()

    def set_text(self, text: str) -> None:
        """Set plain text content."""
        self.setPlainText(text)

    @override
    def insertFromMimeData(self, source: QMimeData | None) -> None:
        """Override paste to preserve formatting."""
        if source is None:
            return
        text = source.text()
        cursor = self.textCursor()

        current_block = cursor.block()
        indent = len(current_block.text()) - len(current_block.text().lstrip())

        cursor.insertText(" " * indent + text.strip())
