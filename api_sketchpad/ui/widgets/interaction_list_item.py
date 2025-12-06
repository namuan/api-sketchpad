"""Interaction list item widget for navigation panel."""

from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from .red_minus_icon import RedMinusIcon


class InteractionListItem(QFrame):
    """
    Custom widget for the navigation list item.
    Includes Title, Description, and Delete button.
    """

    def __init__(
        self,
        title: str,
        description: str,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._setup_ui(title, description)

    def _setup_ui(self, title: str, description: str) -> None:
        """Initialize UI components."""
        self.setObjectName("interactionItem")
        # Styling to look like a card with border
        self.setStyleSheet("""
            #interactionItem {
                border: 1px solid #333;
                border-radius: 4px;
                background-color: white;
            }
            #interactionItem[selected="true"] {
                border: 2px solid #1a73e8;
                background-color: #e8f0fe;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Top Row: Title + Delete Button
        top_row = QHBoxLayout()
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.title_label.setMinimumHeight(24)
        self.title_label.setContentsMargins(0, 2, 0, 2)

        self.delete_btn = RedMinusIcon(size=18)

        top_row.addWidget(self.title_label)
        top_row.addStretch()
        top_row.addWidget(self.delete_btn)

        # Bottom Row: Description
        self.desc_label = QLabel(description)
        self.desc_label.setStyleSheet("color: #555; font-style: italic; border: none;")

        layout.addLayout(top_row)
        layout.addWidget(self.desc_label)

    def set_title(self, title: str) -> None:
        """Update the title text."""
        self.title_label.setText(title)

    def set_description(self, description: str) -> None:
        """Update the description text."""
        self.desc_label.setText(description)

    def set_selected(self, *, selected: bool) -> None:
        self.setProperty("selected", selected)
        s = self.style()
        if s is not None:
            s.unpolish(self)
            s.polish(self)
        self.update()
