"""Red minus icon button widget."""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPainter, QPaintEvent, QPen
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

    def paint_event(self, a0: QPaintEvent | None) -> None:
        _ = a0
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        painter.setBrush(QColor("#d32f2f"))
        painter.setPen(Qt.PenStyle.NoPen)
        rect = self.rect().adjusted(1, 1, -1, -1)
        painter.drawEllipse(rect)

        painter.setPen(QPen(Qt.GlobalColor.white, 2))
        mid_y = self.height() // 2
        margin = 5
        painter.drawLine(margin, mid_y, self.width() - margin, mid_y)


RedMinusIcon.paintEvent = RedMinusIcon.paint_event
