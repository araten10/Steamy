import PyQt6.QtWidgets as QtW
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QPalette, QColor

from game_db import LibraryDumperThread, get_game_db
from pornify import PornifyThread, resteam
from steam import Steam

class SteamyTitleBar(QtW.QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setAutoFillBackground(True)
        self.setBackgroundRole(QPalette.ColorRole.Highlight)
        self.initial_pos = None
        title_bar_layout = QtW.QHBoxLayout(self)
        title_bar_layout.setContentsMargins(1, 1, 1, 1)
        title_bar_layout.setSpacing(2)

        self.title = QtW.QLabel("Steamy", self)

        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_bar_layout.addWidget(self.title)
        effect = QtW.QGraphicsColorizeEffect()
        effect.setColor(QColor("#ffffff"))
        effect.setStrength(1)
         # Min button
        self.min_button = QtW.QToolButton(self)
        min_icon = self.style().standardIcon(
            QtW.QStyle.StandardPixmap.SP_TitleBarMinButton
        )
        self.min_button.setIcon(min_icon)
        self.min_button.setGraphicsEffect(effect)
        self.min_button.clicked.connect(self.window().showMinimized)

        # Close button
        self.close_button = QtW.QToolButton(self)
        close_icon = self.style().standardIcon(
            QtW.QStyle.StandardPixmap.SP_TitleBarCloseButton
        )
        self.close_button.setIcon(close_icon)
        self.close_button.clicked.connect(self.window().close)

        buttons = [
            self.min_button,
            self.close_button,
        ]
        for button in buttons:
            button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            button.setFixedSize(QSize(28, 28))
            title_bar_layout.addWidget(button)

class SteamyMainWindow(QtW.QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.steam = Steam()
        self.game_db = get_game_db()

        self.setWindowTitle("Steamy")
        # Total Height = 300 for top_layout, 300 for bottom layout, add title bar
        self.setFixedSize(QSize(400, 630))
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        # Titlebar
        self.title_bar = SteamyTitleBar(self)
        self.title_bar.setFixedHeight(30)

        # Contains the logo, dropdown, and buttons
        top_layout = QtW.QVBoxLayout()
        # Contains the settings notebook and anything inside of it
        bottom_layout = QtW.QVBoxLayout()

        # === LOGO ===
        logo_layout = QtW.QHBoxLayout()
        top_layout.addLayout(logo_layout)

        self.logo_ascii = QtW.QPlainTextEdit()
        self.logo_ascii.setObjectName("AsciiLogo")
        self.logo_ascii.setReadOnly(True)
        self.logo_ascii.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        self.logo_ascii.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        # TODO: Set height and width to be dynamic so it is easier to center, might not change anything
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

        self.tab_master = QtW.QTabWidget()
        self.tab_booru = QtW.QWidget()
        self.tab_dev = QtW.QWidget()
        self.tab_master.setFixedHeight(300)

        self.tab_master.addTab(self.tab_booru, "Booru")
        self.tab_master.addTab(self.tab_dev, "Tools")

        # === BOORU TAB ===
        self.tab_booru.layout = QtW.QVBoxLayout()

        self.tab_booru.setLayout(self.tab_booru.layout)

        # === DEV TAB ===
        self.tab_dev.layout = QtW.QVBoxLayout()

        self.dump_button = QtW.QPushButton("Dump Game Library")
        self.dump_button.clicked.connect(self.on_dump_click)
        self.tab_dev.layout.addWidget(self.dump_button)

        self.tab_dev.setLayout(self.tab_dev.layout)

        # === TAB WIDGET END ===

        bottom_layout.addWidget(self.tab_master)

        # wrap all of that in a container widget, apply the root layout, then set it
        root = QtW.QWidget()
        root_layout = QtW.QVBoxLayout()
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        root_layout.addWidget(self.title_bar)
        root_layout.addLayout(top_layout)
        root_layout.addLayout(bottom_layout)
        root.setLayout(root_layout)
        self.setCentralWidget(root)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.initial_pos = event.position().toPoint()
        super().mousePressEvent(event)
        event.accept()

    def mouseMoveEvent(self, event):
        if self.initial_pos is not None:
            delta = event.position().toPoint() - self.initial_pos
            self.window().move(
                self.window().x() + delta.x(),
                self.window().y() + delta.y(),
            )
        super().mouseMoveEvent(event)
        event.accept()

    def mouseReleaseEvent(self, event):
        self.initial_pos = None
        super().mouseReleaseEvent(event)
        event.accept()

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
