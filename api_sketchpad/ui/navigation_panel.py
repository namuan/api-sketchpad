"""Navigation panel for API SketchPad."""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..models.interaction import Interaction
from ..repository import InteractionRepository
from .widgets.interaction_list_item import InteractionListItem


class NavigationPanel(QFrame):
    """Left panel displaying list of interactions with add button."""

    interaction_selected = pyqtSignal(Interaction)

    def __init__(
        self, repository: InteractionRepository, parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self.repository = repository
        self._item_widgets: dict[str, InteractionListItem] = {}
        self._setup_ui()
        self._connect_signals()
        self.refresh_list()

    def _setup_ui(self) -> None:
        """Initialize UI components."""
        self.setStyleSheet("""
            NavigationPanel {
                border: 1px solid #333;
                background-color: white;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Add Interaction button (styled like api-window.py)
        self.add_button = QPushButton("+ Add interaction")
        self.add_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_button.setStyleSheet("""
            QPushButton {
                border: 1px solid #333;
                border-radius: 4px;
                padding: 6px;
                background-color: white;
                text-align: left;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
        """)
        layout.addWidget(self.add_button)

        # Interactions list (styled like api-window.py)
        self.interaction_list = QListWidget()
        self.interaction_list.setStyleSheet("""
            QListWidget {
                border: none;
                background-color: transparent;
            }
            QListWidget::item {
                background-color: transparent;
                margin-bottom: 10px;
            }
            QListWidget::item:selected {
                background-color: transparent;
            }
        """)
        self.interaction_list.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        layout.addWidget(self.interaction_list)

        layout.addStretch()

    def _connect_signals(self) -> None:
        """Connect signals to slots."""
        self.add_button.clicked.connect(self.on_add_interaction)
        self.interaction_list.currentItemChanged.connect(self.on_interaction_selected)

    def refresh_list(self) -> None:
        """Refresh the list of interactions from repository."""
        self.interaction_list.clear()
        self._item_widgets.clear()

        for interaction in self.repository.interactions:
            # Create custom item widget
            item_widget = InteractionListItem(
                interaction.name or "Untitled Interaction",
                interaction.description[:50] + "..."
                if len(interaction.description) > 50
                else interaction.description or "No description",
            )

            # Connect delete button
            item_widget.delete_btn.clicked.connect(
                lambda checked, i=interaction: self._on_delete_interaction(i)
            )

            # Create QListWidgetItem container
            item = QListWidgetItem(self.interaction_list)
            item.setSizeHint(item_widget.sizeHint())
            item.setData(Qt.ItemDataRole.UserRole, interaction)
            self.interaction_list.setItemWidget(item, item_widget)

            # Track widget for updates
            self._item_widgets[interaction.id] = item_widget

            # Highlight current interaction
            if interaction == self.repository.current_interaction:
                self.interaction_list.setCurrentItem(item)

    def _on_delete_interaction(self, interaction: Interaction) -> None:
        """Handle deleting an interaction."""
        self.repository.remove_interaction(interaction)
        self.refresh_list()

        # Select first interaction if available
        if self.repository.interactions:
            first = self.repository.interactions[0]
            self.repository.set_current_interaction(first)
            self.interaction_selected.emit(first)

    def on_add_interaction(self) -> None:
        """Handle adding new interaction."""
        new_interaction = Interaction()
        self.repository.add_interaction(new_interaction)
        self.repository.set_current_interaction(new_interaction)
        self.refresh_list()
        self.interaction_selected.emit(new_interaction)

    def on_interaction_selected(
        self, current: QListWidgetItem | None, _previous: QListWidgetItem | None
    ) -> None:
        """Handle interaction selection."""
        if current is not None:
            interaction = current.data(Qt.ItemDataRole.UserRole)
            self.repository.set_current_interaction(interaction)
            self.interaction_selected.emit(interaction)
