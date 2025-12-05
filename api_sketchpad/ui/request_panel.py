"""Request panel for configuring API interactions."""

from typing import override

from PyQt6.QtCore import QModelIndex, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPainter, QPen
from PyQt6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListView,
    QScrollArea,
    QStyle,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ..models.interaction import Interaction
from ..services.validation import ValidationService
from .syntax_highlighter import SyntaxFormat
from .widgets.headers_table import HeadersTableWidget
from .widgets.query_params import QueryParamsWidget
from .widgets.syntax_editor import SyntaxHighlightEditor


class _NoTickDelegate(QStyledItemDelegate):
    def __init__(self, padding: int = 8) -> None:
        super().__init__()
        self._padding = padding

    @override
    def paint(
        self, painter: QPainter | None, option: QStyleOptionViewItem, index: QModelIndex
    ) -> None:
        if painter is None:
            return
        bg = (
            QColor("#f2f2f2")
            if option.state & QStyle.StateFlag.State_MouseOver
            else (
                QColor("#e6e6e6")
                if option.state & QStyle.StateFlag.State_Selected
                else QColor("white")
            )
        )
        painter.fillRect(option.rect, bg)
        painter.setPen(QPen(QColor("black")))
        text = index.data()
        rect = option.rect.adjusted(self._padding, 0, 0, 0)
        painter.drawText(
            rect, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, text
        )


