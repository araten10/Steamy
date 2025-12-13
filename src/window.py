import PyQt6.QtWidgets as QtW
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QCursor

from game_db import LibraryDumperThread, get_game_db
from pornify import PornifyThread, resteam
from steam import Steam


class SteamyMainWindow(QtW.QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.steam = Steam()
        self.game_db = get_game_db()

        self.setWindowTitle("Steamy")
        self.setFixedSize(QSize(400, 300))

        root_layout = QtW.QVBoxLayout()

        # === LOGO ===
        logo_layout = QtW.QHBoxLayout()
        root_layout.addLayout(logo_layout)

        self.logo_ascii = QtW.QPlainTextEdit()
        self.logo_ascii.setObjectName("AsciiLogo")
        self.logo_ascii.setReadOnly(True)
        self.logo_ascii.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        self.logo_ascii.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.logo_ascii.setFixedHeight(96)
        self.logo_ascii.setFixedWidth(375)
        self.logo_ascii.viewport().setCursor(Qt.CursorShape.ArrowCursor)
        self.logo_ascii.setPlainText(r"""      :::::::: ::::::::::: ::::::::::     :::       :::   :::  :::   :::
    :+:    :+:    :+:     :+:          :+: :+:    :+:+: :+:+: :+:   :+:
   +:+           +:+     +:+         +:+   +:+  +:+ +:+:+ +:+ +:+ +:+
  +#++:++#++    +#+     +#++:++#   +#++:++#++: +#+  +:+  +#+  +#++:
        +#+    +#+     +#+        +#+     +#+ +#+       +#+   +#+
#+#    #+#    #+#     #+#        #+#     #+# #+#       #+#   #+#
########     ###     ########## ###     ### ###       ###   ###             """)
        logo_layout.addWidget(self.logo_ascii)

        # === USER SELECTION ===

        dropdown_layout = QtW.QHBoxLayout()
        root_layout.addLayout(dropdown_layout)

        select_label = QtW.QLabel("Select Steam Account")
        dropdown_layout.addWidget(select_label)

        self.user_dropdown = QtW.QComboBox()
        self.user_dropdown.addItems(self.steam.usernames)
        dropdown_layout.addWidget(self.user_dropdown)

        # === BUTTONS ===

        button_layout = QtW.QHBoxLayout()
        root_layout.addLayout(button_layout)

        self.pornify_button = QtW.QPushButton("PORNIFY")
        self.pornify_button.setObjectName("Pornify")
        self.pornify_button.clicked.connect(self.on_pornify_click)
        button_layout.addWidget(self.pornify_button)

        self.resteam_button = QtW.QPushButton("RESTEAM")
        self.resteam_button.setObjectName("Resteam")
        self.resteam_button.clicked.connect(lambda: resteam(self.steam, self.user_dropdown.currentText()))
        button_layout.addWidget(self.resteam_button)

        # === PROGRESS BAR ===

        progress_layout = QtW.QHBoxLayout()
        root_layout.addLayout(progress_layout)

        self.pornify_progress = QtW.QProgressBar()
        self.pornify_progress.setGeometry(50, 100, 250, 30)
        self.pornify_progress.setRange(0, len(self.steam.game_ids))
        progress_layout.addWidget(self.pornify_progress)

        self.dump_button = QtW.QPushButton("Dump Game Library")
        self.dump_button.clicked.connect(self.on_dump_click)
        root_layout.addWidget(self.dump_button)

        # wrap all of that in a container widget, apply the root layout, then set it
        root = QtW.QWidget()
        root.setLayout(root_layout)
        self.setCentralWidget(root)

    def set_buttons_enabled(self, enabled: bool) -> None:
        self.pornify_button.setEnabled(enabled)
        self.resteam_button.setEnabled(enabled)
        self.dump_button.setEnabled(enabled)

    def update_pornify_progress(self) -> None:
        self.pornify_progress.setValue(self.pornify_progress.value() + 1)

    def on_pornify_click(self) -> None:
        self.set_buttons_enabled(False)
        self.pornify_progress.setValue(0)

        self.pornify_thread = PornifyThread(self.steam, self.game_db, self.user_dropdown.currentText())
        self.pornify_thread.done.connect(lambda: self.set_buttons_enabled(True))
        self.pornify_thread.progress.connect(self.update_pornify_progress)
        self.pornify_thread.start()

    def on_dump_click(self) -> None:
        self.set_buttons_enabled(False)

        self.dump_thread = LibraryDumperThread(self.steam, self.game_db)
        self.dump_thread.done.connect(lambda: self.set_buttons_enabled(True))
        self.dump_thread.start()
