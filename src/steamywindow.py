import sys
import asyncio

from PyQt6.QtCore import QSize, Qt
import PyQt6.QtWidgets as qtw

from pornify import pornify, resteam
from steam import Steam

class SteamyMainWindow(qtw.QMainWindow):
    def __init__(self):
        super().__init__()

        steam = Steam()

        self.setWindowTitle("Steamy")
        self.setFixedSize(QSize(400, 300))

        # Layouts are similar to frames in tkinter... i think. QV is vert packing QH is hori packing
        root_layout = qtw.QVBoxLayout()
        button_layout = qtw.QHBoxLayout()
        root_layout.addLayout(button_layout)

        pornify_button = qtw.QPushButton("PORNIFY")
        pornify_button.setCheckable(True)
        pornify_button.clicked.connect(lambda: asyncio.run(pornify(steam, user_var.get(), pornify_progress_var)))
        button_layout.addWidget(pornify_button)

        resteam_button = qtw.QPushButton("RESTEAM")
        resteam_button.setCheckable(True)
        resteam_button.clicked.connect(lambda: resteam(steam, user_var.get()))
        button_layout.addWidget(resteam_button)

        # wrap all of that in a container widget, apply the root layout, then set it
        root = qtw.QWidget()
        root.setLayout(root_layout)
        self.setCentralWidget(root)

        #pornify_button = ttk.Button(start_stop_frame,text="PORNIFY",
            #command=lambda: Thread(target=lambda: asyncio.run(pornify(steam, user_var.get(), pornify_progress_var))).start(),
            #bootstyle="success",
        #)
        #resteam_button = ttk.Button(start_stop_frame, text="RESTEAM", command=lambda: resteam(steam, user_var.get()))
