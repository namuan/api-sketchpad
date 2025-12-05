"""Navigation panel for API SketchPad."""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..models.interaction import Interaction
from ..repository import InteractionRepository


class NavigationPanel(QWidget):
    """Left panel displaying list of interactions with add button."""

    interaction_selected = pyqtSignal(Interaction)

    def __init__(
        self, repository: InteractionRepository, parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self.repository = repository
        self._setup_ui()
        self._connect_signals()
        self.refresh_list()

    def _setup_ui(self) -> None:
        """Initialize UI components."""
        layout = QVBoxLayout(self)

        # Add Interaction button
        self.add_button = QPushButton("+ Add Interaction")
        layout.addWidget(self.add_button)

        # Interactions list
        self.interaction_list = QListWidget()
        self.interaction_list.setAlternatingRowColors(True)
        layout.addWidget(self.interaction_list)

    def _connect_signals(self) -> None:
        """Connect signals to slots."""
        self.add_button.clicked.connect(self.on_add_interaction)
        self.interaction_list.currentItemChanged.connect(self.on_interaction_selected)

    def refresh_list(self) -> None:
        """Refresh the list of interactions from repository."""
        self.interaction_list.clear()

        for interaction in self.repository.interactions:
            item = QListWidgetItem(interaction.name)
            item.setData(Qt.ItemDataRole.UserRole, interaction)
            self.interaction_list.addItem(item)

            # Highlight current interaction
            if interaction == self.repository.current_interaction:
                self.interaction_list.setCurrentItem(item)

    def on_add_interaction(self) -> None:
        """Handle adding new interaction."""
        new_interaction = Interaction()
        self.repository.add_interaction(new_interaction)
        self.repository.set_current_interaction(new_interaction)
        self.refresh_list()
        self.interaction_selected.emit(new_interaction)

    def on_interaction_selected(
        self, current: QListWidgetItem, _previous: QListWidgetItem
    ) -> None:
        """Handle interaction selection."""
        if current is not None:
            interaction = current.data(Qt.ItemDataRole.UserRole)
            self.repository.set_current_interaction(interaction)
            self.interaction_selected.emit(interaction)