class RequestPanel(QFrame):
    """Middle panel for configuring API request parameters."""

    interaction_updated = pyqtSignal(Interaction)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.current_interaction = None
        self._updating = False
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        """Initialize UI components."""
        self.setStyleSheet("""
            RequestPanel {
                border: 1px solid #333;
                background-color: white;
            }
        """)

        # Main layout with scroll area
        frame_layout = QVBoxLayout(self)
        frame_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        vp = scroll.viewport()
        if vp is not None:
            vp.setStyleSheet("background-color: white;")

        content = QWidget()
        content.setStyleSheet("background-color: white;")
        main_layout = QVBoxLayout(content)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Name Input
        self.name_field = QLineEdit()
        self.name_field.setPlaceholderText("Enter API Interaction name")
        self.name_field.setMaxLength(255)
        self.name_field.setStyleSheet(
            "border: 1px solid #333; border-radius: 4px; padding: 5px;"
        )
        main_layout.addWidget(self.name_field)

        # Description Input
        self.description_field = QTextEdit()
        self.description_field.setPlaceholderText("Enter API Interaction description")
        self.description_field.setFixedHeight(100)
        self.description_field.setStyleSheet(
            "border: 1px solid #333; border-radius: 4px; padding: 5px;"
        )
        main_layout.addWidget(self.description_field)

        # HTTP method and endpoint
        endpoint_layout = QHBoxLayout()

        self.method_dropdown = QComboBox()
        self.method_dropdown.addItems([
            "GET",
            "POST",
            "PUT",
            "DELETE",
            "PATCH",
            "HEAD",
            "OPTIONS",
        ])
        self._configure_method_dropdown()

        self.path_field = QLineEdit()
        self.path_field.setPlaceholderText("/api/endpoint")
        self.path_field.setStyleSheet(
            "border: 1px solid #333; border-radius: 4px; padding: 5px;"
        )

        endpoint_layout.addWidget(self.method_dropdown)
        endpoint_layout.addWidget(self.path_field, 1)
        main_layout.addLayout(endpoint_layout)

        # Request headers (now uses styled HeadersTableWidget)
        self.headers_table = HeadersTableWidget()
        main_layout.addWidget(self.headers_table)

        # Query params section
        self.query_params_widget = QueryParamsWidget()
        main_layout.addWidget(self.query_params_widget)

        # Request body section
        body_label = QLabel("Request Body")
        body_label.setStyleSheet("font-size: 12px; color: #555;")
        main_layout.addWidget(body_label)

        self.body_editor = SyntaxHighlightEditor()
        self.body_editor.setStyleSheet(
            "border: 1px solid #333; border-radius: 4px; padding: 5px;"
        )
        main_layout.addWidget(self.body_editor, 1)  # Give it remaining vertical space

        scroll.setWidget(content)
        frame_layout.addWidget(scroll)

    def _configure_method_dropdown(self) -> None:
        self.method_dropdown.setStyleSheet(
            """
            QComboBox {
                border: 1px solid #333;
                border-radius: 4px;
                padding: 5px;
                background-color: white;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: black;
                outline: 0;
                selection-background-color: #e6e6e6;
                selection-color: black;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #f2f2f2;
                color: black;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #e6e6e6;
                color: black;
            }
            """
        )
        popup_view = QListView()
        popup_view.setAlternatingRowColors(False)
        popup_view.setStyleSheet("QListView { background-color: white; color: black; }")
        popup_view.setItemDelegate(_NoTickDelegate())
        self.method_dropdown.setView(popup_view)

    def _connect_signals(self) -> None:
        """Connect UI signals to slots."""
        self.name_field.textChanged.connect(self._on_field_changed)
        self.description_field.textChanged.connect(self._on_field_changed)
        self.method_dropdown.currentTextChanged.connect(self._on_field_changed)
        self.path_field.textChanged.connect(self._on_field_changed)
        self.headers_table.headers_changed.connect(self._on_field_changed)
        self.query_params_widget.params_changed.connect(self._on_field_changed)
        self.body_editor.textChanged.connect(self._on_field_changed)

    def load_interaction(self, interaction: Interaction) -> None:
        """Load an interaction into the panel."""
        self.current_interaction = interaction

        # Block signals while loading to prevent premature updates
        self._set_block_signals(block=True)

        self.name_field.setText(interaction.name)
        self.description_field.setPlainText(interaction.description)
        self.method_dropdown.setCurrentText(interaction.method)
        self.path_field.setText(interaction.path)
        self.headers_table.set_headers(interaction.request_headers)
        self.query_params_widget.set_params(interaction.query_params)
        self.body_editor.set_text(interaction.request_body)

        # Set editor format based on Content-Type header
        content_type = interaction.request_headers.get("Content-Type", "")
        if "xml" in content_type:
            self.body_editor.set_format(SyntaxFormat.XML)
        else:
            self.body_editor.set_format(SyntaxFormat.JSON)

        # Restore signals
        self._set_block_signals(block=False)

    def save_to_interaction(self) -> None:
        """Save current UI state to interaction."""
        if not self.current_interaction:
            return
        ci = self.current_interaction
        ci.name = self.name_field.text()
        ci.description = self.description_field.toPlainText()
        ci.method = self.method_dropdown.currentText()
        ci.path = self.path_field.text()
        ci.request_headers = self.headers_table.get_headers()
        ci.query_params = self.query_params_widget.get_params()
        ci.request_body = self.body_editor.get_text()

    def _on_field_changed(self) -> None:
        """Handle any field change and update interaction."""
        if self.current_interaction and not self._updating:
            self._updating = True
            self.save_to_interaction()

            # Validate path
            valid, error = ValidationService.validate_url_path(
                self.current_interaction.path
            )
            if not valid:
                self.path_field.setStyleSheet(
                    "border: 1px solid red; border-radius: 4px; padding: 5px;"
                )
                self.path_field.setToolTip(error)
            else:
                self.path_field.setStyleSheet(
                    "border: 1px solid #333; border-radius: 4px; padding: 5px;"
                )
                self.path_field.setToolTip("")

            self.interaction_updated.emit(self.current_interaction)
            self._updating = False

    def _set_block_signals(self, *, block: bool) -> None:
        self.name_field.blockSignals(block)
        self.description_field.blockSignals(block)
        self.method_dropdown.blockSignals(block)
        self.path_field.blockSignals(block)
