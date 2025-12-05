import asyncio
import logging
import sys
import tkinter as tk
from threading import Thread
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkextrafont import Font

from pornify import pornify, resteam
from steam import Steam

if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    steam = Steam()
    root = ttk.Tk()
    root.geometry("320x240")

    # Styles
    style = ttk.Style(theme="steamythemey")
    main_font = Font(file="resources/MonaSans-Medium.ttf", family="Mona Sans Medium")
    bold_font = Font(file="resources/MonaSans-Bold.ttf", family="Mona Sans Bold")
    style.configure(".", font=("Mona Sans Medium", 12))
    style.configure("TButton", font=("Mona Sans Bold", 16))
    root.option_add("*TCombobox*Listbox.font", ("Mona Sans Medium", 12))
    root.option_add("*TCombobox.font", ("Mona Sans Medium", 12))
    root.option_add("*TEntry.font", ("Mona Sans Medium", 12))
    root.option_add("*TSpinbox.font", ("Mona Sans Medium", 12))

    run_frame = tk.Frame(root)
    run_frame.pack(expand=1)

    user_select_frame = tk.Frame(run_frame)
    user_select_frame.pack(fill="x")

    # For making sure that the "Select Steam Account" folder isn't accidentally created
    def enable_buttons(*_args) -> None:
        if user_var.get() != "Select Steam Account":
            pornify_button.config(state="normal")
            resteam_button.config(state="normal")

    user_var = tk.StringVar(root)
    user_var.trace("w", enable_buttons)
    user_selection_dropdown = ttk.Combobox(user_select_frame, state="readonly", textvariable=user_var, values=steam.usernames)
    user_selection_dropdown.set("Select Steam Account")
    user_selection_dropdown.pack(pady=5, fill="x")

    start_stop_frame = tk.Frame(run_frame)
    start_stop_frame.pack()

    pornify_progress_var = tk.IntVar()
    pornify_progressbar = ttk.Progressbar(run_frame, mode="determinate", maximum=len(steam.game_ids), variable=pornify_progress_var)
    pornify_button = ttk.Button(
        start_stop_frame,
        text="PORNIFY",
        command=lambda: Thread(target=lambda: asyncio.run(pornify(steam, user_var.get(), pornify_progress_var))).start(),
        bootstyle="success"
    )
    pornify_button.grid(row=0, column=0, ipadx=5, padx=(0,5))
    resteam_button = ttk.Button(start_stop_frame, text="RESTEAM", command=lambda: resteam(steam, user_var.get()))
    resteam_button.grid(row=0, column=1, ipadx=5, padx=(5,0))
    # Initially disable buttons to wait for user to be properly selected
    pornify_button.config(state="disabled")
    resteam_button.config(state="disabled")
    pornify_progressbar.pack(pady=5, fill="x")

    root.mainloop()
