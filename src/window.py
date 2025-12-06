import PyQt6.QtWidgets as QtW
from PyQt6.QtCore import QSize

from pornify import PornifyThread, resteam
from steam import Steam


class SteamyMainWindow(QtW.QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.steam = Steam()

        self.setWindowTitle("Steamy")
        self.setFixedSize(QSize(400, 300))

        root_layout = QtW.QVBoxLayout()
        dropdown_layout = QtW.QHBoxLayout()
        button_layout = QtW.QHBoxLayout()
        root_layout.addLayout(dropdown_layout)
        root_layout.addLayout(button_layout)

        select_label = QtW.QLabel("Select Steam Account")
        dropdown_layout.addWidget(select_label)
        self.user_dropdown = QtW.QComboBox()
        self.user_dropdown.addItems(self.steam.usernames)
        dropdown_layout.addWidget(self.user_dropdown)

        self.pornify_button = QtW.QPushButton("PORNIFY")
        self.pornify_button.clicked.connect(self.on_pornify_click)
        button_layout.addWidget(self.pornify_button)

        self.resteam_button = QtW.QPushButton("RESTEAM")
        self.resteam_button.clicked.connect(lambda: resteam(self.steam, self.user_dropdown.currentText()))
        button_layout.addWidget(self.resteam_button)

        self.pornify_progress = QtW.QProgressBar()
        self.pornify_progress.setRange(0, len(self.steam.game_ids))
        root_layout.addWidget(self.pornify_progress)

        # wrap all of that in a container widget, apply the root layout, then set it
        root = QtW.QWidget()
        root.setLayout(root_layout)
        self.setCentralWidget(root)

    def update_pornify_progress(self) -> None:
        self.pornify_progress.setValue(self.pornify_progress.value() + 1)

    def on_pornify_click(self) -> None:
        self.pornify_button.setEnabled(False)
        self.resteam_button.setEnabled(False)
        self.pornify_progress.setValue(0)

        self.pornify_thread = PornifyThread(self.steam, self.user_dropdown.currentText())
        self.pornify_thread.done.connect(self.on_pornify_done)
        self.pornify_thread.progress.connect(self.update_pornify_progress)
        self.pornify_thread.start()

    def on_pornify_done(self) -> None:
        self.pornify_button.setEnabled(True)
        self.resteam_button.setEnabled(True)
