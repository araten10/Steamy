import logging
import sys

import PyQt6.QtWidgets as QtW

from window import SteamyMainWindow

if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    # holds all events that happen while interfacing with qt program
    app = QtW.QApplication(sys.argv)
    window = SteamyMainWindow()

    window.show()
    app.exec()
