# Copyright (C) 2026 Araten & Marigold
#
# This file is part of Steamy.
#
# Steamy is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Steamy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Steamy.  If not, see <https://www.gnu.org/licenses/>.

import os
import platform
from pathlib import Path

import PyQt6.QtWidgets as QtW
from PyQt6.QtCore import QSize, Qt

from config import Config
from games import LibraryDumperThread, get_game_db, search_games
from gui.title import SteamyTitleBar
from pornify import PornifyThread, resteam
from steam import Steam
from utils import info_message

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
        self.setFixedSize(QSize(400, 630))  # Total Height = 300 for top_layout, 300 for bottom layout, add title bar
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        title_bar = SteamyTitleBar(self)
        title_bar.setFixedSize(400, 30)

        # Contains the logo, dropdown, and buttons
        top_container = QtW.QWidget()
        top_container.setFixedSize(QSize(400, 300))
        top_layout = QtW.QVBoxLayout(top_container)

        # Contains the settings notebook and anything inside of it
        bottom_container = QtW.QWidget()
        bottom_container.setFixedSize(QSize(400, 300))
        bottom_container.setObjectName("Bottom")
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

        # "top_middle_layout" is to keep the buttons and progressbar tight together

        top_middle_layout = QtW.QVBoxLayout()
        top_layout.addLayout(top_middle_layout)

        button_layout = QtW.QHBoxLayout()
        top_middle_layout.addLayout(button_layout)

        self.pornify_button = QtW.QPushButton("PORNIFY")
        self.pornify_button.setObjectName("Pornify")
        self.pornify_button.clicked.connect(self.on_pornify_click)
        button_layout.addWidget(self.pornify_button)

        self.resteam_button = QtW.QPushButton("RESTEAM")
        self.resteam_button.setObjectName("Resteam")
        self.resteam_button.clicked.connect(self.on_resteam_click)
        button_layout.addWidget(self.resteam_button)

        # === PROGRESS BAR ===

        progress_layout = QtW.QHBoxLayout()
        top_middle_layout.addLayout(progress_layout)

        self.progress = QtW.QProgressBar()
        self.progress.setRange(0, len(self.steam.game_ids))
        progress_layout.addWidget(self.progress)

        # === TAB WIDGET ===

        tab_master = QtW.QTabWidget()
        tab_booru = QtW.QWidget()
        tab_dev = QtW.QWidget()
        tab_booru.setObjectName("Tab")
        tab_dev.setObjectName("Tab")
        tab_master.setFixedHeight(285)

        tab_master.addTab(tab_booru, "Booru")
        tab_master.addTab(tab_dev, "Tools")

        # === BOORU TAB ===
        tab_booru.layout = QtW.QVBoxLayout()

        self.booru_dropdown = QtW.QComboBox()
        self.booru_dropdown.addItems(self.config.supported_boorus)
        self.booru_dropdown.setCurrentText(self.config.default_booru)
        booru_dropdown_layout = QtW.QVBoxLayout()
        booru_dropdown_layout.addWidget(self.booru_dropdown)
        booru_dropdown_gb = QtW.QGroupBox("Default Booru")
        booru_dropdown_gb.setLayout(booru_dropdown_layout)
        tab_booru.layout.addWidget(booru_dropdown_gb)

        api_container = QtW.QWidget()
        api_layout = QtW.QHBoxLayout(api_container)
        api_layout.setContentsMargins(0, 0, 0, 0)

        # Rule34 API
        api_r34 = QtW.QGroupBox("rule34")
        r34_layout = QtW.QVBoxLayout(api_r34)

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

        api_r34.setLayout(r34_layout)

        # E621 API
        api_e621 = QtW.QGroupBox("e621")
        e621_layout = QtW.QVBoxLayout(api_e621)

        e621_key_layout = QtW.QHBoxLayout()
        e621_key_layout.addWidget(QtW.QLabel(parent=self, text="API Key:"))
        self.e621_api_key_edit = QtW.QLineEdit(self.config.e621_api_key)
        e621_key_layout.addWidget(self.e621_api_key_edit)
        e621_layout.addLayout(e621_key_layout)

        e621_username_layout = QtW.QHBoxLayout()
        e621_username_layout.addWidget(QtW.QLabel(parent=self, text="Username:"))
        self.e621_username_edit = QtW.QLineEdit(self.config.e621_username)
        e621_username_layout.addWidget(self.e621_username_edit)
        e621_layout.addLayout(e621_username_layout)

        api_e621.setLayout(e621_layout)

        api_layout.addWidget(api_r34)
        api_layout.addWidget(api_e621)
        tab_booru.layout.addWidget(api_container)

        # Save
        booru_save_button = QtW.QPushButton("Save")
        booru_save_button.clicked.connect(self.on_save_click)
        tab_booru.layout.addWidget(booru_save_button)

        tab_booru.setLayout(tab_booru.layout)

        # === DEV TAB ===
        tab_dev.layout = QtW.QVBoxLayout()

        self.dump_button = QtW.QPushButton("Dump Game Library")
        self.dump_button.clicked.connect(self.on_dump_click)
        tab_dev.layout.addWidget(self.dump_button)

        folder_button = QtW.QPushButton("Open Steam Config Folder")
        folder_button.clicked.connect(self.on_folder_click)
        tab_dev.layout.addWidget(folder_button)

        search_groupbox = QtW.QGroupBox("Steam Store Search")
        search_groupbox.setFixedHeight(100)
        search_layout = QtW.QVBoxLayout(search_groupbox)

        search_params_layout = QtW.QHBoxLayout()
        search_params_layout.addWidget(QtW.QLabel(parent=self, text="Search:"))
        self.search_query = QtW.QLineEdit()
        search_params_layout.addWidget(self.search_query)

        search_params_layout.addWidget(QtW.QLabel(parent=self, text="CC:"))
        self.country_code = QtW.QLineEdit("US")
        self.country_code.setText("US")
        self.country_code.setFixedWidth(35)
        search_params_layout.addWidget(self.country_code)
        search_layout.addLayout(search_params_layout)

        self.search_button = QtW.QPushButton("Search Steam")
        self.search_button.clicked.connect(lambda: search_games(self.search_query.text(), self.country_code.text()))
        search_layout.addWidget(self.search_button)

        search_groupbox.setLayout(search_layout)

        tab_dev.layout.addWidget(search_groupbox)

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

    def update_progress(self) -> None:
        self.progress.setValue(self.progress.value() + 1)

    def ask_restart(self, task: str) -> None:
        message = QtW.QMessageBox()
        message.setIcon(QtW.QMessageBox.Icon.NoIcon)
        message.setText(f"{task} Done")
        message.setInformativeText("Restart Steam to refresh your library images?")

        message.setStandardButtons(QtW.QMessageBox.StandardButton.Yes | QtW.QMessageBox.StandardButton.No)
        if message.exec() == QtW.QMessageBox.StandardButton.Yes:
            self.steam.restart()

    def on_pornify_click(self) -> None:
        self.set_buttons_enabled(False)
        self.progress.setValue(0)

        def on_done() -> None:
            self.set_buttons_enabled(True)
            self.ask_restart("Pornify")  # TODO: Should not ask if pornify was cancelled somehow

        self.pornify_thread = PornifyThread(self.config, self.steam, self.game_db, self.user_dropdown.currentText())
        self.pornify_thread.done.connect(on_done)
        self.pornify_thread.progress.connect(self.update_progress)
        self.pornify_thread.start()

    def on_resteam_click(self) -> None:
        resteam(self.steam, self.user_dropdown.currentText())
        self.ask_restart("Resteam")  # TODO: Should not ask if resteam was cancelled somehow

    def on_dump_click(self) -> None:
        self.set_buttons_enabled(False)
        self.progress.setValue(0)

        def on_done(dump_path: Path) -> None:
            self.set_buttons_enabled(True)
            info_message(QtW.QMessageBox.Icon.NoIcon, "Game Library Dump Done", f"Game library dumped to {dump_path}.")

        self.dump_thread = LibraryDumperThread(self.steam, self.game_db)
        self.dump_thread.done.connect(on_done)
        self.dump_thread.progress.connect(self.update_progress)
        self.dump_thread.start()

    def on_folder_click(self) -> None:
        match platform.system():
            case "Linux":
                os.system('xdg-open "%s"' % (self.steam.path / "userdata"))
            case "Windows":
                os.startfile(self.steam.path / "userdata")

    def on_save_click(self) -> None:
        def get_user_id(site: str, text: str) -> int | None:
            if text:
                if text.isdigit():
                    return int(text)
                else:
                    info_message(QtW.QMessageBox.Icon.Warning, "Invalid User ID", f"{site} user ID {text} is invalid, must be an integer.")

            return None

        self.config.raw = {
            "default_booru": self.booru_dropdown.currentText(),
            "concurrent_downloads": self.config.concurrent_downloads,
            "danbooru": {
                "base_query": self.config.dan_base_query,
                "fallback_query": self.config.dan_fallback_query,
            },
            "rule34": {
                "base_query": self.config.r34_base_query,
                "fallback_query": self.config.r34_fallback_query,
                "api_key": self.r34_api_key_edit.text() or None,
                "user_id": get_user_id("Rule34", self.r34_user_id_edit.text()),
            },
            "e621": {
                "base_query": self.config.e621_base_query,
                "fallback_query": self.config.e621_fallback_query,
                "api_key": self.e621_api_key_edit.text() or None,
                "username": self.e621_username_edit.text() or None,
            },
        }
        self.config.save()
