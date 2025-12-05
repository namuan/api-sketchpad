"""Response panel for defining expected API responses."""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QHBoxLayout,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from ..models.interaction import Interaction
from ..models.response import Response
from .widgets.response_editor import ResponseEditor

DEFAULT_STATUS_CODES = (200, 400, 500)


class ResponsePanel(QFrame):
    """Right panel for defining expected responses by status code."""

    interaction_updated = pyqtSignal(Interaction)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.current_interaction: Interaction | None = None
        self.response_editors: dict[int, ResponseEditor] = {}
        self._setup_ui()
        self._connect_signals()
        self.setEnabled(False)

    def _setup_ui(self) -> None:
        """Initialize UI components."""
        self.setStyleSheet("""
            ResponsePanel {
                border: 1px solid #333;
                background-color: white;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Status code buttons (segmented control)
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(0)
        buttons_layout.addStretch()

        self.status_button_group = QButtonGroup(self)
        self.status_button_group.setExclusive(True)
        self.status_buttons: dict[int, QPushButton] = {}

        for i, code in enumerate(DEFAULT_STATUS_CODES):
            btn = QPushButton(str(code))
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedSize(70, 30)

            # Style for segmented button look
            border_radius = ""
            if i == 0:
                border_radius = (
                    "border-top-left-radius: 4px; border-bottom-left-radius: 4px;"
                )
            elif i == len(DEFAULT_STATUS_CODES) - 1:
                border_radius = (
                    "border-top-right-radius: 4px; border-bottom-right-radius: 4px;"
                )

            # Apply negative left margin only for non-first buttons to collapse inner borders
            margin_left = "0px" if i == 0 else "-1px"

            btn.setStyleSheet(f"""
                QPushButton {{
                    background: white;
                    border: 1px solid #333;
                    font-weight: bold;
                    font-size: 14px;
                    color: #333;
                    {border_radius}
                    margin-left: {margin_left};
                }}
                QPushButton:checked {{
                    background: #e0e0e0;
                    color: black;
                }}
                QPushButton:hover {{
                    background: #f5f5f5;
                }}
                QPushButton:checked:hover {{
                    background: #d0d0d0;
                }}
            """)

            self.status_button_group.addButton(btn, code)
            self.status_buttons[code] = btn
            buttons_layout.addWidget(btn)

        buttons_layout.addStretch()
        main_layout.addLayout(buttons_layout)

        # Stacked widget for response editors
        self.editor_stack = QStackedWidget()
        main_layout.addWidget(self.editor_stack, 1)

        # Create default editors immediately (before any interaction is loaded)
        self._create_default_editors()

    def _create_default_editors(self) -> None:
        """Create default empty editors for each status code."""
        for code in DEFAULT_STATUS_CODES:
            response = Response(status_code=code)
            self._add_response_editor(code, response)

        # Select 200 by default
        self.status_buttons[DEFAULT_STATUS_CODES[0]].setChecked(True)
        self.editor_stack.setCurrentWidget(
            self.response_editors[DEFAULT_STATUS_CODES[0]]
        )

    def _connect_signals(self) -> None:
        """Connect signals to slots."""
        self.status_button_group.idClicked.connect(self._on_status_selected)

    def load_interaction(self, interaction: Interaction) -> None:
        """Load interaction responses into editors."""
        self.current_interaction = interaction
        self.response_editors = {}

        # Clear the stack
        while self.editor_stack.count() > 0:
            widget = self.editor_stack.widget(0)
            self.editor_stack.removeWidget(widget)
            if widget is not None:
                widget.deleteLater()

        # Create editors for each status code (200, 400, 500)
        for code in DEFAULT_STATUS_CODES:
            response = interaction.responses.get(code) or Response(status_code=code)
            interaction.responses.setdefault(code, response)
            self._add_response_editor(code, response)

        # Select 200 by default
        self.status_buttons[DEFAULT_STATUS_CODES[0]].setChecked(True)
        self._on_status_selected(DEFAULT_STATUS_CODES[0])
        self.setEnabled(True)

    def _add_response_editor(self, status_code: int, response: Response) -> None:
        """Add a response editor for a status code."""
        editor = ResponseEditor()
        editor.load_response(response)
        editor.headers_table.headers_changed.connect(self._on_response_changed)
        editor.body_editor.textChanged.connect(self._on_response_changed)

        self.editor_stack.addWidget(editor)
        self.response_editors[status_code] = editor

    def _on_status_selected(self, status_code: int) -> None:
        """Handle status code button selection."""
        if status_code in self.response_editors:
            editor = self.response_editors[status_code]
            self.editor_stack.setCurrentWidget(editor)

    def _on_response_changed(self) -> None:
        """Save changes when any response field is modified."""
        if self.current_interaction:
            # Save all responses from editors
            for status_code, editor in self.response_editors.items():
                response = self.current_interaction.responses[status_code]
                editor.save_response(response)

            self.interaction_updated.emit(self.current_interaction)

    def clear(self) -> None:
        """Clear the panel when no interaction is selected."""
        self.current_interaction = None
        # Keep existing editors but reset their content
        for status_code, editor in self.response_editors.items():
            empty = Response(status_code=status_code)
            editor.load_response(empty)
        self.setEnabled(False)
