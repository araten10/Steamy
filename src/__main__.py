import ctypes
import logging
import platform
import sys

import PyQt6.QtWidgets as QtW
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFontDatabase, QIcon

import resources
from gui.window import SteamyMainWindow

if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    # holds all events that happen while interfacing with qt program
    app = QtW.QApplication(sys.argv)

    if platform.system() == "Windows":
        # workaround for windows taskbar icons
        myappid = "mycompany.myproduct.subproduct.version"
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    app.setWindowIcon(QIcon(str(resources.ICON)))

    for font in resources.FONTS:
        QFontDatabase.addApplicationFont(str(font))

    full_style = ""
    for style in resources.STYLES:
        with open(style, "r") as f:
            full_style += f.read()
    app.setStyleSheet(full_style)

    window = SteamyMainWindow()
    window.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    window.show()
    app.exec()
