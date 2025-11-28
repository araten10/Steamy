from tkinter import Tk
from tkinter import ttk

from tkinter import (
    GROOVE,
    RAISED,
    Button,
    Checkbutton,
    Frame,
    Label,
    OptionMenu,
    Scale,
    StringVar,
    Text,
)

if __name__ == "__main__":
    root = Tk()
    root.geometry('320x240')
    
    ttk.Button(root, text='Pornify').pack(pady=5, ipady=10, ipadx=5, expand=1)
    root.mainloop()
