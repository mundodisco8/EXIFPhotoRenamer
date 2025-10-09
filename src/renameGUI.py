"""An Application to rename my photos and videos!"""

import sys

from PySide6.QtWidgets import QApplication

from views import Window


def main():
    """Draws the main windown and runs the event loop"""
    # Create the application
    app = QApplication(sys.argv)
    # Create and show the main window
    win = Window()
    win.show()
    # Run the event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
