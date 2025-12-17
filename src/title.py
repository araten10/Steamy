import PyQt6.QtWidgets as QtW
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QMouseEvent


class SteamyTitleBar(QtW.QWidget):
    def __init__(self, parent: QtW.QWidget) -> None:
        super().__init__(parent)

        title_bar_layout = QtW.QHBoxLayout(self)
        title_bar_layout.setContentsMargins(0, 0, 0, 0)
        title_bar_layout.setSpacing(0)

        title = QtW.QLabel("Steamy", self)
        title.setObjectName("Title")
        title.setContentsMargins(5, 5, 0, 0)

        title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        title_bar_layout.addWidget(title)

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
