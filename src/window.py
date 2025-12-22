import PyQt6.QtWidgets as QtW
from PyQt6.QtCore import QSize, Qt

from config import Config
from games import LibraryDumperThread, get_game_db
from pornify import PornifyThread, resteam
from steam import Steam
from title import SteamyTitleBar

LOGO = r"""      :::::::: ::::::::::: ::::::::::     :::       :::   :::  :::   :::
    :+:    :+:    :+:     :+:          :+: :+:    :+:+: :+:+: :+:   :+:
   +:+           +:+     +:+         +:+   +:+  +:+ +:+:+ +:+ +:+ +:+
  +#++:++#++    +#+     +#++:++#   +#++:++#++: +#+  +:+  +#+  +#++:
        +#+    +#+     +#+        +#+     +#+ +#+       +#+   +#+
#+#    #+#    #+#     #+#        #+#     #+# #+#       #+#   #+#
########     ###     ########## ###     ### ###       ###   ###             """


class SteamyMainWindow(QtW.QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.config = Config()
        self.steam = Steam()
        self.game_db = get_game_db()

        self.setWindowTitle("Steamy")
        # Total Height = 300 for top_layout, 300 for bottom layout, add title bar
        self.setFixedSize(QSize(400, 630))
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        title_bar = SteamyTitleBar(self)
        title_bar.setFixedSize(400, 30)

        # Contains the logo, dropdown, and buttons
        top_container = QtW.QWidget()
        top_container.setFixedSize(QSize(400, 300))
        # top_container.setStyleSheet("background: red")
        top_layout = QtW.QVBoxLayout(top_container)
        # Contains the settings notebook and anything inside of it
        bottom_container = QtW.QWidget()
        bottom_container.setFixedSize(QSize(400, 300))
        bottom_container.setStyleSheet("border-bottom-left-radius: 5px; border-bottom-right-radius: 5px")
        bottom_layout = QtW.QVBoxLayout(bottom_container)

        # === LOGO ===
        logo_layout = QtW.QHBoxLayout()
        top_layout.addLayout(logo_layout)

        logo_ascii = QtW.QPlainTextEdit()
        logo_ascii.setObjectName("AsciiLogo")
        logo_ascii.setReadOnly(True)
        logo_ascii.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        logo_ascii.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        # TODO: Set height and width to be dynamic so it is easier to center, might not change anything
        logo_ascii.setFixedHeight(96)
        logo_ascii.setFixedWidth(375)
        logo_ascii.viewport().setCursor(Qt.CursorShape.ArrowCursor)
        logo_ascii.setPlainText(LOGO)
        logo_layout.addWidget(logo_ascii)

        # === USER SELECTION ===

        dropdown_layout = QtW.QHBoxLayout()
        top_layout.addLayout(dropdown_layout)

        select_label = QtW.QLabel("Select Steam Account")
        dropdown_layout.addWidget(select_label)

        self.user_dropdown = QtW.QComboBox()
        self.user_dropdown.addItems(self.steam.usernames)
        dropdown_layout.addWidget(self.user_dropdown)

        # === BUTTONS ===

        button_layout = QtW.QHBoxLayout()
        top_layout.addLayout(button_layout)

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
        top_layout.addLayout(progress_layout)

        self.pornify_progress = QtW.QProgressBar()
        self.pornify_progress.setGeometry(50, 100, 250, 30)
        self.pornify_progress.setRange(0, len(self.steam.game_ids))
        progress_layout.addWidget(self.pornify_progress)

        # === TAB WIDGET ===

        tab_master = QtW.QTabWidget()
        tab_booru = QtW.QWidget()
        tab_steamy = QtW.QWidget()
        tab_dev = QtW.QWidget()
        tab_booru.setObjectName("Tab")
        tab_steamy.setObjectName("Tab")
        tab_dev.setObjectName("Tab")
        tab_master.setFixedHeight(285)

        tab_master.addTab(tab_booru, "Booru")
        tab_master.addTab(tab_steamy, "Steamy")
        tab_master.addTab(tab_dev, "Tools")

        # === BOORU TAB ===
        tab_booru.layout = QtW.QVBoxLayout()

        self.booru_dropdown = QtW.QComboBox()
        self.booru_dropdown.addItems(self.config.supported_boorus)
        booru_dropdown_layout = QtW.QVBoxLayout()
        booru_dropdown_layout.addWidget(self.booru_dropdown)
        self.booru_dropdown_gb = QtW.QGroupBox("Default Booru")
        self.booru_dropdown_gb.setLayout(booru_dropdown_layout)
        tab_booru.layout.addWidget(self.booru_dropdown_gb)

        self.api_container = QtW.QWidget()
        # Have to manually set the background colour on these ones for stylistic purposes
        self.api_container.setStyleSheet("background-color: #292e37;")
        api_layout = QtW.QHBoxLayout(self.api_container)
        api_layout.setContentsMargins(0, 0, 0, 0)

        # Rule34 API
        self.api_r34 = QtW.QGroupBox("rule34")
        self.api_r34.setStyleSheet("background-color: #171d25;")
        r34_layout = QtW.QVBoxLayout(self.api_r34)

        r34_key_layout = QtW.QHBoxLayout()
        r34_key_layout.addWidget(QtW.QLabel(parent=self, text="API Key:"))
        self.r34_api_key_edit = QtW.QLineEdit(self.config.r34_api_key)
        r34_key_layout.addWidget(self.r34_api_key_edit)
        r34_layout.addLayout(r34_key_layout)

        r34_id_layout = QtW.QHBoxLayout()
        r34_id_layout.addWidget(QtW.QLabel(parent=self, text="User ID:"))
        self.r34_user_id_edit = QtW.QLineEdit(str(self.config.r34_user_id or ""))
        r34_id_layout.addWidget(self.r34_user_id_edit)
        r34_layout.addLayout(r34_id_layout)

        self.api_r34.setLayout(r34_layout)

        # E621 API
        self.api_e621 = QtW.QGroupBox("e621")
        self.api_e621.setStyleSheet("background-color: #171d25;")
        e621_layout = QtW.QVBoxLayout(self.api_e621)

        e621_key_layout = QtW.QHBoxLayout()
        e621_key_layout.addWidget(QtW.QLabel(parent=self, text="API Key:"))
        self.e621_api_key_edit = QtW.QLineEdit(self.config.e621_api_key)
        e621_key_layout.addWidget(self.e621_api_key_edit)
        e621_layout.addLayout(e621_key_layout)

        e621_id_layout = QtW.QHBoxLayout()
        e621_id_layout.addWidget(QtW.QLabel(parent=self, text="User ID:"))
        self.e621_user_id_edit = QtW.QLineEdit(str(self.config.e621_user_id or ""))
        e621_id_layout.addWidget(self.e621_user_id_edit)
        e621_layout.addLayout(e621_id_layout)

        self.api_e621.setLayout(e621_layout)

        api_layout.addWidget(self.api_r34)
        api_layout.addWidget(self.api_e621)
        tab_booru.layout.addWidget(self.api_container)

        # Save
        booru_save_button = QtW.QPushButton("Save")
        booru_save_button.clicked.connect(self.on_save_click)
        tab_booru.layout.addWidget(booru_save_button)

        tab_booru.setLayout(tab_booru.layout)

        # === STEAMY TAB ===
        tab_steamy.layout = QtW.QVBoxLayout()

        api_save_button = QtW.QPushButton("Save")
        api_save_button.clicked.connect(self.on_save_click)
        tab_steamy.layout.addWidget(api_save_button)

        tab_steamy.setLayout(tab_steamy.layout)

        # === DEV TAB ===
        tab_dev.layout = QtW.QVBoxLayout()

        self.dump_button = QtW.QPushButton("Dump Game Library")
        self.dump_button.clicked.connect(self.on_dump_click)
        tab_dev.layout.addWidget(self.dump_button)

        tab_dev.setLayout(tab_dev.layout)

        # === TAB WIDGET END ===

        bottom_layout.addWidget(tab_master)

        # wrap all of that in a container widget, apply the root layout, then set it
        root = QtW.QWidget()
        root.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        root_layout = QtW.QVBoxLayout()
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        root_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        root_layout.addWidget(title_bar)
        root_layout.addWidget(top_container)
        root_layout.addWidget(bottom_container)
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

        self.pornify_thread = PornifyThread(self.config, self.steam, self.game_db, self.user_dropdown.currentText())
        self.pornify_thread.done.connect(lambda: self.set_buttons_enabled(True))
        self.pornify_thread.progress.connect(self.update_pornify_progress)
        self.pornify_thread.start()

    def on_save_click(self) -> None:
        user_id = self.r34_user_id_edit.text()
        self.config.raw = {
            "default_booru": self.booru_dropdown.currentText(),
            "rule34": {
                "api_key": self.r34_api_key_edit.text() or None,
                "user_id": int(user_id) if user_id else None,
            },
        }
        self.config.save()

    def on_dump_click(self) -> None:
        self.set_buttons_enabled(False)

        self.dump_thread = LibraryDumperThread(self.steam, self.game_db)
        self.dump_thread.done.connect(lambda: self.set_buttons_enabled(True))
        self.dump_thread.start()
