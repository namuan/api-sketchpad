"""Navigation panel for API SketchPad."""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..models.interaction import Interaction
from ..repository import InteractionRepository
from .widgets.interaction_list_item import InteractionListItem

DESCRIPTION_PREVIEW_LENGTH = 50


class NavigationPanel(QFrame):
    """Left panel displaying list of interactions with add button."""

    interaction_selected = pyqtSignal(Interaction)
    interactions_empty = pyqtSignal()
    start_server_clicked = pyqtSignal()

    def __init__(
        self, repository: InteractionRepository, parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self.repository = repository
        self._item_widgets: dict[int, InteractionListItem] = {}
        self._is_refreshing = False
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

        # Top controls row: Add Interaction + Start Server (visually separated header)
        controls_frame = QFrame()
        controls_frame.setObjectName("controlsFrame")
        controls_frame.setStyleSheet(
            """
            #controlsFrame {
                background-color: #f7f9fc;
                border: 1px solid #dfe3eb;
                border-radius: 6px;
            }
            """
        )
        top_controls = QHBoxLayout(controls_frame)
        top_controls.setContentsMargins(8, 8, 8, 8)
        top_controls.setSpacing(10)

        self.add_button = QPushButton("+ Add interaction")
        self.add_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_button.setStyleSheet(
            """
            QPushButton {
                background-color: #1a73e8;
                color: white;
                border: 1px solid #1a73e8;
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1669c1;
            }
            """
        )
        top_controls.addWidget(self.add_button)

        self.server_button = QPushButton("Start Server")
        self.server_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.server_button.setStyleSheet(
            """
            QPushButton {
                background-color: transparent;
                color: #1a73e8;
                border: 1px solid #1a73e8;
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e8f0fe;
            }
            """
        )
        top_controls.addWidget(self.server_button)

        layout.addWidget(controls_frame)

        # Empty state hint shown when there are no interactions
        self.empty_state_label = QLabel(
            "No interactions yet. Click '+ Add interaction' to create one."
        )
        self.empty_state_label.setWordWrap(True)
        self.empty_state_label.setStyleSheet(
            "color: #1a73e8; font-size: 12px; padding: 4px 2px;"
        )
        self.empty_state_label.hide()
        layout.addWidget(self.empty_state_label)

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
        self.interaction_list.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.interaction_list.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        layout.addWidget(self.interaction_list, 1)

    def _connect_signals(self) -> None:
        """Connect signals to slots."""
        self.add_button.clicked.connect(self.on_add_interaction)
        self.server_button.clicked.connect(self.start_server_clicked.emit)
        self.interaction_list.currentItemChanged.connect(self.on_interaction_selected)

    def refresh_list(self) -> None:
        """Refresh the list of interactions from repository."""
        self._is_refreshing = True
        block = True
        self.interaction_list.blockSignals(block)
        sb = self.interaction_list.verticalScrollBar()
        prev_scroll = sb.value() if sb is not None else 0
        self.interaction_list.clear()
        self._item_widgets.clear()

        for interaction in self.repository.interactions:
            # Create custom item widget
            item_widget = InteractionListItem(
                interaction.name or "Untitled Interaction",
                interaction.description[:DESCRIPTION_PREVIEW_LENGTH] + "..."
                if len(interaction.description) > DESCRIPTION_PREVIEW_LENGTH
                else interaction.description or "No description",
            )

            # Connect delete button
            item_widget.delete_btn.clicked.connect(
                lambda _, i=interaction: self._on_delete_interaction(i)
            )

            # Create QListWidgetItem container
            item = QListWidgetItem(self.interaction_list)
            item.setSizeHint(item_widget.sizeHint())
            item.setData(Qt.ItemDataRole.UserRole, interaction)
            self.interaction_list.setItemWidget(item, item_widget)

            # Track widget for updates
            self._item_widgets[id(interaction)] = item_widget

            # Highlight current interaction (identity comparison to avoid value-equality collisions)
            if interaction is self.repository.current_interaction:
                self.interaction_list.setCurrentItem(item)
            item_widget.set_selected(
                selected=interaction is self.repository.current_interaction
            )

        if not self.repository.interactions:
            # Show empty indicator and slightly highlight the add button
            self.empty_state_label.show()
            self.add_button.setStyleSheet(
                """
                QPushButton {
                    background-color: #1a73e8;
                    color: white;
                    border: 2px solid #1a73e8;
                    border-radius: 6px;
                    padding: 6px 12px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #1669c1;
                }
                """
            )
            self.interactions_empty.emit()
        else:
            # Hide empty indicator and restore default button style
            self.empty_state_label.hide()
            self.add_button.setStyleSheet(
                """
                QPushButton {
                    background-color: #1a73e8;
                    color: white;
                    border: 1px solid #1a73e8;
                    border-radius: 6px;
                    padding: 6px 12px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #1669c1;
                }
                """
            )
        unblock = False
        self.interaction_list.blockSignals(unblock)
        self._is_refreshing = False
        if sb is not None:
            sb.setValue(prev_scroll)

    def update_server_status(self, port: int | None) -> None:
        """Update server button text to reflect server running state."""
        if port is not None:
            self.server_button.setText(f"Stop Server (port {port})")
        else:
            self.server_button.setText("Start Server")

    def _on_delete_interaction(self, interaction: Interaction) -> None:
        """Handle deleting an interaction."""
        self.repository.remove_interaction(interaction)
        self.refresh_list()

        # Select first interaction if available
        if self.repository.interactions:
            first = self.repository.interactions[0]
            self.repository.set_current_interaction(first)
            self.interaction_selected.emit(first)
        else:
            self.interactions_empty.emit()

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
        if self._is_refreshing:
            return
        if current is not None:
            interaction = current.data(Qt.ItemDataRole.UserRole)
            self.repository.set_current_interaction(interaction)
            for i in self.repository.interactions:
                w = self._item_widgets.get(id(i))
                if w is not None:
                    w.set_selected(selected=i is interaction)
            self.interaction_selected.emit(interaction)
