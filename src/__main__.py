import logging
import sys

import PyQt6.QtWidgets as QtW
from PyQt6.QtGui import QFontDatabase
from PyQt6.QtCore import Qt

from window import SteamyMainWindow

if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    # holds all events that happen while interfacing with qt program
    app = QtW.QApplication(sys.argv)
    QFontDatabase.addApplicationFont("resources/MonaSans-Regular.ttf")
    QFontDatabase.addApplicationFont("resources/Consolas-Regular.ttf")
    with open("resources/steamystyle.qss", "r") as f:
        style = f.read()
        app.setStyleSheet(style)
    window = SteamyMainWindow()
    window.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    window.show()
    app.exec()
