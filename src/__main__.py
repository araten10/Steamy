import logging
import sys

import PyQt6.QtWidgets as QtW
from PyQt6.QtGui import QFont, QFontDatabase

from window import SteamyMainWindow

if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    # holds all events that happen while interfacing with qt program
    app = QtW.QApplication(sys.argv)
    QFontDatabase.addApplicationFont('resources/MonaSans-Medium.ttf')
    with open("src/steamystyle.qss", "r") as f:
        style = f.read()
        app.setStyleSheet(style)
    window = SteamyMainWindow()

    window.show()
    app.exec()
