import PyQt6.QtWidgets as QtW
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QMouseEvent

from config import Config
from games import LibraryDumperThread, get_game_db
from pornify import PornifyThread, resteam
from steam import Steam

LOGO = r"""      :::::::: ::::::::::: ::::::::::     :::       :::   :::  :::   :::
    :+:    :+:    :+:     :+:          :+: :+:    :+:+: :+:+: :+:   :+:
   +:+           +:+     +:+         +:+   +:+  +:+ +:+:+ +:+ +:+ +:+
  +#++:++#++    +#+     +#++:++#   +#++:++#++: +#+  +:+  +#+  +#++:
        +#+    +#+     +#+        +#+     +#+ +#+       +#+   +#+
#+#    #+#    #+#     #+#        #+#     #+# #+#       #+#   #+#
########     ###     ########## ###     ### ###       ###   ###             """


class SteamyTitleBar(QtW.QWidget):
    def __init__(self, parent: QtW.QWidget) -> None:
        super().__init__(parent)
        self.initial_pos = None
        title_bar_layout = QtW.QHBoxLayout(self)
        title_bar_layout.setContentsMargins(0, 0, 0, 0)
        title_bar_layout.setSpacing(0)

        self.title = QtW.QLabel("Steamy", self)
        self.title.setObjectName("Title")
        self.title.setContentsMargins(5, 5, 0, 0)

        self.title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        title_bar_layout.addWidget(self.title)
        # Min button
        self.min_button = QtW.QToolButton(self)
        min_icon = self.style().standardIcon(QtW.QStyle.StandardPixmap.SP_TitleBarMinButton)
        self.min_button.setIcon(min_icon)
        self.min_button.clicked.connect(self.window().showMinimized)

        # Close button
        self.close_button = QtW.QToolButton(self)
        self.close_button.setObjectName("Close")
        close_icon = self.style().standardIcon(QtW.QStyle.StandardPixmap.SP_TitleBarCloseButton)
        self.close_button.setIcon(close_icon)
        self.close_button.clicked.connect(self.window().close)

        buttons = [self.min_button, self.close_button]
        for button in buttons:
            button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            button.setFixedSize(QSize(30, 30))
            title_bar_layout.addWidget(button)

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self.window().windowHandle().startSystemMove()
        super().mousePressEvent(event)
        event.accept()


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
        tab_dev = QtW.QWidget()
        tab_master.setFixedHeight(250)

        tab_master.addTab(tab_booru, "Booru")
        tab_master.addTab(tab_dev, "Tools")

        # === BOORU TAB ===
        tab_booru.layout = QtW.QVBoxLayout()

        self.booru_dropdown = QtW.QComboBox()
        self.booru_dropdown.addItems(self.config.supported_boorus)
        tab_booru.layout.addWidget(self.booru_dropdown)

        self.r34_api_key_edit = QtW.QLineEdit(self.config.r34_api_key)
        tab_booru.layout.addWidget(self.r34_api_key_edit)

        self.r34_user_id_edit = QtW.QLineEdit(str(self.config.r34_user_id or ""))
        tab_booru.layout.addWidget(self.r34_user_id_edit)

        save_button = QtW.QPushButton("Save")
        save_button.clicked.connect(self.on_save_click)
        tab_booru.layout.addWidget(save_button)

        tab_booru.setLayout(tab_booru.layout)

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
