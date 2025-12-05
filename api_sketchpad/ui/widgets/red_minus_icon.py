"""Red minus icon button widget."""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPainter, QPen
from PyQt6.QtWidgets import QPushButton, QWidget


class RedMinusIcon(QPushButton):
    """
    A custom button that draws a red circle with a white minus sign,
    used for delete actions.
    """

    def __init__(self, size: int = 20, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedSize(size, size)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("border: none; background: transparent;")

    def paintEvent(self, event) -> None:  # noqa: ARG002
        """Draw the red circle with white minus sign."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw Red Circle
        painter.setBrush(QColor("#d32f2f"))  # Red color
        painter.setPen(Qt.PenStyle.NoPen)
        rect = self.rect().adjusted(1, 1, -1, -1)
        painter.drawEllipse(rect)

        # Draw White Minus
        painter.setPen(QPen(Qt.GlobalColor.white, 2))
        mid_y = self.height() // 2
        margin = 5
        painter.drawLine(margin, mid_y, self.width() - margin, mid_y)
