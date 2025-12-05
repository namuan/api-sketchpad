"""Syntax highlighter for JSON and XML content."""

from enum import Enum

from PyQt6.QtCore import QRegularExpression
from PyQt6.QtGui import (
    QColor,
    QFont,
    QSyntaxHighlighter,
    QTextCharFormat,
    QTextDocument,
)


class SyntaxFormat(Enum):
    JSON = "json"
    XML = "xml"


class SyntaxHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for JSON and XML content."""

    def __init__(self, parent: QTextDocument = None) -> None:
        super().__init__(parent)
        self._format = SyntaxFormat.JSON
        self._rules = []
        self._setup_formats()
        self._setup_rules()

    def set_format(self, fmt: SyntaxFormat) -> None:
        """Set the syntax format (JSON or XML)."""
        self._format = fmt
        self._setup_rules()
        self.rehighlight()

    def _setup_formats(self) -> None:
        """Initialize text formats for different syntax elements."""
        self._formats = {
            "keyword": self._create_format(QColor("#000080"), "bold"),  # Dark Blue
            "string": self._create_format(QColor("#008000")),  # Green
            "number": self._create_format(QColor("#FF8C00")),  # Dark Orange
            "brace": self._create_format(QColor("#0000FF")),  # Blue
            "tag": self._create_format(QColor("#000080"), "bold"),  # Dark Blue
            "attribute": self._create_format(QColor("#FF4500")),  # OrangeRed
            "comment": self._create_format(QColor("#808080")),  # Gray
            "error": self._create_format(QColor("#FF0000"), "underline"),  # Red
        }

    @staticmethod
    def _create_format(color: QColor, style: str = "") -> QTextCharFormat:
        """Create a text format with specified color and style."""
        fmt = QTextCharFormat()
        fmt.setForeground(color)
        if "bold" in style:
            fmt.setFontWeight(QFont.Weight.Bold)
        if "italic" in style:
            fmt.setFontItalic(True)
        if "underline" in style:
            fmt.setUnderlineStyle(QTextCharFormat.UnderlineStyle.SingleUnderline)
        return fmt

    def _setup_rules(self) -> None:
        """Setup highlighting rules based on current format."""
        self._rules = []

        if self._format == SyntaxFormat.JSON:
            # JSON rules
            self._rules.extend([
                (r"\\b(true|false|null)\\b", 0, self._formats["keyword"]),
                (r'"[^"\\]*(\\.[^"\\]*)*"', 0, self._formats["string"]),
                (r"-?\\d+(\\.\\d+)?([eE][+-]?\\d+)?", 0, self._formats["number"]),
                (r"[{}[\\],]", 0, self._formats["brace"]),
            ])
        elif self._format == SyntaxFormat.XML:
            # XML rules
            self._rules.extend([
                (r"<\\?xml.*?\\?>", 0, self._formats["tag"]),
                (r"<!--.*?-->", 0, self._formats["comment"]),
                (r"<[/?]?\\w+", 0, self._formats["tag"]),
                (r"/?>", 0, self._formats["tag"]),
                (r"\\w+\\s*=", 0, self._formats["attribute"]),
                (r'"[^"]*"', 0, self._formats["string"]),
            ])

        # Compile patterns
        self._compiled_rules = []
        for pattern, group, fmt in self._rules:
            rx = QRegularExpression(pattern)
            rx.setPatternOptions(
                QRegularExpression.PatternOption.InvertedGreedinessOption
            )
            self._compiled_rules.append((rx, group, fmt))

    def highlight_block(self, text: str) -> None:
        """Apply syntax highlighting to the current text block."""
        for pattern, group, fmt in self._compiled_rules:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(
                    match.capturedStart(group), match.capturedLength(group), fmt
                )


SyntaxHighlighter.highlightBlock = SyntaxHighlighter.highlight_block
