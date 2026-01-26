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

import webbrowser
import logging
import requests

import PyQt6.QtWidgets as QtW
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QMouseEvent


class SteamyTitleBar(QtW.QWidget):
    def __init__(self, parent: QtW.QWidget) -> None:
        super().__init__(parent)

        title_bar_layout = QtW.QHBoxLayout(self)
        title_bar_layout.setContentsMargins(0, 0, 0, 0)
        title_bar_layout.setSpacing(0)

        version_url = "https://api.github.com/repos/araten10/Steamy/releases/latest"
        result = requests.get(version_url).json()
        version_number = "1.1"
        release_number = result["tag_name"].replace("v", "")
        print(release_number)
        merged_number = self.numberMerge(version_number)
        latest_release = self.numberMerge(release_number)

        title = QtW.QLabel("Steamy", self)
        title.setFixedWidth(60)
        if latest_release == merged_number:
            title.setObjectName("Title")
            title.setToolTip(f"v{version_number}\nSteamy is up to date.")
        elif latest_release > (int(merged_number) + 9):
            title.setObjectName("TitleMajorRel")
            title.setToolTip(
                f"v{version_number}\nSteamy has a new update! Click here to go to the download page.\nThis is a major release that most likely has brand new features or overhauls!"
            )
            title.mousePressEvent = lambda _: webbrowser.open("https://github.com/araten10/Steamy/releases")
        elif latest_release > merged_number:
            title.setObjectName("TitleMinorRel")
            title.setToolTip(
                f"v{version_number}\nSteamy has a new update! Click here to go to the download page.\nThis is a minor release that usually fixes bugs or adds to the game database."
            )
            title.mousePressEvent = lambda _: webbrowser.open("https://github.com/araten10/Steamy/releases")
        else:
            title.setObjectName("Title")
            logging.warning("Steamy version mismatch. Version number might somehow be more recent than the latest release.")
        title.setContentsMargins(5, 5, 0, 0)

        title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        title_bar_layout.addWidget(title)

        title_padding = QtW.QLabel()
        title_bar_layout.addWidget(title_padding)

        # Min button
        min_button = QtW.QToolButton(self)
        min_icon = self.style().standardIcon(QtW.QStyle.StandardPixmap.SP_TitleBarMinButton)
        min_button.setIcon(min_icon)
        min_button.clicked.connect(self.window().showMinimized)

        # Close button
        close_button = QtW.QToolButton(self)
        close_button.setObjectName("Close")
        close_icon = self.style().standardIcon(QtW.QStyle.StandardPixmap.SP_TitleBarCloseButton)
        close_button.setIcon(close_icon)
        close_button.clicked.connect(self.window().close)

        for button in [min_button, close_button]:
            button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            button.setFixedSize(QSize(30, 30))
            title_bar_layout.addWidget(button)

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self.window().windowHandle().startSystemMove()
        super().mousePressEvent(event)
        event.accept()

    def numberMerge(self, str_number: str) -> int:
        version_number = str_number
        version_number = version_number.split(".")
        version_number = int("".join(version_number))
        return version_number
