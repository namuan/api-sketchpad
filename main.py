"""Main entry point for API SketchPad application."""

import sys

from PyQt6.QtWidgets import QApplication

from api_sketchpad.ui.main_window import MainWindow


def main() -> None:
    """Create and run the application."""
    app = QApplication(sys.argv)

    # Set application metadata
    app.setApplicationName("API SketchPad")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("API Tools")

    # Create and show main window
    window = MainWindow()
    window.show()

    # Start event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
