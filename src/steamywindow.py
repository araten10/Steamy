import sys

from PyQt6.QtCore import QSize, Qt
import PyQt6.QtWidgets as qtw

class SteamyMainWindow(qtw.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Steamy")
        self.setFixedSize(QSize(400, 300))
