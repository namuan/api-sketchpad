"""Main application window for API SketchPad."""

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QFileDialog,
    QMainWindow,
    QMenu,
    QMenuBar,
    QMessageBox,
    QSplitter,
    QStatusBar,
)

from ..models.interaction import Interaction
from ..repository import InteractionRepository
from ..services.serialization import SerializationService
from .navigation_panel import NavigationPanel
from .request_panel import RequestPanel
from .response_panel import ResponsePanel


class MainWindow(QMainWindow):
    """Main application window with three-panel layout."""

    def __init__(self) -> None:
        super().__init__()
        self.repository = InteractionRepository()
        self._setup_ui()
        self._setup_menu()
        self._connect_signals()

    def _setup_ui(self) -> None:
        """Initialize UI components."""
        self.setWindowTitle("API SketchPad")
        self.setMinimumSize(QSize(1200, 800))

        # Create main splitter
        main_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Create panels
        self.navigation_panel = NavigationPanel(self.repository, self)
        self.request_panel = RequestPanel()
        self.response_panel = ResponsePanel()

        # Add panels to splitter
        main_splitter.addWidget(self.navigation_panel)
        main_splitter.addWidget(self.request_panel)
        main_splitter.addWidget(self.response_panel)

        # Set initial sizes
        main_splitter.setSizes([200, 600, 400])

        # Set central widget
        self.setCentralWidget(main_splitter)

        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

    def _setup_menu(self) -> None:
        """Create menu bar and actions."""
        menu_bar = QMenuBar(self)

        # File menu
        file_menu = QMenu("&File", self)

        self.new_action = QAction("&New", self)
        self.new_action.setShortcut("Ctrl+N")

        self.open_action = QAction("&Open...", self)
        self.open_action.setShortcut("Ctrl+O")

        self.save_action = QAction("&Save", self)
        self.save_action.setShortcut("Ctrl+S")

        self.save_as_action = QAction("Save &As...", self)
        self.exit_action = QAction("E&xit", self)

        file_menu.addAction(self.new_action)
        file_menu.addAction(self.open_action)
        file_menu.addAction(self.save_action)
        file_menu.addAction(self.save_as_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)

        menu_bar.addMenu(file_menu)
        self.setMenuBar(menu_bar)

    def _connect_signals(self) -> None:
        """Connect signals between components."""
        # Navigation to other panels
        self.navigation_panel.interaction_selected.connect(
            self._on_interaction_selected
        )

        # Panel updates
        self.request_panel.interaction_updated.connect(self._on_interaction_updated)
        self.response_panel.interaction_updated.connect(self._on_interaction_updated)

        # Menu actions
        self.new_action.triggered.connect(self._on_new)
        self.open_action.triggered.connect(self._on_open)
        self.save_action.triggered.connect(self._on_save)
        self.save_as_action.triggered.connect(self._on_save_as)
        self.exit_action.triggered.connect(self.close)

    def _on_interaction_selected(self, interaction: Interaction) -> None:
        """Handle interaction selection from navigation panel."""
        self.request_panel.load_interaction(interaction)
        self.response_panel.load_interaction(interaction)

    def _on_interaction_updated(self, _interaction: Interaction) -> None:
        """Handle interaction updates from panels."""
        self.navigation_panel.refresh_list()

    def _on_new(self) -> None:
        """Create new empty collection."""
        if self.repository.has_interactions():
            reply = QMessageBox.question(
                self,
                "New Collection",
                "This will clear all current interactions. Continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.No:
                return

        self.repository.clear()
        self.navigation_panel.refresh_list()
        self.status_bar.showMessage("New collection created", 3000)

    def _on_open(self) -> None:
        """Open collection from file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Collection", "", "API SketchPad Files (*.apisketch)"
        )
        if file_path:
            success, interactions, error = SerializationService.import_from_file(
                file_path
            )
            if success:
                self.repository.interactions = interactions
                self.navigation_panel.refresh_list()
                self.status_bar.showMessage(f"Opened: {file_path}", 3000)
            else:
                QMessageBox.critical(self, "Open Error", error)

    def _on_save(self) -> None:
        """Save collection to current file."""
        if not hasattr(self, "current_file"):
            self._on_save_as()
        else:
            success, error = SerializationService.export_to_file(
                self.repository.interactions, self.current_file
            )
            if success:
                self.status_bar.showMessage(f"Saved: {self.current_file}", 3000)
            else:
                QMessageBox.critical(self, "Save Error", error)

    def _on_save_as(self) -> None:
        """Save collection to new file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Collection", "", "API SketchPad Files (*.apisketch)"
        )
        if file_path:
            success, error = SerializationService.export_to_file(
                self.repository.interactions, file_path
            )
            if success:
                self.current_file = file_path
                self.status_bar.showMessage(f"Saved: {file_path}", 3000)
            else:
                QMessageBox.critical(self, "Save Error", error)
