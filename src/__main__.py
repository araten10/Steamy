import ctypes
import logging
import platform
import sys

import PyQt6.QtWidgets as QtW
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFontDatabase, QIcon

from gui.window import SteamyMainWindow

if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    # holds all events that happen while interfacing with qt program
    app = QtW.QApplication(sys.argv)

    if platform.system() == "Windows":
        # workaround for windows taskbar icons
        myappid = "mycompany.myproduct.subproduct.version"
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    app.setWindowIcon(QIcon("resources/steamylogo.ico"))
    QFontDatabase.addApplicationFont("resources/MonaSans-Regular.ttf")
    QFontDatabase.addApplicationFont("resources/Consolas-Regular.ttf")
    with open("resources/steamystyle.qss", "r") as f:
        style = f.read()
        app.setStyleSheet(style)
    window = SteamyMainWindow()
    window.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    window.show()
    app.exec()
