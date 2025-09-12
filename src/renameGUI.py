"""This module provides the RP Renamer application."""

import sys

from PySide6.QtWidgets import QApplication

from views import Window


### TODO List:
# Get origins for files: I think it will be a series of rules that have to be followed one by one in an if-else
# Once I have all the origins locked, I can rename. I think this must run after a JSON load
# Get Renameable files
# See if any file can't be renamed -> all have date, all have source
#     Sort by source
#     Sort by date
# Get proposed new name -> store in the mediaFile?
# Display -> tree view????
# Once happy, trigger rename process


def main():
    # Create the application
    app = QApplication(sys.argv)
    # Create and show the main window
    win = Window()
    win.show()
    # Run the event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
